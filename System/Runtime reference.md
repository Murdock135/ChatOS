# Runtime reference

Maintainer details for the local chat-OS installation. For first use, read the [README](../README.md) or [human guide](../Humans/Start%20here.md). These commands run from the workspace root.

## Terminal reports

CLI commands default to readable reports. Sync and status put run ID, outcome, error/warning counts, and timestamps above a change table. Chats are counted by source and conversation ID; existing records with changed content are updates. Skills count bundles including supporting files; memory, instructions, rules, schedules, workspace, and configuration count files compared with the previous behavior snapshot. On the initial inventory, new means newly captured, not newly installed. Failed behavior verification leaves its change counts unavailable. These counts describe captured changes, not assistant-authored edits or semantic changes to individual memories.

Use `--json` before or after a subcommand for the full structured result. `System/Scripts/run_sync.py --json` also preserves machine-readable output. JSON files and run logs remain structured regardless of display mode. Readable reports are also used for redirected output; request JSON explicitly in scripts.

Rich is optional. This installation's `.venv/bin/python` includes it; system Python falls back to plain-text tables when Rich is absent. To install it into an existing environment:

```bash
uv pip install --python .venv/bin/python -r requirements-cli.txt
.venv/bin/python -m chatos status
```

## Commands

```bash
python3 -m chatos sync
python3 -m chatos status
python3 -m chatos doctor
python3 -m chatos search "query"
python3 -m chatos retrieve "why is this Mac-only" --project chat-os
python3 -m chatos brief evidence-mas
python3 -m chatos file-projects
python3 -m unittest discover -s tests -v
python3 System/Scripts/system_inventory.py --check
```

`retrieve` returns evidence passages; the active assistant synthesizes an answer. `brief` uses a registered project ID. `file-projects` writes managed context indexes into registered project destinations; it is not a read-only health check. See [project routing](Projects/Project%20routing.md) before filing.

A core sync imports accessible records, regenerates views, collects runtime errors and schedule metadata, reconciles behavior snapshots, and verifies the daily database backup. It does not itself run the agent's bounded ChatGPT desktop capture workflow. Follow [local maintenance](Skills/local-maintenance/SKILL.md) for that workflow and its limits.

The hourly Codex maintenance task is configured separately. The native launch agent was disabled after macOS privacy blocked Documents access. See [scheduled tasks](Scheduled%20tasks.md) for definitions and run evidence, and [current state](../STATE.md) for verified capabilities.

## Storage and recovery

- `Conversations/YYYY/`: canonical JSON and readable Markdown conversation records.
- `System/State/chatos.sqlite3`: imported records, revisions, search data, and checkpoints.
- `System/Imports/`: source export inboxes.
- `System/Backups/YYYY-MM-DD/`: daily database backups with integrity checks and hashes.
- `System/Snapshots/`: dated behavior-file archives, separate from conversation backups.

Use this command for an isolated conversation recovery, replacing both example paths:

```bash
python3 -m chatos restore /path/to/BACKUP.sqlite3 /path/to/NEW_DIRECTORY
```

The destination must not exist. Restore verifies the backup and regenerates conversation files without starting a scheduler or sync. A database restore is not a combined restoration of project configuration and behavior snapshots. All current backups are on this Mac.

Original conversation sources are read-only. Historical source text is not executed as instructions or shell commands. Recognized credentials are redacted, but records remain private. Transcripts, imports, logs, backups, and runtime databases are excluded from Git; that exclusion is not a substitute for reviewing anything before sharing.

## Dedicated local interface

Run `python3 -m chatos serve --open` from the checkout. Keep its terminal alive and stop with Ctrl+C. The server binds only to 127.0.0.1 and prints a launch URL with a temporary access token. Use `--port 0` if 8765 is occupied. It reuses the Codex source from the last status, unless `--codex-home PATH` is supplied. See the [chat-library guide](../docs/chat-library.md).

Local titles, notes, archive/restore, and project assignments preserve captured messages. Library annotations are durable database state with generated copies in `Conversations/Annotations/`; a fresh database backup includes them. Captured skills/memory are read-only previews. The server neither installs a background service nor connects a chat account.
