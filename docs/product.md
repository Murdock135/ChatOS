# Product and purpose

## The problem

Useful information accumulates across AI conversations: explanations, code discussions, research notes, preferences, and choices about ongoing work. Finding it later often requires remembering which app, chat, or wording you used. A new conversation may begin without that earlier context, so you repeat yourself or reconstruct the work manually.

chat-OS gives those captured conversations a common, inspectable home. You should be able to find a discussion, read the original messages, understand their limitations, and use relevant context when continuing work.

## What kind of product is it?

The intended product is a user-facing tool for managing AI conversations and the context around them. Its current implementation is an early local workspace application: Python commands import and index records; a local browser app provides chat management; readable files expose their provenance; assistant instructions explain how to use them during a conversation.

A working description is:

> A local workspace for collecting, finding, and using your AI conversations, with readable records that you and your assistant can inspect.

This describes the product direction. A dedicated local browser interface is now implemented. A packaged desktop application, hosted service, and final public positioning remain open. The checkout still contains the original user's configuration and operating history. It is not yet a turnkey installation for another person.

## Who uses it?

There are two complementary ways to use the same workspace:

- **A person managing their chats:** browse captured conversations, search for a subject, inspect original wording, associate a conversation with a project, and see which sources are incomplete or out of date.
- **A person working with an assistant:** ask it to retrieve relevant passages, explain what an earlier exchange establishes, read current project files, and help continue the work.

Researchers, developers, and people working across several AI chats are plausible early audiences. Selecting a narrower first public audience remains a product decision; these examples are not a completed market assessment.

## What is a Chief of Staff here?

It is a role played by an active AI assistant: help maintain continuity across your work, keep useful records organized, identify unresolved work, and carry out actions you authorize. It is not a second person, a model included in the Python package, or a process that is always thinking in the background.

For example, you can ask: “Find our earlier discussion about the evaluation method, show what I actually chose, and compare it with the current project files.” The code retrieves candidate passages. The assistant reads them, checks their context and later changes, and explains the result with links. Its tool access and permissions determine what it can read or change.

The assistant role adds value, but people can browse and search the archive without an active assistant. Today, natural-language interpretation happens in the connected assistant, not in a built-in chat-OS chat service.

## Interaction surfaces

An interaction surface is simply where someone gives the system input and receives a result.

| Participant | Available today | Boundary |
| --- | --- | --- |
| Person | Local browser library (`serve`), Markdown in an editor, generated HTML views, terminal commands | Local titles, notes, archive/restore, project assignment, and cited search are implemented. The map is experimental; source-app edits are outside this surface. |
| Active assistant | Workspace files, CLI evidence retrieval, and instructions called skills | It needs filesystem/tool access and the relevant instructions. Ordinary chats in other apps do not automatically receive the archive. |
| Deterministic runner | `sync`, indexes, snapshots, reports, and database backups | It does not interpret intentions or decide that a suggestion became an accepted action. |

Both people and assistants operate over the same records. The user explicitly requested the dedicated management interface. A general integration API/MCP interface remains future work; the local browser uses a bounded token-protected HTTP API.

## Product requirements already established

- Human-facing chat management is a first-class purpose, alongside assistant workflows.
- Keep the workspace together and visible for now. A conventional hidden directory is not automatically a better design. See [the storage decision](../workspace/chief_of_staff/decisions/README.md#cos-2026-005--keep-the-inspectable-workspace-together).
- Preserve source identities, available messages, capture gaps, and the distinction between evidence and interpretation.
- Explain concepts before using them. Make the path from a fresh clone to first use understandable.
- Eventually support taking useful records and context to another chat application. Migration remains future work.

“Manage chats” currently means capture, inspect, browse, search, annotate, archive/restore locally, and associate records with projects. Renaming/deleting chats in the source application, replying to them, universal tagging, and importing context into another application are not implemented management features.

## What must be resolved before a public release?

The basic initializer creates an independent workspace without inheriting the maintainer's project owners or private operating notes. A complete guided onboarding experience still needs clear source/account configuration and context-artifact instructions. The local interface and annotation rules are documented in the [library guide](chat-library.md). Public packaging, platform support, and update/backup behavior still need broader verification.

Those are adoption gaps in the current implementation. Better documentation makes them understandable; it does not itself implement them. See the [feature map](features.md) and [verification record](verification.md).
