"""Download and verify the pinned optional embedding model; never read chat data."""

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from ..core import write_json
from ..dense import MODEL, REVISION
from ..workspace import default_root, workspace_path

WEIGHTS_SHA256 = "0437e45c94563b09e13cb7a64478fc406947a93cb34a7e05870fc8dcd48e23fd"
MODEL_FILES = [
    "config.json",
    "config_sentence_transformers.json",
    "modules.json",
    "sentence_bert_config.json",
    "1_Pooling/config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.json",
    "merges.txt",
    "model.safetensors",
]


def download(root: Path) -> dict[str, Any]:
    """Download public model files and publish a manifest after verification."""
    directory = workspace_path(root, "System/Models/qwen3-embedding-0.6b")
    os.environ.update(
        {
            "HF_HOME": str(workspace_path(root, "System/Models/hf-cache")),
            "HF_HUB_DISABLE_TELEMETRY": "1",
            "HF_HUB_DISABLE_IMPLICIT_TOKEN": "1",
            "DO_NOT_TRACK": "1",
        }
    )
    for name in ["HF_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HUGGINGFACEHUB_API_TOKEN"]:
        os.environ.pop(name, None)
    from huggingface_hub import snapshot_download

    snapshot_download(
        MODEL,
        revision=REVISION,
        local_dir=str(directory),
        token=False,
        allow_patterns=MODEL_FILES,
    )
    config = json.loads((directory / "config.json").read_text())
    modules = json.loads((directory / "modules.json").read_text())
    allowed = {
        "sentence_transformers.models.Transformer",
        "sentence_transformers.models.Pooling",
        "sentence_transformers.models.Normalize",
    }
    if (
        config.get("auto_map")
        or config.get("model_type") != "qwen3"
        or any(module["type"] not in allowed for module in modules)
    ):
        raise ValueError(
            "Unexpected custom model code/module configuration; model not enabled"
        )
    fingerprint = hashlib.sha256()
    with (directory / "model.safetensors").open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            fingerprint.update(block)
    if fingerprint.hexdigest() != WEIGHTS_SHA256:
        raise ValueError("Pinned model weight hash mismatch")
    report = {
        "model": MODEL,
        "revision": REVISION,
        "directory": str(directory),
        "weights_sha256": WEIGHTS_SHA256,
        "remote_code": False,
        "token": False,
        "source": "https://huggingface.co/Qwen/Qwen3-Embedding-0.6B",
        "note": "Verified model data; embeddings must be built separately.",
    }
    write_json(directory / "download-manifest.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=default_root())
    args = parser.parse_args()
    print(json.dumps(download(args.root), indent=2))


if __name__ == "__main__":
    main()
