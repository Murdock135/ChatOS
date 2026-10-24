"""Browser workflows for setup, reviewed context and local portable handoff."""

import json
from pathlib import Path
import tempfile
import uuid
from typing import Optional

from .core import Store, write_json
from .workspace import Workspace
from .context import import_artifact, accept_artifact, retire_artifact
from .onboarding import setup_status
from .portable import export_bundle


def setup_details(root: Path) -> dict:
    """Describe readiness and the source configuration without scanning a provider."""
    workspace = Workspace(root)
    if workspace.version != 2:
        return {
            "supported": False,
            "detail": "Initialize or migrate to layout version 2 for guided setup.",
        }
    return {
        "supported": True,
        **setup_status(root),
        "codex_path": workspace.config["sources"].get("codex", {}).get("path"),
    }


def configure_codex(root: Path, enabled: object, path: object) -> dict:
    """Save an explicit local-source choice; importing still requires a separate sync."""
    workspace = Workspace(root)
    if workspace.version != 2 or type(enabled) is not bool:
        raise ValueError("Expected a version-2 workspace and a boolean source choice")
    source = workspace.config["sources"].get("codex", {})
    selected = source.get("path")
    if enabled:
        if not isinstance(path, str) or not path.strip():
            raise ValueError("Choose the local Codex directory before enabling capture")
        directory = Path(path).expanduser()
        if not directory.is_absolute() or not directory.is_dir():
            raise ValueError("Codex source must be an existing absolute directory")
        selected = str(directory.resolve())
    workspace.config["sources"]["codex"] = {"enabled": enabled, "path": selected}
    write_json(workspace.path("chatos.json"), workspace.config)
    return {
        "status": "source_saved",
        "enabled": enabled,
        "path": selected,
        "detail": "Run Sync workspace to apply this source choice. Existing captured chats are retained.",
    }


def artifacts(root: Path, identity: Optional[str] = None) -> dict:
    """List review states, or return one retained artifact with its provenance."""
    workspace = Workspace(root)
    if workspace.version != 2:
        raise ValueError("Reviewed context requires a version-2 workspace")
    if identity is not None:
        if len(identity) != 64 or any(c not in "0123456789abcdef" for c in identity):
            raise ValueError("Expected a context artifact SHA-256 ID")
        source = workspace.path("shared_context/inbox") / (identity + ".json")
        if source.is_symlink() or not source.is_file():
            raise LookupError("Context artifact not found")
        record = json.loads(source.read_text())
        if record.get("id") != identity:
            raise ValueError("Context artifact identity mismatch")
        return record
    entries = []
    for file in sorted(workspace.path("shared_context/inbox").glob("*.json")):
        if file.is_symlink():
            continue
        record = json.loads(file.read_text())
        entries.append(
            {
                "id": record["id"],
                "kind": record["artifact"]["kind"],
                "review_status": record["review_status"],
                "imported_at": record["imported_at"],
            }
        )
    return {"items": entries}


def receive_artifact(store: Store, artifact: dict) -> dict:
    """Reuse the strict importer while removing the temporary upload after validation."""
    with tempfile.TemporaryDirectory(
        prefix="context-upload-", dir=store.state
    ) as directory:
        source = Path(directory) / "artifact.json"
        write_json(source, artifact)
        return import_artifact(store.root, source)


def review_artifact(
    store: Store, identity: object, note: object, retire: bool = False
) -> dict:
    """Accept explicitly reviewed context and refresh its local evidence passages."""
    if not isinstance(identity, str) or not isinstance(note, str):
        raise ValueError("Artifact ID and review note must be text")
    result = (retire_artifact if retire else accept_artifact)(
        store.root, identity, note
    )
    from .retrieval import refresh

    refresh(store)
    return result


def create_handoff(store: Store, data: dict) -> dict:
    """Write a selected handoff to a new folder inside this workspace's backups."""
    identities = data.get("conversations")
    project = data.get("project")
    all_chats = data.get("all", False)
    with_context = data.get("with_context", False)
    if identities is not None and (
        not isinstance(identities, list)
        or not all(isinstance(value, str) for value in identities)
    ):
        raise ValueError("Conversations must be a list of SOURCE:ID values")
    if project is not None and not isinstance(project, str):
        raise ValueError("Project must be a registered ID")
    if type(all_chats) is not bool or type(with_context) is not bool:
        raise ValueError("Selection and context choices must be booleans")
    destination = (
        store.paths.path("System/Backups") / "portable-handoffs" / uuid.uuid4().hex
    )
    return export_bundle(
        store, destination, identities, project, all_chats, with_context
    )
