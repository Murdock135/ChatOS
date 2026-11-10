"""Verify source hierarchy and inert imported labels in the map experiment."""

import copy
import json
import unittest

from chatos.experiments.points import embedded_json, exchanges, topic_points


class TopicMapTests(unittest.TestCase):
    def setUp(self):
        self.record = {
            "pilot_id": "P001",
            "source": "fictional",
            "id": "conversation-1",
            "source_sha256": "source-hash",
            "messages": [
                {"role": "user", "text": "Discuss solar batteries"},
                {"role": "assistant", "text": "Battery discussion"},
                {"role": "user", "text": "Now discuss garden irrigation"},
            ],
        }
        self.response = {
            "model": "fictional",
            "pilot_id": "P001",
            "source_sha256": "source-hash",
            "status": "completed",
            "stop_reason": "end_turn",
            "validation": {
                "contract_valid": True,
                "summary": {
                    "main_subject": "Home projects",
                    "semantic_summary": "Two unrelated household topics",
                    "subtopics": [
                        {
                            "subject": subject,
                            "title": "Discussion",
                            "operation": "explanation",
                            "summary": "Source-grounded description",
                            "start_exchange": index,
                            "end_exchange": index,
                            "evidence_exchanges": [index],
                        }
                        for index, subject in enumerate(
                            ["Solar battery storage", "Garden irrigation"], 1
                        )
                    ],
                },
            },
        }

    def test_distinct_subjects_preserve_hierarchy_without_averaging(self):
        original = copy.deepcopy(self.response)
        points = topic_points(self.record, self.response)
        self.assertEqual(
            [p["embedding_text"] for p in points],
            ["Home projects", "Solar battery storage", "Garden irrigation"],
        )
        self.assertEqual([p["parent_id"] for p in points[1:]], [points[0]["id"]] * 2)
        self.assertEqual(points[2]["evidence_exchanges"], [2])
        self.assertEqual(self.response, original)

    def test_invalid_source_ranges_hash_and_partial_responses_are_rejected(self):
        variants = []
        bad = copy.deepcopy(self.response)
        bad["source_sha256"] = "other"
        variants.append(bad)
        bad = copy.deepcopy(self.response)
        bad["stop_reason"] = "max_tokens"
        variants.append(bad)
        bad = copy.deepcopy(self.response)
        bad["validation"]["summary"]["subtopics"][1]["start_exchange"] = 1
        variants.append(bad)
        bad = copy.deepcopy(self.response)
        bad["validation"]["summary"]["subtopics"][1]["evidence_exchanges"] = [3]
        variants.append(bad)
        for response in variants:
            with self.subTest(response=response), self.assertRaises(ValueError):
                topic_points(self.record, response)

    def test_imported_script_text_remains_json_data(self):
        value = {"label": "</script><script>alert('untrusted')</script>&"}
        encoded = embedded_json(value)
        self.assertNotIn("<", encoded)
        self.assertEqual(json.loads(encoded), value)

    def test_exchange_numbering_matches_pilot_with_leading_assistant(self):
        self.record["messages"].insert(
            0, {"role": "assistant", "text": "Partial start"}
        )
        self.assertEqual([len(g) for g in exchanges(self.record)], [1, 2, 1])


if __name__ == "__main__":
    unittest.main()
