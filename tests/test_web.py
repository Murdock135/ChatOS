"""Local UI operations preserve sources and reject unauthenticated/cross-origin access."""

import hashlib
import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from chatos import library
from chatos.core import Store, digest
from chatos.recovery import restore, verify_backup
from chatos.retrieval import retrieve
from chatos.runtime import backup
from chatos.web import LocalServer


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

    def test_browser_authorization_survives_restart_and_is_workspace_scoped(self):
        from chatos.web import workspace_token

        self.assertEqual(workspace_token(self.root), self.server.token)
        other = Path(self.temp.name) / "independent-workspace"
        self.assertNotEqual(workspace_token(other), self.server.token)
        token_file = self.root / "System/State/browser-token"
        self.assertEqual(token_file.stat().st_mode & 0o777, 0o600)
        # A new server process uses the saved token, so open browser tabs survive.
        replacement = LocalServer(self.root, 0)
        try:
            self.assertEqual(replacement.token, self.server.token)
        finally:
            replacement.server_close()

    def test_compiled_frontend_assets_are_served_without_exposing_paths(self):
        import re

        html = self.request("/", authenticated=False)[1]
        stylesheet = re.search(r'href="(/_astro/[^\"]+\.css)"', html)
        self.assertIsNotNone(stylesheet)
        status, content = self.request(stylesheet.group(1), authenticated=False)
        self.assertEqual(status, 200)
        self.assertIn("search-bar", content)
        self.assertEqual(
            self.request("/_astro/missing.css", authenticated=False)[0], 404
        )
        self.assertEqual(
            self.request("/_astro/../../pyproject.toml", authenticated=False)[0], 404
        )

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

    def test_search_ranks_passages_groups_chats_and_preserves_filters(self):
        store = Store(self.root)
        try:
            for identity, title, date, texts in [
                (
                    "focused",
                    "LangChain agent skills",
                    "2020-01-01",
                    [
                        "How do LangChain agent skills work?",
                        "LangChain skills documentation",
                    ],
                ),
                (
                    "incidental",
                    "Weekly planning",
                    "2026-01-01",
                    [
                        (
                            "Discuss hiring, calendars and meeting plans. "
                            "LangChain is one resume skill."
                        )
                    ],
                ),
                ("unrelated", "Cooking", "2027-01-01", ["Bake bread."]),
            ]:
                store.put(
                    {
                        "source": "codex",
                        "id": identity,
                        "title": title,
                        "updated_at": date,
                        "projects": ["research"],
                        "messages": [
                            {"id": identity + str(n), "role": "user", "text": text}
                            for n, text in enumerate(texts)
                        ],
                    }
                )
        finally:
            store.close()
        data = self.request("/api/chats?q=langchain")[1]
        self.assertEqual(data["total"], 2)
        self.assertEqual(
            [item["id"] for item in data["items"]], ["focused", "incidental"]
        )
        match = data["items"][0]["match"]
        self.assertIn("LangChain", match["excerpt"])
        self.assertIn(match["message_id"], ["focused0", "focused1"])
        self.assertEqual(
            self.request("/api/chats?q=langchain&source=chatgpt")[1]["total"], 0
        )
        self.assertEqual(
            self.request("/api/chats?q=langchain&project=missing")[1]["total"], 0
        )
        self.assertEqual(
            self.request("/api/chats?q=langchain&archived=true")[1]["total"], 0
        )
        self.assertEqual(self.request("/api/chats?q=langchain%20skills")[1]["total"], 1)
        self.assertEqual(self.request("/api/chats?q=nonexistentterm")[1]["total"], 0)
        page = self.request("/api/chats?q=langchain&limit=1&offset=1")[1]
        self.assertEqual(page["total"], 2)
        self.assertEqual(page["items"][0]["id"], "incidental")
        self.assertEqual(self.request("/api/chats")[1]["items"][0]["id"], "unrelated")
        html = self.request("/", authenticated=False)[1]
        self.assertNotIn('id="evidence"', html)

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
                    "input_fingerprint": digest([self.original]),
                    "documents": [
                        {
                            "source": "chatgpt",
                            "id": "one",
                            "title": "Old title",
                            "projects": [],
                            "x": 1,
                            "y": 2,
                        }
                    ],
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
        response = self.request("/api/map")[1]
        self.assertIn("changed", response["freshness_note"])
        point = response["documents"][0]
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


class GuidedWebTests(unittest.TestCase):
    """Exercise the same setup, review and handoff boundaries used by the browser."""

    request = WebTests.request
    stop = WebTests.stop

    def setUp(self):
        from chatos.setup import initialize

        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "Avery's workspace"
        initialize(self.root)
        store = Store(self.root)
        for identity, text in [
            ("selected", "Keep my reading notes in Markdown."),
            ("private", "Leave this conversation out of the handoff."),
        ]:
            store.put(
                {
                    "source": "chatgpt",
                    "id": identity,
                    "title": identity,
                    "created_at": "2026-10-23",
                    "messages": [
                        {"id": identity + "-message", "role": "user", "text": text}
                    ],
                }
            )
        self.records = store.records()
        store.close()
        self.server = LocalServer(self.root, 0)
        self.worker = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.worker.start()
        self.addCleanup(self.stop)

    def test_setup_source_selection_and_guide_are_explicit(self):
        status, setup = self.request("/api/setup")
        self.assertEqual(status, 200)
        self.assertEqual(setup["records"], 2)
        self.assertFalse(setup["codex_enabled"])
        self.assertEqual(
            self.request(
                "/api/source/codex", "POST", {"enabled": True, "path": "relative"}
            )[0],
            400,
        )
        self.assertEqual(
            self.request("/api/source/codex", "POST", {"enabled": "yes"})[0], 400
        )
        codex = Path(self.temp.name) / "fictional-codex"
        codex.mkdir()
        status, result = self.request(
            "/api/source/codex", "POST", {"enabled": True, "path": str(codex)}
        )
        self.assertEqual(status, 200)
        self.assertTrue(result["enabled"])
        self.assertEqual(self.server.codex_home, codex.resolve())
        self.assertFalse((self.root / "app_data/state/status.json").exists())
        self.assertEqual(
            self.request("/api/source/codex", "POST", {"enabled": False})[0], 200
        )
        self.assertFalse(self.request("/api/setup")[1]["codex_enabled"])
        status, result = self.request("/api/guide", "POST", {})
        self.assertEqual(status, 200)
        self.assertFalse(result["host_integration_installed"])
        status, skill = self.request("/api/assistant-skill", "POST", {})
        self.assertEqual(status, 200)
        self.assertTrue(Path(skill["entrypoint"]).is_file())
        self.assertFalse(skill["host_activation_verified"])
        self.assertTrue(self.request("/api/setup")[1]["assistant_skill_ready"])
        (self.root / "ASSISTANT.md").write_text("My own assistant guide")
        self.assertEqual(self.request("/api/guide", "POST", {})[0], 400)
        self.assertEqual(
            (self.root / "ASSISTANT.md").read_text(), "My own assistant guide"
        )

    def test_context_requires_review_before_search_and_portable_export(self):
        artifact = {
            "schema_version": 1,
            "kind": "preferences",
            "body": "For the fictional reading project prefer quartznimbus Markdown notes.",
            "created_at": "2026-10-24T00:00:00-05:00",
            "generated_by": "Fictional assistant; model unknown",
            "source_references": ["chatgpt:selected, selected-message"],
            "uncertainties": ["Scope is this project only."],
        }
        status, imported = self.request("/api/artifact/import", "POST", artifact)
        self.assertEqual(status, 200)
        identity = imported["id"]
        self.assertEqual(
            self.request("/api/artifact?id=" + identity)[1]["review_status"],
            "unreviewed",
        )
        self.assertEqual(self.request("/api/artifacts")[1]["items"][0]["id"], identity)
        self.assertEqual(self.request("/api/artifact?id=../../secret")[0], 400)
        before = self.request("/api/retrieve?q=quartznimbus")[1]
        self.assertFalse(before["passages"])
        status, first = self.request(
            "/api/bundle",
            "POST",
            {"conversations": ["chatgpt:selected"], "with_context": True},
        )
        self.assertEqual(status, 200)
        self.assertEqual(first["context_files"], 2)
        self.assertEqual(
            self.request(
                "/api/artifact/accept",
                "POST",
                {"id": identity, "review_note": ""},
            )[0],
            400,
        )
        self.assertEqual(
            self.request(
                "/api/artifact/accept",
                "POST",
                {
                    "id": identity,
                    "review_note": "Verified source and project-specific scope.",
                },
            )[0],
            200,
        )
        after = self.request("/api/retrieve?q=quartznimbus")[1]
        self.assertTrue(after["passages"])
        status, exported = self.request(
            "/api/bundle",
            "POST",
            {"conversations": ["chatgpt:selected"], "with_context": True},
        )
        self.assertEqual(status, 200)
        self.assertEqual(exported["context_files"], 3)
        directory = Path(exported["directory"])
        self.assertIn(self.root.resolve(), directory.resolve().parents)
        payload = json.loads((directory / "conversations.json").read_text())
        self.assertEqual([r["id"] for r in payload["conversations"]], ["selected"])
        self.assertEqual(self.request("/api/bundle", "POST", {})[0], 400)
        self.assertEqual(self.request("/api/bundle", "POST", {"all": "yes"})[0], 400)
        self.assertEqual(
            self.request(
                "/api/bundle",
                "POST",
                {"all": True, "conversations": ["chatgpt:selected"]},
            )[0],
            400,
        )
        self.assertEqual(
            self.request(
                "/api/artifact/retire",
                "POST",
                {"id": identity, "review_note": "Superseded; stop reuse."},
            )[0],
            200,
        )
        self.assertFalse(self.request("/api/retrieve?q=quartznimbus")[1]["passages"])
        retired = self.request("/api/artifact?id=" + identity)[1]
        self.assertEqual(retired["review_status"], "retired")
        self.assertEqual(
            [review["status"] for review in retired["review_history"]],
            ["accepted", "retired"],
        )
        self.assertTrue(
            list((self.root / "shared_context/retired" / identity).glob("*.md"))
        )
        next_bundle = self.request(
            "/api/bundle",
            "POST",
            {"conversations": ["chatgpt:selected"], "with_context": True},
        )[1]
        self.assertEqual(next_bundle["context_files"], 2)
        self.assertEqual(
            self.request(
                "/api/artifact/accept",
                "POST",
                {"id": identity, "review_note": "Reviewed again for a new task."},
            )[0],
            200,
        )
        self.assertTrue(self.request("/api/retrieve?q=quartznimbus")[1]["passages"])
        store = Store(self.root)
        try:
            self.assertEqual(store.records(), self.records)
        finally:
            store.close()

    def test_new_workflows_keep_authentication_and_lock_boundaries(self):
        from chatos.core import locked

        for endpoint in [
            "/api/setup",
            "/api/artifacts",
            "/api/artifact?id=" + "a" * 64,
        ]:
            self.assertEqual(self.request(endpoint, authenticated=False)[0], 401)
        for endpoint in [
            "/api/guide",
            "/api/assistant-skill",
            "/api/artifact/import",
            "/api/artifact/accept",
            "/api/artifact/retire",
            "/api/source/codex",
            "/api/bundle",
        ]:
            self.assertEqual(
                self.request(endpoint, "POST", {}, authenticated=False)[0], 401
            )
            self.assertEqual(
                self.request(endpoint, "POST", {}, Origin="https://example.invalid")[0],
                403,
            )
        with locked(self.root / "app_data/state/sync.lock", blocking=False):
            self.assertEqual(self.request("/api/bundle", "POST", {"all": True})[0], 409)
