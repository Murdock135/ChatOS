"""Loopback-only chat management interface over the existing local workspace."""

from .workspace import workspace_path

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
import hashlib
import hmac
import json
import secrets
import threading
import traceback
import uuid
import webbrowser
from typing import Optional, Union

from .core import ROOT, Store, digest, now
from .workspace import Workspace
from . import library
from .changes import snapshot_manifest

STATIC = Path(__file__).with_name("static")


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(
        self,
        root: Union[str, Path] = ROOT,
        port: int = 8765,
        codex_home: Optional[Union[str, Path]] = None,
    ):
        self.root = Path(root).resolve()
        status_path = workspace_path(self.root, "System/State/status.json")
        saved = json.loads(status_path.read_text()) if status_path.exists() else {}
        paths = Workspace(self.root)
        configured = codex_home or (
            saved.get("codex_home") if paths.version == 1 else None
        )
        self.codex_home = paths.codex_home(configured).resolve()
        self.token = secrets.token_urlsafe(32)
        self.sync_lock = threading.Lock()
        self.log_lock = threading.Lock()
        super().__init__(("127.0.0.1", port), Handler)
        self.origin = "http://127.0.0.1:" + str(self.server_port)
        self.host = "127.0.0.1:" + str(self.server_port)


class Handler(BaseHTTPRequestHandler):
    server: LocalServer

    def log_message(self, format, *args):
        pass  # Request headers and local chat details do not belong in access logs.

    def reply(self, payload, status=200, content_type="application/json"):
        body = (
            json.dumps(payload, ensure_ascii=False).encode()
            if content_type == "application/json"
            else payload
        )
        self.send_response(status)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'",
        )
        self.end_headers()
        self.wfile.write(body)

    def allowed(self, api=False):
        if self.headers.get("Host") != self.server.host:
            self.reply({"error": "Unexpected host"}, 403)
            return False
        origin = self.headers.get("Origin")
        if origin and origin != self.server.origin:
            self.reply({"error": "Cross-origin requests are not allowed"}, 403)
            return False
        token = self.headers.get("X-ChatOS-Token", "")
        if api and not hmac.compare_digest(
            token.encode("utf-8"), self.server.token.encode("ascii")
        ):
            self.reply({"error": "Open the launch URL printed by chatos serve"}, 401)
            return False
        return True

    def body(self):
        length = int(self.headers.get("Content-Length", "0"))
        if not 0 <= length <= 1024 * 1024:
            raise ValueError("Request exceeds the 1 MiB limit")
        data = json.loads(self.rfile.read(length) or "{}")
        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object")
        return data

    def do_GET(self):
        self.dispatch("GET")

    def do_POST(self):
        self.dispatch("POST")

    def do_PUT(self):
        self.dispatch("PUT")

    def dispatch(self, method):
        parsed = urlsplit(self.path)
        api = parsed.path.startswith("/api/")
        if not self.allowed(api):
            return
        if not api:
            assets = {
                "/": ("index.html", "text/html"),
                "/app.js": ("app.js", "text/javascript"),
                "/styles.css": ("styles.css", "text/css"),
            }
            if method != "GET" or parsed.path not in assets:
                self.reply({"error": "Not found"}, 404)
                return
            name, kind = assets[parsed.path]
            self.reply((STATIC / name).read_bytes(), content_type=kind)
            return
        query = {key: values[-1] for key, values in parse_qs(parsed.query).items()}
        store = Store(self.server.root)
        try:
            result = self.api(store, method, parsed.path, query)
            self.reply(result)
        except LookupError as error:
            self.reply({"error": str(error)}, 404)
        except (ValueError, KeyError, json.JSONDecodeError) as error:
            self.reply({"error": str(error)}, 400)
        except BlockingIOError:
            self.reply(
                {"error": "Another workspace operation is running; try again shortly"},
                409,
            )
        except Exception as error:
            incident = uuid.uuid4().hex[:12]
            frames = [
                {"file": frame.filename, "line": frame.lineno, "function": frame.name}
                for frame in traceback.extract_tb(error.__traceback__)
            ]
            event = {
                "id": incident,
                "at": now(),
                "method": method,
                "path": parsed.path,
                "error_type": type(error).__name__,
                "frames": frames,
            }
            try:
                with self.server.log_lock:
                    logs = workspace_path(store.root, "System/Logs")
                    logs.mkdir(parents=True, exist_ok=True)
                    with (logs / "interface-errors.jsonl").open("a") as output:
                        output.write(json.dumps(event) + "\n")
                message = (
                    "Workspace operation failed. Reference "
                    + incident
                    + " in "
                    + str((logs / "interface-errors.jsonl").relative_to(store.root))
                    + "."
                )
            except OSError:
                message = "Workspace operation failed and its local diagnostic log could not be written. Run chatos doctor."
            self.reply({"error": message}, 500)
        finally:
            store.close()

    def api(self, store: Store, method: str, path: str, query: dict) -> dict:
        if path == "/api/setup" and method == "GET":
            from .web_workflows import setup_details

            return setup_details(store.root)
        if path in ["/api/artifacts", "/api/artifact"] and method == "GET":
            from .web_workflows import artifacts

            return artifacts(
                store.root, query.get("id") if path == "/api/artifact" else None
            )
        if (
            path
            in [
                "/api/source/codex",
                "/api/artifact/import",
                "/api/artifact/accept",
                "/api/artifact/retire",
                "/api/guide",
                "/api/assistant-skill",
                "/api/bundle",
            ]
            and method == "POST"
        ):
            from .core import locked
            from .web_workflows import (
                configure_codex,
                receive_artifact,
                review_artifact,
                create_handoff,
            )
            from .onboarding import write_guide

            data = self.body()
            with locked(store.state / "sync.lock", blocking=False):
                if path == "/api/source/codex":
                    result = configure_codex(
                        store.root, data.get("enabled"), data.get("path")
                    )
                    self.server.codex_home = (
                        Workspace(store.root).codex_home().resolve()
                    )
                    return result
                if path == "/api/artifact/import":
                    return receive_artifact(store, data)
                if path in ["/api/artifact/accept", "/api/artifact/retire"]:
                    return review_artifact(
                        store,
                        data.get("id"),
                        data.get("review_note"),
                        path.endswith("/retire"),
                    )
                if path == "/api/assistant-skill":
                    from .assistant_skill import export_skill

                    return export_skill(store.root)
                if path == "/api/guide":
                    return write_guide(store.root)
                return create_handoff(store, data)
        if path == "/api/overview" and method == "GET":
            status_path = store.state / "status.json"
            status = (
                json.loads(status_path.read_text())
                if status_path.exists()
                else {"status": "never_run"}
            )
            return {
                "workspace": str(store.root),
                "projects": store.registry(),
                "chats": library.list_chats(store)["total"],
                "archived": library.list_chats(store, archived=True)["total"],
                "status": status,
            }
        if path == "/api/retrieve" and method == "GET":
            from .retrieval import retrieve

            return retrieve(store, query.get("q", ""), query.get("project") or None)
        if path == "/api/chats" and method == "GET":
            limit = max(1, min(int(query.get("limit", 50)), 100))
            return library.list_chats(
                store,
                query.get("q", ""),
                query.get("source", ""),
                query.get("project", ""),
                query.get("archived") == "true",
                max(0, int(query.get("offset", 0))),
                limit,
            )
        if path == "/api/chat" and method == "GET":
            record, annotation = library.get(store, query["source"], query["id"])
            return {"record": record, "annotation": annotation}
        if path == "/api/annotation" and method == "PUT":
            data = self.body()
            return library.update(store, data["source"], data["id"], data["changes"])
        if path == "/api/assign" and method == "POST":
            from .routing import assign

            data = self.body()
            projects = data["projects"]
            if not isinstance(projects, list) or not all(
                isinstance(item, str) for item in projects
            ):
                raise ValueError("Projects must be a list of registered IDs")
            return assign(
                store.root,
                data["source"],
                data["id"],
                projects,
                "Explicit assignment made through the local chat-management interface",
            )
        if path == "/api/health" and method == "GET":
            from .recovery import doctor

            return doctor(store.root)
        if path == "/api/import" and method == "POST":
            from .uploads import receive_export

            return receive_export(
                store.root,
                self.rfile,
                int(self.headers.get("Content-Length", "0")),
                query.get("format", ""),
            )
        if path == "/api/backup" and method == "POST":
            from .runtime import backup
            from .core import locked

            with locked(store.state / "sync.lock", blocking=False):
                return backup(store, fresh=True)
        if path == "/api/sync" and method == "POST":
            from .runtime import sync

            if not self.server.sync_lock.acquire(blocking=False):
                raise BlockingIOError()
            try:
                return sync(store.root, self.server.codex_home)
            finally:
                self.server.sync_lock.release()
        if path in ["/api/context", "/api/context/read"] and method == "GET":
            manifest = snapshot_manifest(store.root)
            entries = []
            for item in manifest.get("files", []):
                category = item["category"]
                source = Path(item["source"])
                if source.suffix.lower() not in [
                    ".md",
                    ".txt",
                    ".json",
                    ".jsonl",
                    ".toml",
                    ".yaml",
                    ".yml",
                ]:
                    continue
                if source.name == "SKILL.md":
                    category = "skills"
                elif "/System/Memory/" in source.as_posix() or source.name in {
                    "memory.md",
                    "profile.md",
                    "preferences.md",
                }:
                    category = "memory"
                elif source.name in {"AGENTS.md", "instructions.md"}:
                    category = "instructions"
                if (
                    category in ["memory", "instructions"]
                    or category == "skills"
                    and source.name == "SKILL.md"
                ):
                    entries.append({**item, "category": category})
            if path == "/api/context":
                return {
                    "captured_at": manifest.get("captured_at_utc"),
                    "items": entries,
                }
            selected = next(
                (item for item in entries if item["snapshot"] == query.get("path")),
                None,
            )
            if not selected:
                raise LookupError("Captured context file not found")
            manifest_root = (
                workspace_path(store.root, "System/Snapshots")
                / manifest["captured_at_utc"]
            )
            file = (manifest_root / selected["snapshot"]).resolve()
            if (
                manifest_root.resolve() not in file.parents
                or file.stat().st_size > 2 * 1024 * 1024
            ):
                raise ValueError(
                    "Context file is outside the archive or exceeds the 2 MiB preview limit"
                )
            content = file.read_bytes()
            if hashlib.sha256(content).hexdigest() != selected["sha256"]:
                raise ValueError("Snapshot integrity mismatch; run health check")
            return {
                "text": content.decode("utf-8"),
                "source": selected["source"],
                "captured_at": manifest["captured_at_utc"],
            }
        if path == "/api/map" and method == "GET":
            page = workspace_path(store.root, "Humans/explorer.html")
            if not page.is_file():
                return {
                    "documents": [],
                    "groups": {},
                    "limits": "Run sync to generate the map.",
                }
            text = page.read_text()
            start = text.index('<script type="application/json" id="data">') + len(
                '<script type="application/json" id="data">'
            )
            data = json.loads(text[start : text.index("</script>", start)])
            captured_records = store.records()
            records = {
                (record["source"], record["id"]): record for record in captured_records
            }
            if data.get("input_fingerprint"):
                data["freshness_note"] = (
                    "Matches current captured records."
                    if data["input_fingerprint"] == digest(captured_records)
                    else "Captured records changed; the map needs a refresh."
                )
            else:
                data["freshness_note"] = (
                    "Freshness is unverified; inspect the generation time."
                )

            library.initialize(store)
            annotations = {
                (row["source"], row["id"]): row["title"]
                for row in store.db.execute(
                    "SELECT source,id,title FROM library_annotations"
                )
            }
            # Local organization can change without rebuilding experimental coordinates.
            for point in data.get("documents", []):
                key = point["source"], point["id"]
                if key in records:
                    point["projects"] = records[key].get("projects", [])
                    point["title"] = annotations.get(key) or records[key]["title"]
            return data
        raise LookupError("Not found")


def serve(
    root: Union[str, Path] = ROOT,
    port: int = 8765,
    open_browser: bool = False,
    as_json: bool = False,
    codex_home: Optional[Union[str, Path]] = None,
) -> None:
    """Run the local interface in the foreground until interrupted."""
    with LocalServer(root, port, codex_home) as server:
        url = server.origin + "/#token=" + server.token
        print(
            json.dumps({"url": url, "workspace": str(server.root)})
            if as_json
            else "chat-OS local interface\n"
            + url
            + "\nWorkspace: "
            + str(server.root)
            + "\nStop with Ctrl+C.",
            flush=True,
        )
        if open_browser:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
