"""Exercise the real background server with an independent fictional workspace."""

import json
import os
import socket
import subprocess
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]


class AppControlTests(unittest.TestCase):
    def test_lifecycle_and_occupied_port(self) -> None:
        with tempfile.TemporaryDirectory(prefix="smriti-lifecycle-") as folder:
            root = Path(folder) / "fictional workspace"
            subprocess.run(
                [str(REPOSITORY / "scripts/chatos"), "init", str(root)],
                check=True,
                stdout=subprocess.DEVNULL,
            )

            def run(action: str, *extra: str, expected: int = 0) -> str:
                result = subprocess.run(
                    [str(REPOSITORY / "scripts" / action), "--root", str(root), *extra],
                    check=False,
                    cwd=folder,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertEqual(result.returncode, expected, result.stderr)
                return result.stdout

            state_path = root / "app_data/state/server/process.json"
            try:
                run("status", expected=1)
                run("start", "--port", "0")
                self.assertIn("ready:", run("status"))
                state = json.loads(state_path.read_text())
                self.assertIn("already running", run("start", "--port", "0"))
                self.assertEqual(
                    json.loads(state_path.read_text())["pid"], state["pid"]
                )
                self.assertEqual(
                    (state_path.parent / "server.log").stat().st_mode & 0o777, 0o600
                )
                run("stop")
                run("status", expected=1)
                run("stop")
                # A stale PID record must never terminate a different process.
                state_path.write_text(
                    json.dumps({"pid": os.getpid(), "identity": "stale"})
                )
                run("status", expected=1)
                run("stop")
                with socket.socket() as occupied:
                    occupied.bind(("127.0.0.1", 0))
                    occupied.listen()
                    result = subprocess.run(
                        [
                            str(REPOSITORY / "scripts/start"),
                            "--root",
                            str(root),
                            "--port",
                            str(occupied.getsockname()[1]),
                        ],
                        check=False,
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertIn("already in use", result.stderr)
                    self.assertIn("--port 0", result.stderr)
                    self.assertFalse(state_path.exists())
                run("status", expected=1)
            finally:
                run("stop")
