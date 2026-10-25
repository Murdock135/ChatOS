"""Concurrent searches share initialized models without overlapping cold loads."""

import json
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from chatos import search_models


class ModelLoadingTests(unittest.TestCase):
    def test_concurrent_cold_loads_are_serialized_and_cached(self):
        active = 0
        calls = []
        guard = threading.Lock()
        start = threading.Barrier(4)

        def constructor(*args, **kwargs):
            nonlocal active
            with guard:
                active += 1
                self.assertEqual(active, 1, "Model constructors overlapped")
                calls.append(args[0])
            time.sleep(0.03)
            with guard:
                active -= 1
            return SimpleNamespace(num_labels=1)

        def load(kind):
            start.wait(timeout=5)
            return search_models.load_model(
                str(root), kind, json.dumps({"max_length": 256}), "fixture"
            )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            search_models._load_model.cache_clear()
            self.addCleanup(search_models._load_model.cache_clear)
            with (
                patch.object(search_models, "manifest", return_value={"files": {}}),
                patch.object(search_models, "model_directory", return_value=root),
                patch.object(search_models, "validate_files"),
                patch.dict(
                    "sys.modules",
                    {
                        "torch": SimpleNamespace(set_num_threads=lambda count: None),
                        "sentence_transformers": SimpleNamespace(
                            SentenceTransformer=constructor, CrossEncoder=constructor
                        ),
                    },
                ),
                ThreadPoolExecutor(4) as pool,
            ):
                futures = [
                    pool.submit(load, kind)
                    for kind in ("embedding", "embedding", "reranker", "reranker")
                ]
                results = [future.result(timeout=5) for future in futures]
            self.assertIs(results[0], results[1])
            self.assertIs(results[2], results[3])
            self.assertEqual(len(calls), 2)

    def test_initialization_error_is_actionable_and_can_be_retried(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            spec = json.dumps({"max_length": 256})
            search_models._load_model.cache_clear()
            self.addCleanup(search_models._load_model.cache_clear)
            constructor = unittest.mock.Mock(
                side_effect=[
                    NotImplementedError("uninitialized tensor"),
                    SimpleNamespace(),
                ]
            )
            with (
                patch.object(search_models, "manifest", return_value={"files": {}}),
                patch.object(search_models, "model_directory", return_value=root),
                patch.object(search_models, "validate_files"),
                patch.dict(
                    "sys.modules",
                    {
                        "torch": SimpleNamespace(set_num_threads=lambda count: None),
                        "sentence_transformers": SimpleNamespace(
                            SentenceTransformer=constructor, CrossEncoder=constructor
                        ),
                    },
                ),
            ):
                with self.assertRaisesRegex(
                    ValueError, "embedding model is incompatible"
                ):
                    search_models.load_model(str(root), "embedding", spec, "fixture")
                self.assertIsNotNone(
                    search_models.load_model(str(root), "embedding", spec, "fixture")
                )
