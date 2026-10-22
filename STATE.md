---
type: state
project: chat-os
reviewed: 2026-10-22
maintenance_owner: Chief of Staff
---
# Current state

The Chief of Staff manages this local workspace. Zayan uses it as a reference.

**Start with [sync status](STATUS.md), [the offline dashboard](Humans/dashboard.html), or [conversations](Conversations/Index.md).** Those generated views show their last scan time.

## Working and verified

- 78 local Codex conversations imported with visible user/assistant messages, model history, source IDs, and dates. Original sources are read-only; private reasoning/tool payloads are excluded.
- Incremental checkpoints, duplicate prevention, prior revisions, full-text search, project views, and offline HTML browsing.
- Source-linked conversation indexes verified in the existing SPARQ and evidence-combination Scratch folders (29 and 19 conversations respectively). Ambiguous/unassigned items are queued; automatic context indexes do not create accepted tasks or decisions.
- Daily online SQLite backup with integrity checks; restore content tested in isolation.
- Local failure collection, skill inventory, workspace-inclusive behavior snapshots, and consistency checks.
- Seventeen tests pass, covering imports, model changes, exports, privacy exclusions, retries, concurrency, backup integrity, and inventory drift.
- Local Git repository initialized; no remote configured. Private data and runtime files are ignored.

## Scheduling and limitations

Hourly **Maintain chat-OS** Codex automation is configured. It requires the Mac and app available; the first scheduled execution remains unverified. Its prompt defers agent work at 30 percent or less remaining in the five-hour window and stays quiet on unchanged state.

The native five-minute launch agent was blocked by macOS Documents privacy and disabled. No privacy/security protections were weakened. Manual sync succeeds through Codex.

144 historical Codex database references have no retained local transcript file. The archive reports partial history. ChatGPT export import is implemented; live account sync is not. Muse's export control was found, but the Mac locked before download could complete. Normalized Muse import is supported; no verified raw Muse-export parser exists yet.

Keyword topic browsing and experimental local LSA groups/search are available. LSA uses term co-occurrence, not pretrained embeddings, and must not decide project ownership or factual confidence. Its first broad live query was too loose, so term-based anchoring was added; evaluation beyond small checks remains needed.

## Reference

- [Working memory](System/Memory/Working%20memory.md)
- [Skills](System/Skills/Index.md)
- [Logs](System/Logs/Event%20log.md) and [sync runs](System/Logs/sync-runs.jsonl)
- [Projects](Projects/Index.md), [pending routing](System/Projects/Automatic%20routing%20queue.md), [delivery receipts](System/Projects/Automatic%20filing%20receipts.md)
- [Schedules](System/Scheduled%20tasks.md), [latest behavior archive](System/Latest%20snapshot.md)
- [Remaining implementation work](IMPLEMENTATION.md)

## Next work

Verify the first scheduled maintenance result; complete Muse/ChatGPT source access; review queued routing; add source-reviewed decisions/tasks and stronger semantic retrieval evaluation. Finish outstanding work after the usage window allows it. The agent owns routine maintenance.
