---
type: guide
audience: human
project: chat-os
updated: 2026-10-22
---
# Start here

This is the Chief of Staff's operating workspace. The assistant manages its organization, synchronization, maintenance, and records. You use it mainly as a reference to inspect the assistant's state and work.

Start with [Current state](../STATE.md). You can then browse memory, skills, logs, project filing, and implementation progress without needing to maintain their structure or run the tools yourself. Continue giving work and direction through chat; the assistant handles routine upkeep within its available access and runtime.

**A local Codex archive/search runtime now works. [Current sync status](../STATUS.md) and [offline dashboard](dashboard.html) show its last scan. Full cross-app capture remains incomplete.**

## Where to go

| What you want | Open |
| --- | --- |
| Inspect the assistant's current state | [Current state](../STATE.md) |
| Read the memory maintained in this workspace | [Working memory](../System/Memory/Working%20memory.md) |
| Understand what still needs building | [Implementation roadmap](../IMPLEMENTATION.md) |
| Explore possible improvements | [ideas.md](../ideas.md) |
| Browse the workspace | [Home](../Home.md) |
| See the apps and sync limitations | [Sync sources](../System/Sync%20sources.md) |
| See where project material belongs | [Project routing](../System/Projects/Project%20routing.md) |
| Check items waiting to be filed | [Routing queue](../System/Projects/Routing%20queue.md) |
| Check what was actually filed | [Routing log](../System/Projects/Routing%20log.md) |
| Read failures and recoveries | [Event log](../System/Logs/Event%20log.md) |
| Review negative feedback and adjustments | [Feedback log](../System/Feedback%20log.md) |
| Inspect saved scheduled tasks | [Scheduled tasks](../System/Scheduled%20tasks.md) |
| Inspect archived skills and memory | [Latest system snapshot](../System/Latest%20snapshot.md) |
| Find currently discovered skills | [Current skills inventory](../System/Skills/Index.md) |
| Understand known gaps and consistency checks | [Consistency audit](../System/Audits/2026-10-22%20consistency%20audit.md) |

## Initial scaffold capabilities (historical)

- This setup conversation is recorded as a partial capture, with verified model metadata.
- Local scripts can refresh one Codex conversation's metadata, collect retained runtime errors, and make a dated copy of accessible system files.
- Workspace instructions define project filing, feedback logging, and incident recording.
- A project-router skill has an initial registry of nine project, paper, and system destinations. There is a queue for ambiguous or blocked deliveries.

**Original backlog; see STATE.md for current completion:** automatic conversation import, recurring Mac sync, Muse/ChatGPT ingestion, semantic clustering, complete scheduled-run tracking, and reliable end-to-end project delivery. The roadmap has the details and completion checks.

The initial runtime is your Mac. Codex, ChatGPT, and Muse are in scope. VS Code and a standard repository are being considered; this folder is now a local Git repository, with no remote configured.

## How to use this with the assistant

Start a conversation with the outcome you want. Name a project when you know it; the assistant should use the project registry and relevant files to recover context.

Examples:

- “Resume SPARQ v1 JAMIA. What did we decide, and what is still open?”
- “This belongs to Concerted Abduction. Save the decision with its source.”
- “Show me anything waiting to be filed into a project.”
- “What failed recently, and what recovered?”
- “Work on the first unfinished implementation milestone.”

These are requests the system is being built to support. The assistant is responsible for verifying output, retaining source evidence, and checking filing receipts; those records are available for you to inspect. An instruction in a file does not prove automatic execution is working.

## A small map of the files

| Location | Purpose |
| --- | --- |
| `Humans/` | Orientation and instructions for you |
| `Conversations/` | Captured conversations and their metadata |
| `Topics/` | Topic notes linking related conversations |
| `System/Memory/` | Vault-owned working memory |
| `System/Projects/` | Project destinations, filing receipts, and pending items |
| `System/Skills/` | Skills owned by this workspace |
| `System/Logs/` | Operational events and collection state |
| `System/Scripts/` | The current local tools |
| `System/Snapshots/` | Dated copies of files from the live Codex installation |
| `AGENTS.md` | Instructions for agents working in this workspace |

Your existing projects stay in their own vault folders or code repositories. This workspace links to them; it does not replace their task and note conventions.

## Editing and interpreting the records

You can inspect and edit the files, but routine editing and verification belong to the assistant. Give corrections through chat when convenient; the assistant should update the appropriate active records and retain the evidence.

Snapshots are historical copies. Editing a snapshot does not change the live app, install a skill, or alter a scheduled task. The assistant must use supported live configuration/task tools for those changes and then refresh the archive as appropriate.

“Latest snapshot” means the most recently captured archive, not a continuously updated view. The current skills inventory includes workspace-owned skills as well as configured local/cache roots; it also has a scan date. The assistant owns consistency checks and should disclose drift rather than relying on you to notice it.

For event logs, retain the original evidence and append a correction or recovery. In project routing, **filed** means the destination was written and checked; **pending** means delivery still needs work. An enabled schedule does not prove its last run succeeded.

## Where to start next

The assistant's next implementation milestone is the [first implementation slice](../IMPLEMENTATION.md#first-implementation-slice): import one Codex conversation reliably, then attach regular sync after retries and duplicate prevention are verified. The assistant maintains this guide as capabilities become operational. Hourly Codex maintenance is configured, but its first scheduled run still needs verification. Muse and ChatGPT need completed source/export access.
