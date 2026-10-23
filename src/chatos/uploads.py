"""Receive bounded ChatGPT exports into the local inbox without extracting media."""
from .workspace import workspace_path

import hashlib
from pathlib import Path
import tempfile
from typing import Protocol
import zipfile

from .importers import read_export_file

MAXIMUM = 128 * 1024 * 1024


class BinaryReader(Protocol):
    """The upload receiver needs only bounded binary reads."""

    def read(self, size: int = -1, /) -> bytes: ...


def receive_export(
    root: Path, stream: BinaryReader, length: int, extension: str
) -> dict:
    """Validate a complete upload before publishing its content-addressed inbox file.

    Args:
        root: Destination workspace.
        stream: Request body, read only up to the declared length.
        length: Declared byte count, bounded to 128 MiB.
        extension: Supported input format: json or zip.

    Returns:
        Validated conversation count and local inbox path. Sync remains separate.
    """
    if extension not in ["json", "zip"]:
        raise ValueError("Choose a ChatGPT JSON or ZIP export")
    if not 0 < length <= MAXIMUM:
        raise ValueError("Export upload must be between 1 byte and 128 MiB")
    state = workspace_path(root, 'System/State')
    state.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="upload-", dir=state) as temporary:
        staging = Path(temporary) / ("export." + extension)
        digest = hashlib.sha256()
        remaining = length
        with staging.open("wb") as output:
            while remaining:
                chunk = stream.read(min(remaining, 1024 * 1024))
                if not chunk:
                    raise ValueError("Upload ended before its declared length")
                output.write(chunk)
                digest.update(chunk)
                remaining -= len(chunk)
        try:
            records = read_export_file(staging, "chatgpt")
            for record in records:
                if record.get("source") != "chatgpt":
                    raise ValueError("This importer accepts ChatGPT exports only")
                if not isinstance(record.get("id"), str) or not record["id"]:
                    raise ValueError("Every conversation needs a stable source ID")
                if not isinstance(record.get("messages"), list):
                    raise ValueError("Every conversation needs a message list")
                for message in record["messages"]:
                    if not isinstance(message, dict) or message.get("role") not in [
                        "user",
                        "assistant",
                    ]:
                        raise ValueError(
                            "Only visible user/assistant messages may be imported"
                        )
                    if message.get("phase") in ["analysis", "reasoning", "summary"]:
                        raise ValueError("Private reasoning is excluded")
                    if not isinstance(message.get("text", ""), str):
                        raise ValueError("Message text must be text")
        except (
            AttributeError,
            TypeError,
            KeyError,
            zipfile.BadZipFile,
            UnicodeError,
        ) as error:
            raise ValueError("Unsupported or damaged ChatGPT export") from error
        from .workspace import Workspace
        paths = Workspace(root)
        if not paths.enabled("chatgpt"):
            raise ValueError("ChatGPT imports are disabled in this workspace")
        inbox = paths.imports("chatgpt")
        inbox.mkdir(parents=True, exist_ok=True)
        destination = inbox / ("upload-" + digest.hexdigest() + "." + extension)
        repeated = destination.exists()
        staging.replace(destination)
    return {
        "path": str(destination),
        "conversations": len(records),
        "already_received": repeated,
        "status": "ready_for_sync",
    }
