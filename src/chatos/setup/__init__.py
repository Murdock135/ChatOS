"""Independent workspace initialization without eager service imports."""

from __future__ import annotations

from pathlib import Path


def initialize(destination: Path, codex_home: Path | None = None) -> dict:
    """Preserve the initializer API while avoiding an onboarding import cycle."""
    from .initialization import initialize as initialize_workspace

    return initialize_workspace(destination, codex_home)


__all__ = ["initialize"]
