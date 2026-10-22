---
type: roadmap
project: chat-os
updated: 2026-10-22
status: planned
---
# Making the chat-OS operational

The goal is to use the Chief of Staff as the main entry point for projects: discuss work once, retain the conversation, recover its context later, and put useful results in the project that owns them. The system should also keep skills, memory, schedules, metadata, failures, and user feedback inspectable.

The Chief of Staff owns the repository's operation, synchronization, upkeep, and recovery within authorized scope. Zayan primarily uses it as a reference for current state and records. Human-facing pages should expose freshness and results rather than require manual execution of routine maintenance. [STATE.md](STATE.md) is the maintained status entry point.

The initial runtime is Zayan's Mac. Sources are Codex, ChatGPT, and Muse. VS Code and a standard Git repository are being considered as the primary interface; Obsidian compatibility should remain useful during that decision.

This is an implementation backlog. Items below describe work to build and verify, not features that already run or permission to execute every proposed action.

## Initial state before the runtime build (historical)

The table below records the initial scaffold. The runtime has since been built in part: local Codex import, search, revisions, project-context delivery, offline UI, daily verified database backup, local Git, and hourly Codex maintenance configuration. Seventeen tests pass. **See [STATE.md](STATE.md) and [STATUS.md](STATUS.md) for current capabilities and remaining gaps.** Full Muse/ChatGPT ingestion and the first scheduled run remain unverified.

Initial inventory on 2026-10-22:

| Component | What exists | What is missing |
| --- | --- | --- |
| Conversation archive | One manually maintained partial conversation record | Historical import and automatic capture of new messages |
| Metadata | A tested extractor for a specified local Codex conversation, with model history | Integration into ingestion and equivalent coverage for other sources |
| System files | Dated copies of accessible skills, memory, instructions, rules, and configuration inventory | Incremental refresh and a deliberate path for publishing active changes |
| Scheduled tasks | Two locally discovered Codex definitions, archived and indexed | Complete source coverage, run history, missed-run detection, and execution verification |
| Failure logs | A tested local runtime error collector with deduplication and a manual incident command | Background collection, source-specific failure ingestion, and incident follow-up |
| Feedback | Recording guidance and an empty feedback log | Integration into the conversation-processing workflow and review of recurring issues |
| Projects | Project-router skill, nine initial registered destinations, receipt log, and pending queue | Complete discovery, end-to-end delivery tests, and ongoing cross-app routing |
| Topic organization | One linked topic note | Incremental semantic indexing, clustering, and retrieval |
| Runtime/interface | Markdown, JSON, and Python files | Background runner, sync health view, backup workflow; no Git repository initialized at the last check |

The project-router is invoked by this workspace's instructions. Archived skills are reference copies; their presence does not install them globally. An active task definition does not establish successful execution. At this initial stage none of the proposed cadences was configured. The current supported fallback is hourly Codex maintenance; native five-minute sync was privacy-blocked and disabled.

Consistency repair: snapshots now include workspace-owned behavior files, a current skills inventory uses shared discovery with snapshots, and a checker detects drift and corruption. Local logger concurrency is protected and covered by regression tests. See the [consistency audit](System/Audits/2026-10-22%20consistency%20audit.md) for remaining gaps. These repairs do not establish background sync.

## 1. Establish the data model and file ownership

- [ ] Define a common record format for conversations, messages, turns, attachments, project links, decisions, tasks, and operational events.
- [ ] Use stable identities that include source app and source ID. Keep edit/revision relationships and source timestamps; preserve model and effort by turn when available.
- [ ] Keep captured source content separate from generated summaries, extracted actions, clusters, and indexes. Label transcript completeness and unavailable metadata explicitly.
- [ ] Define where mutable sync state lives. Do not use a Markdown summary as the only checkpoint or task execution record.
- [ ] Decide which instructions, memory, and skills are vault-owned active sources and which are snapshots of another application. Document how approved changes reach each runtime.
- [ ] Set up the local repository/interface if selected. Decide which generated, large, or sensitive records belong in Git and which belong in the local data archive. No remote is required for the initial runtime.

**Done when:** a sample conversation with a model change, edited message, attachment, and two project links can be represented without losing provenance or duplicating the source record. Rebuilding derived views preserves captured evidence.

## 2. Build incremental Codex ingestion first

- [ ] Discover eligible conversations across local workspaces and historical archives, not just this directory. Identify reviewer/subagent records separately from ordinary user chats.
- [ ] Import available user and assistant messages in order. Handle partial trailing records, ongoing writes, missing source files, edits/forks, and interrupted conversations without inventing content.
- [ ] Reuse the metadata extractor inside the import pipeline; retain model IDs, provider, effort, source ID, dates, client, workspace, and model history where available.
- [ ] Maintain durable per-source/per-conversation checkpoints and revision identities. Repeating an import must not repeat messages, project notes, or tasks.
- [ ] Preserve attachment references and copy permitted local artifacts when appropriate. Report inaccessible attachments rather than claiming a complete capture.
- [ ] Validate source schema assumptions and report drift. Current local database/session layouts are implementation details, not a guaranteed integration contract.

**Done when:** import an existing chat, add another turn, change its model, run sync twice, interrupt an import, and resume. Verify correct ordering, model history, no duplicate content, and no modification of the original source.

## 3. Run sync regularly on the Mac

- [ ] Create one sync entry point that coordinates ingestion, metadata, changed system files, error collection, and downstream processing.
- [ ] Choose and configure a Mac background runner with startup/login behavior, overlap prevention, timeouts, and bounded retries. Verify whether each adapter needs its source app running.
- [ ] Implement catch-up after sleep, disconnection, crashes, and missed intervals. Commit checkpoints only after durable writes; retain failed items for retry.
- [ ] Record each attempt's start/end, source, counts, checkpoint, outcome, and error. Track last attempt separately from last successful sync.
- [ ] Expose a health summary showing freshness and unresolved failures per source. An unchanged archive is not evidence that its source was successfully checked.
- [ ] Refresh system files by change/hash and keep useful versions; avoid a complete 60+ MB system copy every five minutes.

**Proposed cadence:** conversations/metadata/errors every five minutes; changed system files hourly; reconciliation and backup checks daily. These are starting proposals, not configured schedules. The Mac-only service cannot run while the machine is asleep or powered off; recovery must catch up afterward.

**Done when:** scheduled sync works without an active chat, overlapping runs are prevented, sleep/wake catch-up succeeds, and a deliberately failed adapter produces a visible failure followed by a verified recovery.

## 4. Add Muse and ChatGPT adapters

- [ ] Verify an appropriate data-access/export path for the installed Muse app, `com.meta.endo`. Test coverage of main chat, side chats, system files, task definitions, and available activity/run records separately.
- [ ] Verify ChatGPT history import and a sustainable path for new updates. Record whether each capability is automatic, export-based, or manual.
- [ ] Test whether source exports include stable message IDs, edits, attachments, model information, and schedules. Preserve unknowns where they do not.
- [ ] Implement each adapter against the common record format and shared retry/deduplication rules.
- [ ] Import a bounded sample, compare it against the source, then expand the historical import with a coverage report.

**Dependency:** source access is unverified for ongoing Muse and ChatGPT sync. Do not assume Allume or Muse Code documentation describes the installed Muse application. If a source supports only manual export, show that limitation in health/status; it does not satisfy automatic cross-app sync.

**Done when:** each source has a tested import, an explicit completeness/coverage report, and a verified update mechanism. Clearly distinguish a working Codex-only release from full three-source operation.

## 5. Make project routing reliable

- [ ] Expand and reconcile the project registry across the work vault, code repositories, and other confirmed project locations. Preserve paper/parent-project boundaries and Personal versus Work ownership.
- [ ] Establish permitted write access to actual project destinations. Current external project files are outside this workspace's writable roots.
- [ ] Extract useful decisions, accepted actions, notes, resources, and artifacts from conversations with source links and explicit proposal/decision/completion states.
- [ ] Route using explicit references and project context; use semantic similarity as supporting evidence. Queue ambiguity rather than silently choosing a project.
- [ ] Deliver through each destination's existing convention, check for previous delivery, reopen the result, and retain a receipt. Track pending drafts and failures through resolution.
- [ ] Make project briefing/resume retrieve recent decisions, current tasks, blockers, relevant artifacts, and unresolved feedback before starting similar work.

**Done when:** a JAMIA-specific decision reaches its paper, shared SPARQ work reaches the parent, a personal item stays in Personal, and a cross-project item is linked without duplicate canonical tasks. An ambiguous item and a blocked write remain visible in the queue. Reprocessing the source creates no duplicate delivery.

## 6. Implement semantic organization and usable retrieval

- [ ] Index source conversations and project material with links back to exact supporting messages or records.
- [ ] Choose a retrieval/embedding implementation after testing a small representative set. Reindex changes incrementally and invalidate obsolete derived content.
- [ ] Generate meaningful topic clusters with summaries and cross-links. Let a conversation belong to several topics and retain chronological navigation.
- [ ] Retrieve project context and past decisions with source evidence. Flag conflicting or superseded decisions and stale memory instead of blending them into a confident answer.

**Done when:** known conversations can be found by wording and by meaning; a project briefing uses relevant evidence; changed decisions appear as changes; unrelated chats are not merged solely because they mention common terms such as “LLM.”

## 7. Close the task and feedback loops

- [ ] Record scheduled-task definitions and run instances separately, including scheduled time, actual start, completion, target, result, and retry relationship where available.
- [ ] Detect missing/late runs only when the expected schedule and observed run coverage support that conclusion. Keep unknown outcomes explicit.
- [ ] Connect chat failures, runtime events, task failures, and recoveries while retaining their distinct evidence. Group repeated symptoms without discarding individual events.
- [ ] Process user feedback with the existing rules: quote relevant wording, retain context and uncertainty, record the adjustment, and avoid treating neutral clarification as dissatisfaction.
- [ ] Implement a periodic Chief of Staff review of commitments, blocked projects, pending deliveries, sync health, and needed follow-up. Advance authorized work; notify on meaningful results or required action rather than unchanged checks.
- [ ] Persist actions and delivery receipts so retries do not repeat external side effects.

**Done when:** a scheduled run failure is traceable to its source and recovery, a feedback-driven adjustment can be inspected, and a repeated review neither loses an open commitment nor sends the same action twice.

## 8. Verify recovery and daily use

- [ ] Provide a repeatable setup, start/stop/status commands, and a small dependency/configuration specification. Keep credentials in their supported stores rather than the archive.
- [ ] Choose a local backup destination and retention policy; test restoration of conversations, system guidance, and execution/sync state. Git history alone does not cover data excluded from Git.
- [ ] Test unavailable sources, malformed records, concurrent writes, disk/write failures, restarts, duplicate events, and stale metadata. Store failures and recovery evidence in system logs.
- [ ] Add a readable status page or command and concise instructions for adding a source/project, correcting routing, retrying a failed sync, and restoring a backup.
- [ ] Verify the chosen VS Code/Obsidian navigation renders usable file links and that a new session can resume project context from the repository.

**Done when:** Zayan can use the Chief of Staff as the project entry point without manually maintaining the archive; outstanding limitations are visible; the system can recover from interruption using documented steps.

## Delivery order

1. Common records and incremental Codex import.
2. Recurring Mac sync, health reporting, and restart recovery.
3. Verified project filing and project briefing.
4. Muse and ChatGPT ingestion as access becomes available.
5. Semantic organization, scheduled-run reconciliation, and proactive review.
6. Restore testing and end-to-end acceptance across the supported sources.

Investigate Muse/ChatGPT access early while building the Codex path. Backups and failure reporting should be introduced with the first importer, not deferred until all sources work.

## First implementation slice

Build one command that imports a specified Codex conversation into a source-linked record, updates its metadata, and resumes safely on rerun. Use this conversation as one acceptance case. Only attach a recurring schedule after the command passes its import/retry checks.

## Related files

- [Source readiness](System/Sync%20sources.md)
- [Project routing](System/Projects/Project%20routing.md)
- [Conversation metadata](System/Conversation%20metadata.md)
- [System logs](System/System%20logs.md)
- [Scheduled tasks](System/Scheduled%20tasks.md)
- [Optional improvements](ideas.md)
