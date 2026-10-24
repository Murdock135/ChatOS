"""Coverage counts must distinguish known gaps from capture completeness."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from chatos.core import Store, write_json
from chatos.coverage import report


class CoverageTests(unittest.TestCase):
    def test_observed_counts_keep_missing_references_and_unknown_denominator(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            store = Store(root)
            try:
                store.put(
                    {
                        "source": "chatgpt",
                        "id": "sample",
                        "title": "A partial sample",
                        "capture": "partial_desktop_tool_capture",
                        "messages": [
                            {"id": "u", "role": "user", "text": "Available question"}
                        ],
                        "evidence": {"unavailable_message_text": [{"id": "reply"}]},
                    }
                )
                store.put(
                    {
                        "source": "codex",
                        "id": "retained",
                        "title": "Earlier retained source",
                        "capture": "available_visible_messages",
                        "messages": [
                            {"id": "u", "role": "user", "text": "Earlier capture"}
                        ],
                    }
                )
                write_json(
                    store.state / "status.json",
                    {
                        "status": "ok",
                        "sources": {"chatgpt": {"status": "partial_app_capture"}},
                        "unavailable_history": [
                            {"id": "projected"},
                            {"id": "missing"},
                            {"id": "retained"},
                        ],
                        "unrecovered_history": [{"id": "missing"}, {"id": "retained"}],
                    },
                )
                changes = store.db.total_changes
                result = report(store)
                self.assertEqual(store.db.total_changes, changes)
                self.assertEqual(result["sources"]["chatgpt"]["records"], 1)
                self.assertEqual(
                    result["sources"]["chatgpt"]["unavailable_message_references"], 1
                )
                self.assertEqual(
                    result["sources"]["codex"]["known_uncaptured_history_ids"],
                    ["missing"],
                )
                self.assertEqual(
                    result["sources"]["codex"]["unavailable_rollout_files_last_scan"], 3
                )
                self.assertIn("not all account history", result["limits"][0])
                self.assertEqual(result["sources"]["muse"]["records"], 0)
            finally:
                store.close()

    def test_checkout_command_reports_an_empty_workspace_without_a_source_scan(self):
        with tempfile.TemporaryDirectory() as directory:
            command = Path(__file__).resolve().parents[1] / "scripts/chatos"
            process = subprocess.run(
                [str(command), "--root", directory, "coverage", "--json"],
                cwd=directory,
                capture_output=True,
                text=True,
                check=True,
            )
            result = json.loads(process.stdout)
            self.assertEqual(result["last_sync_status"], "never_run")
            self.assertIsNone(result["sources"]["codex"]["last_scan"])


if __name__ == "__main__":
    unittest.main()
