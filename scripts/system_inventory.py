"""Compatibility entrypoint; implementation is in the installed chatos package."""

from pathlib import Path
import sys

repository = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "src/chatos").is_dir()
)
sys.path.insert(0, str(repository / "src"))
from chatos.maintenance.system_inventory import check, refresh  # noqa: E402

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    options = parser.parse_args()
    result = check() if options.check else {"indexed_skills": len(refresh())}
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if not options.check or result["ok"] else 1)
