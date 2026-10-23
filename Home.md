---
type: index
---
# chat-OS workspace

Keep captured AI conversations and related context in one place. Browse and search the records yourself, or work with an assistant that can retrieve relevant messages and help you continue a project.

**New here? Start with [the README](README.md) and [the fictional walkthrough](docs/getting-started.md).** No existing archive or connected account is needed for the sample.

An assistant acting as a **Chief of Staff** helps organize context and carry out work you authorize. That role needs an active assistant and access to the workspace; the repository is not an always-running AI agent.

## Understand the application

[Product and purpose](docs/product.md) · [Concepts](docs/concepts.md) · [Features](docs/features.md) · [Architecture](docs/how-it-works.md) · [Using earlier conversations](docs/using-history.md)

## Use this configured workspace

Start the local app with `python3 -m chatos serve --open`. The [library guide](docs/chat-library.md) covers import, search, local annotations, archive/restore, project assignment, context, and health.

- [Conversations](Conversations/Index.md) and [HTML dashboard](Humans/dashboard.html) — browse captured chats.
- [Projects](Projects/Index.md) and [topics](Topics/Index.md) — generated ways to navigate related context.
- [Human guide](Humans/Start%20here.md) — where to start and what the views mean.
- [Sync status](STATUS.md) and [current state](STATE.md) — actual run evidence, coverage, and remaining work for this installation.
- [Skills](System/Skills/Index.md), [memory](System/Memory/Working%20memory.md), and [snapshots](System/Latest%20snapshot.md) — inspect accessible assistant-context records.
- [System index](System/Index.md) — operating guidance, reviewed choices, schedules, logs, and maintainer records.

These generated views and private records are created during use and are not all shipped in Git. For a new clone, use the demo path above. Source coverage is incomplete; a recorded message, generated summary, and live installed resource are different things.

[Roadmap](IMPLEMENTATION.md) · [Ideas](ideas.md) · [Runtime reference](System/Runtime%20reference.md) · [Documentation verification](docs/verification.md)
