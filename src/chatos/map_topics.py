"""Deterministic, source-grounded topic labels for experimental map groups."""

import math
import re
from collections import Counter, defaultdict
from typing import Any

from .semantic import tokens
from .visibility import HARNESS

LABEL_VERSION = "distinctive-source-phrases-v2"
_GENERIC = set(
    "help question questions explain thanks thank chat conversation please today work working make implement want know would could code using need file files update updated project user assistant text message messages attached screenshot instructions context system output request".split()
)


_GENERIC.update(
    {
        "content",
        "content_type",
        "input_text",
        "output_text",
        "role",
        "user_instructions",
        "ambient-ui-state",
        "block",
        "active",
        "tabs",
        "open",
        "setup",
        "png",
        "var",
        "folders",
        "users",
        "zayan",
        "instructions",
        "environment",
        "image",
        "attachment",
        "true",
        "false",
        "null",
    }
)


def topic_text(text: str) -> str:
    """Remove recognized capture wrappers from derived topic input only."""
    text = text.strip()
    wrappers = (
        "## Referenced",
        "## Prior conversation",
        "# Files mentioned",
        "<in-app-browser-context",
    )
    if text.startswith(wrappers):
        if "## My request:" not in text:
            return ""
        text = text.split("## My request:", 1)[1].strip()
    text = re.sub(r"\[@?[^\]]+\]\((?:plugin|app)://[^)]+\)", "", text)
    if text.startswith(
        HARNESS + ("<ambient-ui-state", "<ambient_ui_state", "<user_instructions>")
    ):
        return ""
    if text.startswith("<heartbeat>"):
        match = re.search(r"<instructions>(.*?)</instructions>", text, re.S)
        text = match[1] if match else ""
    # Paths and capture keys are provenance, not the subject of a conversation.
    text = re.sub(r"(?<![\w:])(?:/|~/)[^\s<>\"']+", " ", text)
    return text.strip()


def semantic_samples(record: dict[str, Any]) -> tuple[list[str], bool]:
    """Take bounded, evenly spaced user samples, with an explicit assistant fallback."""
    users = [
        topic_text(m.get("text", ""))
        for m in record.get("messages", [])
        if m.get("role") == "user"
    ]
    users = [text for text in users if text]
    fallback = not users
    if fallback:
        users = [
            topic_text(m.get("text", ""))
            for m in record.get("messages", [])
            if m.get("role") == "assistant"
        ]
        users = [text for text in users if text]
    positions = (
        sorted({round(i * (len(users) - 1) / 11) for i in range(12)}) if users else []
    )
    title = topic_text(record.get("title", ""))
    # Very long auto-titles are often truncated wrappers rather than useful subjects.
    title = title if len(title) <= 240 and not title.startswith(("{", "<")) else ""
    samples = ([title] if title else []) + [users[i][:900] for i in positions]
    return samples, fallback


def terms(record: dict[str, Any]) -> tuple[set[str], set[str]]:
    """Use the same distributed, wrapper-free source sample for topic naming."""
    samples, _ = semantic_samples(record)
    title = topic_text(record.get("title", ""))
    candidates: set[str] = set()
    title_terms: set[str] = set()
    for text in samples:
        words = [
            w
            for w in tokens(text)
            if w not in _GENERIC
            and not w.startswith(("http", "www"))
            and not (len(w) > 14 and any(c.isdigit() for c in w))
        ]
        found = set(words)
        found.update(" ".join(words[i : i + 2]) for i in range(len(words) - 1))
        candidates.update(found)
        if text == title:
            title_terms = found
    return candidates, title_terms


def label_groups(
    records: list[dict[str, Any]], memberships: list[str]
) -> dict[str, str]:
    """Rank shared phrases against corpus frequency, with bounded per-chat votes."""
    background: Counter[str] = Counter()
    grouped: dict[str, list[tuple[set[str], set[str]]]] = defaultdict(list)
    for record, group in zip(records, memberships):
        sample = terms(record)
        background.update(sample[0])
        grouped[group].append(sample)
    labels = {}
    for group, samples in grouped.items():
        if group == "unclustered":
            labels[group] = "Unclustered"
            continue
        votes: Counter[str] = Counter()
        title_votes: Counter[str] = Counter()
        for found, title_terms in samples:
            votes.update(found)
            title_votes.update(title_terms)
        minimum = 2 if len(samples) > 2 else 1
        scores = {
            phrase: count
            / len(samples)
            * (1 + math.log((len(records) + 1) / (background[phrase] + 1)))
            * (1.5 if " " in phrase else 1)
            * (1 + 0.3 * title_votes[phrase] / len(samples))
            for phrase, count in votes.items()
            if count >= minimum
        }
        ordered = sorted(scores, key=lambda phrase: (-scores[phrase], phrase))
        chosen: list[str] = []
        used: set[str] = set()
        for phrase in ordered:
            if used.intersection(phrase.split()):
                continue
            chosen.append(phrase[0].upper() + phrase[1:])
            used.update(phrase.split())
            if len(chosen) == 2:
                break
        labels[group] = " · ".join(chosen) or "Mixed topics"
    return labels
