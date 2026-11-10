"""Checkout entrypoint for chatos.experiments.topic_map."""

import sys
from pathlib import Path

repository = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "src/chatos").is_dir()
)
sys.path.insert(0, str(repository / "src"))

from chatos.experiments.topic_map import build, main  # noqa: F401

if __name__ == "__main__":
    main()
