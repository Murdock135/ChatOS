"""Summarize captured evidence without implying account-wide completeness."""

import json
from collections import Counter

from .core import Store, now


def report(store: Store) -> dict:
    """Read current records and the most recent source-scan evidence."""
    status_path = store.state / "status.json"
    status = json.loads(status_path.read_text()) if status_path.exists() else {}
    records = store.records()
    sources = {}
    for source in ["codex", "chatgpt", "muse"]:
        captured = [record for record in records if record["source"] == source]
        captured_ids = {record["id"] for record in captured}
        messages = [message for record in captured for message in record["messages"]]
        sources[source] = {
            "records": len(captured),
            "capture_types": dict(
                Counter(record.get("capture", "unspecified") for record in captured)
            ),
            "visible_messages": len(messages),
            "assistant_messages_without_model_metadata": sum(
                message["role"] == "assistant" and not message.get("model")
                for message in messages
            ),
            "last_scan": status.get("sources", {}).get(source),
        }
        if source == "codex":
            sources[source].update(
                fork_records=sum(
                    bool(record.get("evidence", {}).get("forked_from_id"))
                    for record in captured
                ),
                inherited_messages=sum(
                    message.get("inherited") is True for message in messages
                ),
                unavailable_rollout_files_last_scan=len(
                    status.get("unavailable_history", [])
                ),
                known_uncaptured_history_ids=[
                    item["id"]
                    for item in status.get("unrecovered_history", [])
                    if item["id"] not in captured_ids
                ],
            )
        if source == "chatgpt":
            sources[source]["unavailable_message_references"] = sum(
                len(record.get("evidence", {}).get("unavailable_message_text", []))
                for record in captured
            )
    return {
        "checked_at": now(),
        "last_sync": status.get("finished_at"),
        "last_sync_status": status.get("status", "never_run"),
        "sources": sources,
        "limits": [
            "Counts describe captured records and the last locally enumerated source scan, not all account history.",
            "Available visible messages are not proof of a full original transcript; missing rollout files may have partial projections or earlier retained captures.",
            "ChatGPT desktop windows and unavailable reply references remain partial even when no next page is returned.",
            "Muse raw export and ongoing capture remain deferred; source settings alone do not establish coverage.",
        ],
    }
