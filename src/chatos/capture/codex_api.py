"""Read persisted Codex history through the official app-server protocol."""

from __future__ import annotations

import json
import os
import queue
import subprocess
import threading
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from chatos.core import now, redact, safe_id, timestamp, write_json
from chatos.visibility import clean_text, origin_hint
from chatos.workspace import Workspace

SOURCE_KINDS = ["cli", "vscode", "exec", "appServer", "unknown"]


class HistoryError(ValueError):
    """The source could not provide a verified history response."""


class AppServer:
    """A bounded, sequential JSONL client; never starts or resumes a turn."""

    def __init__(self, home: Path, executable: str = "codex", timeout: float = 60):
        environment = dict(os.environ, CODEX_HOME=str(home.expanduser().resolve()))
        self.process = subprocess.Popen(
            [executable, "app-server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            env=environment,
        )
        self.timeout = timeout
        self.sequence = 0
        self.responses: queue.Queue = queue.Queue()
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()
        try:
            self.request(
                "initialize",
                {
                    "clientInfo": {"name": "smriti_history", "version": "0.2.0"},
                    "capabilities": {"experimentalApi": True},
                },
            )
            self._send({"method": "initialized", "params": {}})
        except BaseException:
            self.close()
            raise

    def _read(self) -> None:
        assert self.process.stdout is not None
        try:
            for line in self.process.stdout:
                self.responses.put(json.loads(line))
        except (ValueError, OSError):
            self.responses.put(None)
        finally:
            self.responses.put(None)

    def _send(self, message: dict) -> None:
        assert self.process.stdin is not None
        self.process.stdin.write(json.dumps(message) + "\n")
        self.process.stdin.flush()

    def request(self, method: str, params: dict) -> dict:
        """Return one result, rejecting server requests instead of executing them."""
        if method not in {
            "initialize",
            "thread/list",
            "thread/read",
            "thread/turns/list",
            "thread/items/list",
        }:
            raise HistoryError("Only history reads are supported")
        self.sequence += 1
        identity = self.sequence
        self._send({"id": identity, "method": method, "params": params})
        deadline = time.monotonic() + self.timeout
        while True:
            try:
                response = self.responses.get(
                    timeout=max(0, deadline - time.monotonic())
                )
            except queue.Empty as exc:
                raise HistoryError(f"{method} timed out") from exc
            if response is None:
                raise HistoryError(f"{method}: app-server closed its output")
            if "method" in response and "id" in response:
                self._send(
                    {
                        "id": response["id"],
                        "error": {
                            "code": -32601,
                            "message": "History importer does not execute server requests",
                        },
                    }
                )
                continue
            if response.get("id") != identity:
                continue
            if "error" in response:
                # Server error bodies can contain source content; retain only the code.
                raise HistoryError(
                    f"{method} failed (code {response['error'].get('code')})"
                )
            result = response.get("result")
            if not isinstance(result, dict):
                raise HistoryError(f"{method}: expected an object result")
            return result

    def close(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
        for stream in (self.process.stdin, self.process.stdout):
            if stream:
                stream.close()
        self.reader.join(timeout=1)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()


def pages(client: Any, method: str, params: dict) -> Iterator[dict]:
    """Consume all pages; repeated cursors are a failure, never silent truncation."""
    cursor = None
    seen = set()
    while True:
        result = client.request(
            method, {**params, **({"cursor": cursor} if cursor else {})}
        )
        data = result.get("data")
        if not isinstance(data, list) or not all(
            isinstance(item, dict) for item in data
        ):
            raise HistoryError(f"{method}: invalid page data")
        yield from data
        if "nextCursor" not in result:
            raise HistoryError(f"{method}: missing pagination boundary")
        cursor = result["nextCursor"]
        if cursor is None:
            break
        if not isinstance(cursor, str) or not cursor or cursor in seen:
            raise HistoryError(f"{method}: invalid or repeated pagination cursor")
        seen.add(cursor)


def visible_item(item: dict, turn_id: str, recorded_at: Any = None) -> dict | None:
    """Whitelist visible text and attachment references, excluding internal items."""
    kind = item.get("type")
    if kind not in {"userMessage", "agentMessage"}:
        return None
    role = "user" if kind == "userMessage" else "assistant"
    phase = item.get("phase")
    if phase in {"analysis", "reasoning", "summary"}:
        return None
    content = item.get("content") or []
    text = (
        item.get("text", "")
        if role == "assistant"
        else "\n".join(
            part.get("text", "") for part in content if part.get("type") == "text"
        )
    )
    text = clean_text(role, text)
    attachments = [
        {"type": part["type"], "reference": part.get("path") or part.get("url")}
        for part in content
        if part.get("type") in {"image", "localImage"}
    ]
    if text is None or (not text and not attachments):
        return None
    if not isinstance(item.get("id"), str) or not item["id"]:
        raise HistoryError("Visible history item has no stable ID")
    message = {
        "id": item["id"],
        "role": role,
        "phase": phase,
        "text": redact(text),
        "timestamp": timestamp(recorded_at),
        "turn_id": turn_id,
        "model": None,
        "reasoning_effort": None,
        "attachments": attachments,
        **origin_hint(role, text),
    }
    citation = item.get("memoryCitation")
    if isinstance(citation, dict):
        message["memory_citation"] = {
            "entries": [
                {
                    key: entry[key]
                    for key in ("path", "lineStart", "lineEnd", "note")
                    if key in entry
                }
                for entry in citation.get("entries", [])
                if isinstance(entry, dict)
            ],
            "thread_ids": citation.get("threadIds", []),
        }
    return message


def read_thread(client: Any, thread: dict) -> dict:
    """Fetch every turn and item before publishing a normalized source snapshot."""
    identity = thread["id"]
    turns = list(
        pages(
            client,
            "thread/turns/list",
            {
                "threadId": identity,
                "itemsView": "full",
                "sortDirection": "asc",
                "limit": 100,
            },
        )
    )
    messages, runs, seen = [], [], set()
    for turn in turns:
        if turn.get("itemsView", "full") != "full":
            raise HistoryError("Server returned summarized turn items")
        # Full turn items support legacy stores; dedicated item pagination adds timestamps.
        # Unsupported item pagination is documented for older stores, so full turns remain valid.
        try:
            entries = list(
                pages(
                    client,
                    "thread/items/list",
                    {
                        "threadId": identity,
                        "turnId": turn["id"],
                        "sortDirection": "asc",
                        "limit": 100,
                    },
                )
            )
        except HistoryError as exc:
            if "code -32600" not in str(exc) and "code -32601" not in str(exc):
                raise
            entries = [{"item": item, "turnId": turn["id"]} for item in turn["items"]]
        for entry in entries:
            if entry.get("turnId", turn["id"]) != turn["id"]:
                raise HistoryError("History item belongs to a different turn")
            message = visible_item(
                entry["item"],
                turn["id"],
                entry.get("startedAtMs") or entry.get("completedAtMs"),
            )
            if message and message["id"] not in seen:
                seen.add(message["id"])
                messages.append(message)
        runs.append(
            {
                "turn_id": turn["id"],
                "status": turn.get("status"),
                "started_at": timestamp(turn.get("startedAt")),
                "completed_at": timestamp(turn.get("completedAt")),
            }
        )
    return {
        "source": "codex",
        "id": identity,
        "title": thread.get("name") or thread.get("preview") or "Untitled",
        "created_at": timestamp(thread.get("createdAt")),
        "updated_at": timestamp(thread.get("updatedAt")),
        "workspace": thread.get("cwd"),
        "provider": thread.get("modelProvider"),
        "model": thread.get("model"),
        "reasoning_effort": thread.get("reasoningEffort"),
        "model_history": [],
        "messages": messages,
        "runs": runs,
        "capture": "persisted_api_visible_messages",
        "evidence": {
            "parser": "codex-app-server-v1",
            "api_capture": {
                "thread_id": identity,
                "source_updated_at": thread.get("updatedAt"),
                "turn_count": len(turns),
                "items_view": "full",
                "model_provenance": "Latest thread metadata; per-message model and effort are unknown.",
                "forked_from_id": thread.get("forkedFromId"),
            },
        },
        "limits": [
            "All pages of available persisted visible history were read; source completeness is unknown.",
            "Per-message model and effort are unknown unless enriched from retained local sources.",
            "Private reasoning and tool payloads excluded; attachment references only.",
        ],
    }


def capture(
    root: Path,
    home: Path,
    executable: str = "codex",
    thread_ids: list | None = None,
    force: bool = False,
) -> dict:
    """Stage API snapshots for ordinary sync; failed threads retain their prior snapshot."""
    paths = Workspace(root)
    folder = paths.imports("codex")
    report = {
        "started_at": now(),
        "source": "codex-api",
        "captured": 0,
        "unchanged": 0,
        "messages": 0,
        "errors": [],
    }
    with AppServer(home, executable) as client:
        if thread_ids:
            threads = []
            for identity in thread_ids:
                try:
                    thread = client.request("thread/read", {"threadId": identity})[
                        "thread"
                    ]
                    if thread.get("id") != identity:
                        raise HistoryError("Thread response has a different source ID")
                    threads.append(thread)
                except (ValueError, OSError, KeyError, TypeError) as exc:
                    report["errors"].append(
                        {
                            "id": identity,
                            "error": str(exc)
                            if isinstance(exc, HistoryError)
                            else type(exc).__name__,
                        }
                    )
        else:
            threads = []
            for archived in (False, True):
                threads.extend(
                    pages(
                        client,
                        "thread/list",
                        {
                            "archived": archived,
                            "sourceKinds": SOURCE_KINDS,
                            "modelProviders": [],
                            "useStateDbOnly": True,
                            "limit": 100,
                        },
                    )
                )
        by_id = {thread["id"]: thread for thread in threads}
        report["discovered"] = len(by_id)
        for thread in by_id.values():
            try:
                destination = folder / (safe_id(thread["id"]) + ".json")
                if (
                    not force
                    and thread.get("updatedAt") is not None
                    and destination.is_file()
                ):
                    previous = json.loads(destination.read_text())
                    if (
                        previous.get("evidence", {})
                        .get("api_capture", {})
                        .get("source_updated_at")
                        == thread["updatedAt"]
                    ):
                        report["unchanged"] += 1
                        continue
                record = read_thread(client, thread)
                write_json(destination, record)
                report["captured"] += 1
                report["messages"] += len(record["messages"])
            except (ValueError, OSError, KeyError, TypeError) as exc:
                report["errors"].append(
                    {
                        "id": thread["id"],
                        "error": str(exc)
                        if isinstance(exc, HistoryError)
                        else type(exc).__name__,
                    }
                )
    report["finished_at"] = now()
    report["status"] = "partial" if report["errors"] else "ok"
    write_json(paths.path("System/State/codex-api-capture.json"), report)
    return report
