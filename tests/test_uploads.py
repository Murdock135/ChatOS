"""User-selected exports publish only after validation and remain local."""

import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from chatos.uploads import MAXIMUM, receive_export


class UploadTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.export = (
            Path(__file__).parents[1] / "docs/examples/conversations.json"
        ).read_bytes()

    def upload(self, payload, extension="json"):
        return receive_export(self.root, io.BytesIO(payload), len(payload), extension)

    def test_repeated_export_has_stable_inbox_identity(self):
        first = self.upload(self.export)
        second = self.upload(self.export)
        self.assertEqual(first["conversations"], 1)
        self.assertEqual(first["path"], second["path"])
        self.assertFalse(first["already_received"])
        self.assertTrue(second["already_received"])
        self.assertEqual(Path(first["path"]).read_bytes(), self.export)
        self.assertEqual(list((self.root / "System/State").iterdir()), [])

    def test_zip_reads_only_conversation_payload_and_never_extracts_members(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("conversations.json", self.export)
            archive.writestr("../../escaped.txt", "must not be extracted")
        self.assertEqual(self.upload(buffer.getvalue(), "zip")["conversations"], 1)
        self.assertFalse((self.root.parent / "escaped.txt").exists())
        self.assertEqual(
            [file.suffix for file in self.root.rglob("*") if file.is_file()], [".zip"]
        )

    def test_invalid_incomplete_and_oversized_inputs_never_publish(self):
        invalid = [
            b"not JSON",
            json.dumps(
                {
                    "id": "one",
                    "messages": [
                        {"role": "assistant", "phase": "analysis", "text": "private"}
                    ],
                }
            ).encode(),
            b'[{"mapping":{}, "id":9}]',
            b'[{"mapping":null}]',
        ]
        for payload in invalid:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                self.upload(payload)
        with self.assertRaises(ValueError):
            receive_export(self.root, io.BytesIO(b"[]"), 3, "json")
        with self.assertRaises(ValueError):
            receive_export(self.root, io.BytesIO(), MAXIMUM + 1, "json")
        with self.assertRaises(ValueError):
            self.upload(b"[]", "../txt")
        self.assertFalse((self.root / "System/Imports").exists())


if __name__ == "__main__":
    unittest.main()
