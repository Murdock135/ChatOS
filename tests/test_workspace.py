"""Independent-user setup, versioned storage, context review, and recovery checks."""

import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from chatos.context import accept_artifact, import_artifact
from chatos.core import Store
from chatos.library import get, update
from chatos.recovery import doctor, restore
from chatos.retrieval import retrieve
from chatos.runtime import backup, sync
from chatos.setup import initialize
from chatos.workspace import Workspace

EXAMPLE = Path(__file__).resolve().parents[1] / "docs/examples/conversations.json"


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.parent = Path(self.temporary.name).resolve()
        self.root = self.parent / "A new user's workspace"
        initialize(self.root)

    def import_example(self):
        shutil.copy2(EXAMPLE, self.root / "your_ais/chatgpt/imports/conversations.json")
        return sync(self.root)

    def test_new_user_import_search_and_repeat_without_host_history(self):
        fake_home = self.parent / "another home"
        private = fake_home / ".codex/sessions/private.jsonl"
        private.parent.mkdir(parents=True)
        private.write_text("UNRELATED USER HISTORY")
        with patch.object(Path, "home", return_value=fake_home):
            first = self.import_example()
            second = sync(self.root)
        self.assertEqual(first["changes"]["chats"], {"new": 1, "updated": 0, "removed": 0, "total": 1})
        self.assertEqual(second["changed"], 0)
        self.assertEqual(second["sources"]["codex"]["status"], "disabled")
        self.assertFalse((self.root / "your_ais/codex").exists())
        store = Store(self.root)
        try:
            record = store.records()[0]
            self.assertTrue(record["file_path"].startswith("your_ais/chatgpt/chats/2026/"))
            self.assertTrue(retrieve(store, "Markdown")["passages"])
            self.assertEqual(store.registry(), [])
        finally:
            store.close()
        report = doctor(self.root)
        self.assertTrue(report["ok"], report)
        self.assertFalse((self.root / "System").exists())
        self.assertTrue((self.root / "Home.md").is_file())

    def test_second_independent_user_and_non_overwriting_initialization(self):
        other = self.parent / "Another workspace"
        initialize(other)
        (self.root / "shared_context/profile.md").write_text("Private user one")
        self.assertNotIn("Private user one", (other / "shared_context/profile.md").read_text())
        with self.assertRaises(ValueError):
            initialize(self.root)
        self.assertEqual((self.root / "shared_context/profile.md").read_text(), "Private user one")

    def test_unknown_layout_and_inbox_symlink_are_rejected(self):
        manifest = self.root / "chatos.json"
        config = json.loads(manifest.read_text())
        config["layout_version"] = 999
        manifest.write_text(json.dumps(config))
        with self.assertRaises(ValueError):
            Workspace(self.root)
        config["layout_version"] = 2
        manifest.write_text(json.dumps(config))
        inbox = self.root / "your_ais/chatgpt/imports"
        inbox.rmdir()
        outside = self.parent / "outside"
        outside.mkdir()
        inbox.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            Workspace(self.root).imports("chatgpt")

    def test_explicit_codex_source_is_opt_in_and_not_copied_as_preferences(self):
        home = self.parent / "configured source"
        home.mkdir()
        other = self.parent / "Opt in"
        initialize(other, home)
        self.assertEqual(Workspace(other).codex_home(), home)
        self.assertTrue((other / "your_ais/codex/imports").is_dir())
        self.assertFalse((other / "shared_context/preferences.md").read_text().find("Zayan") >= 0)

    def test_backup_restores_layout_and_annotations_without_enabling_sources(self):
        self.import_example()
        store = Store(self.root)
        try:
            record = store.records()[0]
            update(store, record["source"], record["id"], {"note": "A private reading note", "archived": True})
            retained = backup(store, fresh=True)
        finally:
            store.close()
        destination = self.parent / "Recovered user"
        restore(retained["path"], destination)
        self.assertEqual(Workspace(destination).version, 2)
        self.assertFalse(Workspace(destination).enabled("codex"))
        store = Store(destination)
        try:
            _, annotation = get(store, record["source"], record["id"])
            self.assertEqual(annotation["note"], "A private reading note")
            self.assertTrue(annotation["archived"])
            self.assertTrue((destination / store.records()[0]["file_path"]).is_file())
        finally:
            store.close()

    def test_context_artifact_requires_explicit_review_and_retains_provenance(self):
        artifact = self.parent / "context.json"
        artifact.write_text(json.dumps({
            "schema_version": 1, "kind": "preferences", "body": "Prefer paper notebooks for reading.",
            "created_at": "2026-10-23T09:00:00-05:00", "generated_by": "Fictional assistant",
            "source_references": ["User statement in fictional chat demo-2"],
            "uncertainties": ["Preference may depend on the task"],
        }))
        pending = import_artifact(self.root, artifact)
        self.assertFalse(pending["active_instructions"])
        self.assertFalse((self.root / "shared_context/accepted").exists())
        sync(self.root)
        store = Store(self.root)
        try:
            self.assertFalse(retrieve(store, "notebooks")["passages"])
        finally:
            store.close()
        accepted = accept_artifact(self.root, pending["id"], "Reviewed the wording against my chat")
        self.assertIn("demo-2", Path(accepted["path"]).read_text())
        self.assertFalse(accepted["active_instructions"])
        sync(self.root)
        store = Store(self.root)
        try:
            evidence = retrieve(store, "notebooks")
            self.assertTrue(evidence["passages"])
            self.assertEqual(evidence["passages"][0]["source"], "workspace")
        finally:
            store.close()
        record = json.loads(Path(pending["path"]).read_text())
        record["artifact"]["body"] = "An unreviewed replacement"
        Path(pending["path"]).write_text(json.dumps(record))
        with self.assertRaises(ValueError):
            accept_artifact(self.root, pending["id"], "Review")


if __name__ == "__main__":
    unittest.main()
