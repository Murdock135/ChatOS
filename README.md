# chat-OS

chat-OS is a local workspace for keeping AI conversations, project context, and assistant settings in one place. It helps you find earlier discussions, see which decisions were made, and resume work with the supporting sources close at hand.

Conversations are stored as readable Markdown and structured records. You can browse them in Obsidian, open the offline dashboard, or ask Codex to retrieve relevant passages. This installation is configured for Zayan’s Mac and projects; it is not a general-purpose installer.

## Start here

Open this folder as an Obsidian vault, or open [Home.md](Home.md) in your editor.

- **[Start here](Humans/Start%20here.md)** explains how to use the workspace.
- **[Dashboard](Humans/dashboard.html)** lets you browse and filter captured conversations. Open the HTML file in a browser.
- **[Current state](STATE.md)** describes what works and what remains incomplete.
- **[Sync status](STATUS.md)** shows the most recent sync results and source coverage.

When using Codex with this workspace, you can ask things like:

> What did we decide about this project last time?
>
> Find the conversation where we discussed my coding preferences.
>
> Help me resume work on SPARQ, starting with the recorded decisions and open questions.

Answers can only use accessible records. Missing conversations and partial captures remain visible as coverage gaps.

## Sync and check health

The core commands require Python 3.9 or later. They use the standard library and need no API key or package installation. Optional semantic-search tools have separate dependencies.

From Terminal:

```bash
cd /Users/zayan/Documents/obsidian_vaults/chats
python3 -m chatos sync
python3 -m chatos doctor
```

`sync` imports accessible local records and refreshes the archive. `doctor` checks the database, conversation files, latest backup, and freshness, and reports coverage warnings. For the full last-sync report, run `python3 -m chatos status`.

Reports show run metadata first, then counts of new and updated chats, skills, memory, and other captured changes. For Rich tables and colors, use `.venv/bin/python -m chatos sync` in this installation; `python3` also produces a readable report without Rich. Add `--json` to any command for machine-readable output, for example `python3 -m chatos status --json`.

You can also search directly:

```bash
python3 -m chatos search "coding preferences"
```

## What is captured?

Codex history is imported from available local files. ChatGPT supports export imports and partial desktop captures; a core sync does not fetch your entire ChatGPT account. Muse capture is deferred. The configured hourly Codex maintenance task can do additional agent work, but a saved schedule does not guarantee a completed run.

The archive contains private conversation data. Recognized credential formats are redacted, but that does not make it safe to publish. Backups currently remain on the same Mac.

For maintenance commands, storage locations, and recovery, see the [runtime reference](System/Runtime%20reference.md). Design details and planned work live in the [implementation roadmap](IMPLEMENTATION.md).
