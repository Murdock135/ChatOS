# chat-OS

**Keep your AI conversations and useful context in one visible local workspace.**

A useful discussion can be hard to find a week later—especially when it happened in another chat or application. chat-OS collects available conversation records, makes them readable and searchable, and preserves links to the messages behind an explanation or project note.

You can use the workspace yourself or let an assistant with access help you find and use earlier context.

## What you can do

- **Collect and read chats:** import available local Codex history or supported ChatGPT exports, with source information and capture gaps preserved.
- **Find earlier discussions:** search transcript text, retrieve specific message excerpts, and inspect the original wording.
- **Manage your library:** add local titles and notes, archive/restore chats, and associate them with projects in a dedicated local browser app.
- **Inspect assistant context:** see accessible skills, memory, instructions, and their dated captured copies in the workspace.
- **Continue earlier work with an assistant:** ask it to read relevant messages and current project files, explain what is established, and propose a next step with evidence.

The assistant can act as a **Chief of Staff**: a role that helps organize context and follow through on work you authorize. It needs an active host and tool access; chat-OS does not include an always-running AI agent.

## Try it with a fictional chat

The current prototype targets macOS and Python 3.9+ with SQLite FTS5. Core commands need no API key or extra packages. From the cloned repository folder:

```bash
mkdir -p Demo/empty-source Demo/System/Imports/chatgpt
cp docs/examples/conversations.json Demo/System/Imports/chatgpt/conversations.json
python3 -m chatos --root Demo sync --codex-home Demo/empty-source
python3 -m chatos --root Demo serve --open
```

This creates a separate sample workspace under `Demo/` and imports one fictional conversation. It does not scan your real chat history, connect an account, or install a schedule. Keep the terminal running while you use the browser app; stop it with Ctrl+C. Follow [Getting started](docs/getting-started.md) or the [chat-library guide](docs/chat-library.md).

## Learn the system

- [Product and purpose](docs/product.md) — the problem, intended users, and human/assistant interfaces.
- [Core concepts](docs/concepts.md) — sources, captures, memory, skills, and recorded choices.
- [Features and limits](docs/features.md) — what works today and what remains incomplete.
- [How it works](docs/how-it-works.md) — diagrams, data flow, components, and storage.
- [Using earlier conversations](docs/using-history.md) — a worked example of evidence-based project continuity.

## Current status

This is an early application with a local browser app, readable files, and CLI commands. The sample is usable independently, but personal configuration still needs generalizing for other users. Cross-application migration remains future work. Source coverage varies; see [Features and limits](docs/features.md).

Real archives contain private data. Some authored notes and configuration are tracked even though conversation payloads and runtime directories are Git-ignored. Review contents before sharing; current backups stay on the same device.

[Documentation](docs/README.md) · [Roadmap](IMPLEMENTATION.md) · [Maintainer reference](System/Runtime%20reference.md) · [Verification record](docs/verification.md)
