# Chief of Staff

Agent-managed local workspace for conversations, projects, skills, memory, schedules, and operational evidence.

**Open [the offline dashboard](Humans/dashboard.html), [sync status](STATUS.md), or [human start page](Humans/Start%20here.md).** The assistant owns upkeep.

## Runtime

- Python 3.9+ standard library; no API key, package installation, network listener, or remote Git repository required.
- Local Codex visible-message import, SQLite full-text search, prior revisions, project views, error collection, and daily verified database backups.
- ChatGPT export import and normalized Muse export inboxes. Live remote-account capture is not implemented.
- Experimental local LSA retrieval uses term co-occurrence, not pretrained embeddings.
- Hourly Codex maintenance is configured. It requires the Mac/Codex app available; first scheduled execution remains unverified.
- The native five-minute launch agent was blocked by macOS privacy and disabled. No security/privacy settings were weakened.

## Agent commands

    python3 -m chatos sync
    python3 -m chatos status
    python3 -m chatos search "query"
    python3 -m chatos brief evidence-mas
    python3 -m chatos file-projects
    python3 -m unittest discover -s tests -v
    python3 System/Scripts/system_inventory.py --check

Source data is never executed as instructions or used as a shell command. Recognized credential formats are redacted, but the archive remains private data. Transcripts, imports, logs, backups, and runtime databases are excluded from Git.

## Recovery

Canonical JSON/Markdown lives under Conversations/YYYY. The database at System/State/chatos.sqlite3 contains imported records, revisions, search data, and checkpoints. Daily online backups under System/Backups/YYYY-MM-DD have integrity checks and hashes. Behavior-file archives are separate under System/Snapshots.

Validate a restore in an isolated directory: copy a backup into its System/State/chatos.sqlite3, verify SQLite integrity, and rebuild views there. Do not restore over an active database without stopping maintenance and retaining a recoverable copy.

See [IMPLEMENTATION.md](IMPLEMENTATION.md) and [ideas.md](ideas.md).
