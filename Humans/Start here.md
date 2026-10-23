---
type: guide
audience: human
project: chat-os
updated: 2026-10-23
---
# Start here

chat-OS is a local workspace for collecting, finding, and using AI conversations. The aim is to keep chats and related context visible together, so you can inspect them yourself and use relevant material when continuing work.

An assistant can help maintain that continuity: retrieve earlier messages, read current project files, organize useful outcomes, and carry out work you authorize. We call that assistant role the **Chief of Staff**. It is not a separate person or a built-in background intelligence. Ordinary browsing and searching do not require an active assistant.

## If you just cloned this repository

Start with [Getting started](../docs/getting-started.md). It imports a fictional conversation into a separate `Demo/` workspace, searches it, retrieves a passage, and checks health. It does not connect your accounts or use the maintainer's existing archive.

Then read [Product and purpose](../docs/product.md), [Core concepts](../docs/concepts.md), and [How it works](../docs/how-it-works.md). These explain the problem, terminology, interfaces, and architecture. [Features and limits](../docs/features.md) distinguishes implemented mechanisms from assistant workflows and future work.

The main workspace is currently a personal installation with machine-specific paths and authored records. Cloning it does not initialize your projects, install skills in a host, or configure scheduled maintenance. The getting-started guide explains this boundary.

## If this workspace is already configured for you

| You want to… | Start here |
| --- | --- |
| Browse and manage chats | `python3 -m chatos serve --open`; see the [library guide](../docs/chat-library.md) |
| Find something in transcript text | `python3 -m chatos search "subject"` from the workspace root |
| Inspect exact message passages | `python3 -m chatos retrieve "subject"`; see [the worked example](../docs/using-history.md) |
| Continue work with an assistant | Ask it to read current project files and relevant earlier chats, distinguish established choices from suggestions, and link the evidence |
| See current source coverage and the last run | [Sync status](../STATUS.md) and `python3 -m chatos doctor` |
| Inspect memory, skills, or instructions | [Working memory](../System/Memory/Working%20memory.md), [skills inventory](../System/Skills/Index.md), [snapshot index](../System/Latest%20snapshot.md) |
| Inspect operating history | [Schedules](../System/Schedules/Index.md), [event log](../System/Logs/Event%20log.md), [feedback log](../System/Feedback%20log.md) |
| Understand remaining work | [Current installation state](../STATE.md) and [roadmap](../IMPLEMENTATION.md) |

The dashboard filters titles, project fields, and short previews. It is not full transcript search. The [conversation map](explorer.html) is experimental and may describe an older set of inputs.

## Know what you are looking at

A conversation record preserves available source messages. A project note is maintained context. A search result is a candidate to read, not proof of a decision. A dated skill snapshot is a copy, not the installed live skill. Definitions and examples are in [Core concepts](../docs/concepts.md).

Generated conversation files and indexes can be replaced by sync. Use the library for durable local titles/notes, or keep authored notes linked to the source. Generated annotation files are readable database views. Your projects remain in their configured locations; associating a chat does not relocate those projects or create accepted tasks.

For maintenance commands, backup/restore scope, and configuration details, use the [runtime reference](../System/Runtime%20reference.md). Source exports, the conversation database, behavior snapshots, and attachments are different recovery scopes. Current same-device backups do not protect against losing the device.
