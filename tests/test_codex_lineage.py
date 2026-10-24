"""Fork history must retain identity, chronology and message provenance."""

import json
from pathlib import Path
import tempfile
import unittest

from chatos.core import Store
from chatos.importers import read_codex
from chatos.retrieval import refresh, retrieve


def event(kind: str, payload: dict) -> str:
    return (
        json.dumps(
            {"type": kind, "timestamp": "2026-10-23T16:35:12Z", "payload": payload}
        )
        + "\n"
    )


def message(text: str, role: str = "user") -> str:
    return event(
        "response_item",
        {
            "type": "message",
            "role": role,
            "content": [{"type": "input_text", "text": text}],
        },
    )


class ForkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.path = self.root / "fork.jsonl"
        self.child = {
            "id": "child",
            "forked_from_id": "parent",
            "timestamp": "2026-10-23T16:35:11Z",
            "cwd": "/child",
        }
        self.parent = {
            "id": "parent",
            "timestamp": "2026-10-23T16:28:31Z",
            "cwd": "/parent",
        }

    def read(self, *events: str) -> dict:
        self.path.write_text("".join(events))
        return read_codex(self.path, {"id": "child", "title": "Fork fixture"})

    def test_inherited_history_preserves_owner_and_cited_origin(self):
        record = self.read(
            event("session_meta", self.child),
            event("session_meta", self.parent),
            event(
                "turn_context", {"turn_id": "inherited-turn", "model": "parent-model"}
            ),
            message("Inherited cobalt decision"),
            event("session_meta", self.parent),
            event("session_meta", self.child),
            event("turn_context", {"turn_id": "child-turn", "model": "child-model"}),
            message("New child question"),
            message("Child answer", "assistant"),
            message("PRIVATE", "developer"),
        )
        original = self.path.read_bytes()
        repeated = read_codex(self.path, {"id": "child", "title": "Fork fixture"})
        self.assertEqual(record, repeated)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(record["id"], "child")
        self.assertEqual(record["created_at"], self.child["timestamp"])
        self.assertEqual(record["workspace"], "/child")
        self.assertEqual(record["evidence"]["forked_from_id"], "parent")
        self.assertEqual(
            [m["origin_conversation_id"] for m in record["messages"]],
            ["parent", "child", "child"],
        )
        self.assertEqual(
            [m["inherited"] for m in record["messages"]], [True, False, False]
        )
        self.assertEqual(record["model_history"][0]["origin_conversation_id"], "parent")
        self.assertEqual(record["messages"][-1]["model"], "child-model")
        self.assertNotIn("PRIVATE", json.dumps(record))
        store = Store(self.root / "archive")
        try:
            self.assertTrue(store.put(record))
            self.assertFalse(store.put(record))
            refresh(store)
            evidence = retrieve(store, "cobalt")["passages"][0]
            self.assertEqual(evidence["id"], "child")
            self.assertEqual(evidence["origin_conversation_id"], "parent")
            self.assertTrue(evidence["inherited"])
        finally:
            store.close()

    def test_unrelated_session_and_wrong_owner_remain_rejected(self):
        for events in [
            [
                event("session_meta", self.child),
                event("session_meta", {"id": "unrelated"}),
            ],
            [event("session_meta", self.parent), event("session_meta", self.child)],
            [
                event("session_meta", {"id": "child"}),
                event("session_meta", self.parent),
            ],
        ]:
            with self.subTest(events=events), self.assertRaises(ValueError):
                self.read(*events)

    def test_transitive_ancestry_is_explicit_and_cycles_are_rejected(self):
        record = self.read(
            event("session_meta", self.child),
            event("session_meta", {**self.parent, "forked_from_id": "grandparent"}),
            event("session_meta", {"id": "grandparent"}),
            message("Older inherited text"),
        )
        self.assertEqual(record["messages"][0]["origin_conversation_id"], "grandparent")
        for payload in [
            {**self.child, "forked_from_id": "another-parent"},
            {**self.parent, "forked_from_id": "child"},
            {**self.parent, "forked_from_id": []},
        ]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                self.read(
                    event("session_meta", self.child), event("session_meta", payload)
                )


if __name__ == "__main__":
    unittest.main()
