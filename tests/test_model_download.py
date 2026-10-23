"""Verify model setup publication without downloading weights or using a GPU."""

import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from chatos.maintenance import download_embedding_model as setup
from chatos.setup import initialize


class ModelDownloadTests(unittest.TestCase):
    def test_manifest_requires_pinned_weights_and_library_owned_modules(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve() / "workspace"
            initialize(root)
            weights = b"fictional model data"
            calls = []

            def receive(model, **kwargs):
                calls.append((model, kwargs))
                directory = Path(kwargs["local_dir"])
                directory.mkdir(parents=True, exist_ok=True)
                (directory / "config.json").write_text(
                    json.dumps({"model_type": "qwen3"})
                )
                (directory / "modules.json").write_text(
                    json.dumps([{"type": "sentence_transformers.models.Pooling"}])
                )
                (directory / "model.safetensors").write_bytes(weights)

            hub = SimpleNamespace(snapshot_download=receive)
            manifest = (
                root
                / "app_data/cache/models/qwen3-embedding-0.6b/download-manifest.json"
            )
            with (
                patch.dict(os.environ, {"HF_TOKEN": "fictional token"}),
                patch.dict("sys.modules", {"huggingface_hub": hub}),
            ):
                with self.assertRaisesRegex(ValueError, "hash mismatch"):
                    setup.download(root)
                self.assertFalse(manifest.exists())
                with patch.object(
                    setup, "WEIGHTS_SHA256", hashlib.sha256(weights).hexdigest()
                ):
                    result = setup.download(root)
                self.assertNotIn("HF_TOKEN", os.environ)
            self.assertEqual(result["revision"], setup.REVISION)
            self.assertFalse(calls[-1][1]["token"])
            self.assertNotIn("*.py", calls[-1][1]["allow_patterns"])
            self.assertEqual(json.loads(manifest.read_text())["model"], setup.MODEL)
            self.assertFalse((root / "System").exists())

    def test_custom_module_cannot_publish_verification_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve() / "workspace"
            initialize(root)

            def receive(model, **kwargs):
                directory = Path(kwargs["local_dir"])
                directory.mkdir(parents=True, exist_ok=True)
                (directory / "config.json").write_text(
                    json.dumps({"model_type": "qwen3"})
                )
                (directory / "modules.json").write_text(
                    json.dumps([{"type": "unrecognized.RemoteCode"}])
                )

            with (
                patch.dict(os.environ, {}),
                patch.dict(
                    "sys.modules",
                    {"huggingface_hub": SimpleNamespace(snapshot_download=receive)},
                ),
            ):
                with self.assertRaisesRegex(ValueError, "custom model code"):
                    setup.download(root)
            self.assertFalse(
                (
                    root
                    / "app_data/cache/models/qwen3-embedding-0.6b/download-manifest.json"
                ).exists()
            )


if __name__ == "__main__":
    unittest.main()
