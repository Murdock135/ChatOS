# Versioned visible workspace and source package

Date: 2026-10-23. Status: adopted implementation direction; activation evidence is recorded in the reorganization guide and workspace migration receipt.

Authority: Zayan requested conventional repository organization and meaningful platform/Chief of Staff directories in codex:01a16510-7f12-78b0-afa9-d5aee24d915b, then authorized implementation with “continue working.” The latest instruction was to stop when reorganization is complete; codex:01a169ec-18f1-7d32-8090-90d0a116c56d resumes that work.

Application code is packaged from `src/chatos/`. A private, visible `workspace/` contains platform chats/inboxes, shared context, Chief of Staff guidance, library views, durable application data, and backups. `chatos.json` declares layout version 2 and source settings. Version 1 remains readable for compatibility. Storage stays together on disk; no hidden platform-directory relocation is introduced.

A copy-first migration compares conversation content, revisions, checkpoints, annotations and feedback reviews. Only current generated file paths change. Earlier revision JSON, immutable snapshot payloads/manifests and backup bytes retain their historical paths and hashes. The initial activation retained compatibility aliases. After user review, those aliases were retired from the visible root and workspace; active host entry references, instructions and schedules now use canonical paths. Historical absolute links can be located through the migration receipt; message text remains unchanged. Original directories remain recoverable until a retention decision is made.

This decision does not authorize broader onboarding work, new source connectors, raw Muse parsing, external publishing, or selecting an off-device backup service.
