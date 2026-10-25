"""Package the Chief of Staff skill and bind exported copies to a selected workspace."""

from pathlib import Path
import shutil
import tempfile
from typing import Optional

from .onboarding import assistant_command
from .workspace import Workspace

BUNDLE = Path(__file__).with_name("skills") / "chatos"


def skill_files(root: Path) -> dict[str, str]:
    """Return public instructions plus a connection reference for the selected root."""
    root = root.expanduser().resolve()
    files = {
        name: (BUNDLE / name).read_text()
        for name in [
            "SKILL.md",
            "agents/openai.yaml",
            "references/connection.md",
            "references/operations.md",
        ]
    }
    command = assistant_command(root)
    files["references/connection.md"] = (
        "# This skill's ChatGrep connection\n\n"
        + "Workspace: "
        + str(root)
        + "\n\n"
        + "This binding selects a local archive; it does not install a host integration or grant permissions. "
        + "Verify chatos.json and the workspace's current ASSISTANT.md before using its scoped guidance. "
        + "If this workspace moves or you change installations, generate a new skill copy. "
        + "An explicit workspace in the current request takes precedence; verify it before switching.\n\n"
        + "Commands for this workspace:\n\n```bash\n"
        + command
        + " coverage --json\n"
        + command
        + ' retrieve "reading note format" --json\n'
        + command
        + " doctor --json\n```\n\n"
        + "The host must have local file and terminal access. If it cannot access this path, report that boundary and use a selected portable bundle instead.\n"
    )
    return files


def export_skill(root: Path, destination: Optional[Path] = None) -> dict:
    """Create a bound skill without replacing existing files or installing globally."""
    workspace = Workspace(root)
    if workspace.version != 2:
        raise ValueError(
            "Assistant skill preparation requires an initialized version-2 workspace"
        )
    target = (
        destination.expanduser().absolute()
        if destination is not None
        else workspace.path("shared_context/skills/chatos")
    )
    files = skill_files(workspace.root)
    if target.is_symlink():
        raise ValueError("Skill destination must not be a symlink")
    if target.exists():
        if not target.is_dir():
            raise ValueError("Skill destination must be a new directory")
        entries = list(target.rglob("*"))
        if any(path.is_symlink() for path in entries):
            raise ValueError("Existing skill symlinks are left untouched")
        existing = {
            path.relative_to(target).as_posix(): path.read_text()
            for path in entries
            if path.is_file()
        }
        if existing != files:
            raise ValueError(
                "Existing skill differs; choose a new destination to preserve its contents"
            )
        status = "unchanged"
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=".chatos-skill-", dir=target.parent))
        try:
            for relative, text in files.items():
                path = staging / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text)
            staging.rename(target)
        finally:
            if staging.exists():
                shutil.rmtree(staging)
        status = "skill_ready"
    return {
        "status": status,
        "path": str(target),
        "entrypoint": str(target / "SKILL.md"),
        "workspace": str(workspace.root),
        "host_activation_verified": False,
        "next": "Read SKILL.md directly, or copy this folder into your assistant's documented skill location and verify discovery. Invoke chatos explicitly for a first cited retrieval.",
    }
