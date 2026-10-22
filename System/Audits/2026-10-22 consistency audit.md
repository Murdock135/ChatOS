# System consistency audit — 2026-10-22

Trigger: Zayan found that project-router was missing from the skills index in the latest snapshot and asked what other gaps existed.

## Defects found and repaired

| Finding | Cause | Repair and evidence |
| --- | --- | --- |
| Workspace skill absent from snapshot | Snapshot discovery scanned only the Codex installation/cache/memory skill roots. | Shared discovery now includes `System/Skills`; new snapshots preserve workspace skill files and list their scope. Regression test adds a skill after a snapshot and requires the check to fail. |
| Workspace behavior files absent from snapshot | Snapshot captured external files but omitted the active workspace's AGENTS, guidance, working memory, routing data, scripts, and documentation. | Capture them under `Workspace/`, with source paths and hashes. Changes to instructions are detected by the checker. Event data and conversation history remain outside this behavior archive. |
| No current skills inventory or freshness check | The dated snapshot index was the only consolidated skill listing. | Added `System/Skills/Index.md` and `inventory.json`; live indexing and snapshots use the same discovery code. `--check` reports added, removed, modified, uncaptured, and corrupted files and exits nonzero on drift. |
| Concurrent log writes could duplicate or race | Ledger deduplication, view generation, and collector checkpoints had no interprocess locks. | Added separate exclusive locks for ledger writes and collection; regenerate the view atomically. A four-process regression test verifies one event remains after concurrent retries, including duplicate IDs within one batch. |
| Human navigation did not explain current versus captured state | “Latest” could be read as “complete and current.” | Added prominent current-inventory links, explicit snapshot scope/date, and maintenance instructions. Old snapshots remain unchanged historical records. |

## Checks performed

- Read the snapshot, inventory, logging, and metadata scripts and current system guidance.
- Compared the old snapshot's 46 skill entries against 47 currently discovered bundles, including one workspace-owned skill.
- Checked existing current-document Markdown navigation and snapshot-index links for missing file targets; none were missing in that scoped check.
- Added regression tests for current inventory, omitted/removed skills, added supporting files, changed instructions, corrupted snapshot files, and concurrent ledger writes.
- A full integrity/freshness check is run after the corrected snapshot is published. Its result is operational evidence, not a guarantee that future changes will remain synchronized.

## Remaining gaps and boundaries

| Gap | What it means | Where it is tracked |
| --- | --- | --- |
| No background sync | Indexes and snapshots only change when invoked. The checker detects drift when run; it is not a daemon. | IMPLEMENTATION.md, recurring Mac sync |
| Incomplete ingestion | One manually maintained partial conversation; no complete Codex/Muse/ChatGPT history import. | IMPLEMENTATION.md, source adapters |
| Workspace-scoped activation | The router is referenced by this workspace's AGENTS; it is not globally installed or verified active in every app/chat. Cached skill presence does not prove runtime availability. | Project routing; skills inventory |
| Project delivery limits | Registry is initial; external project writes still need usable filesystem access. Local tags/receipts do not prove delivery elsewhere. | Project routing and pending queue |
| Error collection limits | Collector reads retained local ERROR rows, initially from a 24-hour window. Warnings, failures absent from that database, missed scheduled runs, and other apps require separate evidence. | System logs; implementation roadmap |
| Metadata updates are manual | Per-conversation refresh is not wired into universal ingestion. The note and JSON sidecar are separate writes, not a transactional pair. | Conversation metadata; ingestion/recovery work |
| No complete scheduler audit | Local saved task definitions are an inventory, not verified run history, target health, or cross-app coverage. | Scheduled tasks; task-run reconciliation |
| Scoped source roots | Skill discovery covers four explicitly listed roots; other installations/project-local skill locations need registration. Unreadable sources or schema changes must not be assumed complete. | Inventory JSON; source integration work |
| Archive is not a runtime backup | Archived relative links may lead to deliberately excluded conversation/event data; external package/runtime dependencies and credentials are not bundled. | Snapshot scope and manifest |

This was a targeted consistency and concurrency audit of the current scaffold, not an exhaustive security review or a proof that every failure mode has been removed.

## Routine check

```bash
python3 System/Scripts/system_inventory.py --check
```

If skills changed, refresh their inventory. If the archive is meant to include the latest state, create a new snapshot; do not rewrite an old snapshot to make it appear current. Run the checker again. Regression tests are available with:

```bash
python3 -m unittest discover -s tests -p 'test_system_consistency.py' -v
```
