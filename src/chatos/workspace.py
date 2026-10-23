"""Resolve explicit workspace versions without mixing application and user data."""

import json
import os
from pathlib import Path
from typing import Optional, Union

PathLike = Union[str, Path]
MANIFEST = "chatos.json"

# Legacy names are centralized here while older workspaces remain supported.
LOCATIONS = {
    "System/Skills/inventory.json": "app_data/state/skills/inventory.json",
    "System/Skills/Index.md": "library/Skills.md",
    "System/Memory/Working memory.md": "chief_of_staff/memory.md",
    "System/Operating guidance.md": "chief_of_staff/instructions.md",
    "System/Decisions.md": "chief_of_staff/decisions/README.md",
    "System/Feedback log.md": "chief_of_staff/feedback/log.md",
    "System/Latest snapshot.md": "app_data/latest-snapshot.md",
    "System/Projects": "chief_of_staff/projects",
    "System/Skills": "chief_of_staff/skills",
    "System/Feedback": "chief_of_staff/feedback",
    "System/Schedules": "library/schedules",
    "System/State": "app_data/state",
    "System/Logs": "app_data/logs",
    "System/Snapshots": "app_data/snapshots",
    "System/Models": "app_data/cache/models",
    "System/Backups": "backups",
    "System/Scripts": "chief_of_staff/reference/scripts",
    "System": "chief_of_staff/reference",
    "Conversations/Index.md": "library/Chats.md",
    "Projects": "library/projects",
    "Topics": "library/topics",
    "Humans": "library",
}


def default_root() -> Path:
    """Use an explicit override, or preserve the existing checkout workspace."""
    configured = os.environ.get("CHATOS_WORKSPACE")
    if configured:
        return Path(configured).expanduser().resolve()
    package = Path(__file__).resolve().parent
    checkout = package.parent.parent if package.parent.name == "src" else package.parent
    if (checkout / "workspace/chatos.json").is_file():
        config = json.loads((checkout / "workspace/chatos.json").read_text())
        if not config.get("migrated_from") or config.get("activated") is True:
            return checkout / "workspace"
    if (checkout / "System/State/chatos.sqlite3").exists():
        return checkout
    if (checkout / "pyproject.toml").exists():
        return checkout / "workspace"
    return Path.cwd() / "workspace"


class Workspace:
    """A selected workspace and its validated on-disk layout."""

    def __init__(self, root: PathLike):
        self.root = Path(root).expanduser().absolute()
        nested = self.root / "workspace" / MANIFEST
        if not (self.root / MANIFEST).exists() and nested.is_file():
            if json.loads(nested.read_text()).get("activated") is True:
                self.root = nested.parent
        manifest = self.root / MANIFEST
        self.config = json.loads(manifest.read_text()) if manifest.exists() else {}
        self.version = self.config.get("layout_version", 1)
        if type(self.version) is not int or self.version not in (1, 2):
            raise ValueError("Unsupported workspace layout version")
        if self.version == 2 and not isinstance(self.config.get("sources"), dict):
            raise ValueError("Workspace manifest must define sources")
        if self.version == 2:
            for name, settings in self.config["sources"].items():
                self.validate_source(name)
                if (
                    not isinstance(settings, dict)
                    or type(settings.get("enabled")) is not bool
                ):
                    raise ValueError("Each source needs a boolean enabled setting")

    def path(self, legacy: PathLike) -> Path:
        """Resolve a known workspace location, never an arbitrary absolute path."""
        relative = Path(legacy)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Workspace locations must be relative")
        if self.version == 2:
            name = relative.as_posix()
            for old in sorted(LOCATIONS, key=len, reverse=True):
                if name == old or name.startswith(old + "/"):
                    relative = Path(LOCATIONS[old]) / Path(name).relative_to(old)
                    break
        result = self.root / relative
        if (
            self.root.resolve() not in result.resolve().parents
            and result.resolve() != self.root.resolve()
        ):
            raise ValueError("Workspace location escapes through a symlink")
        return result

    def imports(self, source: str) -> Path:
        """Return a platform-specific export inbox."""
        self.validate_source(source)
        if self.version == 1:
            return self.path(Path("System/Imports") / source)
        return self.path(Path("your_ais") / source / "imports")

    def conversation(self, source: str, year: str, filename: str) -> Path:
        self.validate_source(source)
        if self.version == 1:
            return self.root / "Conversations" / year / filename
        return self.root / "your_ais" / source / "chats" / year / filename

    def annotations(self, source: str) -> Path:
        self.validate_source(source)
        if self.version == 1:
            return self.root / "Conversations/Annotations"
        return self.root / "your_ais" / source / "annotations"

    def enabled(self, source: str) -> bool:
        self.validate_source(source)
        return (
            self.version == 1
            or self.config["sources"].get(source, {}).get("enabled") is True
        )

    @staticmethod
    def validate_source(source: str) -> None:
        if source not in {"codex", "chatgpt", "muse"}:
            raise ValueError("Unsupported source: " + source)

    def codex_home(self, explicit: Optional[PathLike] = None) -> Path:
        """Select only configured sources in versioned workspaces."""
        if explicit is not None:
            return Path(explicit).expanduser().resolve()
        if self.version == 1:
            return Path.home() / ".codex"
        if self.enabled("codex"):
            source = self.config["sources"]["codex"].get("path")
            if not isinstance(source, str) or not Path(source).is_absolute():
                raise ValueError("Enabled Codex source needs an absolute path")
            return Path(source).expanduser().resolve()
        # A private empty directory keeps legacy readers away from the user's home.
        empty = self.path("System/State/disconnected-source")
        empty.mkdir(parents=True, exist_ok=True)
        return empty


def workspace_path(root: PathLike, legacy: PathLike) -> Path:
    """Resolve an operational location for either supported workspace layout."""
    return Workspace(root).path(legacy)
