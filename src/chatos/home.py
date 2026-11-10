"""Live home registry, explicitly mounted local sources, and Gmail reads."""

from __future__ import annotations

import hashlib
import json
import re
import socket
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from . import library
from .changes import snapshot_manifest
from .core import Store, now, write_json
from .workspace import workspace_path

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".json",
    ".py",
    ".js",
    ".ts",
    ".yaml",
    ".yml",
    ".toml",
}


def directives(root: Path) -> list[dict]:
    """List known instruction/memory/skill sources without reading their bodies."""
    candidates = []
    for item in snapshot_manifest(root).get("files", []):
        source = Path(item["source"])
        category = item["category"]
        if source.name == "SKILL.md" or (
            category == "skills" and source.suffix in {".py", ".js", ".ts"}
        ):
            category = "skills"
        elif (
            source.name in {"memory.md", "STATE.md", "profile.md", "preferences.md"}
            or category == "memory"
        ):
            category = "memory"
        elif (
            source.name in {"AGENTS.md", "instructions.md", "SYSTEM_PROMPT.md"}
            or category == "instructions"
        ):
            category = "instructions"
        else:
            continue
        if source.suffix.lower() in TEXT_EXTENSIONS:
            candidates.append((source, category))
    candidates += [
        (root / "AGENTS.md", "instructions"),
        (root / "ASSISTANT.md", "instructions"),
        (root / "STATE.md", "memory"),
        (workspace_path(root, "System/Operating guidance.md"), "instructions"),
        (workspace_path(root, "System/Memory/Working memory.md"), "memory"),
    ]
    candidates += [
        (file, "skills")
        for file in workspace_path(root, "System/Skills").glob("*/SKILL.md")
    ]
    candidates += [
        (file, "skills") for file in (root / "shared_context/skills").glob("*/SKILL.md")
    ]
    entries = {}
    for source, category in candidates:
        if source.is_symlink() or not source.is_file():
            continue
        identity = hashlib.sha256(str(source).encode()).hexdigest()
        entries[identity] = {
            "id": identity,
            "name": source.name,
            "source": str(source),
            "category": category,
            "label": source.parent.name if source.name == "SKILL.md" else source.name,
        }
    return sorted(
        entries.values(),
        key=lambda item: (item["category"], item["label"].lower(), item["source"]),
    )


def read_directive(root: Path, identity: str) -> dict:
    selected = next((item for item in directives(root) if item["id"] == identity), None)
    if not selected:
        raise LookupError("Directive not found")
    source = Path(selected["source"])
    return {**selected, **read_text(source), "read_at": now()}


def read_text(path: Path) -> dict:
    if (
        path.is_symlink()
        or not path.is_file()
        or path.suffix.lower() not in TEXT_EXTENSIONS
    ):
        raise ValueError("Choose an available text source")
    with path.open("rb") as stream:
        content = stream.read(2 * 1024 * 1024 + 1)
    if len(content) > 2 * 1024 * 1024:
        raise ValueError("File exceeds the 2 MiB preview limit")
    return {
        "text": content.decode("utf-8", errors="replace"),
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def mounted_sources(root: Path) -> list[dict]:
    path = workspace_path(root, "System/State/home-sources.json")
    return json.loads(path.read_text()).get("sources", []) if path.exists() else []


def mount_source(root: Path, kind: object, location: object) -> dict:
    if kind not in {"git", "vault"} or not isinstance(location, str):
        raise ValueError(
            "Select a Git repository or Obsidian vault and an absolute directory"
        )
    path = Path(location).expanduser()
    if not path.is_absolute() or not path.is_dir() or path.is_symlink():
        raise ValueError("Choose an existing absolute directory")
    marker = ".git" if kind == "git" else ".obsidian"
    if not (path / marker).exists():
        raise ValueError("The directory must contain " + marker)
    entry = {
        "id": hashlib.sha256(str(path.resolve()).encode()).hexdigest(),
        "kind": kind,
        "path": str(path.resolve()),
        "name": path.name,
    }
    entries = mounted_sources(root)
    entries = [item for item in entries if item["id"] != entry["id"]] + [entry]
    write_json(
        workspace_path(root, "System/State/home-sources.json"), {"sources": entries}
    )
    return entry


def source_list(store: Store) -> list[dict]:
    entries = mounted_sources(store.root)
    paths = [store.root, store.root.parent]
    for project in store.registry():
        if project.get("root"):
            paths.append(Path(project["root"]))
        paths += [Path(path) for path in project.get("related_repositories", [])]
    for path in paths:
        for kind, marker in [("git", ".git"), ("vault", ".obsidian")]:
            if path.is_dir() and (path / marker).exists():
                entries.append(
                    {
                        "id": hashlib.sha256(str(path.resolve()).encode()).hexdigest(),
                        "kind": kind,
                        "path": str(path.resolve()),
                        "name": path.name,
                    }
                )
    return list({(item["id"], item["kind"]): item for item in entries}.values())


def browse_source(store: Store, identity: str, relative: str = "") -> dict:
    entry = next((item for item in source_list(store) if item["id"] == identity), None)
    if not entry:
        raise LookupError("Mounted source not found")
    root = Path(entry["path"]).resolve()
    requested = Path(relative)
    if (
        requested.is_absolute()
        or ".." in requested.parts
        or any(part.startswith(".") for part in requested.parts)
    ):
        raise ValueError("Choose a visible path within the mounted source")
    path = root / requested
    if root not in path.resolve().parents and path.resolve() != root:
        raise ValueError("Source path escapes mounted directory")
    if path.is_symlink():
        raise ValueError("Symlink sources cannot be opened")
    if path.is_file():
        return {"path": relative, "kind": "file", **read_text(path)}
    if not path.is_dir():
        raise LookupError("Source directory not found")
    items = []
    for child in sorted(
        path.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower())
    ):
        if (
            child.name.startswith(".")
            or child.is_symlink()
            or child.name in {"node_modules", "__pycache__"}
        ):
            continue
        if child.is_dir() or child.suffix.lower() in TEXT_EXTENSIONS:
            items.append(
                {
                    "name": child.name,
                    "path": str(child.relative_to(root)),
                    "directory": child.is_dir(),
                }
            )
    return {
        "path": relative,
        "kind": "directory",
        "items": items[:300],
        "total": len(items),
    }


def overview(store: Store) -> dict:
    return {
        "directives": directives(store.root),
        "sources": source_list(store),
        "conversations": library.list_chats(store)["total"],
        "workspace": str(store.root),
        "checked_at": now(),
    }


def gmail_request(token: str, resource: str) -> dict:
    request = Request(
        "https://gmail.googleapis.com/gmail/v1/users/me/" + resource,
        headers={"Authorization": "Bearer " + token},
    )
    try:
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read(1024 * 1024))
    except HTTPError as error:
        raise ValueError(
            "Gmail rejected the request (HTTP "
            + str(error.code)
            + "). Reconnect with a valid Gmail read-only access token."
        ) from None
    except (URLError, TimeoutError, socket.timeout):
        raise ValueError(
            "Gmail could not be reached; check the connection and retry"
        ) from None


def connect_gmail(token: object) -> dict:
    if (
        not isinstance(token, str)
        or not token.strip()
        or len(token) > 8192
        or re.search(r"\s", token)
    ):
        raise ValueError(
            "Provide a valid OAuth access token with Gmail read-only access"
        )
    profile = gmail_request(token, "profile")
    if not profile.get("emailAddress"):
        raise ValueError("Gmail did not return an account profile")
    return {
        "email": profile["emailAddress"],
        "verified_at": now(),
        "messages": profile.get("messagesTotal"),
    }


def gmail_messages(token: str | None, query: str = "") -> dict:
    if not token:
        raise ValueError("Connect Gmail first")
    results = gmail_request(
        token,
        "messages?" + urlencode({"maxResults": 10, "q": query[:500] or "in:inbox"}),
    )
    messages = []
    for item in results.get("messages", []):
        identity = item.get("id", "")
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", identity):
            continue
        message = gmail_request(
            token,
            "messages/"
            + identity
            + "?format=metadata&metadataHeaders=Subject&metadataHeaders=From&metadataHeaders=Date",
        )
        headers = {
            header["name"].lower(): header["value"]
            for header in message.get("payload", {}).get("headers", [])
        }
        messages.append(
            {
                "id": identity,
                "subject": headers.get("subject", "(No subject)"),
                "from": headers.get("from", ""),
                "date": headers.get("date", ""),
                "snippet": message.get("snippet", ""),
            }
        )
    return {"items": messages}
