# Working memory

Vault-owned durable notes explicitly requested by Zayan. This file is separate from imported memory snapshots and is read through the vault's operating guidance.

## 2026-10-22 — Scope

- The assistant is Zayan's main Chief of Staff.
- The vault should hold chats across Codex, ChatGPT, and other chat apps, organized by topic or semantic meaning.
- The vault should also contain skills, memory, and accessible files related to the assistant's operating behavior.
- Scheduled tasks must also be included as part of the operating system.
- Maintain system logs in this vault, including failures in ordinary and scheduled chats.
- Maintain a log when negative responses from Zayan are detected, with evidence, uncertainty where appropriate, and the resulting adjustment.
- Log metadata with every conversation, including which model was used and other available source details.
- Regular synchronization is required for the chat-OS. Hourly supported Codex maintenance is now configured, with first scheduled execution pending verification. Native five-minute launchd sync was privacy-blocked and disabled.
- Confirmed additional source: Muse. Initial chat-OS runtime should run on Zayan's Mac only; no always-on remote host is requested.
- Zayan is considering VS Code and a standard repository as the primary interface; no migration decision has been finalized.
- Zayan wants the Chief of Staff to be the main entry point for all projects and to file project-relevant material in the relevant projects without repeated manual direction.
- Clarified on 2026-10-22: this workspace is for both Zayan and the assistant. Zayan wants transparent provenance over chats, skills, memory, and their changes. The assistant still owns routine management, sync, and maintenance; human inspectability is a core requirement.

Source: [[2026-10-22 Chief of Staff and chat archive]].

## 2026-10-22 — Later search and visualization requirements

- Zayan eventually wants an interactive 2D clustering visualization and RAG search for the chat-OS. These are future requirements, not implemented capabilities. The current keyword/LSA groups are provisional.

## 2026-10-22 — Desktop source and current priority

- Zayan uses the ChatGPT/Codex desktop app.
- Muse export is explicitly deferred; focus on essential operation and stop when that work is done.
- Continue to preserve the 30 percent remaining threshold in the five-hour account window.

## 2026-10-22 — Future chat application migration

- Zayan wants a future way to use the accumulated chat-OS archive and context to migrate to another chat application.
- Explicitly note-only for now: no implementation, destination selection, or data transfer authorized. See [future migration requirement](../../ideas.md#deferred--migration-to-another-chat-application).
- Source: codex:01a16510-7f12-78b0-afa9-d5aee24d915b, “we should also implement a way to use this treasure trove of stuff for migrating to a different chat application. just note this for future”.

## 2026-10-22 — Highest priority on next chat-OS resume

- Zayan explicitly says current README/conceptual organization still fails a new user who has just cloned the repo. The prior rewrite is not a confirmed resolution.
- Topmost priority when asked to resume: teach purpose, problem, exact features and how they work, concepts defined before use, architecture/design, and a coherent new-user path. No redesign now because of token constraints.
- Preserve and follow the [verbatim request](../Feedback/2026-10-22-new-user-documentation.md). Evidence-backed retrieval and project resumption were explicitly recognized as a feature.
