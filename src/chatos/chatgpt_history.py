"""Run the user's local chatgpt-history checkout and stage individual exports."""

from __future__ import annotations

import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any

from .core import now, safe_id, write_json
from .importers import read_export_file
from .workspace import Workspace


def stage(root: Path, export_directory: Path) -> dict:
    """Validate and stage each conversation, skipping the exporter's index.json."""
    paths = Workspace(root)
    folder = export_directory.expanduser().resolve() / "conversations"
    if not folder.is_dir():
        raise ValueError("Expected a chatgpt-history export containing conversations/")
    report = {"source": "chatgpt-history", "staged": 0, "errors": []}
    for file in sorted(folder.glob("*.json")):
        try:
            records = read_export_file(file, "chatgpt")
            if (
                len(records) != 1
                or records[0].get("capture") != "exported_visible_branches"
            ):
                raise ValueError("Expected one raw ChatGPT mapping per file")
            identity = records[0].get("id")
            if not isinstance(identity, str) or not identity:
                raise ValueError("Conversation has no source ID")
            # Retain the source mapping, including branch relationships, for reprocessing.
            data = json.loads(file.read_text())
            write_json(
                paths.imports("chatgpt") / ("history-" + safe_id(identity) + ".json"),
                data,
            )
            report["staged"] += 1
        except (ValueError, OSError) as exc:
            report["errors"].append({"file": file.name, "error": type(exc).__name__})
    report["status"] = "partial" if report["errors"] else "ok"
    return report


def capture(
    root: Path, exporter: Path, config: Path, python: Path | None = None
) -> dict:
    """Capture incrementally, including archived chats, using explicit local auth.

    Credentials stay in the user's config; exporter output is reduced to numeric counts because its
    HTTP exceptions can contain sensitive response bodies. No browser secrets are read.
    """
    paths = Workspace(root)
    if not paths.enabled("chatgpt"):
        raise ValueError("ChatGPT source is disabled; enable it before capture")
    exporter, config = exporter.expanduser().resolve(), config.expanduser().resolve()
    if not exporter.is_file() or not config.is_file():
        raise ValueError("Exporter script and authentication config must exist")
    if os.name == "posix" and stat.S_IMODE(config.stat().st_mode) & 0o077:
        raise ValueError("Authentication config must be private: chmod 600 CONFIG")
    output = paths.path("System/State/chatgpt-history-export")
    report: dict[str, Any] = {"source": "chatgpt-history", "started_at": now()}
    command = [
        str(python or sys.executable),
        str(exporter),
        "--config",
        str(config),
        "export",
        "--archived",
        "--output",
        str(output),
    ]
    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=3600,
            cwd=str(exporter.parent),
        )
    except subprocess.TimeoutExpired:
        # Do not retain TimeoutExpired.output: it may contain source titles/errors.
        result = subprocess.CompletedProcess(command, 1, stdout="")
        report["timed_out"] = True
    report.update(
        stage(root, output) if (output / "conversations").is_dir() else {"staged": 0}
    )
    if result.returncode:
        report["status"] = "partial" if report["staged"] else "error"
        report["error"] = (
            "Exporter failed; check authentication and optional curl_cffi installation locally."
        )
    # Upstream exits zero even when individual downloads fail. Only retain the
    # numeric completion summary, never its titles or potentially sensitive errors.
    summary = re.search(
        r"Done: (\d+) downloaded, (\d+) unchanged, (\d+) failed", result.stdout
    )
    if summary:
        report.update(
            zip(("downloaded", "unchanged", "failed"), map(int, summary.groups()))
        )
        if (
            report["failed"]
            or report["downloaded"] + report["unchanged"] > report["staged"]
        ):
            report["status"] = "partial"
    elif not result.returncode:
        report["status"] = "partial"
        report["error"] = (
            "Exporter completion summary unavailable; capture outcome unverified."
        )
    report["exporter_exit_code"] = result.returncode
    report.setdefault("status", "ok")
    report["limits"] = [
        "Private undocumented backend; project chats may be absent.",
        "Exporter may skip individual failed downloads; staged count is not account coverage.",
        "Attachments are references only; original raw exports stay local.",
    ]
    report["finished_at"] = now()
    write_json(paths.path("System/State/chatgpt-history-capture.json"), report)
    return report
