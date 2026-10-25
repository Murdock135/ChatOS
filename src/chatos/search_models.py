"""User-selected local model downloads and offline inference adapters."""

import hashlib
import importlib.util
import json
import math
import re
import threading
from functools import lru_cache
from pathlib import Path
from typing import Any

from .core import digest, write_json
from .workspace import workspace_path

DEFAULTS = {
    "embedding": {
        "model_id": "sentence-transformers/all-MiniLM-L6-v2",
        "revision": "main",
        "max_length": 256,
        "query_prompt": "",
        "document_prompt": "",
    },
    "reranker": {
        "model_id": "cross-encoder/ms-marco-MiniLM-L-6-v2",
        "revision": "main",
        "max_length": 512,
    },
    "candidate_limit": 60,
    "minimum_score": None,
}


def config_path(root: Path) -> Path:
    return workspace_path(root, "System/State/search-models.json")


def validate(data: dict) -> dict:
    """Validate settings without downloading anything or importing model runtimes."""
    if not isinstance(data, dict) or set(data) != set(DEFAULTS):
        raise ValueError(
            "Expected embedding, reranker, candidate_limit and minimum_score"
        )
    result = json.loads(json.dumps(data))
    for kind in ("embedding", "reranker"):
        spec = result[kind]
        if not isinstance(spec, dict) or set(spec) != set(DEFAULTS[kind]):
            raise ValueError("Invalid " + kind + " settings")
        if (
            not isinstance(spec["model_id"], str)
            or not re.fullmatch(r"[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+", spec["model_id"])
            or ".." in spec["model_id"]
        ):
            raise ValueError(
                "Use a public Hugging Face model ID such as organization/model"
            )
        if not isinstance(spec["revision"], str) or not re.fullmatch(
            r"[A-Za-z0-9_.-]{1,100}", spec["revision"]
        ):
            raise ValueError("Revision must be a branch, tag or commit ID")
        if type(spec["max_length"]) is not int or not 32 <= spec["max_length"] <= 8192:
            raise ValueError("Model text limit must be between 32 and 8192 tokens")
        for key in ("query_prompt", "document_prompt") if kind == "embedding" else ():
            if not isinstance(spec[key], str) or len(spec[key]) > 2000:
                raise ValueError(
                    "Model prompts must be text of at most 2000 characters"
                )
    if (
        type(result["candidate_limit"]) is not int
        or not 10 <= result["candidate_limit"] <= 200
    ):
        raise ValueError("Candidate limit must be between 10 and 200")
    cutoff = result["minimum_score"]
    if cutoff is not None and (
        type(cutoff) not in (int, float) or not math.isfinite(cutoff)
    ):
        raise ValueError("Minimum score must be a finite number or null")
    return result


def settings(root: Path) -> dict:
    path = config_path(root)
    return validate(json.loads(path.read_text()) if path.exists() else DEFAULTS)


def save(root: Path, data: dict) -> dict:
    config = validate(data)
    write_json(config_path(root), config)
    with _MODEL_LOAD_LOCK:
        _load_model.cache_clear()
    return config


def model_directory(root: Path, spec: dict) -> Path:
    key = digest([spec["model_id"], spec["revision"]])[:24]
    return workspace_path(root, "System/Models/search") / key


def manifest(root: Path, spec: dict) -> dict:
    path = model_directory(root, spec) / "chatos-model.json"
    if not path.exists():
        raise ValueError("Download the selected model first: " + spec["model_id"])
    data = json.loads(path.read_text())
    if (
        data.get("model_id") != spec["model_id"]
        or data.get("requested_revision") != spec["revision"]
    ):
        raise ValueError("Model manifest does not match the selected model")
    return data


def fingerprint(root: Path, spec: dict) -> str:
    return digest([spec, manifest(root, spec)])


def validate_files(directory: Path) -> None:
    """Support library-owned architectures and safetensors, never remote Python."""
    if not list(directory.rglob("*.safetensors")):
        raise ValueError(
            "This model has no safetensors weights; choose a compatible model"
        )
    for path in directory.rglob("*.json"):
        if ".cache" in path.parts or path.name == "tokenizer.json":
            continue
        data = json.loads(path.read_text())
        if isinstance(data, dict) and data.get("auto_map"):
            raise ValueError(
                "This model requires custom code; choose a library-supported model"
            )
    modules_path = directory / "modules.json"
    if modules_path.exists():
        allowed = {"Transformer", "Pooling", "Normalize", "Dense"}
        for module in json.loads(modules_path.read_text()):
            if module.get("type") not in {
                "sentence_transformers.models." + name for name in allowed
            }:
                raise ValueError(
                    "Unsupported Sentence Transformers module: "
                    + str(module.get("type"))
                )
            relative = Path(module.get("path", ""))
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("Model module path is outside its download")


def download(root: Path, kind: str) -> dict:
    """Download public model data, pin the resolved commit and record file hashes."""
    if kind not in ("embedding", "reranker"):
        raise ValueError("Select embedding or reranker")
    try:
        from huggingface_hub import HfApi, snapshot_download
    except ImportError as error:
        raise ValueError(
            "Install the optional search dependencies before downloading models"
        ) from error
    spec = settings(root)[kind]
    directory = model_directory(root, spec)
    old_manifest = directory / "chatos-model.json"
    if old_manifest.exists():
        return manifest(root, spec)
    info = HfApi().model_info(spec["model_id"], revision=spec["revision"], token=False)
    snapshot_download(
        spec["model_id"],
        revision=info.sha,
        token=False,
        local_dir=str(directory),
        allow_patterns=[
            "*.json",
            "*.safetensors",
            "*.txt",
            "*.model",
            "*.vocab",
            "*.merges",
        ],
        ignore_patterns=["onnx/*", "openvino/*", "*.bin", "*.py", ".git/*"],
    )
    validate_files(directory)
    files = {}
    for path in sorted(directory.rglob("*")):
        if path.is_file() and ".cache" not in path.relative_to(directory).parts:
            checksum = hashlib.sha256()
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    checksum.update(block)
            files[path.relative_to(directory).as_posix()] = checksum.hexdigest()
    report = {
        "model_id": spec["model_id"],
        "requested_revision": spec["revision"],
        "resolved_revision": info.sha,
        "files": files,
    }
    write_json(old_manifest, report)
    return report


def status(root: Path) -> dict:
    config = settings(root)
    downloaded = {}
    for kind in ("embedding", "reranker"):
        try:
            downloaded[kind] = manifest(root, config[kind])["resolved_revision"]
        except ValueError:
            downloaded[kind] = None
    return {
        "settings": config,
        "downloaded": downloaded,
        "runtime_ready": importlib.util.find_spec("sentence_transformers") is not None,
    }


_MODEL_LOAD_LOCK = threading.Lock()


def load_model(
    root: str, kind: str, serialized_spec: str, model_fingerprint: str
) -> Any:
    """Serialize cold loads, including cache lookup, across request threads."""
    # Runtime initialization changes process-wide state; concurrent cold loads
    # can leave tensors uninitialized. lru_cache alone permits duplicate misses.
    with _MODEL_LOAD_LOCK:
        return _load_model(root, kind, serialized_spec, model_fingerprint)


@lru_cache(maxsize=2)
def _load_model(
    root: str, kind: str, serialized_spec: str, model_fingerprint: str
) -> Any:
    """Load explicitly downloaded weights offline; cache only the selected models."""
    del model_fingerprint  # Cache identity includes the exact download and settings.
    spec = json.loads(serialized_spec)
    directory = model_directory(Path(root), spec)
    saved = manifest(Path(root), spec)
    for relative, checksum in saved["files"].items():
        path = (directory / relative).resolve()
        try:
            path.relative_to(directory.resolve())
        except ValueError:
            raise ValueError("Invalid model file path")
        hasher = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                hasher.update(block)
        if hasher.hexdigest() != checksum:
            raise ValueError("Downloaded model file changed: " + relative)
    validate_files(directory)
    try:
        import torch
        from sentence_transformers import CrossEncoder, SentenceTransformer
    except ImportError as error:
        raise ValueError(
            "Install optional search dependencies and restart ChatOS in that environment"
        ) from error
    torch.set_num_threads(4)
    try:
        if kind == "embedding":
            model = SentenceTransformer(
                str(directory),
                local_files_only=True,
                trust_remote_code=False,
                token=False,
            )
            model.max_seq_length = spec["max_length"]
        else:
            model = CrossEncoder(
                str(directory),
                max_length=spec["max_length"],
                local_files_only=True,
                trust_remote_code=False,
                token=False,
            )
            if getattr(model, "num_labels", 1) != 1:
                raise ValueError(
                    "Choose a reranker that returns one relevance score per passage"
                )
        return model
    except (OSError, TypeError, ValueError, RuntimeError, NotImplementedError) as error:
        raise ValueError(
            "Selected "
            + kind
            + " model is incompatible with this runtime: "
            + str(error)
        ) from error


def model(root: Path, kind: str, config: dict) -> Any:
    spec = config[kind]
    return load_model(
        str(root), kind, json.dumps(spec, sort_keys=True), fingerprint(root, spec)
    )
