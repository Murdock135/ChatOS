"""Copy a legacy archive into a versioned workspace before changing live paths."""

import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
from typing import Any

from .core import Store, locked, now, write_json
from .workspace import Workspace


TREES = ("System", "Conversations", "Projects", "Topics", "Humans")


def copy_file(source: Path, target: Path) -> None:
    """Use macOS copy-on-write when possible, otherwise retain an ordinary copy."""
    target.parent.mkdir(parents=True, exist_ok=True)
    if sys.platform == "darwin":
        result = subprocess.run(
            ["cp", "-c", "-p", str(source), str(target)], capture_output=True
        )
        if result.returncode == 0:
            return
    shutil.copy2(source, target)


def destination_path(paths: Workspace, relative: Path) -> Path:
    """Map legacy files, including platform inboxes and canonical transcripts."""
    parts = relative.parts
    if (
        len(parts) > 3
        and parts[:2] == ("System", "Imports")
        and parts[2] in {"codex", "chatgpt", "muse"}
    ):
        return paths.imports(parts[2]) / Path(*parts[3:])
    if len(parts) > 2 and parts[0] == "Conversations" and parts[1] != "Annotations":
        source = parts[-1].split("-", 1)[0]
        if source in {"codex", "chatgpt", "muse"}:
            return paths.conversation(source, parts[1], parts[-1])
    if len(parts) > 2 and parts[:2] == ("Conversations", "Annotations"):
        source = parts[-1].split("-", 1)[0]
        if source in {"codex", "chatgpt", "muse"}:
            return paths.annotations(source) / parts[-1]
    return paths.path(relative)


def _fingerprint(store: Store) -> dict[str, Any]:
    """Compare source records and durable side tables independently of their paths."""
    records = []
    for record in store.records():
        record.pop("file_path", None)
        records.append(record)
    tables = {}
    for name in ["revisions", "checkpoints", "library_annotations", "feedback_reviews"]:
        if store.db.execute(
            "SELECT 1 FROM sqlite_master WHERE name=?", (name,)
        ).fetchone():
            rows = [
                tuple(row) for row in store.db.execute('SELECT * FROM "' + name + '"')
            ]
            tables[name] = sorted(rows, key=repr)
    return {"records": records, "tables": tables}


def migrate(source: Path, destination: Path) -> dict[str, Any]:
    """Create and verify a separate copy; never activate it or delete the source."""
    source, destination = source.resolve(), destination.absolute()
    if not (source / "System/State/chatos.sqlite3").is_file():
        raise ValueError("Migration requires an existing conversation database")
    if Workspace(source).version != 1:
        raise ValueError("Migration requires a legacy workspace")
    if destination.exists() or destination.is_symlink():
        raise ValueError("Migration destination must not exist")
    if source == destination.resolve() or destination.resolve() in source.parents:
        raise ValueError("Migration cannot replace a source ancestor")
    with locked(source / "System/State/sync.lock", blocking=False):
        destination.mkdir(parents=True)
        config = {
            "layout_version": 2,
            "sources": {
                "codex": {"enabled": True, "path": str(Path.home() / ".codex")},
                "chatgpt": {"enabled": True},
                "muse": {"enabled": True},
            },
            "external_delivery_roots": [],
            "migrated_from": str(source),
        }
        write_json(destination / "chatos.json", config)
        paths = Workspace(destination)
        mapping = {}
        bulk_trees = {
            "System/State",
            "System/Snapshots",
            "System/Models",
            "System/Backups",
        }
        for old in sorted(bulk_trees):
            original = source / old
            if not original.exists():
                continue
            target = paths.path(old)
            target.parent.mkdir(parents=True, exist_ok=True)
            if sys.platform == "darwin":
                subprocess.run(
                    ["cp", "-cR", "-p", str(original), str(target)], check=True
                )
            else:
                shutil.copytree(original, target)
            mapping[old] = str(target.relative_to(destination))
        for name in [
            "chatos.sqlite3",
            "chatos.sqlite3-wal",
            "chatos.sqlite3-shm",
            "sync.lock",
        ]:
            (paths.path("System/State") / name).unlink(missing_ok=True)
        # Sources are preserved byte-for-byte. No symlink is followed during copying.
        for tree in TREES:
            for original in sorted((source / tree).rglob("*")):
                if any(original.is_relative_to(source / old) for old in bulk_trees):
                    continue
                if original.is_symlink():
                    raise ValueError(
                        "Review source symlink before migration: " + str(original)
                    )
                if not original.is_file() or "__pycache__" in original.parts:
                    continue
                relative = original.relative_to(source)
                if relative.as_posix() in {
                    "System/State/chatos.sqlite3",
                    "System/State/chatos.sqlite3-wal",
                    "System/State/chatos.sqlite3-shm",
                    "System/State/sync.lock",
                }:
                    continue
                target = destination_path(paths, relative)
                copy_file(original, target)
                mapping[str(relative)] = str(target.relative_to(destination))
        for name in [
            "STATE.md",
            "STATUS.md",
            "AGENTS.md",
            "ideas.md",
            "IMPLEMENTATION.md",
        ]:
            if (source / name).is_file():
                copy_file(source / name, destination / name)
        original_store = Store(source)
        try:
            before = _fingerprint(original_store)
            state = paths.path("System/State")
            state.mkdir(parents=True, exist_ok=True)
            database = sqlite3.connect(str(state / "chatos.sqlite3"))
            try:
                original_store.db.backup(database)
            finally:
                database.close()
        finally:
            original_store.close()
        migrated = Store(destination)
        try:
            for record in migrated.records():
                year = (record.get("created_at") or "undated")[:4]
                if not year.isdigit():
                    year = "undated"
                from .core import safe_id

                target = paths.conversation(
                    record["source"],
                    year,
                    record["source"] + "-" + safe_id(record["id"]) + ".md",
                )
                record["file_path"] = str(target.relative_to(destination))
                write_json(target.with_suffix(".json"), record)
                migrated.render(record)
                with migrated.db:
                    migrated.db.execute(
                        "UPDATE conversations SET file_path=?, record_json=? WHERE source=? AND id=?",
                        (
                            record["file_path"],
                            json.dumps(record, ensure_ascii=False),
                            record["source"],
                            record["id"],
                        ),
                    )
            if _fingerprint(migrated) != before:
                raise RuntimeError(
                    "Migration changed source records or durable side tables"
                )
            if migrated.db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise RuntimeError("Migrated database failed integrity check")
            from .library import restore_annotations

            restore_annotations(migrated)
            from .retrieval import refresh

            refresh(migrated)
            count = len(migrated.records())
        finally:
            migrated.close()
        for label in ["codex", "chatgpt", "muse"]:
            context = destination / "your_ais" / label / "context"
            context.mkdir(parents=True, exist_ok=True)
            (context / "README.md").write_text(
                "# Captured context\n\nDated context and its original manifests are retained in "
                "[workspace snapshots](../../../app_data/snapshots/). Source and category fields "
                "identify each capture. Availability varies by platform; this folder does not imply "
                "that a platform supplied memory or skills.\n"
            )
        report = {
            "status": "verified_copy",
            "created_at": now(),
            "source": str(source),
            "destination": str(destination.resolve()),
            "conversations": count,
            "preserved": "Source records, revisions, checkpoints, annotations and feedback reviews compared exactly; only current file_path changed.",
            "files": mapping,
            "activated": False,
        }
        write_json(destination / "app_data/migration.json", report)
        return {key: value for key, value in report.items() if key != "files"}
