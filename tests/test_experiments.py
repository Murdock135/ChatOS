"""Experiment protocols freeze evidence and never overwrite existing runs."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from chatos.experiments.artifacts import seal, verify, write_json
from chatos.experiments.config import load_config
from chatos.experiments.runner import run


class ExperimentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.model = self.root / "model"
        self.model.mkdir()
        self.sample = self.root / "sample.json"
        write_json(
            self.sample,
            [
                {
                    "source": "fictional",
                    "id": str(i),
                    "title": subject,
                    "messages": [{"role": "user", "text": subject}],
                }
                for i, subject in enumerate(
                    ["Solar batteries", "Garden irrigation", "Bread baking"]
                )
            ],
        )
        self.protocol = self.root / "protocol.json"
        write_json(
            self.protocol,
            {"dataset": "sample.json", "model_path": "model", "projection": "none"},
        )
        self.output = self.root / "run"

    def test_config_resolves_paths_and_rejects_mistakes_before_running(self):
        config = load_config(self.protocol)
        self.assertEqual(config.dataset, str(self.sample.resolve()))
        for changes in (
            {"seed": True},
            {"min_dist": float("inf")},
            {"clustering": "unknown"},
            {"unexpected": 1},
        ):
            value = {"dataset": "sample.json", "model_path": "model", **changes}
            self.protocol.write_text(json.dumps(value))
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                load_config(self.protocol)
        self.assertFalse(self.output.exists())

    def test_failure_preserves_frozen_inputs_and_failed_status(self):
        with (
            patch("chatos.experiments.runner.provenance", return_value={}),
            patch(
                "chatos.experiments.runner.embed",
                side_effect=RuntimeError("Local model unavailable"),
            ),
            self.assertRaises(RuntimeError),
        ):
            run(self.protocol, self.output)
        saved = json.loads((self.output / "run.json").read_text())
        self.assertEqual(saved["status"], "failed")
        self.assertEqual(saved["stage"], "embedding")
        self.assertEqual(verify(self.output)["status"], "failed")
        self.sample.write_text("changed original dataset")
        self.assertEqual(verify(self.output)["integrity"], "ok")
        with self.assertRaises(FileExistsError):
            run(self.protocol, self.output)

    @unittest.skipUnless(
        importlib.util.find_spec("numpy"), "Optional NumPy not installed"
    )
    def test_success_retains_order_and_absent_clustering_is_not_noise(self):
        import numpy as np

        with (
            patch("chatos.experiments.runner.provenance", return_value={}),
            patch(
                "chatos.experiments.runner.embed",
                return_value=(np.eye(3), {"input_pieces": 3}),
            ),
        ):
            result = run(self.protocol, self.output)
        self.assertEqual(result["status"], "complete")
        results = json.loads((self.output / "results.json").read_text())
        self.assertEqual(
            [r["point_id"] for r in results],
            ["fictional:0", "fictional:1", "fictional:2"],
        )
        self.assertTrue(
            all(r["cluster"] is None and r["coordinates"] is None for r in results)
        )
        metrics = json.loads((self.output / "metrics.json").read_text())
        self.assertIsNone(metrics["semantic_accuracy"])
        self.assertIsNone(metrics["unclustered"])
        self.assertEqual(verify(self.output)["status"], "complete")
        (self.output / "points.json").write_text("tampered")
        with self.assertRaisesRegex(ValueError, "integrity mismatch"):
            verify(self.output)

    def test_bundle_verification_rejects_extra_files_and_path_traversal(self):
        self.output.mkdir()
        write_json(self.output / "run.json", {"status": "complete"})
        seal(self.output)
        (self.output / "extra.txt").write_text("unrecorded")
        with self.assertRaisesRegex(ValueError, "Unrecorded"):
            verify(self.output)
        write_json(
            self.output / "manifest.json",
            {"schema_version": 1, "files": {"../outside": "hash"}},
        )
        with self.assertRaisesRegex(ValueError, "artifact path"):
            verify(self.output)

    def test_keyboard_interrupt_is_recorded_and_never_marks_complete(self):
        with (
            patch(
                "chatos.experiments.runner.provenance", side_effect=KeyboardInterrupt
            ),
            self.assertRaises(KeyboardInterrupt),
        ):
            run(self.protocol, self.output)
        self.assertEqual(verify(self.output)["status"], "interrupted")


if __name__ == "__main__":
    unittest.main()
