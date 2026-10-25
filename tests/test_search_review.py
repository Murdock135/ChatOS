"""Assistant results must point to current captured evidence within the scope."""

import json
import tempfile
import unittest
from pathlib import Path

from chatos.core import Store
from chatos.search_models import DEFAULTS, save, settings
from chatos.search_review import path, prepare, results


class SearchReviewTests(unittest.TestCase):
    def test_source_checked_results_and_changed_query(self):
        with tempfile.TemporaryDirectory() as directory:
            store = Store(Path(directory))
            self.addCleanup(store.close)
            store.put(
                {
                    "source": "codex",
                    "id": "one",
                    "title": "Skills",
                    "messages": [
                        {
                            "id": "m1",
                            "role": "user",
                            "text": "LangChain skills documentation",
                        }
                    ],
                }
            )
            review = prepare(store, "langchain")
            output = path(store, review["id"]).with_suffix(".results.json")
            hit = {
                "source": "codex",
                "id": "one",
                "message_id": "m1",
                "excerpt": "LangChain skills",
                "reason": "Discusses agent skills",
            }
            output.write_text(json.dumps([hit]))
            self.assertEqual(
                results(store, review["id"], "langchain")["items"][0]["match"][
                    "message_id"
                ],
                "m1",
            )
            with self.assertRaises(ValueError):
                results(store, review["id"], "different query")
            hit["excerpt"] = "Invented evidence"
            output.write_text(json.dumps([hit]))
            with self.assertRaises(ValueError):
                results(store, review["id"], "langchain")
            output.write_text("[]")
            self.assertEqual(results(store, review["id"], "langchain")["total"], 0)

    def test_model_choice_is_not_restricted_to_presets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = json.loads(json.dumps(DEFAULTS))
            config["embedding"]["model_id"] = "another/compatible-model"
            save(root, config)
            self.assertEqual(
                settings(root)["embedding"]["model_id"], "another/compatible-model"
            )
