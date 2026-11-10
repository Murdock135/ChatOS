"""History adapters preserve identity, pagination, source evidence and visible text."""

import json
import subprocess
import tempfile
import unittest
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import patch

from chatos.capture_merge import merge_codex
from chatos.chatgpt_history import capture as capture_chatgpt
from chatos.chatgpt_history import stage
from chatos.codex_api import HistoryError, pages, read_thread
from chatos.codex_api import capture as capture_codex
from chatos.core import Store
from chatos.importers import read_export_file
from chatos.runtime import sync
from chatos.setup import initialize


class FakeServer:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def request(self, method, params):
        self.calls.append((method, params))
        return next(self.responses)


def record(messages, api=False):
    return {
        "source": "codex",
        "id": "fictional",
        "title": "Fixture",
        "created_at": "2026-10-28T01:00:00Z",
        "updated_at": "2026-10-28T02:00:00Z",
        "messages": [
            {"id": identity, "role": role, "text": text, "model": None}
            for identity, role, text in messages
        ],
        "evidence": {"api_capture": {"items_view": "full"}}
        if api
        else {"parser": "codex-jsonl-v1"},
    }


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_pagination_follows_even_empty_pages_and_rejects_repeated_cursor(self):
        server = FakeServer(
            [
                {"data": [], "nextCursor": "next"},
                {"data": [{"id": "one"}], "nextCursor": None},
            ]
        )
        self.assertEqual(
            list(pages(server, "thread/list", {"archived": True})), [{"id": "one"}]
        )
        self.assertEqual(server.calls[1][1], {"archived": True, "cursor": "next"})
        server = FakeServer([{"data": [], "nextCursor": "same"}] * 2)
        with self.assertRaises(HistoryError):
            list(pages(server, "thread/list", {}))

    def test_full_history_filters_private_items_and_preserves_item_timestamps(self):
        server = FakeServer(
            [
                {
                    "data": [
                        {
                            "id": "turn",
                            "itemsView": "full",
                            "items": [],
                            "status": "completed",
                        }
                    ],
                    "nextCursor": None,
                },
                {
                    "data": [
                        {
                            "turnId": "turn",
                            "startedAtMs": 1793145600123,
                            "item": {
                                "id": "u",
                                "type": "userMessage",
                                "content": [{"type": "text", "text": "A question"}],
                            },
                        },
                        {
                            "turnId": "turn",
                            "item": {
                                "id": "r",
                                "type": "reasoning",
                                "content": ["PRIVATE"],
                            },
                        },
                        {
                            "turnId": "turn",
                            "item": {
                                "id": "tool",
                                "type": "commandExecution",
                                "aggregatedOutput": "PRIVATE",
                            },
                        },
                    ],
                    "nextCursor": "more",
                },
                {
                    "data": [
                        {
                            "turnId": "turn",
                            "item": {
                                "id": "a",
                                "type": "agentMessage",
                                "text": "An answer",
                                "phase": "final",
                            },
                        }
                    ],
                    "nextCursor": None,
                },
            ]
        )
        result = read_thread(
            server, {"id": "fictional", "name": "Test", "createdAt": 1793145600}
        )
        self.assertEqual(
            [m["text"] for m in result["messages"]], ["A question", "An answer"]
        )
        self.assertTrue(result["messages"][0]["timestamp"].endswith("00.123000+00:00"))
        self.assertIsNone(result["messages"][1]["model"])
        self.assertNotIn("PRIVATE", json.dumps(result))
        self.assertEqual(server.calls[0][1]["itemsView"], "full")

    def test_summary_response_cannot_be_published(self):
        server = FakeServer(
            [{"data": [{"id": "turn", "itemsView": "summary"}], "nextCursor": None}]
        )
        with self.assertRaises(HistoryError):
            read_thread(server, {"id": "fictional"})

    def test_merge_preserves_repeated_text_metadata_and_is_idempotent(self):
        before = record(
            [
                ("one", "user", "Again"),
                ("two", "assistant", "Answer"),
                ("three", "user", "Again"),
            ]
        )
        before["messages"][1]["model"] = "observed-model"
        api = record(
            [
                ("api-one", "user", "Again"),
                ("api-two", "assistant", "Answer"),
                ("api-three", "user", "Again"),
                ("api-four", "assistant", "New answer"),
            ],
            api=True,
        )
        combined = merge_codex(before, api)
        self.assertEqual(len(combined["messages"]), 4)
        self.assertEqual(combined["messages"][1]["model"], "observed-model")
        self.assertEqual(combined, merge_codex(combined, api))
        store = Store(self.root / "archive")
        self.addCleanup(store.close)
        self.assertTrue(store.put(before))
        self.assertTrue(store.put(api))
        self.assertFalse(store.put(api))
        store.put(before)
        saved = json.loads(
            store.db.execute("SELECT record_json FROM conversations").fetchone()[0]
        )
        self.assertEqual(len(saved["messages"]), 4)

    def test_single_raw_export_stages_all_branches_and_sync_imports_it(self):
        workspace = self.root / "workspace"
        initialize(workspace)
        exported = self.root / "export" / "conversations"
        exported.mkdir(parents=True)
        data = {
            "conversation_id": "chat-example",
            "title": "Branch fixture",
            "create_time": 1793145600,
            "mapping": {
                "u": {
                    "parent": None,
                    "message": {
                        "id": "u",
                        "author": {"role": "user"},
                        "content": {"parts": ["Question"]},
                    },
                },
                "a": {
                    "parent": "u",
                    "message": {
                        "id": "a",
                        "author": {"role": "assistant"},
                        "content": {"parts": ["First answer"]},
                    },
                },
                "b": {
                    "parent": "u",
                    "message": {
                        "id": "b",
                        "author": {"role": "assistant"},
                        "content": {"parts": ["Alternative answer"]},
                    },
                },
            },
            "current_node": "b",
        }
        file = exported / "chat-example.json"
        file.write_text(json.dumps(data))
        original = file.read_bytes()
        self.assertEqual(len(read_export_file(file, "chatgpt")[0]["messages"]), 3)
        self.assertEqual(stage(workspace, exported.parent)["staged"], 1)
        self.assertEqual(file.read_bytes(), original)
        result = sync(workspace)
        self.assertEqual(result["status"], "ok", result["errors"])
        store = Store(workspace)
        self.addCleanup(store.close)
        row = store.db.execute(
            "SELECT record_json FROM conversations WHERE source='chatgpt'"
        ).fetchone()
        self.assertEqual(len(json.loads(row[0])["messages"]), 3)

    def test_codex_api_snapshot_syncs_even_with_no_rollout(self):
        workspace = self.root / "workspace"
        home = self.root / "codex"
        home.mkdir()
        initialize(workspace, home)
        inbox = workspace / "your_ais/codex/imports"
        inbox.mkdir(parents=True, exist_ok=True)
        (inbox / "fictional.json").write_text(
            json.dumps(record([("m", "assistant", "Recovered answer")], api=True))
        )
        result = sync(workspace)
        self.assertEqual(result["status"], "ok", result["errors"])
        store = Store(workspace)
        self.addCleanup(store.close)
        self.assertEqual(
            store.db.execute("SELECT count(*) FROM conversations").fetchone()[0], 1
        )

    def test_known_separated_wrappers_align_without_losing_original_text(self):
        text = "Answer<oai-mem-citation>source citation</oai-mem-citation>"
        local = record([("local", "assistant", text)])
        api = record([("api", "assistant", "Answer")], api=True)
        merged = merge_codex(local, api)
        self.assertEqual(len(merged["messages"]), 1)
        self.assertEqual(merged["messages"][0]["text"], text)
        self.assertEqual(merged["messages"][0]["source_item_ids"], ["api", "local"])
        local = record(
            [
                (
                    "local",
                    "user",
                    'Photo\n<image name=[Image #1] path="/fictional.png">\n</image>',
                )
            ]
        )
        api = record([("api", "user", "Photo")], api=True)
        api["messages"][0]["attachments"] = [
            {"type": "localImage", "reference": "/fictional.png"}
        ]
        self.assertEqual(len(merge_codex(local, api)["messages"]), 1)

    def test_older_snapshot_cannot_revert_a_revised_stable_item(self):
        newer = record([("stable", "assistant", "Revised answer")], api=True)
        older = record([("stable", "assistant", "Earlier answer")])
        older["updated_at"] = "2026-10-27T01:00:00Z"
        merged = merge_codex(newer, older)
        self.assertEqual(merged["messages"][0]["text"], "Revised answer")
        self.assertEqual(merged["updated_at"], newer["updated_at"])

    def test_revised_api_alias_updates_the_same_retained_item(self):
        local = record([("local", "assistant", "Earlier answer")])
        api = record([("api", "assistant", "Earlier answer")], api=True)
        combined = merge_codex(local, api)
        revised = record([("api", "assistant", "Revised answer")], api=True)
        revised["updated_at"] = "2026-10-29T01:00:00Z"
        result = merge_codex(combined, revised)
        self.assertEqual(len(result["messages"]), 1)
        self.assertEqual(result["messages"][0]["id"], "local")
        self.assertEqual(result["messages"][0]["text"], "Revised answer")

    def test_failed_later_page_keeps_last_successful_api_snapshot(self):
        workspace, home = self.root / "workspace", self.root / "codex"
        home.mkdir()
        initialize(workspace, home)
        destination = workspace / "your_ais/codex/imports/fictional.json"
        destination.write_text(
            json.dumps(record([("m", "assistant", "Retained")], api=True))
        )
        before = destination.read_bytes()
        server = FakeServer(
            [
                {"thread": {"id": "fictional"}},
                {
                    "data": [{"id": "turn", "items": [], "itemsView": "full"}],
                    "nextCursor": "older",
                },
                {"data": [], "nextCursor": "older"},
            ]
        )
        with patch("chatos.codex_api.AppServer", return_value=nullcontext(server)):
            result = capture_codex(
                workspace, home, thread_ids=["fictional"], force=True
            )
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["captured"], 0)
        self.assertEqual(result["errors"][0]["id"], "fictional")
        self.assertEqual(destination.read_bytes(), before)

    def test_exporter_zero_exit_with_failed_downloads_is_partial(self):
        workspace = self.root / "workspace"
        initialize(workspace)
        exporter, config = self.root / "exporter.py", self.root / "private.json"
        exporter.write_text("# fictional exporter; never executed")
        config.write_text("{}")
        config.chmod(0o600)
        process = subprocess.CompletedProcess(
            [],
            0,
            stdout="SENSITIVE RESPONSE\nDone: 0 downloaded, 0 unchanged, 2 failed -> export",
        )
        with patch("chatos.chatgpt_history.subprocess.run", return_value=process):
            result = capture_chatgpt(workspace, exporter, config)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["failed"], 2)
        self.assertNotIn("SENSITIVE", json.dumps(result))
        receipt = (
            workspace / "app_data/state/chatgpt-history-capture.json"
        ).read_text()
        self.assertNotIn("SENSITIVE", receipt)

    def test_exporter_timeout_and_public_config_are_reported_safely(self):
        workspace = self.root / "workspace"
        initialize(workspace)
        exporter, config = self.root / "exporter.py", self.root / "private.json"
        exporter.write_text("# fixture")
        config.write_text("{}")
        config.chmod(0o644)
        with self.assertRaisesRegex(ValueError, "chmod 600"):
            capture_chatgpt(workspace, exporter, config)
        config.chmod(0o600)
        with patch(
            "chatos.chatgpt_history.subprocess.run",
            side_effect=subprocess.TimeoutExpired([], 3600, output="PRIVATE"),
        ):
            result = capture_chatgpt(workspace, exporter, config)
        self.assertEqual(result["status"], "error")
        self.assertTrue(result["timed_out"])
        self.assertNotIn("PRIVATE", json.dumps(result))

    def test_chatgpt_active_branch_media_and_hidden_messages(self):
        file = self.root / "conversation.json"
        file.write_text(
            json.dumps(
                {
                    "id": "media-chat",
                    "current_node": "visible",
                    "mapping": {
                        "visible": {
                            "parent": None,
                            "children": ["hidden"],
                            "message": {
                                "id": "m",
                                "author": {"role": "user"},
                                "content": {
                                    "parts": [
                                        {
                                            "content_type": "audio_transcription",
                                            "text": "Spoken words",
                                        },
                                        {
                                            "content_type": "audio",
                                            "audio_asset_pointer": "asset:audio",
                                        },
                                    ]
                                },
                                "metadata": {
                                    "attachments": [
                                        {
                                            "id": "file",
                                            "name": "notes.pdf",
                                            "mime_type": "application/pdf",
                                        }
                                    ]
                                },
                            },
                        },
                        "hidden": {
                            "parent": "visible",
                            "message": {
                                "id": "hidden-message",
                                "author": {"role": "assistant"},
                                "content": {"parts": ["PRIVATE"]},
                                "metadata": {
                                    "is_visually_hidden_from_conversation": True
                                },
                            },
                        },
                    },
                }
            )
        )
        result = read_export_file(file, "chatgpt")[0]
        self.assertEqual(len(result["messages"]), 1)
        message = result["messages"][0]
        self.assertEqual(message["text"], "Spoken words")
        self.assertTrue(message["on_active_branch"])
        self.assertEqual(message["children_ids"], ["hidden"])
        self.assertEqual(message["attachments"][1]["name"], "notes.pdf")
        self.assertNotIn("PRIVATE", json.dumps(result))


if __name__ == "__main__":
    unittest.main()
