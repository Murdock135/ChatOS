---
name: local-maintenance
description: Run and verify chat-OS sync, inspect coverage and failures, reconcile skill/snapshot indexes, and maintain accurate status without weakening computer protections.
---

# Local maintenance

Run python3 System/Scripts/run_sync.py. Inspect System/State/status.json, source coverage, and errors. Successful scans can still have unavailable historical transcripts or export-only sources. Preserve that distinction; absent history is not a new transfer failure.

Use python3 -m chatos file-projects for agent-managed context indexes in registered project Scratch/Notes folders when permitted. Inspect System/State/routing.json and the automatic queue/receipts; only verified writes are delivered. Review uncertain ownership before creating tasks or decisions.

Refresh skills, check consistency, snapshot changed behavior files when needed, then recheck. Keep runtime databases, imports, and backups outside behavior snapshots. Verify local backups; keep original sources read-only.

Use the supported hourly Codex automation. The native launch agent was disabled after macOS denied Documents access. Do not bypass privacy protections or restart the failing job to make status appear healthy.

Check account usage before scheduled agent work; defer at 30 percent or less remaining in the 300-minute window. Stay quiet on unchanged/non-actionable state. Log failures/recovery and notify only on meaningful completion, actionable problems, or required user input.
