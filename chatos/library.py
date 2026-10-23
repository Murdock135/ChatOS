"""Local library annotations, kept separate from captured source messages."""

import json
from pathlib import Path
from typing import Any
from .core import Store, atomic, now, safe_id


def initialize(store: Store) -> None:
    """Create annotation storage without modifying captured conversations."""
    store.db.execute("""CREATE TABLE IF NOT EXISTS library_annotations (
        source TEXT NOT NULL, id TEXT NOT NULL, title TEXT NOT NULL DEFAULT '',
        note TEXT NOT NULL DEFAULT '', archived INTEGER NOT NULL DEFAULT 0,
        updated_at TEXT NOT NULL, PRIMARY KEY(source,id))""")


def get(store: Store, source: str, identity: str) -> tuple[dict, dict]:
    """Return the captured record and its separate local annotations."""
    initialize(store)
    row = store.db.execute(
        "SELECT record_json FROM conversations WHERE source=? AND id=?",
        (source, identity),
    ).fetchone()
    if not row:
        raise ValueError("Conversation not captured")
    record = json.loads(row[0])
    saved = store.db.execute(
        "SELECT * FROM library_annotations WHERE source=? AND id=?", (source, identity)
    ).fetchone()
    annotation = (
        dict(saved)
        if saved
        else {
            "source": source,
            "id": identity,
            "title": "",
            "note": "",
            "archived": False,
            "updated_at": None,
        }
    )
    annotation["archived"] = bool(annotation["archived"])
    return record, annotation


def annotation_path(store: Store, source: str, identity: str) -> Path:
    return (
        store.root
        / "Conversations/Annotations"
        / (safe_id(source) + "-" + safe_id(identity) + ".md")
    )


def render(store: Store, annotation: dict) -> Path:
    """Publish a readable view; the database remains authoritative."""
    path = annotation_path(store, annotation["source"], annotation["id"])
    body = "# Local chat annotations\n\n"
    body += "Source: " + annotation["source"] + ":" + annotation["id"] + "\n"
    body += "Local title: " + annotation["title"] + "\n"
    body += "Archived in library: " + str(bool(annotation["archived"])) + "\n\n"
    body += annotation["note"] + "\n"
    atomic(path, body)
    return path


def update(store: Store, source: str, identity: str, changes: dict[str, Any]) -> dict:
    """Validate and save local changes while preserving the source record."""
    if not isinstance(changes, dict):
        raise ValueError("Changes must be a JSON object")
    _, annotation = get(store, source, identity)
    if set(changes) - {"title", "note", "archived"}:
        raise ValueError("Unknown annotation field")
    for field, maximum in [("title", 300), ("note", 100000)]:
        if field in changes and (
            not isinstance(changes[field], str) or len(changes[field]) > maximum
        ):
            raise ValueError(field + " is not valid text or exceeds its length limit")
    if "archived" in changes and not isinstance(changes["archived"], bool):
        raise ValueError("Archived must be true or false")
    annotation.update(changes)
    annotation["updated_at"] = now()
    with store.db:
        store.db.execute(
            "INSERT OR REPLACE INTO library_annotations VALUES(?,?,?,?,?,?)",
            (
                source,
                identity,
                annotation["title"],
                annotation["note"],
                int(annotation["archived"]),
                annotation["updated_at"],
            ),
        )
    render(store, annotation)
    return annotation


def list_chats(
    store: Store,
    query: str = "",
    source: str = "",
    project: str = "",
    archived: bool = False,
    offset: int = 0,
    limit: int = 50,
) -> dict:
    """Filter captured chats and annotations, returning a stable page."""
    initialize(store)
    matches = None
    if query.strip():
        matches = {
            (item["source"], item["conversation_id"])
            for item in store.search(query, 100000)
        }
    annotations = {
        (row["source"], row["id"]): dict(row)
        for row in store.db.execute("SELECT * FROM library_annotations")
    }
    words = query.lower().split()
    result = []
    for record in store.records():
        key = record["source"], record["id"]
        local = annotations.get(key, {})
        if bool(local.get("archived")) != archived:
            continue
        if source and record["source"] != source:
            continue
        if project and project not in record.get("projects", []):
            continue
        local_text = (local.get("title", "") + " " + local.get("note", "")).lower()
        if (
            matches is not None
            and key not in matches
            and not all(word in local_text for word in words)
        ):
            continue
        result.append(
            {
                "source": record["source"],
                "id": record["id"],
                "title": local.get("title") or record["title"],
                "source_title": record["title"],
                "updated_at": record.get("updated_at"),
                "projects": record.get("projects", []),
                "capture": record.get("capture"),
                "messages": len(record["messages"]),
                "has_note": bool(local.get("note")),
                "archived": bool(local.get("archived")),
            }
        )
    result.sort(
        key=lambda item: (item.get("updated_at") or "", item["id"]), reverse=True
    )
    return {
        "total": len(result),
        "items": result[offset : offset + limit],
        "offset": offset,
        "limit": limit,
    }


def restore_annotations(store: Store) -> None:
    """Regenerate readable annotations from a restored database."""
    initialize(store)
    for row in store.db.execute("SELECT * FROM library_annotations"):
        render(store, dict(row))
