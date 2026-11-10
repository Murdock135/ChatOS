"""Hash and verify experiment bundles independently of the optional ML runtime."""

import hashlib
import json
from pathlib import Path
from typing import Any


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    """Save finite JSON with stable formatting."""
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    )


def seal(directory: Path) -> None:
    """Record relative artifact paths; exclude the manifest's own circular hash."""
    files = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise ValueError("Experiment artifacts cannot contain symlinks")
        if path.is_file() and path != directory / "manifest.json":
            files[path.relative_to(directory).as_posix()] = file_hash(path)
    write_json(directory / "manifest.json", {"schema_version": 1, "files": files})


def verify(directory: Path) -> dict[str, Any]:
    """Reject missing, altered, extra, symlinked or escaping bundle files."""
    directory = directory.resolve()
    if (directory / "manifest.json").is_symlink():
        raise ValueError("The experiment manifest cannot be a symlink")
    manifest = json.loads((directory / "manifest.json").read_text())
    if manifest.get("schema_version") != 1 or not manifest.get("files"):
        raise ValueError("Invalid experiment manifest")
    for name, expected in manifest["files"].items():
        relative = Path(name)
        path = directory / relative
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Invalid experiment artifact path")
        if path.is_symlink() or not path.resolve().is_relative_to(directory):
            raise ValueError("Artifact escapes the experiment directory")
        if not path.is_file() or file_hash(path) != expected:
            raise ValueError("Experiment integrity mismatch: " + name)
    actual = set()
    for path in directory.rglob("*"):
        if path.is_symlink():
            raise ValueError("Experiment artifacts cannot contain symlinks")
        if path.is_file() and path != directory / "manifest.json":
            actual.add(path.relative_to(directory).as_posix())
    if actual != set(manifest["files"]):
        raise ValueError("Unrecorded experiment artifact files")
    result = json.loads((directory / "run.json").read_text())
    return {
        "status": result["status"],
        "integrity": "ok",
        "files": len(actual),
        "directory": str(directory),
    }
