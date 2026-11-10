"""Checkout entrypoint for chatos.maintenance.app_control."""

import sys
from pathlib import Path

repository = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "src/chatos").is_dir()
)
sys.path.insert(0, str(repository / "src"))

from chatos.maintenance.app_control import main

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(2)
