"""Evaluate passage-level success, negative noise and map limitations separately."""

from pathlib import Path
import tempfile
import unittest
from chatos.core import Store, write_json
from chatos.evaluation import evaluate, map_diagnostics


class EvaluationTests(unittest.TestCase):
    def test_real_retrieval_positive_negative_and_scope_cases(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            store = Store(root)
            try:
                write_json(
                    root / "System/Projects/registry.json",
                    {"projects": [{"id": "reading", "root": "/reading"}]},
                )
                store.put(
                    {
                        "source": "chatgpt",
                        "id": "reading",
                        "title": "Reading notes",
                        "workspace": "/reading",
                        "messages": [
                            {
                                "id": "choice",
                                "role": "user",
                                "text": "Use Markdown notebooks for reading notes.",
                            }
                        ],
                    }
                )
                cases = root / "cases.json"
                write_json(
                    cases,
                    {
                        "cases": [
                            {
                                "id": "positive",
                                "question": "Markdown notebooks",
                                "project": "reading",
                                "expected": {
                                    "source": "chatgpt",
                                    "conversation_id": "reading",
                                    "contains": "Use Markdown notebooks",
                                },
                            },
                            {
                                "id": "negative",
                                "question": "zygomorphxqv",
                                "expected": None,
                            },
                        ]
                    },
                )
                result = evaluate(store, cases)
                self.assertEqual(result["recall_at_k"], 1)
                self.assertEqual(result["negative_queries_with_results"], 0)
                self.assertEqual(result["scope_violations"], 0)
                self.assertEqual(result["positive_cases"], 1)
                self.assertEqual(result["negative_cases"], 1)
                self.assertEqual(map_diagnostics(store)["status"], "unavailable")
            finally:
                store.close()

    def test_wrong_chunk_in_correct_message_is_not_a_passage_hit(self):
        with tempfile.TemporaryDirectory() as directory:
            store = Store(Path(directory))
            try:
                store.put(
                    {
                        "source": "chatgpt",
                        "id": "one",
                        "title": "Notes",
                        "messages": [
                            {
                                "id": "u",
                                "role": "user",
                                "text": "Expected evidence followed by much unrelated material.",
                            }
                        ],
                    }
                )
                cases = Path(directory) / "cases.json"
                write_json(
                    cases,
                    {
                        "cases": [
                            {
                                "id": "one",
                                "question": "evidence",
                                "expected": {
                                    "source": "chatgpt",
                                    "conversation_id": "one",
                                    "contains": "Expected evidence",
                                },
                            }
                        ]
                    },
                )

                def unrelated(*args):
                    return {
                        "passages": [
                            {
                                "source": "chatgpt",
                                "id": "one",
                                "message_id": "u",
                                "excerpt": "unrelated material",
                            }
                        ]
                    }

                result = evaluate(store, cases, backend=unrelated)
                self.assertEqual(result["message_hit_rate"], 1)
                self.assertEqual(result["recall_at_k"], 0)
                self.assertEqual(result["mean_reciprocal_rank"], 0)
                write_json(
                    store.state / "dense-map.json",
                    {
                        "documents": [
                            {
                                "source": "chatgpt",
                                "id": "one",
                                "x": 0,
                                "y": 1,
                                "group": "unclustered",
                            }
                        ]
                    },
                )
                diagnostic = map_diagnostics(store)
                self.assertFalse(diagnostic["fresh"])
                self.assertEqual(diagnostic["unclustered"], 1)
                self.assertIn("Unmeasured", diagnostic["semantic_cluster_quality"])
            finally:
                store.close()

    def test_topic_pairs_need_actual_labels_and_detect_false_merges(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            store = Store(root)
            try:
                for identity in ["a", "b", "c"]:
                    store.put(
                        {
                            "source": "chatgpt",
                            "id": identity,
                            "title": identity,
                            "messages": [
                                {
                                    "id": "u",
                                    "role": "user",
                                    "text": "Fixture " + identity,
                                }
                            ],
                        }
                    )
                write_json(
                    store.state / "dense-map.json",
                    {
                        "documents": [
                            {
                                "source": "chatgpt",
                                "id": identity,
                                "x": i,
                                "y": 0,
                                "group": "one",
                            }
                            for i, identity in enumerate(["a", "b", "c"])
                        ]
                    },
                )
                labels = root / "labels.json"
                write_json(
                    labels,
                    {
                        "labels": [
                            {
                                "source": "chatgpt",
                                "id": identity,
                                "topics": ["reading"]
                                if identity in ["a", "b"]
                                else ["cooking"],
                            }
                            for identity in ["a", "b", "c"]
                        ]
                    },
                )
                score = map_diagnostics(store, labels)["topic_pair_evaluation"]
                self.assertEqual(score["positive_pairs_found"], 1)
                self.assertEqual(score["false_positive_pairs"], 2)
                self.assertAlmostEqual(score["pair_precision"], 1 / 3)
                self.assertEqual(score["pair_recall"], 1)
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
