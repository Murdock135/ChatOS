"""Checkout entrypoint for chatos.maintenance.design_archive."""

import sys
from pathlib import Path

repository = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "src/chatos").is_dir()
)
sys.path.insert(0, str(repository / "src"))

from chatos.maintenance.design_archive import create_archive, main, verify_archive  # noqa: F401

if __name__ == "__main__":
    main()
