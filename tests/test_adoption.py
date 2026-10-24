"""Fictional-user setup, context review and portable migration acceptance."""

import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from chatos.context import accept_artifact, import_artifact, retire_artifact
from chatos.core import Store
from chatos.library import update
from chatos.onboarding import setup_status, write_guide
from chatos.portable import check_bundle, export_bundle
from chatos.retrieval import retrieve
from chatos.runtime import sync
from chatos.setup import initialize

ROOT = Path(__file__).resolve().parents[1]


class AdoptionTests(unittest.TestCase):
    def test_two_independent_users_follow_documented_setup_and_review_flow(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory).resolve()
            for name, preference in [
                ("Ada", "plain Markdown"),
                ("Bryn", "index cards"),
            ]:
                home = parent / (name + " home")
                home.mkdir()
                root = parent / (name + "'s workspace")
                with patch.object(Path, "home", return_value=home):
                    initialize(root)
                    self.assertFalse(setup_status(root)["archive_ready"])
                    shutil.copy2(
                        ROOT / "docs/examples/conversations.json",
                        root / "your_ais/chatgpt/imports/conversations.json",
                    )
                    result = sync(root)
                    self.assertEqual(result["changes"]["chats"]["new"], 1)
                    self.assertFalse((home / ".codex").exists())
                    self.assertEqual(sync(root)["changed"], 0)
                artifact = json.loads((ROOT / "docs/examples/context.json").read_text())
                artifact["body"] = "For reading, I prefer " + preference + "."
                file = parent / (name + ".json")
                file.write_text(json.dumps(artifact))
                pending = import_artifact(root, file)
                self.assertEqual(
                    setup_status(root)["pending_context_ids"], [pending["id"]]
                )
                accept_artifact(
                    root, pending["id"], "Fictional user reviewed source and scope"
                )
                self.assertEqual(import_artifact(root, file)["status"], "accepted")
                self.assertEqual(setup_status(root)["pending_context_ids"], [])
                self.assertIn(str(root), (root / "ASSISTANT.md").read_text())
                self.assertFalse(write_guide(root)["host_integration_installed"])
                sync(root)
                store = Store(root)
                try:
                    self.assertEqual(store.registry(), [])
                    hit = retrieve(store, preference)["passages"]
                    self.assertTrue(any(preference in p["excerpt"] for p in hit))
                finally:
                    store.close()
            self.assertNotIn(
                "index cards",
                next(
                    (parent / "Ada's workspace/shared_context/accepted").glob("*.md")
                ).read_text(),
            )

    def test_context_failed_review_is_not_published_and_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve() / "workspace"
            initialize(root)
            pending = import_artifact(root, ROOT / "docs/examples/context.json")
            with patch(
                "chatos.context.write_json", side_effect=OSError("Interrupted review")
            ):
                with self.assertRaises(OSError):
                    accept_artifact(root, pending["id"], "Reviewed fictional sources")
            self.assertFalse(
                (root / "shared_context/accepted" / (pending["id"] + ".md")).exists()
            )
            inbox = root / "shared_context/inbox"
            shutil.rmtree(inbox)
            outside = Path(directory).resolve() / "outside"
            outside.mkdir()
            inbox.symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                import_artifact(root, ROOT / "docs/examples/context.json")

    def test_selected_bundle_preserves_text_annotations_and_review_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory).resolve()
            root = parent / "workspace"
            initialize(root)
            store = Store(root)
            try:
                for identity in ["one", "private-unselected"]:
                    store.put(
                        {
                            "source": "chatgpt",
                            "id": identity,
                            "title": identity,
                            "capture": "exported_visible_branches",
                            "workspace": "/private/source/path",
                            "evidence": {"path": "/private/source/file"},
                            "messages": [
                                {
                                    "id": "u",
                                    "role": "user",
                                    "text": "Exact source text " + identity,
                                }
                            ],
                        }
                    )
                update(
                    store,
                    "chatgpt",
                    "one",
                    {"note": "A local annotation", "archived": True},
                )
                snapshot = store.records()
                destination = parent / "portable bundle"
                with self.assertRaises(ValueError):
                    export_bundle(store, destination)
                report = export_bundle(store, destination, ["chatgpt:one"])
                self.assertEqual(report["conversations"], 1)
                self.assertEqual(report["context_files"], 0)
                self.assertEqual(store.records(), snapshot)
                data = json.loads((destination / "conversations.json").read_text())
                self.assertEqual(
                    data["conversations"][0]["messages"][0]["text"],
                    "Exact source text one",
                )
                self.assertNotIn("workspace", data["conversations"][0])
                self.assertNotIn("path", data["conversations"][0]["evidence"])
                self.assertEqual(
                    data["local_annotations"][0]["note"], "A local annotation"
                )
                self.assertNotIn("private-unselected", json.dumps(data))
                pending = import_artifact(root, ROOT / "docs/examples/context.json")
                pending_bundle = parent / "pending only"
                export_bundle(store, pending_bundle, ["chatgpt:one"], with_context=True)
                self.assertFalse(
                    list((pending_bundle / "context").glob(pending["id"] + "*"))
                )
                accept_artifact(root, pending["id"], "Reviewed fictional context")
                accepted_bundle = parent / "accepted"
                export_bundle(
                    store, accepted_bundle, ["chatgpt:one"], with_context=True
                )
                self.assertTrue(
                    (accepted_bundle / "context" / (pending["id"] + ".md")).is_file()
                )
                (destination / "START_HERE.md").write_text("Tampered")
                with self.assertRaises(ValueError):
                    check_bundle(destination)
                with self.assertRaises(ValueError):
                    export_bundle(store, accepted_bundle, ["chatgpt:one"])
                # A different application's minimal reader can reconstruct the selected visible conversation.
                reconstructed = [
                    (
                        r["source"],
                        r["id"],
                        [(m["id"], m["text"]) for m in r["messages"]],
                    )
                    for r in data["conversations"]
                ]
                self.assertEqual(
                    reconstructed,
                    [("chatgpt", "one", [("u", "Exact source text one")])],
                )
            finally:
                store.close()

    def test_user_guide_and_malformed_bundle_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory).resolve()
            root = parent / "workspace"
            initialize(root)
            guide = root / "ASSISTANT.md"
            guide.write_text("My own assistant guide")
            with self.assertRaises(ValueError):
                write_guide(root)
            self.assertEqual(guide.read_text(), "My own assistant guide")
            artifact = json.loads((ROOT / "docs/examples/context.json").read_text())
            artifact["schema_version"] = True
            file = parent / "bad-context.json"
            file.write_text(json.dumps(artifact))
            with self.assertRaises(ValueError):
                import_artifact(root, file)
            store = Store(root)
            try:
                store.put(
                    {
                        "source": "chatgpt",
                        "id": "one",
                        "title": "One",
                        "messages": [{"id": "u", "role": "user", "text": "Original"}],
                    }
                )
                destination = parent / "bundle"
                export_bundle(store, destination, ["chatgpt:one"])
                extra = destination / "unlisted-link"
                extra.symlink_to(root, target_is_directory=True)
                with self.assertRaises(ValueError):
                    check_bundle(destination)
                extra.unlink()
                manifest = json.loads((destination / "manifest.json").read_text())
                manifest["files"]["../outside"] = "hash"
                (destination / "manifest.json").write_text(json.dumps(manifest))
                with self.assertRaises(ValueError):
                    check_bundle(destination)
                accepted = root / "shared_context/accepted"
                accepted.mkdir()
                (accepted / "orphan.md").write_text("Not reviewed")
                failed = parent / "failed export"
                with self.assertRaises(ValueError):
                    export_bundle(store, failed, ["chatgpt:one"], with_context=True)
                self.assertFalse(failed.exists())
                self.assertFalse(list(parent.glob(".chatos-bundle-*")))
            finally:
                store.close()

    def test_retirement_preserves_published_note_if_review_write_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "workspace"
            initialize(root)
            result = import_artifact(root, ROOT / "docs/examples/context.json")
            identity = result["id"]
            accepted = accept_artifact(
                root, identity, "Verified fictional source and scope."
            )
            note = Path(accepted["path"])
            original = note.read_bytes()
            with patch(
                "chatos.context.write_json",
                side_effect=OSError("Interrupted review write"),
            ):
                with self.assertRaises(OSError):
                    retire_artifact(root, identity, "Superseded.")
            self.assertEqual(note.read_bytes(), original)
            record = json.loads(
                (root / "shared_context/inbox" / (identity + ".json")).read_text()
            )
            self.assertEqual(record["review_status"], "accepted")
            # Older envelopes stored just their latest review; preserve it on upgrade.
            inbox = root / "shared_context/inbox" / (identity + ".json")
            record.pop("review_history")
            inbox.write_text(json.dumps(record))
            retire_artifact(root, identity, "Superseded.")
            history = json.loads(inbox.read_text())["review_history"]
            self.assertEqual([r["status"] for r in history], ["accepted", "retired"])
            self.assertFalse(note.exists())
            self.assertEqual(
                import_artifact(root, ROOT / "docs/examples/context.json")["status"],
                "retired",
            )


if __name__ == "__main__":
    unittest.main()
