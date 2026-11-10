"""Manage a checkout server without affecting unrelated listeners."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import signal
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, build_opener

from chatos.workspace import workspace_path

REPOSITORY = Path(__file__).resolve().parents[3]


def process_identity(pid: int) -> str:
    """Identify a live process, including its start time to detect reused PIDs."""
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "stat=", "-o", "lstart=", "-o", "command="],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError("Cannot inspect server process: " + result.stderr.strip())
    value = result.stdout.strip()
    if not value or value.startswith("Z"):
        return ""
    # Process state changes while running; the start time and command do not.
    return value.split(None, 1)[1]


def running(state: dict) -> bool:
    return bool(state) and process_identity(state["pid"]) == state["identity"]


def ready(url: str) -> bool:
    try:
        with build_opener(ProxyHandler({})).open(url, timeout=1) as response:
            return response.status == 200
    except (URLError, OSError):
        return False


def launch(root: Path, port: int, directory: Path, state_path: Path) -> dict:
    log_path = directory / "server.log"
    descriptor = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.fchmod(descriptor, 0o600)
    environment = dict(os.environ)
    environment["PYTHONPATH"] = (
        str(REPOSITORY / "src") + os.pathsep + environment.get("PYTHONPATH", "")
    )
    with os.fdopen(descriptor, "w") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "chatos",
                "--root",
                str(root),
                "--json",
                "serve",
                "--port",
                str(port),
            ],
            cwd=REPOSITORY,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            close_fds=True,
        )
    try:
        state = {"pid": process.pid, "identity": process_identity(process.pid)}
        state_path.write_text(json.dumps(state))
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if process.poll() is not None:
                try:
                    error = json.loads(log_path.read_text()).get("error", "")
                except (ValueError, AttributeError):
                    error = ""
                if "Address already in use" in error:
                    raise RuntimeError(
                        f"Port {port} is already in use. "
                        "Choose a free port with scripts/start --port 0 --open, "
                        "or select another port with --port NUMBER. "
                        "The existing listener was left running."
                    )
                raise RuntimeError(f"Server exited. Inspect {log_path}")
            with log_path.open() as log:
                first_line = log.readline()
            try:
                launch_url = json.loads(first_line)["url"]
            except (ValueError, KeyError):
                time.sleep(0.1)
                continue
            parsed = urlsplit(launch_url)
            state["url"] = f"{parsed.scheme}://{parsed.netloc}/"
            if ready(state["url"]) and process.poll() is None:
                state["identity"] = process_identity(process.pid)
                state_path.write_text(json.dumps(state))
                return state
            time.sleep(0.1)
        raise RuntimeError(f"Server did not become ready. Inspect {log_path}")
    except BaseException:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        state_path.unlink(missing_ok=True)
        raise


def open_browser(root: Path, url: str) -> None:
    token = workspace_path(root, "System/State/browser-token").read_text().strip()
    webbrowser.open(url + "#token=" + token)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("start", "stop", "status"))
    parser.add_argument("--root", type=Path, default=REPOSITORY / "workspace")
    parser.add_argument(
        "--port", type=int, default=8765, help="Start port; 0 chooses a free port"
    )
    parser.add_argument(
        "--open", action="store_true", help="Open the browser when starting"
    )
    args = parser.parse_args(argv)
    if not 0 <= args.port <= 65535:
        parser.error("--port must be between 0 and 65535")
    root = args.root.resolve()
    if not root.is_dir():
        parser.error(
            f"Workspace does not exist: {root}. Initialize it with scripts/chatos init."
        )
    directory = workspace_path(root, "System/State") / "server"
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    state_path = directory / "process.json"
    with (directory / "control.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = json.loads(state_path.read_text()) if state_path.exists() else {}
        alive = running(state)
        if args.action == "status":
            if not alive:
                print("smriti is stopped (no managed server).")
                return 1
            healthy = ready(state.get("url", "")) if state.get("url") else False
            print(
                f"smriti is running (PID {state['pid']}); "
                f"{'ready' if healthy else 'HTTP not ready'}: {state.get('url', 'starting')}"
            )
            return 0 if healthy else 2
        if args.action == "stop":
            if alive:
                os.kill(state["pid"], signal.SIGTERM)
                deadline = time.monotonic() + 10
                while running(state):
                    if time.monotonic() >= deadline:
                        raise RuntimeError(
                            "Server has not stopped; keeping its process record."
                        )
                    time.sleep(0.1)
            state_path.unlink(missing_ok=True)
            print("smriti is stopped.")
            return 0
        if not alive:
            state = launch(root, args.port, directory, state_path)
        print(
            f"smriti is {'already running' if alive else 'running'} "
            f"(PID {state['pid']}): {state['url']}"
        )
        print(f"Log: {directory / 'server.log'}")
        if args.open:
            open_browser(root, state["url"])
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(2)
