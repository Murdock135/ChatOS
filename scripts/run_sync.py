"""Absolute-path entry point for launchd, independent of its Python import path."""

from pathlib import Path
import sys

repository = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "src/chatos").is_dir()
)
sys.path.insert(0, str(repository / "src"))
from chatos.runtime import sync  # noqa: E402

if __name__ == "__main__":
    import argparse
    from chatos.terminal import print_report

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    options = parser.parse_args()
    try:
        result = sync()
        print_report(result, "sync", options.json)
        raise SystemExit(0 if result["status"] == "ok" else 1)
    except BlockingIOError:
        print_report({"status": "already_running"}, "sync", options.json)
