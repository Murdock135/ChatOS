"""Reconcile API projections with retained local Codex evidence."""

import re
from datetime import datetime
from difflib import SequenceMatcher

from chatos.core import redact


def merge_codex(previous: dict, incoming: dict) -> dict:
    """Retain unmatched messages and enrich matches without inventing model evidence.

    Source IDs can differ between JSONL and API projections. Align exact visible
    bodies in sequence, including repeated messages, rather than deduplicating text.
    When sources disagree between anchors, preserve both and disclose the ambiguity.
    """
    incoming_is_older = False
    try:
        incoming_is_older = datetime.fromisoformat(
            incoming["updated_at"].replace("Z", "+00:00")
        ) < datetime.fromisoformat(previous["updated_at"].replace("Z", "+00:00"))
    except (KeyError, TypeError, ValueError, AttributeError):
        pass
    old, new = previous["messages"], incoming["messages"]

    def aliases(message: dict) -> set[str]:
        return {
            identity
            for identity in message.get("source_item_ids", [message["id"]])
            if not identity.startswith(("line-", "message-"))
        }

    old_ids = {identity for message in old for identity in aliases(message)}
    new_ids = {identity for message in new for identity in aliases(message)}
    common_ids = old_ids & new_ids

    def body(message: dict) -> str:
        text = redact(message["text"])
        # The API separates memory citations and image markers from rendered text.
        # Ignore only those known wrappers while aligning; keep original text below.
        text = re.sub(r"<oai-mem-citation>[\s\S]*?</oai-mem-citation>", "", text)
        text = re.sub(r"<image name=[^>]*>\s*</image>", "", text)
        return text.strip()

    def key(message: dict):
        shared = aliases(message) & common_ids
        if shared:
            return ("id", message["role"], min(shared))
        text = body(message)
        return (
            "body",
            message["role"],
            text,
            "" if text else str(message.get("attachments", [])),
        )

    matcher = SequenceMatcher(
        a=[key(m) for m in old], b=[key(m) for m in new], autojunk=False
    )
    messages, ambiguous = [], False
    for operation, a, b, c, d in matcher.get_opcodes():
        if operation == "equal":
            for before, after in zip(old[a:b], new[c:d]):
                # New source text can revise a stable item; null projection metadata
                # must not erase observed per-message model/lineage from JSONL.
                first, last = (after, before) if incoming_is_older else (before, after)
                merged = {**first, **{k: v for k, v in last.items() if v is not None}}
                if body(before) == body(after) and len(before["text"]) > len(
                    after["text"]
                ):
                    merged["text"] = before["text"]
                merged["id"] = before["id"]
                source_ids = sorted(
                    set(before.get("source_item_ids", [before["id"]]))
                    | set(after.get("source_item_ids", [after["id"]]))
                )
                if len(source_ids) > 1:
                    merged["source_item_ids"] = source_ids
                messages.append(merged)
        else:
            messages.extend(old[a:b])
            messages.extend(new[c:d])
            if operation == "replace":
                ambiguous = True
    first, last = (incoming, previous) if incoming_is_older else (previous, incoming)
    result = {**first, **{k: v for k, v in last.items() if v is not None}}
    result.pop("file_path", None)
    result["messages"] = messages
    evidence = {**previous.get("evidence", {}), **incoming.get("evidence", {})}
    evidence["parser"] = "codex-combined-v1"
    evidence["alignment"] = (
        "exact_body_or_stable_id; unmatched source intervals retained"
    )
    if ambiguous or previous.get("evidence", {}).get("ordering_uncertain"):
        evidence["ordering_uncertain"] = True
    result["evidence"] = evidence
    result["capture"] = "combined_visible_sources"
    # A source with no per-turn evidence cannot clear previously observed history.
    result["model_history"] = incoming.get("model_history") or previous.get(
        "model_history", []
    )
    result["runs"] = incoming.get("runs") or previous.get("runs", [])
    result["limits"] = sorted(
        set(
            previous.get("limits", [])
            + incoming.get("limits", [])
            + [
                "Combined persisted API and local captures; unmatched intervals may have uncertain order.",
            ]
        )
    )
    return result
