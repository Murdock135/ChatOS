"""Design archives preserve their public inputs and reject silent replacement."""

import importlib.util
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "archive_design", Path(__file__).resolve().parents[1] / "scripts/archive_design.py"
)
assert spec is not None and isinstance(spec.loader, SourceFileLoader)
archive_design = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive_design)


class DesignArchiveTests(unittest.TestCase):
    def test_snapshot_preserves_sources_excludes_workspace_and_detects_tampering(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name, text in {
                "frontend/src/styles/design-tokens.css": ":root { --text: #fff; }",
                "docs/design/STYLEGUIDE.md": "# Active guide",
                "docs/design/evidence/v1/README.md": "# Fictional verification",
                "workspace/private.md": "Private workspace must not be archived",
                "frontend/src/.env": "FICTIONAL_SECRET=exclude-me",
                "frontend/src/records.json": "Not an allowed public source",
            }.items():
                file = root / name
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text(text)
            target = archive_design.create_archive(
                root, "v1", "test:fictional", "A fictional design snapshot"
            )
            self.assertTrue(archive_design.verify_archive(target)["ok"])
            self.assertFalse((target / "sources/workspace").exists())
            self.assertFalse((target / "sources/frontend/src/.env").exists())
            self.assertFalse((target / "sources/frontend/src/records.json").exists())
            original = target / "sources/frontend/src/styles/design-tokens.css"
            (root / "frontend/src/styles/design-tokens.css").write_text(
                "Changed current source"
            )
            self.assertEqual(original.read_text(), ":root { --text: #fff; }")
            with self.assertRaises(FileExistsError):
                archive_design.create_archive(
                    root, "v1", "test:fictional", "Do not overwrite"
                )
            original.write_text("Tampered")
            with self.assertRaisesRegex(ValueError, "integrity mismatch"):
                archive_design.verify_archive(target)

    def test_invalid_version_cannot_escape_archive_root(self):
        with tempfile.TemporaryDirectory() as folder, self.assertRaises(ValueError):
            archive_design.create_archive(
                Path(folder), "../outside", "test:fictional", "Invalid"
            )
