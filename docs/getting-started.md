# Getting started

Use the sample below to see a conversation become a readable archive and a search result. It works in a cloned source checkout without connecting your chat accounts. All sample messages are fictional.

## What you need

The current implementation targets macOS. Use Python 3.9 or later with SQLite FTS5 support; the core commands use the standard library. Obsidian is optional. The generated HTML views can be opened in a browser, and Markdown files in an editor.

Run the commands below from the folder containing this repository's README. There is no packaged installer or general new-user initialization command yet. This checkout also contains maintainer-specific project paths, instructions, and operating notes; the sample keeps those out of its own workspace.

## 1. Import the sample

```bash
./scripts/chatos init Demo
cp docs/examples/conversations.json Demo/your_ais/chatgpt/imports/conversations.json
./scripts/chatos --root Demo sync
```

`--root Demo` creates a separate sample workspace inside this checkout. `--codex-home Demo/empty-source` deliberately supplies an empty local source folder, so this command does not scan your real Codex history. Only the supplied fictional ChatGPT export is imported. It does not log into an account or install a schedule.

Expect one **new chat**, no new skills or memory files, and a total of one conversation. The first behavior inventory is labeled as an initial capture. Sample data belongs to `Demo/`, which is excluded from Git.

## 2. Open the conversation

Open `Demo/your_ais/chatgpt/chats/2026/chatgpt-chatos-demo-reading-plan.md` in your editor. It contains the question, the assistant's suggestion, and the user's later choice in order. The neighboring JSON file holds structured metadata. Model information is unknown because the sample does not provide it.

Start the dedicated chat library:

```bash
./scripts/chatos --root Demo serve --open
```

Keep the terminal running; stop with Ctrl+C. Select the sample chat. Expand Local title, notes & project to add a local note or archive/restore it. Find evidence returns cited passages; Import chats receives supported exports before sync; Health & sync reports coverage, checks health, and creates fresh database backups. See the [library guide](chat-library.md) for the full workflow. The server reuses the saved empty Codex source for demo sync.

You can also open the older `Demo/library/dashboard.html` in a browser. Filter for “reading” to find the chat, then follow its source link. This filter searches titles, project fields, and short previews; use the CLI for full transcript search.

## 3. Find the relevant passage

```bash
./scripts/chatos --root Demo search "reading notes"
./scripts/chatos --root Demo retrieve "Markdown reading notes"
```

Search returns conversations and snippets. Retrieval returns message passages with speaker roles and archived source locations. The sample contains both an assistant's suggestion and a user's choice; a result's relevance does not make every passage a decision. The [worked example](using-history.md) explains how to interpret them.

## 4. Check the sample's health

```bash
./scripts/chatos --root Demo status
./scripts/chatos --root Demo doctor
```

A successful run does not establish full source coverage. Warnings about export-based ChatGPT capture or an unconnected Muse source are expected. Health checks inspect the local archive and report these distinctions.

Run the import command again without changing the sample file. Expect zero new chats and zero updated chats. The existing conversation is retained, not duplicated.

## Using your own sources

The demo is an isolated walkthrough, not an initializer for all your personal integrations. Before using the main workspace with real chats, its configuration and instructions need to match your machine and projects:

- `System/Projects/registry.json` and `overrides.json` currently describe the maintainer's projects and reviewed assignments.
- Workspace instructions and skills contain personal paths. Several maintenance scripts also default to the maintainer's Codex folder.
- Project-index delivery has a personal destination restriction. It is separate from core sync and is not portable merely by changing the registry.
- Cloning does not install an assistant integration or schedule. Existing installation records are not proof those are configured on your machine.

These are public-onboarding gaps to resolve, not routine maintenance we expect every new user to perform indefinitely. The [product brief](product.md#what-must-be-resolved-before-a-public-release) explains the remaining design work.

Once a workspace has been configured, the ordinary command is `./scripts/chatos sync`, which scans its local Codex source and supported export inboxes. ChatGPT JSON or ZIP exports go in `workspace/your_ais/chatgpt/imports/`; the ZIP importer expects one `conversations.json` payload and does not download media. Muse only has normalized-input support; a general raw export adapter remains deferred. See [features and limits](features.md).

## Optional display and developer checks

Plain-text reports work without extra packages. For Rich tables and colors, an optional environment can be created with uv:

```bash
uv venv
uv pip install --python .venv/bin/python -r requirements-cli.txt
.venv/bin/python -m chatos --root Demo status
```

Add `--json` to a command when another program needs structured output. This changes the presentation, not the stored records.

The repository's tests use synthetic fixtures:

```bash
python3 -B -m unittest discover -s tests -v
```

Optional semantic-search dependencies and model files are separate from the core walkthrough. The [runtime reference](../workspace/chief_of_staff/reference/Runtime%20reference.md) covers maintainer operations and recovery.
