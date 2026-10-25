# Use the chat library

The local browser app lets you manage captured chats without an active assistant. Start it from the repository folder:

```bash
./scripts/chatos serve --open
```

Keep that terminal running. Stop the app with Ctrl+C. It listens only on `127.0.0.1`; the printed launch URL contains a temporary access token. Use that URL to open another tab. Restarting the server creates a new token. `--port 0` chooses a free port if the default 8765 is occupied.

For the [fictional walkthrough](getting-started.md), use `./scripts/chatos --root Demo serve --open`. The app reuses the source folder recorded by the sample's sync. `--codex-home PATH` explicitly overrides that source for the server's sync button.

## Import an export

Open **Settings → Import chats → Choose export…** and choose a supported ChatGPT JSON or ZIP export, up to 128 MiB. The app validates it before saving an inbox copy; ZIP attachments are not extracted. Select **Sync now** in Settings or **Sync** in the header to ingest the received records. Imports stay on your machine and do not connect your ChatGPT account. The source export can contain private material and is kept in the local inbox.

Source IDs prevent duplicate chats. Older exports with known earlier conversation update times cannot replace a newer exported snapshot. Missing or equal timestamps cannot establish recency; stored revisions remain available, and import order can determine the current snapshot in that case.

## Read and find conversations

Conversations opens your active library. Search matches captured transcript text and local titles/notes; source and project filters narrow the results. Select a card to read the captured messages, including speaker, timestamp, model when known, and message ID. Capture labels and the original source ID stay visible. Captured text is displayed as text, including code and any HTML it contains. About this capture explains source limits. Branch relationship exposes exported parent/node links where available, so separate branches are not mistaken for one linear exchange.

Search returns one list of conversations ranked by their best matching passage, with an excerpt explaining each match. All meaningful query words must match the passage or its conversation title. Source, Project and Archived filters apply to the same results. Select a result to jump to its matching message; local-note matches open the conversation and are labeled separately. Clear the search to return to newest-first browsing. Search is lexical: incidental mentions can still match, and paraphrases may be missed. Check surrounding context and later changes before interpreting a passage. The terminal `retrieve` command remains available for cited evidence across chats and workspace notes.

## Add your own context

Expand **Local title, notes & project** in a conversation:

- Save a local title or note. A blank local title falls back to the captured title. Neither field changes messages or renames the chat in its original app.
- Archive locally to remove a chat from the active list. Check **Archived**, open the chat, and select **Restore to library** to undo it. Archiving does not delete records, remove them from evidence search or the map, or archive them in the source app.
- Select registered projects and apply the assignment. This saves an explicit local association that survives reimport; it does not write external project notes. With no registered projects, there is nothing to assign.

Annotations live in the workspace database. Readable copies appear under `workspace/your_ais/<source>/annotations/`; editing those generated copies does not update the database. Use the app or `library` command. Database backup/restore preserves annotations. Existing daily backups can predate later edits; make a fresh backup when needed using `./scripts/chatos backup --fresh`. Backups remain on this device.

The CLI exposes the same local annotation operation:

```bash
./scripts/chatos library chatgpt CONVERSATION_ID --title "Reading notes" --note "Compare the later revision."
./scripts/chatos library chatgpt CONVERSATION_ID --archive
./scripts/chatos library chatgpt CONVERSATION_ID --restore
```

## Inspect the rest of the workspace

**Conversation map** shows the generated experimental map. Filter by title, source, or project; pan and zoom; or use the keyboard-accessible title list to open a conversation. Local titles and project associations are current, while coordinates can come from an older representation. It shows method/freshness limits. Nearness is a discovery hint, not evidence that chats share an accepted decision. Optional semantic inference remains a separate maintenance operation.

**Skills & memory** lists captured skills, memory, and instructions from the published behavior snapshot. Filter by type/path and select a file to read its captured copy. The view identifies its live source path and capture time. It does not activate, edit, or install a skill. Run sync to reconcile accessible live files; a discovered file does not prove it is active in an assistant.

**Health & sync** puts the last run ID, status, errors, and library counts first. The following tables show new/updated behavior counts and actual source coverage. Back up now creates and verifies a fresh conversation-database backup, including local annotations. This does not back up every source file or behavior snapshot; use the CLI restore procedure for a new destination. Check health runs the existing doctor checks. Sync workspace runs the existing import/inventory workflow against the configured source and workspace inboxes. It does not connect a new account or perform the host assistant's desktop capture procedure.

The server is a foreground local application, not a hosted service or an always-running AI agent. Its API requires the temporary token and rejects other hosts/origins. Files are served through fixed assets and checked snapshot entries, rather than a general filesystem browser.

Unexpected interface failures return a reference to `workspace/app_data/logs/interface-errors.jsonl`. Its diagnostics contain operation names, error types, and code locations, without request bodies, query text, or exception messages. These are troubleshooting events, not proof of a scheduled task outcome.

## Setup and portable handoff

A new empty library opens Setup & handoff. This page lets you choose local Codex capture before scanning, inspect setup readiness, create an optional assistant-access guide, import a context artifact and inspect its sources/uncertainty before accepting it. Accepted context becomes searchable immediately. Retiring it with a reason removes it from retrieval and future bundles while preserving the source artifact, published note and review history. Already exported bundles remain historical copies.

Choose one conversation, a registered project or explicitly all captured records to create a portable bundle. Context is opt-in. The result shows a verified local folder containing START_HERE.md, readable records, separate annotations and integrity hashes. Open that folder yourself and review files before supplying them to a different application. This does not transmit anything or install destination memory. See [Onboarding](onboarding.md), [Context artifacts](context-artifacts.md) and [Portable bundles](portable-bundles.md).

## Sync status

The header's **Sync** control uses a green dot, matching the local-workspace indicator. During a run it reads **Syncing…**; the control is disabled until the request finishes. A compact status line shows the completed new/updated chat counts. Partial runs and failed requests show a red dot and an explanatory message instead of terminal output. Partial capture warnings still require attention even when some chats were updated. Text labels accompany color, and reduced-motion preferences disable the running pulse.

## Conversation list

The white library panel aligns conversation titles, last-updated dates/times and captured models. Dates use your browser's local timezone. Blue model tags indicate captured information; red Unknown tags mean the model was not captured. If a chat has multiple captured models, the row shows an additional-model count and the tag tooltip lists their names. Open the row to inspect message-level model evidence. Narrow layouts place metadata beneath the title.

## Pages and page size

Use the controls above the conversation list to show **10**, **50** (default) or **100** conversations per page. Previous/Next navigation shows the current page and visible range. Search, source/project/archive filters and page-size changes return to page 1. Pagination applies to keyword, bounded smart-search and assistant-reviewed results; page size does not expand the underlying smart-search candidate limit. Controls disable while loading and at the first/last boundaries. If records change and the current page disappears, the list returns to the last available page.

## User settings

Open **Settings** from the sidebar to see the local workspace path, import a ChatGPT JSON/ZIP export, sync configured sources, inspect the last completed sync and manage local search models. Import and workspace-path details live here rather than in the header/sidebar. **Sync** remains available in both Settings and the header; both controls share running/error states and disable together during a run. Source opt-in, assistant/context setup and portable handoff remain under Setup & handoff.
