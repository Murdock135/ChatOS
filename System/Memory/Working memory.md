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

## 2026-10-22 — Public adoption and explanatory docs

- Zayan wants chat-OS to become an app others can adopt. Define what kind of product/repository it is and the interaction surfaces for users and the Chief of Staff; specific interfaces remain undecided.
- Explicit future requirement: “there should also exist docs that explain how everything works. just note this for the future”. Include explanatory docs beyond the README in the existing topmost next-resume documentation priority.
- [Full requirement](../Feedback/2026-10-22-new-user-documentation.md#follow-up-requirements--product-identity-and-how-it-works-documentation). No implementation now.

## 2026-10-22 — User-facing chat management is first-class

- Explicit clarification: “keep in mind that i want to make this a user-facing tool. They can use it to manage their AI-chats as well”.
- Serve people managing their AI chats directly, alongside assistant/Chief of Staff workflows. Do not frame the app solely as internal agent infrastructure.
- Product surfaces and separation of application code, private user data, settings, caches, and optional readable workspace need design before broad adoption. No UI or storage migration selected/implemented. See the existing top-priority [requirements note](../Feedback/2026-10-22-new-user-documentation.md).

## 2026-10-22 — Keep everything together for inspectability

- Current user direction: keep everything in this workspace for now so people can see chats, skills, memory, and related records in one place.
- Do not assume ~/Library or hidden application directories are preferable merely because they are conventional. Evaluate actual user utility before proposing relocation.
- Assistant's earlier split-storage layout was not adopted. See [COS-2026-005](../Decisions.md#cos-2026-005--keep-the-inspectable-workspace-together).

## 2026-10-22 — Updated completion and setup sequence

- User authorizes continuing until the tool's essential features are complete, excluding unnecessary features. Complete the current installation's workflows before general public adaptation.
- Future setup must help a new user ask their own AI for usable memory/context artifacts, explain what chat-OS accepts, and avoid importing Zayan's preferences and personal paths. Test full setup with independent fictional users later.
- AI-generated artifact summaries need provenance/user review and are not a promised export of inaccessible provider-internal memory. Full setup work/testing is future work, distinct from the existing fictional import walkthrough.
- Full wording and sequence: [requirements note](../Feedback/2026-10-22-new-user-documentation.md#updated-sequence--complete-core-features-then-generalize-setup).

## 2026-10-23 — Dedicated app and overnight continuation

- User explicitly chose a dedicated chat-management interface now and prefers an Apple-inspired UI for this product. Implemented local browser app over the existing core; see docs/chat-library.md and docs/adr/0001-local-browser-library.md. This supersedes earlier notes that no interface was selected.
- Current scope includes validated ChatGPT export upload, library search/read, local notes/titles, local archive/restore, registered project assignment, cited evidence, map filters/pan/zoom, captured context previews, health/sync and fresh database backups. Source-app mutation and a built-in reply model are not implemented.
- Full suite passed 72 tests; new module lint/format/type checks passed. Browser fixture workflows and read-only actual-library/context/map checks have evidence; public setup and clean-machine/cross-platform testing remain future work.
- User is sleeping and authorizes continued essential development until done or this five-hour allowance is exhausted. This explicit development authorization overrides the routine scheduled-maintenance reserve for this task, without changing that task's own policy.
- One-time heartbeat resume-chatos-after-allowance-refresh targets this chat at 4:16 AM October 23 America/Chicago. The account reported reset at 4:15:36 AM. Saved configuration is not execution evidence; recheck live usage before continuation. Do not use reset credits or manufacture work solely to consume tokens.
