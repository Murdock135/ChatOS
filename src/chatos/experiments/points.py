"""Source-linked topic points for an unclustered, local representation experiment."""

import hashlib
import json
from pathlib import Path
from typing import Any


def exchanges(record: dict[str, Any]) -> list[list[dict[str, Any]]]:
    """Reproduce the saved pilot's exchange numbering without changing text."""
    groups: list[list[dict[str, Any]]] = []
    for message in record.get("messages", []):
        if message.get("role") not in ("user", "assistant") or not message.get("text"):
            continue
        if message["role"] == "user" or not groups:
            groups.append([])
        groups[-1].append(message)
    return groups


def topic_points(
    record: dict[str, Any], response: dict[str, Any]
) -> list[dict[str, Any]]:
    """Retain separate subject vectors and validated chronological segment links."""
    if response.get("pilot_id") != record["pilot_id"]:
        raise ValueError("Response identity does not match the frozen conversation")
    if response.get("source_sha256") != record["source_sha256"]:
        raise ValueError("Response source hash does not match the frozen conversation")
    validation = response.get("validation", {})
    if (
        not validation.get("contract_valid")
        or response.get("status") != "completed"
        or response.get("stop_reason") == "max_tokens"
    ):
        raise ValueError("Response is incomplete or failed the saved contract checks")
    summary = validation["summary"]
    main_subject = summary["main_subject"]
    if not isinstance(main_subject, str) or not main_subject.strip():
        raise ValueError("A main subject is required")
    groups = exchanges(record)
    parent = response["model"] + ":" + record["pilot_id"] + ":main"
    shared = {
        "model": response["model"],
        "pilot_id": record["pilot_id"],
        "source": record["source"],
        "conversation_id": record["id"],
        "source_sha256": record["source_sha256"],
        "title": record.get("title", ""),
        "file_path": record.get("file_path"),
        "capture": record.get("capture"),
        "capture_caveat": summary.get("capture_caveat"),
    }
    points = [
        {
            **shared,
            "id": parent,
            "kind": "main",
            "parent_id": None,
            "label": main_subject,
            "embedding_text": main_subject,
            "description": summary["semantic_summary"],
            "start_exchange": 1,
            "end_exchange": len(groups),
            "evidence_exchanges": [],
        }
    ]
    expected_start = 1
    for index, segment in enumerate(summary["subtopics"], 1):
        start, end = segment["start_exchange"], segment["end_exchange"]
        evidence = segment["evidence_exchanges"]
        if (
            type(start) is not int
            or type(end) is not int
            or start != expected_start
            or end < start
            or end > len(groups)
            or any(type(i) is not int or not start <= i <= end for i in evidence)
        ):
            raise ValueError(
                "Subtopic ranges or evidence do not match source exchanges"
            )
        subject = segment["subject"]
        if not isinstance(subject, str) or not subject.strip():
            raise ValueError("A subtopic subject is required")
        # A short subject carries meaning; title, operation and prose remain metadata.
        points.append(
            {
                **shared,
                "id": parent + ":" + str(index),
                "kind": "subtopic",
                "parent_id": parent,
                "label": subject,
                "embedding_text": subject,
                "segment_title": segment["title"],
                "operation": segment["operation"],
                "description": segment["summary"],
                "start_exchange": start,
                "end_exchange": end,
                "evidence_exchanges": evidence,
            }
        )
        expected_start = end + 1
    if expected_start != len(groups) + 1:
        raise ValueError("Subtopics do not cover all available exchanges")
    return points


def load_points(pilot: Path) -> tuple[dict[str, list[dict[str, Any]]], list[dict]]:
    """Read saved responses without choosing a winning summarizer or using fallbacks."""
    records = {
        record["pilot_id"]: record
        for record in json.loads((pilot / "sample.json").read_text())
    }
    grouped: dict[str, list[dict[str, Any]]] = {}
    excluded = []
    for path in sorted((pilot / "responses").glob("*.json")):
        response = json.loads(path.read_text())
        key = response.get("model", "unknown")
        try:
            points = topic_points(records[response["pilot_id"]], response)
        except (KeyError, ValueError, TypeError) as error:
            excluded.append({"response": path.name, "reason": str(error)})
            continue
        grouped.setdefault(key, []).extend(points)
    if not grouped:
        raise ValueError("No complete, source-matched topic summaries were found")
    return grouped, excluded


def embedded_json(value: Any) -> str:
    """Keep imported text inert inside an HTML script data element."""
    return (
        json.dumps(value, ensure_ascii=False, allow_nan=False)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )


def sha256(path: Path) -> str:
    """Hash a saved input or artifact for the experiment manifest."""
    return hashlib.sha256(path.read_bytes()).hexdigest()
