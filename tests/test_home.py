"""Live dashboard sources and connector boundaries in fictional workspaces."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from chatos.web import home
from chatos.core import Store


class HomeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = Store(self.root / "workspace")
        self.addCleanup(self.store.close)

    def test_directives_read_current_content_and_reject_unregistered_files(self):
        source = self.store.root / "AGENTS.md"
        source.write_text("First revision")
        identity = home.directives(self.store.root)[0]["id"]
        source.write_text("Updated live instructions")
        self.assertEqual(
            home.read_directive(self.store.root, identity)["text"],
            "Updated live instructions",
        )
        with self.assertRaises(LookupError):
            home.read_directive(self.store.root, "../../outside.md")
        source.unlink()
        outside = self.root / "outside.md"
        outside.write_text("not mounted")
        source.symlink_to(outside)
        with self.assertRaises(LookupError):
            home.read_directive(self.store.root, identity)

    def test_mount_persists_and_browse_preserves_boundaries(self):
        vault = self.root / "Fictional vault"
        (vault / ".obsidian").mkdir(parents=True)
        (vault / "Notes").mkdir()
        (vault / "Notes/task.md").write_text("A fictional project")
        (vault / ".secret.md").write_text("hidden")
        outside = self.root / "private.md"
        outside.write_text("outside")
        (vault / "escape.md").symlink_to(outside)
        mounted = home.mount_source(self.store.root, "vault", str(vault))
        self.assertEqual(
            home.mounted_sources(self.store.root)[0]["path"], str(vault.resolve())
        )
        listing = home.browse_source(self.store, mounted["id"])
        self.assertEqual([item["name"] for item in listing["items"]], ["Notes"])
        self.assertEqual(
            home.browse_source(self.store, mounted["id"], "Notes/task.md")["text"],
            "A fictional project",
        )
        for path in ["../private.md", "/etc/passwd", ".secret.md", "escape.md"]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                home.browse_source(self.store, mounted["id"], path)
        with self.assertRaises(ValueError):
            home.mount_source(self.store.root, "git", str(vault))

    def test_gmail_verifies_before_connecting_and_does_not_persist_tokens(self):
        with patch(
            'chatos.web.home.gmail_request',
            return_value={
                "emailAddress": "fictional@example.test",
                "messagesTotal": 12,
            },
        ) as request:
            result = home.connect_gmail("fictional-token")
            request.assert_called_once_with("fictional-token", "profile")
            self.assertNotIn("token", result)
            self.assertEqual(result["email"], "fictional@example.test")
        with self.assertRaises(ValueError):
            home.gmail_messages(None)
        with patch(
            'chatos.web.home.gmail_request',
            side_effect=[
                {"messages": [{"id": "abc123"}]},
                {
                    "payload": {
                        "headers": [{"name": "Subject", "value": "Fictional subject"}]
                    }
                },
            ],
        ):
            result = home.gmail_messages("fictional-token")
            self.assertEqual(result["items"][0]["subject"], "Fictional subject")
        self.assertFalse((self.store.state / "gmail.json").exists())
