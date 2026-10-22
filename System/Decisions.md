# Recorded chat-OS decisions

These are source-reviewed decisions for this project. They are maintained records, not an automatic decision extractor. Proposed alternatives remain separate.

## Record format

Each entry has a stable ID, date, status, scope, authority, supporting source message, and supersession relationship. If a decision changes, retain the old entry and link the replacement; do not silently rewrite history.

## COS-2026-001 — Run locally on the Mac

- Date: 2026-10-22
- Status: adopted
- Authority: explicit user instruction
- Scope: Applies to the initial chat-OS runtime. No always-on server or remote publication is selected.
- Supersedes: none
- Source: [user message](</Users/zayan/Documents/obsidian_vaults/chats/Conversations/2026/codex-01a16442-0b52-7260-8019-a855dff30567.md:393>); conversation codex:01a16442-0b52-7260-8019-a855dff30567; message msg_01a1644e-95f9-7dc3-98e6-24e94732e712

## COS-2026-002 — The assistant owns maintenance

- Date: 2026-10-22
- Status: adopted
- Authority: explicit user instruction
- Scope: The assistant manages filing, sync, records, and recovery within available permissions. Zayan uses the repository primarily as a reference.
- Supersedes: none
- Source: [user message](</Users/zayan/Documents/obsidian_vaults/chats/Conversations/2026/codex-01a16442-0b52-7260-8019-a855dff30567.md:692>); conversation codex:01a16442-0b52-7260-8019-a855dff30567; message msg_01a16462-1c66-7c20-a13c-2a0a5e8e13ed

## COS-2026-003 — Archive conversations and operating records

- Date: 2026-10-22
- Status: adopted
- Authority: explicit user instruction
- Scope: Scope includes Codex, ChatGPT and Muse conversations, topic organization, accessible behavior files, memory, skills, schedules, metadata, and failures. Coverage remains source-dependent.
- Supersedes: none
- Source: [user message](</Users/zayan/Documents/obsidian_vaults/chats/Conversations/2026/codex-01a16442-0b52-7260-8019-a855dff30567.md:21>); conversation codex:01a16442-0b52-7260-8019-a855dff30567; message msg_01a16442-1468-7683-b090-17b3ccba016d

## Still undecided

- VS Code versus Obsidian as the preferred rendering interface: discussed, with no final selection recorded. The repository currently preserves Markdown/Obsidian compatibility and includes VS Code tasks.
- Pretrained embedding model, clustering algorithm, and production RAG backend: not selected. The current LSA map is an experiment.
- Unattended ChatGPT and Muse capture: required but source access is incomplete. No remote bridge or additional access permissions have been approved or enabled.
