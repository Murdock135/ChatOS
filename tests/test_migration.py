"""Migration preserves source evidence and separate durable user edits."""

import json
from pathlib import Path
import tempfile
import unittest

from chatos.core import Store
from chatos.library import update
from chatos.migration import migrate
from chatos.recovery import doctor
from chatos.retrieval import retrieve
from chatos.runtime import backup, sync


class MigrationTests(unittest.TestCase):
    def test_activated_checkout_selects_workspace_for_explicit_root(self):
        from chatos.setup import initialize
        from chatos.workspace import Workspace

        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary).resolve()
            destination = repository / "workspace"
            initialize(destination)
            self.assertEqual(Workspace(repository).version, 1)
            config = json.loads((destination / "chatos.json").read_text())
            config["activated"] = True
            (destination / "chatos.json").write_text(json.dumps(config))
            self.assertEqual(Workspace(repository).root, destination)
            store = Store(repository)
            try:
                self.assertEqual(store.root, destination)
                self.assertEqual(store.state, destination / "app_data/state")
            finally:
                store.close()

    def test_copy_preserves_records_revisions_annotations_and_original(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary).resolve()
            source, destination = parent / "legacy", parent / "organized"
            store = Store(source)
            record = {
                "source": "chatgpt",
                "id": "demo",
                "title": "Reading",
                "created_at": "2026-10-23T10:00:00Z",
                "messages": [{"role": "user", "text": "Use Markdown notes."}],
            }
            store.put(record)
            record["title"] = "Revised reading"
            store.put(record)
            update(
                store,
                "chatgpt",
                "demo",
                {"note": "Keep my annotation", "archived": True},
            )
            backup(store, fresh=True)
            original = store.records()[0]
            store.close()
            report = migrate(source, destination)
            self.assertEqual(report["conversations"], 1)
            self.assertFalse(report["activated"])
            new = Store(destination)
            try:
                current = new.records()[0]
                self.assertEqual(current["messages"], original["messages"])
                self.assertTrue(
                    current["file_path"].startswith("your_ais/chatgpt/chats/")
                )
                self.assertEqual(
                    new.db.execute("SELECT count(*) FROM revisions").fetchone()[0], 1
                )
                self.assertEqual(
                    new.db.execute("SELECT note FROM library_annotations").fetchone()[
                        0
                    ],
                    "Keep my annotation",
                )
                self.assertTrue(retrieve(new, "Markdown")["passages"])
                self.assertEqual(
                    json.loads(
                        (destination / current["file_path"])
                        .with_suffix(".json")
                        .read_text()
                    ),
                    current,
                )
            finally:
                new.close()
            old = Store(source)
            try:
                self.assertEqual(old.records()[0], original)
            finally:
                old.close()
            # A normal repeat sync must keep using canonical folders without aliases.
            config = json.loads((destination / "chatos.json").read_text())
            config["sources"]["codex"]["enabled"] = False
            (destination / "chatos.json").write_text(json.dumps(config))
            sync(destination)
            for name in ["System", "Conversations", "Projects", "Topics", "Humans"]:
                self.assertFalse((destination / name).exists(), name)
            self.assertTrue(doctor(destination)["ok"])
            with self.assertRaises(ValueError):
                migrate(source, destination)


if __name__ == "__main__":
    unittest.main()
