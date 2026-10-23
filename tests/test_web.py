"""Local UI operations preserve sources and reject unauthenticated/cross-origin access."""

import hashlib
import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from chatos.core import Store
from chatos.web import LocalServer
from chatos import library
from chatos.retrieval import retrieve
from chatos.runtime import backup
from chatos.recovery import restore, verify_backup


class WebTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "workspace"
        store = Store(self.root)
        self.record = {
            "source": "chatgpt",
            "id": "one",
            "title": "Original title",
            "created_at": "2026-01-01",
            "messages": [
                {
                    "id": "question",
                    "role": "user",
                    "text": "<script>alert(1)</script> readable transcript",
                },
                {"id": "answer", "role": "assistant", "text": "A source answer"},
            ],
        }
        store.put(self.record)
        self.original = store.records()[0]
        registry = self.root / "System/Projects/registry.json"
        registry.parent.mkdir(parents=True)
        registry.write_text(
            json.dumps(
                {
                    "projects": [
                        {
                            "id": "research",
                            "name": "Research",
                            "root": "/research",
                            "entrypoint": "/research/Home.md",
                        }
                    ]
                }
            )
        )
        store.close()
        self.server = LocalServer(self.root, 0)
        self.worker = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.worker.start()
        self.addCleanup(self.stop)

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.worker.join()

    def request(self, path, method="GET", data=None, authenticated=True, **extra):
        connection = http.client.HTTPConnection(
            "127.0.0.1", self.server.server_port, timeout=5
        )
        headers = {"Content-Type": "application/json"}
        if authenticated:
            headers["X-ChatOS-Token"] = self.server.token
        headers.update(extra)
        connection.request(
            method,
            path,
            data
            if isinstance(data, bytes)
            else json.dumps(data)
            if data is not None
            else None,
            headers,
        )
        response = connection.getresponse()
        body = response.read()
        result = (
            json.loads(body)
            if response.getheader("Content-Type").startswith("application/json")
            else body.decode()
        )
        status = response.status
        connection.close()
        return status, result

    def test_api_requires_token_and_rejects_cross_origin_and_host(self):
        self.assertEqual(self.request("/api/chats", authenticated=False)[0], 401)
        self.assertEqual(
            self.request("/api/chats", Origin="https://example.com")[0], 403
        )
        self.assertEqual(self.request("/api/chats", Host="example.com")[0], 403)
        self.assertEqual(self.request("/../../etc/passwd")[0], 404)
        self.assertEqual(
            self.request("/api/context/read?path=../../etc/passwd")[0], 404
        )
        code, html = self.request("/", authenticated=False)
        self.assertEqual(code, 200)
        self.assertNotIn("<script>alert(1)</script>", html)

    def test_annotations_search_archive_restore_and_source_preservation(self):
        self.assertEqual(self.request("/api/chats?q=readable")[1]["total"], 1)
        changes = {"title": "My local title", "note": "Remember the violet protocol"}
        self.assertEqual(
            self.request(
                "/api/annotation",
                "PUT",
                {"source": "chatgpt", "id": "one", "changes": changes},
            )[0],
            200,
        )
        self.assertEqual(
            self.request("/api/chats?q=violet")[1]["items"][0]["title"],
            "My local title",
        )
        self.request(
            "/api/annotation",
            "PUT",
            {"source": "chatgpt", "id": "one", "changes": {"archived": True}},
        )
        self.assertEqual(self.request("/api/chats")[1]["total"], 0)
        self.assertEqual(self.request("/api/chats?archived=true")[1]["total"], 1)
        self.request(
            "/api/annotation",
            "PUT",
            {"source": "chatgpt", "id": "one", "changes": {"archived": False}},
        )
        data = self.request("/api/chat?source=chatgpt&id=one")[1]
        self.assertEqual(data["record"], self.original)
        self.assertEqual(data["annotation"]["note"], changes["note"])
        store = Store(self.root)
        try:
            passages = retrieve(store, "violet protocol")["passages"]
            self.assertTrue(
                any(item["role"] == "local_annotation" for item in passages)
            )
            self.assertTrue(all(item["source"] == "workspace" for item in passages))
        finally:
            store.close()

    def test_assignment_and_invalid_annotation_do_not_change_source_messages(self):
        self.assertEqual(
            self.request(
                "/api/annotation",
                "PUT",
                {"source": "chatgpt", "id": "one", "changes": {"archived": "yes"}},
            )[0],
            400,
        )
        self.assertEqual(
            self.request(
                "/api/assign",
                "POST",
                {"source": "chatgpt", "id": "one", "projects": ["missing"]},
            )[0],
            400,
        )
        self.assertEqual(
            self.request(
                "/api/assign",
                "POST",
                {"source": "chatgpt", "id": "one", "projects": ["research"]},
            )[0],
            200,
        )
        data = self.request("/api/chat?source=chatgpt&id=one")[1]
        self.assertEqual(data["record"]["projects"], ["research"])
        self.assertEqual(data["record"]["messages"], self.original["messages"])

    def test_unexpected_failures_have_local_diagnostics_without_request_or_error_text(
        self,
    ):
        with patch(
            "chatos.web.library.list_chats",
            side_effect=RuntimeError("PRIVATE TEST TEXT"),
        ):
            code, result = self.request("/api/chats?q=PRIVATE_QUERY_TEXT")
        self.assertEqual(code, 500)
        log = (self.root / "System/Logs/interface-errors.jsonl").read_text()
        self.assertNotIn("PRIVATE TEST TEXT", log + result["error"])
        self.assertNotIn("PRIVATE_QUERY_TEXT", log + result["error"])
        event = json.loads(log)
        self.assertEqual(event["error_type"], "RuntimeError")
        self.assertIn(event["id"], result["error"])
        self.assertTrue(event["frames"])

    def test_map_uses_current_local_titles_and_project_assignments(self):
        page = self.root / "Humans/explorer.html"
        page.parent.mkdir(parents=True)
        original = (
            '<script type="application/json" id="data">'
            + json.dumps(
                {
                    "documents": [
                        {
                            "source": "chatgpt",
                            "id": "one",
                            "title": "Old title",
                            "projects": [],
                            "x": 1,
                            "y": 2,
                        }
                    ]
                }
            )
            + "</script>"
        )
        page.write_text(original)
        self.request(
            "/api/annotation",
            "PUT",
            {
                "source": "chatgpt",
                "id": "one",
                "changes": {"title": "Current local title"},
            },
        )
        self.request(
            "/api/assign",
            "POST",
            {"source": "chatgpt", "id": "one", "projects": ["research"]},
        )
        point = self.request("/api/map")[1]["documents"][0]
        self.assertEqual(point["title"], "Current local title")
        self.assertEqual(point["projects"], ["research"])
        self.assertEqual((point["x"], point["y"]), (1, 2))
        self.assertEqual(page.read_text(), original)

    def test_import_action_validates_before_publishing_a_local_inbox_file(self):
        payload = (
            Path(__file__).parents[1] / "docs/examples/conversations.json"
        ).read_bytes()
        code, result = self.request("/api/import?format=json", "POST", payload)
        self.assertEqual(code, 200)
        self.assertEqual(result["conversations"], 1)
        self.assertEqual(Path(result["path"]).read_bytes(), payload)
        self.assertEqual(
            self.request("/api/import?format=json", "POST", b"not JSON")[0], 400
        )
        self.assertEqual(len(list((self.root / "System/Imports/chatgpt").iterdir())), 1)
        self.assertEqual(self.request("/api/chats")[1]["total"], 1)

    def test_backup_action_creates_a_fresh_verified_database(self):
        self.request(
            "/api/annotation",
            "PUT",
            {
                "source": "chatgpt",
                "id": "one",
                "changes": {"note": "A note before backup"},
            },
        )
        code, result = self.request("/api/backup", "POST", {})
        self.assertEqual(code, 200)
        self.assertEqual(verify_backup(result["path"])["conversations"], 1)
        self.assertNotEqual(
            result["path"], self.request("/api/backup", "POST", {})[1]["path"]
        )

    def test_context_preview_is_allowlisted_and_integrity_checked(self):
        captured = "2026-01-01T00-00-00Z"
        snapshot = self.root / "System/Snapshots" / captured
        snapshot.mkdir(parents=True)
        content = "A fictional captured memory."
        (snapshot / "memory.md").write_text(content)
        manifest = {
            "captured_at_utc": captured,
            "files": [
                {
                    "source": "/fictional/memory.md",
                    "snapshot": "memory.md",
                    "category": "memory",
                    "sha256": hashlib.sha256(content.encode()).hexdigest(),
                }
            ],
        }
        (snapshot / "manifest.json").write_text(json.dumps(manifest))
        (self.root / "System/Latest snapshot.md").write_text(
            "[Snapshot](Snapshots/" + captured + "/Index.md)"
        )
        self.assertEqual(len(self.request("/api/context")[1]["items"]), 1)
        self.assertEqual(
            self.request("/api/context/read?path=memory.md")[1]["text"], content
        )
        self.assertEqual(self.request("/api/context/read?path=other.md")[0], 404)
        (snapshot / "memory.md").write_text("Changed outside the archive")
        self.assertEqual(self.request("/api/context/read?path=memory.md")[0], 400)

    def test_annotation_backup_and_restore_retains_both_database_and_readable_note(
        self,
    ):
        store = Store(self.root)
        try:
            library.update(
                store,
                "chatgpt",
                "one",
                {"note": "A durable annotation", "archived": True},
            )
            result = backup(store, fresh=True)
        finally:
            store.close()
        destination = Path(self.temp.name) / "restored"
        restore(result["path"], destination)
        store = Store(destination)
        try:
            self.assertEqual(
                library.get(store, "chatgpt", "one")[1]["note"], "A durable annotation"
            )
            self.assertTrue(library.get(store, "chatgpt", "one")[1]["archived"])
            self.assertIn(
                "A durable annotation",
                library.annotation_path(store, "chatgpt", "one").read_text(),
            )
        finally:
            store.close()


if __name__ == "__main__":
    unittest.main()
