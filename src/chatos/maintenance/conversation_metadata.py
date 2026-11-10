"""Read observed metadata for a specified captured Codex conversation."""

import argparse
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from chatos.workspace import default_root


def iso(seconds):
    return (
        datetime.fromtimestamp(seconds, timezone.utc).isoformat()
        if seconds is not None
        else None
    )


def extract(thread_id, codex_home):
    db = codex_home / "state_5.sqlite"
    connection = sqlite3.connect(db.as_uri() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        row = connection.execute(
            "SELECT id,title,cwd,model,model_provider,reasoning_effort,created_at,updated_at,"
            "rollout_path,source,cli_version FROM threads WHERE id=?",
            (thread_id,),
        ).fetchone()
    finally:
        connection.close()
    if row is None:
        raise ValueError("Conversation ID not found; no files changed.")
    row = dict(row)
    session = Path(row["rollout_path"])
    history, session_meta, last_timestamp = [], {}, None
    partial_lines = 0
    if session.is_file():
        with session.open() as f:
            for line in f:
                try:
                    event = json.loads(line)
                except ValueError:
                    partial_lines += 1
                    continue
                last_timestamp = event.get("timestamp") or last_timestamp
                payload = event.get("payload") or {}
                if event.get("type") == "session_meta":
                    if payload.get("id") != thread_id:
                        raise ValueError("Session ID mismatch; no files changed.")
                    session_meta = {
                        k: payload.get(k)
                        for k in [
                            "id",
                            "timestamp",
                            "originator",
                            "cli_version",
                            "source",
                            "model_provider",
                        ]
                    }
                elif event.get("type") == "turn_context":
                    history.append(
                        {
                            "turn_id": payload.get("turn_id"),
                            "timestamp": event.get("timestamp"),
                            "model": payload.get("model"),
                            "reasoning_effort": payload.get("effort")
                            or payload.get("reasoning_effort"),
                        }
                    )
    latest = history[-1] if history else {}
    return {
        "source_app": "Codex",
        "source_id": thread_id,
        "source_url": None,
        "source_title": row["title"],
        "created_at": session_meta.get("timestamp") or iso(row["created_at"]),
        "last_activity_at": last_timestamp or iso(row["updated_at"]),
        "metadata_checked_at": datetime.now(timezone.utc).isoformat(),
        "model": latest.get("model") or row["model"],
        "model_provider": session_meta.get("model_provider") or row["model_provider"],
        "reasoning_effort": latest.get("reasoning_effort") or row["reasoning_effort"],
        "model_evidence": "turn_context" if latest.get("model") else "thread_database",
        "workspace": row["cwd"],
        "client": session_meta.get("originator"),
        "client_version": session_meta.get("cli_version") or row["cli_version"],
        "source_kind": row["source"],
        "model_history": history,
        "evidence": {
            "database": str(db),
            "table": "threads",
            "row_id": thread_id,
            "session_path": str(session),
            "session_present": session.is_file(),
            "unparsed_lines": partial_lines,
        },
        "limits": [
            "Metadata snapshot of an ongoing conversation; later turns may differ.",
            "Internal execution model IDs do not verify UI labels or manual model selection.",
            "Transcript completeness is recorded separately in the conversation note.",
        ],
    }


def write_note(note, data):
    text = note.read_text()
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.DOTALL)
    if not match:
        raise ValueError("Conversation note needs YAML frontmatter; no files changed.")
    fields = {
        k: data[k]
        for k in [
            "source_app",
            "source_id",
            "source_url",
            "created_at",
            "last_activity_at",
            "metadata_checked_at",
            "model",
            "model_provider",
            "reasoning_effort",
            "workspace",
        ]
    }
    sidecar = note.with_suffix(".metadata.json")
    fields["metadata_file"] = sidecar.name
    original = match.group(1).splitlines()
    # Only replace known single-line properties; preserve topic lists and authored fields.
    kept = [
        line
        for line in original
        if not any(re.match(r"^" + re.escape(k) + r":", line) for k in fields)
    ]
    updated = "\n".join(
        kept + [k + ": " + json.dumps(v, ensure_ascii=False) for k, v in fields.items()]
    )
    updated = "---\n" + updated + "\n---\n" + text[match.end() :]
    sidecar.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    note.write_text(updated)
    return sidecar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--thread-id", required=True)
    parser.add_argument("--note", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=default_root())
    parser.add_argument("--codex-home", type=Path, default=Path.home() / ".codex")
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    candidate = args.note.expanduser()
    note = candidate.resolve() if candidate.exists() else (root / candidate).resolve()
    if not note.is_relative_to(root) or not note.is_file():
        parser.error(
            "--note must identify an existing file inside the selected workspace"
        )
    data = extract(args.thread_id, args.codex_home.expanduser().resolve())
    sidecar = write_note(note, data)
    print(
        json.dumps(
            {
                "source_id": data["source_id"],
                "model": data["model"],
                "turns_observed": len(data["model_history"]),
                "metadata_file": str(sidecar),
            }
        )
    )


if __name__ == "__main__":
    main()
