# ChatOS

**A local library for your AI conversations and the context around them.**

Import chats, find earlier discussions, keep notes, and inspect the messages behind a remembered choice. Your records live in a visible folder on your machine. Browse them in the local web app or let an assistant with file access use them to help you resume work.

## Setup

You need **macOS and Python 3.9+ with SQLite FTS5**. The core app uses Python's standard library; no model, API key, or additional packages are required for the basic archive and keyword search. Obsidian is optional.

Download or clone this repository, open a terminal in its root folder, then run:

```bash
./scripts/chatos init workspace
./scripts/chatos --root workspace serve --open
```

The first command creates your private workspace. The second opens the chat library in your browser. Keep the terminal running while using the app; stop it with **Ctrl+C**. If the browser does not open, use the launch URL printed in the terminal. If port 8765 is occupied, add `--port 0` to choose a free port.

**Already have a configured workspace?** Skip `init` and run the second command. Initialization refuses an existing nonempty directory. You can choose another data folder by replacing `workspace` in both commands.

### Add your chats

The library starts empty. To import a supported **ChatGPT JSON or ZIP export**:

1. Click **Import chats** in the app and choose your export, up to 128 MiB.
2. Click **Sync workspace** to import the received records.
3. Select a conversation to read it, or search for a topic you remember.

This imports a local export; it does not connect your ChatGPT account. ZIP attachments are not extracted. Reimporting the same source conversations does not create duplicate chats.

To include local **Codex history**, use this initialization command *instead of* the plain `init` command above, then run sync and open the app:

```bash
./scripts/chatos init workspace --codex-home "$HOME/.codex"
./scripts/chatos --root workspace sync
./scripts/chatos --root workspace serve --open
```

Codex capture is disabled unless you opt in. The initializer creates an empty project registry and does not install an assistant integration or scheduled task. See [Getting started](docs/getting-started.md) for source configuration and setup limits.

### Try it before importing personal data

This separate demo imports one fictional conversation:

```bash
./scripts/chatos init Demo
cp docs/examples/conversations.json Demo/your_ais/chatgpt/imports/conversations.json
./scripts/chatos --root Demo sync
./scripts/chatos --root Demo serve --open
```

`Demo/` stays separate from `workspace/`. The sample does not scan your Codex history or connect an account.

### Optional semantic search and clustering

The pretrained semantic features need **Qwen/Qwen3-Embedding-0.6B** downloaded locally, additional Python packages, and embeddings built from your chats. HDBSCAN creates clusters; UMAP creates the 2D projection. No separate chat-generation model or inference API key is required.

These are separate from the core setup above. Follow [Semantic setup](docs/semantic-search.md) to install the optional runtime and pinned model, build passage embeddings, and generate the map. The pretrained map needs at least six conversations with current embeddings; the one-chat demo cannot produce it. Ordinary sync does not download the model or rebuild embeddings.

## Everyday use

Open the app with `./scripts/chatos --root workspace serve --open` whenever you want to use your library.

- **Find a chat:** search its transcript text or your local notes; filter by source or project.
- **Read and organize:** select a conversation, add a local title or note, or archive/restore it. These changes stay separate from the captured messages.
- **Inspect evidence:** choose **Find evidence** to see matching passages with message citations.
- **Check your archive:** open **Health & sync** to inspect coverage, run checks, or create a fresh database backup.

You can also use the terminal:

```bash
./scripts/chatos --root workspace sync
./scripts/chatos --root workspace search "reading notes"
./scripts/chatos --root workspace retrieve "Markdown reading notes"
./scripts/chatos --root workspace doctor
./scripts/chatos --root workspace backup --fresh
```

`search` finds conversations; `retrieve` finds specific passages. Both return captured evidence that you or an assistant can inspect. An assistant acting as your **Chief of Staff** can use those passages and current project files to help resume work. That role needs an active host with file/tool access; ChatOS does not include an always-running AI agent.

[Chat-library guide](docs/chat-library.md) · [Using earlier conversations](docs/using-history.md)

## Features

Checked features are implemented within the [documented limits](docs/features.md). They do not imply complete capture or a connected account.

- [x] Import available local Codex history and supported ChatGPT exports, retaining source IDs, metadata, capture gaps, and revisions.
- [x] Browse, search, filter, annotate, archive/restore, and associate captured chats with projects.
- [x] Retrieve cited message passages, optionally scoped to a project.
- [x] Inspect accessible skills, memory, instructions, and dated captured copies.
- [x] Resume project work through documented assistant retrieval, briefing, and filing procedures.
- [x] Explore related chats with an experimental map and optional local semantic retrieval.
- [x] Inspect sync results, change counts, source coverage, and diagnostics.
- [x] Create verified database backups and restore them into a new directory.
- [x] Keep application code and a visible private workspace separately organized.

### Planned

- [ ] Guided onboarding for sources, reusable context, and assistant integration, with broader independent-user validation.
- [ ] A guide for asking your AI to prepare inspectable memory/context artifacts with provenance and review.
- [ ] Migration of selected chats and context to another chat application.
- [ ] Broader verified source capture and better-evaluated semantic discovery. Raw Muse export work remains deferred.

## Data and current limits

Your chats, settings, context, and database live in `workspace/`, which is excluded from Git and the Python package. Source applications and their original files remain separate. See [Folder layout](docs/reorganization.md) for editing and recovery rules.

This is an early local application. Capture can be partial; source coverage is reported explicitly. Semantic search and clustering are optional experiments. Sync runs when invoked; scheduled maintenance requires separate configuration. Database backups do not include the entire workspace, original attachments, or protection against losing this device. Review files before sharing them.

## Documentation and development

[Documentation index](docs/README.md) · [Concepts](docs/concepts.md) · [Architecture](docs/how-it-works.md) · [Features and limits](docs/features.md) · [Verification](docs/verification.md) · [Contributing](CONTRIBUTING.md)

For a configured installation: [current state](workspace/STATE.md) · [sync report](workspace/STATUS.md) · [roadmap](workspace/IMPLEMENTATION.md). These private records are absent from a fresh clone.
