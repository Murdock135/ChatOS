# Higher-fidelity history capture

Manual ChatGPT JSON/ZIP import remains available. Two additional commands stage source snapshots for ordinary sync. They preserve source conversation IDs, so reimports update the existing record and retain revisions.

## Codex app-server API

Use the installed Codex CLI and an explicitly selected local source:

```bash
./scripts/chatos --root workspace capture-codex --codex-home "$HOME/.codex"
./scripts/chatos --root workspace sync
```

The adapter initializes a local stdio app-server, lists active and archived threads across `cli`, `vscode`, `exec`, `appServer` and `unknown` sources, and exhausts turn and item pagination in chronological order. Subagent threads are excluded, consistent with the existing importer. It requests `itemsView: full`; summarized responses and repeated cursors fail visibly. It never resumes a thread or starts a turn. Codex startup can write its own runtime files; conversation reads do not edit source messages.

Snapshots contain visible user/assistant text, item/turn IDs, available item timestamps, attachment references and thread metadata. Internal tools and reasoning are excluded. Per-message model/effort remain unknown unless retained local evidence supplies them. Full turn items support older stores where dedicated item pagination is unsupported.

To include API capture on each ordinary sync, set `sources.codex.api_enabled` to `true` in the selected workspace's `chatos.json`. Codex must also be enabled with its absolute source path. This is opt-in; fresh workspaces do not launch the API automatically. API failures are reported while local-file fallback continues. Incremental capture compares source update timestamps; `capture-codex --force` rereads every discovered thread. `--thread ID` restricts an explicit capture.

API snapshots are under `your_ais/codex/imports/` in a version 2 workspace. `app_data/state/codex-api-capture.json` records discovery, staged/unchanged counts and failed IDs. Failed captures retain the previous snapshot and retry on the next capture.

During sync, API and local records align on stable IDs or exact visible text in sequence. Known separated memory-citation/image wrappers are ignored only for alignment; original text and source IDs remain available. Repeated identical messages stay distinct. Unmatched intervals from both sources are retained with an ordering-uncertainty flag. Revisions preserve earlier records. This is evidence reconciliation, not proof that every retained variant is a separately authored message.

## ChatGPT with chatgpt-history

[chatgpt-history](https://github.com/xavierdpt/chatgpt-history) is a separate MIT-licensed exporter using ChatGPT's undocumented authenticated backend. smriti runs an explicitly supplied local checkout and stages its individual conversation files. Python 3.10+ and the exporter's `curl_cffi` dependency are needed for capture; the archive itself still supports Python 3.9 without that dependency.

Install the exporter in a private location and follow its README. The integration was inspected and tested against upstream commit `b2683b4043523115258ed293f1136cf019e00e0b`. Keep its authentication config outside version control and set file permissions to `600`. Supply credentials locally using the upstream authentication instructions, never through a chat or a command-line token argument.

```bash
./scripts/chatos --root workspace capture-chatgpt \
  --exporter /absolute/private/chatgpt-history/chatgpt_export.py \
  --config /absolute/private/chatgpt-history/config.json \
  --python /absolute/private/chatgpt-history/.venv/bin/python
./scripts/chatos --root workspace sync
```

This runs an incremental export including archived chats. The wrapper reduces exporter output to numeric completion counts; HTTP error bodies and authentication values are not logged. Upstream's nonzero failed-download count produces a partial result even if the process exits zero. An unrecognized completion summary is unverified, not success. Authentication errors require updating the local config. Capture is explicit; normal sync does not authenticate to ChatGPT or schedule exports.

Already have a downloaded export directory?

```bash
./scripts/chatos --root workspace import-chatgpt-history /absolute/path/to/export
./scripts/chatos --root workspace sync
```

The importer reads `export/conversations/*.json`; `index.json` is not a transcript. Both individual backend mappings and official `conversations.json` arrays use the same normalizer. It retains all visible branches, parent/children IDs, active-branch membership, model metadata and supported text/media/file references. Known hidden messages and private reasoning are excluded. Existing dated newer archive snapshots take precedence over older imports.

Raw exporter responses stay in the private workspace under `app_data/state/chatgpt-history-export/`; staged source mappings go to `your_ais/chatgpt/imports/`. These original exports can contain private data beyond the normalized visible archive. Do not share the config, exports or private workspace. A run receipt is stored in `app_data/state/chatgpt-history-capture.json`.

## Coverage limits

These tools read available persisted data. Neither route promises recovery of deleted or inaccessible chats. ChatGPT project conversations may be missing from upstream discovery, and media bytes are not downloaded. Counts cover discovered/staged records, not every conversation in an account. Source variants and inherited fork messages can contribute multiple entries to aggregate message counts.

Run `coverage --json` after sync and inspect the capture receipts separately. [Source coverage](source-coverage.md) explains the archive's counts and gaps.

Protocol reference: official [Codex App Server](https://learn.chatgpt.com/docs/app-server), sections Initialization, Read a stored thread, List thread turns, List thread items, and List threads.
