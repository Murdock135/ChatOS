# chat-OS

**Keep your AI conversations and useful context in one visible local workspace.**

A useful discussion can be hard to find a week later—especially when it happened in another chat or application. chat-OS collects available conversation records, makes them readable and searchable, and preserves links to the messages behind an explanation or project note.

You can use the workspace yourself or let an assistant with access help you find and use earlier context.

## Feature checklist

Checked items are implemented within the limits stated here. They do not imply complete source coverage or that a fresh installation has connected your accounts. See [Features and limits](docs/features.md) for details and [Verification](docs/verification.md) for the checks performed.

- [x] **Collect chats:** import available local Codex history and supported ChatGPT JSON/ZIP exports; preserve source IDs, capture gaps, and revisions.
- [x] **Browse and organize:** use the local browser library to read transcripts, search, filter, add local titles/notes, archive/restore, and associate chats with projects.
- [x] **Find evidence:** search transcript text and retrieve cited message excerpts, optionally scoped to a project.
- [x] **Inspect assistant context:** browse accessible skills, memory, instructions, and dated captured copies; captured files are distinct from active host configuration.
- [x] **Resume work with an assistant:** use documented retrieval, briefing, and project-filing workflows. Requires an active assistant with file/tool access.
- [x] **Explore related chats:** experimental conversation map and optional local semantic retrieval; dependencies, coverage, freshness, and quality limits apply.
- [x] **Check health and changes:** inspect sync results, new/updated chat counts, context-file changes, capture warnings, and diagnostics.
- [x] **Back up and recover the database:** create verified local database backups and restore into a new directory. This does not restore the whole workspace or source attachments.

### Planned

- [ ] **Clearer project organization:** conventional application source/docs and a visible user workspace, with meaningful platform and Chief of Staff folders. [Structure proposal](docs/proposals/0001-repository-and-workspace-layout.md); no migration yet.
- [ ] **Independent new-user setup:** initialize a workspace without inheriting the maintainer's personal paths, preferences, or project registry; verify with fictional users.
- [ ] **Bring your own context:** prompts and accepted formats for asking your AI to prepare inspectable memory/context artifacts, with provenance and user review.
- [ ] **Cross-app migration:** prepare selected chats and context for another chat application; destination and transfer format remain to be defined.
- [ ] **Broader verified capture and better discovery:** improve source coverage and evaluate retrieval against real use cases. General raw Muse export work remains deferred.

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
