"""Import inspectable AI-prepared context without activating it as instructions."""

import hashlib
import json
import stat
import uuid
from datetime import datetime
from pathlib import Path

from .core import atomic, now, redact, write_json
from .workspace import Workspace

MAX_BYTES = 1024 * 1024


def _append_review(record: dict, status: str, review_note: str) -> None:
    """Keep earlier review evidence, including envelopes predating review history."""
    if "review_history" not in record:
        record["review_history"] = []
        if record.get("reviewed_at"):
            record["review_history"].append(
                {
                    "status": record["review_status"],
                    "reviewed_at": record["reviewed_at"],
                    "review_note": record.get("review_note", ""),
                }
            )
    reviewed_at = now()
    record["review_history"].append(
        {
            "status": status,
            "reviewed_at": reviewed_at,
            "review_note": redact(review_note),
        }
    )
    record.update(
        review_status=status, reviewed_at=reviewed_at, review_note=redact(review_note)
    )


def import_artifact(root: Path, source: Path) -> dict:
    """Validate a context envelope and retain it as unreviewed workspace data."""
    workspace = Workspace(root)
    if workspace.version != 2:
        raise ValueError("Context artifacts require an initialized version-2 workspace")
    if (
        source.is_symlink()
        or not stat.S_ISREG(source.stat().st_mode)
        or source.stat().st_size > MAX_BYTES
    ):
        raise ValueError("Context artifact must be a regular JSON file up to 1 MiB")
    with source.open("rb") as stream:
        payload = stream.read(MAX_BYTES + 1)
    if len(payload) > MAX_BYTES:
        raise ValueError("Context artifact exceeds 1 MiB")
    artifact = json.loads(payload)
    if not isinstance(artifact, dict) or (
        type(artifact.get("schema_version")) is not int
        or artifact["schema_version"] != 1
    ):
        raise ValueError("Expected context artifact schema_version 1")
    required = {
        "schema_version",
        "kind",
        "body",
        "created_at",
        "generated_by",
        "source_references",
        "uncertainties",
    }
    if set(artifact) != required:
        raise ValueError("Context artifact fields do not match the documented schema")
    if not isinstance(artifact["kind"], str) or artifact["kind"] not in {
        "profile",
        "preferences",
        "project_context",
    }:
        raise ValueError("Unsupported context artifact kind")
    for name in ["body", "created_at", "generated_by"]:
        if not isinstance(artifact[name], str) or not artifact[name].strip():
            raise ValueError(name + " must be non-empty text")
    created = datetime.fromisoformat(artifact["created_at"].replace("Z", "+00:00"))
    if created.tzinfo is None:
        raise ValueError("created_at must include a timezone")
    for name in ["source_references", "uncertainties"]:
        if not isinstance(artifact[name], list) or not all(
            isinstance(item, str) for item in artifact[name]
        ):
            raise ValueError(name + " must be a list of text values")
    # The source hash identifies the submitted file; retained text uses archive redaction.
    identity = hashlib.sha256(payload).hexdigest()
    path = workspace.path("shared_context/inbox") / (identity + ".json")
    retained = json.loads(redact(json.dumps(artifact, ensure_ascii=False)))
    retained_hash = hashlib.sha256(
        json.dumps(retained, sort_keys=True).encode()
    ).hexdigest()
    record = {
        "id": identity,
        "imported_at": now(),
        "source_sha256": identity,
        "retained_sha256": retained_hash,
        "review_status": "unreviewed",
        "active_instructions": False,
        "artifact": retained,
    }
    if not path.exists():
        write_json(path, record)
    else:
        if path.is_symlink():
            raise ValueError("Context inbox entries must not be symlinks")
        record = json.loads(path.read_text())
    return {
        "status": record["review_status"],
        "id": identity,
        "path": str(path),
        "active_instructions": False,
    }


def accept_artifact(root: Path, identity: str, review_note: str) -> dict:
    """Record explicit review and publish a cited context note, never a host rule."""
    if len(identity) != 64 or any(char not in "0123456789abcdef" for char in identity):
        raise ValueError("Expected a context artifact SHA-256 ID")
    if not review_note.strip() or len(review_note) > 4000:
        raise ValueError("An explicit review note is required (up to 4000 characters)")
    workspace = Workspace(root)
    if workspace.version != 2:
        raise ValueError("Context artifacts require a version-2 workspace")
    source = workspace.path("shared_context/inbox") / (identity + ".json")
    if source.is_symlink():
        raise ValueError("Context inbox entries must not be symlinks")
    record = json.loads(source.read_text())
    if record["id"] != identity or record["source_sha256"] != identity:
        raise ValueError("Context artifact identity mismatch")
    artifact = record["artifact"]
    if hashlib.sha256(
        json.dumps(artifact, sort_keys=True).encode()
    ).hexdigest() != record.get("retained_sha256"):
        raise ValueError(
            "Retained context changed; import the revised artifact for review"
        )
    _append_review(record, "accepted", review_note)
    target = workspace.path("shared_context/accepted") / (identity + ".md")
    note = "# Reviewed " + artifact["kind"] + "\n\n"
    note += "AI-prepared context, reviewed for reuse. This is not a provider memory export or an active host instruction.\n\n"
    note += "Artifact ID/source SHA-256: `" + identity + "`\n\n"
    note += (
        "Generated by: "
        + artifact["generated_by"]
        + "\n\nCreated: "
        + artifact["created_at"]
        + "\n\n"
    )
    note += "Review note: " + record["review_note"] + "\n\n" + artifact["body"] + "\n\n"
    note += (
        "## Source references\n\n"
        + "\n".join("- " + item for item in artifact["source_references"])
        + "\n\n"
    )
    note += (
        "## Uncertainties\n\n"
        + "\n".join("- " + item for item in artifact["uncertainties"])
        + "\n"
    )
    write_json(source, record)
    atomic(target, note)
    return {
        "status": "accepted",
        "id": identity,
        "path": str(target),
        "active_instructions": False,
    }


def retire_artifact(root: Path, identity: str, review_note: str) -> dict:
    """Stop reusing context while preserving the artifact, review and published note."""
    if len(identity) != 64 or any(char not in "0123456789abcdef" for char in identity):
        raise ValueError("Expected a context artifact SHA-256 ID")
    if not review_note.strip() or len(review_note) > 4000:
        raise ValueError(
            "An explicit retirement note is required (up to 4000 characters)"
        )
    workspace = Workspace(root)
    if workspace.version != 2:
        raise ValueError("Context artifacts require a version-2 workspace")
    source = workspace.path("shared_context/inbox") / (identity + ".json")
    if source.is_symlink():
        raise ValueError("Context inbox entries must not be symlinks")
    record = json.loads(source.read_text())
    if record.get("id") != identity or record.get("source_sha256") != identity:
        raise ValueError("Context artifact identity mismatch")
    if record.get("review_status") == "retired":
        return {"status": "retired", "id": identity, "active_instructions": False}
    note = workspace.path("shared_context/accepted") / (identity + ".md")
    if note.is_symlink():
        raise ValueError("Accepted context must not be a symlink")
    retained = None
    if note.exists():
        retained = (
            workspace.path("shared_context/retired")
            / identity
            / (uuid.uuid4().hex + ".md")
        )
        retained.parent.mkdir(parents=True, exist_ok=True)
        note.rename(retained)
    _append_review(record, "retired", review_note)
    try:
        write_json(source, record)
    except OSError:
        if retained is not None:
            retained.rename(note)
        raise
    return {"status": "retired", "id": identity, "active_instructions": False}
