---
type: implementation-plan
project: chat-os
updated: 2026-10-22
---
# Making the chat-OS operational

The Chief of Staff owns implementation and upkeep. Zayan uses the workspace as a reference and directs work through chat. This is the current plan; Git retains earlier scaffold versions. [STATE.md](STATE.md) describes verified capabilities, and [STATUS.md](STATUS.md) reports the last sync.

## Current priority — Essential feature completion, then public setup

Updated by the user on 2026-10-22: finish essential functionality in the current installation first, excluding unnecessary features; then adapt and test setup for other users. The earlier documentation work was resumed and its baseline remains available. [Product brief](docs/product.md), [verified feature map](docs/features.md), and the [documentation path](docs/README.md) now provide a concrete baseline. The original [verbatim request](System/Feedback/2026-10-22-new-user-documentation.md) remains preserved; delivery is not user-confirmed resolution.

- [x] Define a working product description, human and assistant interfaces, and current capability boundaries from inspected implementation.
- [x] Provide a README-to-walkthrough-to-concepts reading path, architecture diagrams, and a worked evidence-retrieval example.
- [x] Verify fictional import, search, cited retrieval, health, and duplicate-free repeat sync in an isolated copy. Record fresh-copy and test limits.
- [x] Implement the user-selected dedicated local browser interface with Apple-inspired styling: import, library search/read, separate local annotations, archive/restore, project assignment, evidence passages, map filters/pan/zoom, captured context, health/sync and fresh conversation-database backup.
- [x] Verify source preservation, validated uploads, recovery, API access boundaries, export recency, and project-filter scope; lint/format/type-check the new modules and inspect the browser workflows. See docs/verification.md for scope and limits.
- [ ] Settle public positioning, first audience, packaging and general setup. The current local interface is selected; these broader public-release choices remain open.
- [ ] Later: implement and verify general real-user initialization without inheriting maintainer paths, project assignments, or private operating notes. This is an adoption gap, not completed by writing documentation.
- [ ] Later: provide a prompt/artifact guide for users to obtain usable, inspectable memory/context from their own AI; define formats and provenance and test setup with separate fictional users and paths.
- [ ] Later: evaluate the learning path with a new user and resolve remaining conceptual/navigation gaps before declaring onboarding complete.

Human-facing AI-chat management remains first-class alongside Chief of Staff workflows. The requested local browser app uses the existing standard-library core and keeps the workspace together. No platform-directory relocation was performed.

## 1. Local records and Codex capture

- [x] Stable source/conversation identities; visible messages, message IDs, model/effort history, timestamps, attachment references, workspace and provenance.
- [x] Read-only retained Codex history discovery, incremental checkpoints, revisions and duplicate prevention.
- [x] Exclude system/developer/private reasoning/tool payloads; redact recognized credential formats.
- [x] Retry malformed/incomplete source lines and report them; fail visibly when a source root is unavailable.
- [x] Separate canonical source records from generated views and runtime state.
- [ ] 142 of 144 missing rollout histories now have partial visible-message projection recovery. Reconcile the remaining two and verify projection coverage. An export or other supported source may recover them; metadata alone cannot recreate messages.
- [ ] Expand schema-drift and edit/fork/attachment coverage against representative real exports. Attachment references do not mean media bytes are backed up.

## 2. Regular maintenance and operating files

- [x] One sync command coordinates ingestion, error collection, schedules, behavior-file reconciliation, views and backup verification.
- [x] Process lock prevents overlapping syncs; interrupted run rows are retained and checkpoints support catch-up.
- [x] Hash-based skill/memory/instruction/rule/configuration/schedule/workspace checks; staged snapshot publication and archive integrity checks.
- [x] Supported hourly Codex heartbeat saved; account-usage guard defers at 30 percent or less remaining in the five-hour window.
- [x] Disable the privacy-blocked native launch agent; retain diagnostic evidence without weakening Mac protections.
- [x] Install a bounded global Chief of Staff reference and user skill; preserve original instructions. The new reference was observed loading into this conversation.
- [x] A heartbeat-triggered bounded core sync and bounded changed-desktop-chat refresh have execution evidence. Saved active state, due times, and manual runs alone remain insufficient. Longer-term recurring reliability is still unverified.
- [ ] Verify real sleep/wake and restart catch-up. The Mac-only runner cannot operate while powered off.
- [ ] Choose snapshot/backup retention and storage thresholds; avoid deleting historical records without an agreed recoverable policy.

## 3. ChatGPT and Muse capture

- [x] ChatGPT JSON/ZIP export parser, branch relationships, model evidence where present, safe ZIP payload reading without attachment extraction, and retry/duplicate checks.
- [x] Normalized Muse conversation inbox; failed raw/unrecognized exports stay visible as failures.
- [ ] Muse export is explicitly deferred until requested again. Inspect its actual schema before implementing raw chat, side-chat, library/system-file, task, or activity adapters.
- [x] Confirm desktop-app use; capture available text from 31 recent/pinned ChatGPT chats with explicit unavailable-reply/model labels. The supported tool does not supply a complete transcript.
- [ ] Verify a sustainable update path for ordinary ChatGPT and Muse. Export snapshots do not satisfy automatic cross-app sync.
- [ ] Compare a bounded real import against each original app, then expand history with a coverage report.
- [ ] Preserve source-specific skills/memory/task definitions only through verified access. No existing integration publishes this repository's guidance back into ChatGPT or Muse.

Any new persistent sensitive access must be reviewed at the point it is enabled. Do not use undocumented private APIs, authentication scraping, security bypasses, or an exposed local server to make capture appear complete.

## 4. Project continuity and filing

- [x] Eleven registered project/paper/system/repository owners with verified paths and existing filing conventions.
- [x] Exact workspace ownership before title candidates; ambiguous and unassigned records remain queued.
- [x] Reviewed ownership assignments persist across reimports and support multiple owners.
- [x] Verified managed context-index delivery into SPARQ, evidence combination, Finding a job and Organizing Myself, with receipts and no inferred commitments.
- [x] Project-router, briefing and archive-retrieval skills; global entry reference for substantive Codex project work.
- [x] Source-reviewed chat-OS decision record with explicit authority and supersession convention.
- [ ] Review remaining queued sources and identify useful outcomes beyond links. File actual accepted decisions/tasks/research results into existing destination conventions, with exact sources.
- [ ] Test a manuscript-specific decision, shared parent-project result, Personal item, superseded decision and cross-project action end to end. Avoid duplicate tasks and preserve user dates/owners.
- [ ] Expand the registry only when ownership is verified; do not force unrelated practical chats into research projects.

## 5. Retrieval and topic exploration

**Confirmed requirements: interactive 2D clustering visualization and RAG search.**

- [x] Full-text conversation search and incremental passage index with exact text offsets/message IDs/file-line citations.
- [x] Project-filtered evidence retrieval and a skill for the active assistant to synthesize grounded answers, state conflicts, and acknowledge missing support.
- [x] Keyword topic browsing and provisional local LSA groups/search.
- [x] Generate a self-contained offline 2D map with pan/zoom, project/source/date/group filters, source links and nearby conversations. Show method, retained variance and neighbor retention.
- [x] Render the map in the requested local browser app and verify its list navigation and controls without bypassing the blocked local-file preview. The original offline page remains a separate artifact.
- [ ] Extend evaluation beyond the optional pinned Qwen/HDBSCAN/UMAP experiment. The first seven-question hybrid result matched lexical retrieval at 4/7, so it remains optional. No broad SOTA claim is supported.
- [ ] Evaluate retrieval on real questions, paraphrases, hard negatives, contradictory/superseded decisions and partial histories. Small fixture tests are not a full quality evaluation.
- [ ] Extend retrieval to registered project documents and external memory under deliberate ownership/freshness rules. Current passage retrieval covers imported chats and selected current chat-OS notes.

## 6. Task, failure and feedback loops

- [x] Preserve saved schedules and refresh host-reported task state/timestamps plus bounded run metadata without private result bodies.
- [x] Collect retained local ERROR evidence with hashed provenance, concurrency-safe deduplication and task association where known.
- [x] Curated incident/recovery log, reviewed feedback queue with duplicate prevention, and feedback recording rules; distinguish unknown impact and neutral clarification.
- [ ] Verify scheduled execution outcomes independently of enabled state or last-run timestamps. Heartbeats may lack automation_runs rows.
- [ ] Detect genuinely missed runs only after schedule interpretation and execution coverage are established.
- [ ] Connect accepted project actions to durable review checkpoints and receipts, so repeated Chief of Staff reviews advance work without repeating side effects.
- [ ] Inventory ChatGPT/Muse schedules and failures after their source access is verified.

## 7. Recovery and everyday use

- [x] Local Git with sensitive/generated-data exclusions; no remote configured.
- [x] Daily online SQLite backup, hash/integrity verification on every sync, and isolated restore that refuses existing destinations.
- [x] Doctor command checks runtime database, canonical JSON/Markdown, latest backup and freshness/coverage warnings.
- [x] Human orientation, current state, dashboard, schedule inventory, commands and VS Code tasks.
- [ ] Verify a combined restore of runtime data, project registry and behavior guidance from their separate recovery sources.
- [ ] Choose an off-device backup destination and retention policy. Same-device copies do not protect against device loss.
- [ ] Verify navigation in the user's preferred VS Code/Obsidian surface and real fresh-project behavior after the global entry reference.

## Deferred future requirement — Chat application migration

- [ ] Provide a way to use the accumulated archive and operating context when migrating to another chat application. Destination and scope are unspecified; note only, not authorization to implement or transfer data now. See [migration requirement](ideas.md#deferred--migration-to-another-chat-application).

## Next acceptance milestone

Complete and record the current-installation browser acceptance checks, then address public-user setup when that phase is resumed. Keep the broader source-access and project-filing quality backlog visible. Full three-source operation remains incomplete: ChatGPT capture is bounded/export-based and raw Muse work remains explicitly deferred. Neither UI completion nor a passing doctor establishes complete source coverage.

[Source readiness](System/Sync%20sources.md) · [Project routing](System/Projects/Project%20routing.md) · [Recorded decisions](System/Decisions.md) · [Optional ideas](ideas.md)
