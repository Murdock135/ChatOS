"""Compatibility entrypoint; implementation is in the installed chatos package."""

from pathlib import Path
import sys

repository = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "src/chatos").is_dir()
)
sys.path.insert(0, str(repository / "src"))
from chatos.maintenance.snapshot_codex_state import create_snapshot  # noqa: E402

if __name__ == "__main__":
    import json

    print(json.dumps(create_snapshot()))
