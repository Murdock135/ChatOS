"""The relocated metadata command stays bound to explicitly selected files."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from chatos.maintenance.conversation_metadata import main, write_note


class MetadataTests(unittest.TestCase):
    def test_note_refresh_preserves_authored_fields_and_body(self):
        with tempfile.TemporaryDirectory() as directory:
            note = Path(directory) / "conversation.md"
            note.write_text(
                "---\nsource_id: old\ntopics: [fictional]\n---\nOriginal source text.\n"
            )
            data = dict.fromkeys(
                [
                    "source_app",
                    "source_id",
                    "source_url",
                    "created_at",
                    "last_activity_at",
                    "metadata_checked_at",
                    "model",
                    "model_provider",
                    "reasoning_effort",
                    "workspace",
                ]
            )
            data["source_id"] = "fixture-id"
            data["model"] = "observed-model"
            sidecar = write_note(note, data)
            self.assertIn("topics: [fictional]", note.read_text())
            self.assertTrue(note.read_text().endswith("Original source text.\n"))
            self.assertEqual(json.loads(sidecar.read_text())["model"], "observed-model")

    def test_command_rejects_a_note_outside_its_selected_workspace(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "workspace"
            root.mkdir()
            outside = Path(directory) / "outside.md"
            outside.write_text("Original")
            with (
                patch(
                    "sys.argv",
                    [
                        "metadata",
                        "--root",
                        str(root),
                        "--thread-id",
                        "fixture",
                        "--note",
                        str(outside),
                    ],
                ),
                contextlib.redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit),
            ):
                main()
            self.assertEqual(outside.read_text(), "Original")


if __name__ == "__main__":
    unittest.main()
