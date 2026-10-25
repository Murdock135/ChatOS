import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from chatos.core import Store


@unittest.skipUnless(
    importlib.util.find_spec("numpy"),
    "Optional semantic environment is not installed in this interpreter",
)
class DenseTests(unittest.TestCase):
    def test_semantic_only_hit_keeps_exact_citation_and_stale_text_is_excluded(self):
        import numpy as np

        from chatos.dense import REVISION, passages, retrieve

        with tempfile.TemporaryDirectory() as temp:
            store = Store(Path(temp))
            self.addCleanup(store.close)
            record = {
                "source": "muse",
                "id": "one",
                "title": "A choice",
                "messages": [
                    {"id": "m1", "role": "user", "text": "Readable modular functions."}
                ],
            }
            store.put(record)
            item = passages(store)[0]
            vector = np.zeros(1024, dtype="<f4")
            vector[0] = 1
            with store.db:
                store.db.execute(
                    "INSERT INTO dense_vectors VALUES(?,?,?)",
                    (item["identity"], REVISION, vector.tobytes()),
                )

            class FakeEncoder:
                def encode(self, *args, **kwargs):
                    return np.array([vector])

            class FakeReranker:
                def predict(self, pairs, **kwargs):
                    return [1.0] * len(pairs)

            from chatos.search_models import DEFAULTS

            with (
                patch("chatos.dense.settings", return_value=DEFAULTS),
                patch("chatos.dense.fingerprint", return_value=REVISION),
                patch(
                    "chatos.dense.model",
                    side_effect=lambda root, kind, config: (
                        FakeEncoder() if kind == "embedding" else FakeReranker()
                    ),
                ),
            ):
                packet = retrieve(store, "engineering preferences", limit=1)
                self.assertEqual(
                    packet["passages"][0]["excerpt"], "Readable modular functions."
                )
                self.assertEqual(packet["passages"][0]["message_id"], "m1")
                self.assertEqual(
                    packet["coverage"], {"current_vectors": 1, "current_passages": 1}
                )
                record["messages"][0]["text"] = "A revised source statement."
                store.put(record)
                with self.assertRaises(ValueError):
                    retrieve(store, "engineering preferences")


if __name__ == "__main__":
    unittest.main()
