---
type: state
project: chat-os
reviewed: 2026-10-22
maintenance_owner: Chief of Staff
---
# Current state

The Chief of Staff manages this local workspace. Zayan uses it as a reference.

**[Sync status](STATUS.md) · [Human guide](Humans/Start%20here.md) · [What happens when I chat?](Humans/What%20happens%20when%20I%20chat.md) · [Dashboard](Humans/dashboard.html) · [Conversation map](Humans/explorer.html)**

## Working and verified

- 251 conversation records: 220 Codex (78 retained transcripts and 142 partial history-cache recoveries) plus 31 partial ChatGPT desktop captures. Two Codex histories remain uncaptured. Source IDs, available dates, provenance and model evidence are retained; unavailable per-turn models remain unknown. Original sources are read-only.
- Incremental import, duplicate prevention, revisions, full-text search, and project views. Incomplete source lines remain visible as warnings and retry; a missing source root fails visibly.
- Ordinary sync now refreshes skill discovery, checks live behavior-file hashes, snapshots changes, and verifies the result. Skills, file-based memory, instructions, rules, configuration inventory, saved schedules, and workspace behavior files are covered. Unchanged files do not cause a new full snapshot.
- Passage-level retrieval with exact message IDs, offsets, and file/line citations. The archive-retrieval skill guides the active assistant's grounded answer. Retrieval is local BM25; it does not call an external model.
- Seven reviewed project assignments persist across imports. Verified context indexes reach SPARQ (58), evidence combination (63), Finding a job (2), and Organizing Myself (3). Eleven existing project/repository owners are registered. Uncertain ownership and code-project delivery conventions remain queued.
- A Chief of Staff skill is installed in the user skill location. Its bounded global instruction reference was observed loading into this conversation. Project instructions and filesystem permissions still govern actual filing.
- Daily database backup is hash/integrity-checked on every sync. Isolated restore regenerates conversation files and refuses an existing destination. The doctor command checks database, canonical files, backup, freshness, and coverage warnings.
- Conservative feedback cues are reviewed before being logged; six initial cues were reviewed, including one neutral bug report dismissed without negative labeling. Stable review identities prevent duplicate entries.
- Schedule inventory now reads saved definitions and host-reported timing/run metadata without copying private result bodies. Curated failure collection and feedback records remain separate.
- 50 tests pass, covering source filtering, model changes, import/retry health, ZIP handling, routing persistence, retrieval citations, backup corruption/restore, snapshot drift, concurrency, and projection data.
- Local Git repository; no remote configured. Private archives/runtime data are ignored.

## Explorer and retrieval limits

The offline explorer has pan/zoom, project/source/date/group filters, source links and nearest conversations. An optional pinned Qwen embedding model, HDBSCAN and UMAP map were built locally. Its first 220-conversation map left 52 unclustered and retained about 38% of its own five-neighbor relationships. Ordinary sync preserves this dated map and flags input changes; new desktop captures currently await optional reindexing. Math/data/JavaScript checks pass; browser/visual verification remains pending because local-file preview was blocked. No bypass was attempted.

On seven source-labeled questions, both lexical and optional hybrid retrieval found the exact supporting user message in the top eight for 4/7 cases. The new model has not demonstrated improvement on this small diagnostic and remains optional. Core lexical retrieval and sync remain independent of it. No SOTA quality claim is made. See [semantic implementation and evaluation](System/Semantic%20search.md).

## Scheduling and source gaps

Hourly **Maintain chat-OS** is configured and stays quiet on unchanged state. It requires the Mac and app available and defers at 30 percent or less remaining in the five-hour window. The first heartbeat-triggered bounded core sync completed successfully on 2026-10-22 at 18:30:23 UTC (run 12, exit 0). This verifies the triggered core sync, not a full desktop refresh or a pattern of reliable recurring execution. Inspect [current schedules](System/Schedules/Index.md) for newer evidence.

The native five-minute launch agent was privacy-blocked and disabled. Manual sync through Codex succeeds. No security/privacy protections were weakened.

144 Codex rollout files are unavailable; 142 have partial visible-message recovery from the read-only history projection. The remaining two include the daily news digest target, whose history access failed with a missing-source-rollout error. Its execution/delivery outcome remains unknown.

Zayan uses the ChatGPT/Codex desktop app. Supported tools supplied 86 visible messages across 31 recent/pinned ChatGPT chats and 34 unavailable message references. These are explicitly partial captures; models/effort unavailable from the source remain null. The hourly agent prompt now includes bounded refresh of changed desktop chats, but no unattended refresh is verified. Ordinary ChatGPT does not automatically read this repository. JSON/ZIP export import remains the fuller-history path.

Muse export is deferred at Zayan's request. Raw Muse parsing and ongoing capture remain unverified.

Backups remain on the same Mac. Full recovery of behavior files, project registry and runtime together, plus off-device backup/retention choices, remains open.

## Reference and next work

[Memory](System/Memory/Working%20memory.md) · [Skills](System/Skills/Index.md) · [Decisions](System/Decisions.md) · [Logs](System/Logs/Event%20log.md) · [Routing](System/Projects/Automatic%20routing%20queue.md) · [Roadmap](IMPLEMENTATION.md)

Verify recurring maintenance reliability and the first unattended desktop refresh, review meaningful queued project items, and retain explicit capture gaps. Muse resumes only when requested. Broader semantic evaluation, optional index refresh and visual verification remain later work. The agent owns routine maintenance.
