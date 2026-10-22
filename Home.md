---
type: index
---
# Chief of Staff workspace

**[Current state](STATE.md)** — capabilities, coverage, memory, skills, logs, and current development priority.

**New here? [Start here — human guide](Humans/Start%20here.md).**

Agent-managed operating workspace and conversation archive. The Chief of Staff maintains the records and infrastructure; Zayan uses them as a reference. Conversations are intended to span Codex, ChatGPT, and Muse, with navigation by topic and date.

[Offline dashboard](Humans/dashboard.html) · [Sync status](STATUS.md) · [Conversations](Conversations/Index.md) · [Projects](Projects/Index.md)

## Building the chat-OS

- [Implementation roadmap](IMPLEMENTATION.md) — remaining work, dependencies, and acceptance checks.
- [Ideas](ideas.md) — optional improvements and small experiments.

## Chief of Staff system

- [[System/Index|System files]] — operating guidance, skills, memory, configuration, rules, and automations.
- [[Working memory]] — vault-owned durable notes.
- [[Scheduled tasks]] — task schedules, saved state, and archived definitions.
- [[System logs]] — chat and scheduled-task incidents and recoveries.
- [[Feedback log]] — negative feedback and how the assistant responds to it.
- [[Conversation metadata]] — model, source, timestamps, and other conversation details.
- [[Project routing]] — keep project material with its owner.
- [[Latest snapshot]] — dated copies of accessible local Codex behavior files.
- [Current skills inventory](System/Skills/Index.md) — workspace skills and discovered local/cached skills, with activation limits.
- [Consistency audit](System/Audits/2026-10-22%20consistency%20audit.md) — repaired defects, remaining gaps, and the check command.

## Topics

- [[Conversation knowledge management]] — archiving, semantic organization, and continuity across chats.

## Conversations

- [[2026-10-22 Chief of Staff and chat archive]] — archive scope and initial setup.

## Capture status

The vault structure and local agent guidance are in place. The initial conversation record is a partial capture of the setup exchange, with a labeled summary. Local Codex import, incremental sync, search, and project context views now work. Full cross-app capture remains incomplete; see STATE.md and the timestamped sync status.

## Open work

- Identify the other chat apps to include and their available exports or connectors.
- Import available histories with stable source identifiers and completeness labels.
- Establish and verify ongoing capture for each source.
- Expand and refine topic links as conversations arrive.
