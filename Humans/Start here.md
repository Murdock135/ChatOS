---
type: guide
audience: human
project: chat-os
updated: 2026-10-22
---
# Start here

This is your shared workspace with the Chief of Staff. The assistant handles routine upkeep; you can inspect the sources, history, capture gaps, and changes behind your chats, skills, and memory. Transparency and provenance are core purposes, alongside helping you resume projects.

Start with **[Current state](../STATE.md)** and **[What happens when I chat?](What%20happens%20when%20I%20chat.md)**. The archive contains 220 Codex and 31 partial ChatGPT records. Complete cross-app capture and the first unattended maintenance run remain unverified; Muse is deferred.

| What you want | Open |
| --- | --- |
| Current capabilities and gaps | [Current state](../STATE.md) |
| Last sync and source coverage | [Sync status](../STATUS.md) |
| Browse or filter conversations | [Dashboard](dashboard.html) |
| Explore the provisional 2D map | [Conversation map](explorer.html) |
| Workspace memory | [Working memory](../System/Memory/Working%20memory.md) |
| Current discovered skills | [Skills inventory](../System/Skills/Index.md) |
| Copies of behavior files and external memory | [Latest snapshot](../System/Latest%20snapshot.md) |
| Established system decisions | [Recorded decisions](../System/Decisions.md) |
| Failures and recoveries | [Event log](../System/Logs/Event%20log.md) |
| Feedback and adjustments | [Feedback log](../System/Feedback%20log.md) |
| Current Codex task metadata | [Schedules](../System/Schedules/Index.md) |
| Project ownership and deliveries | [Projects](../Projects/Index.md), [receipts](../System/Projects/Automatic%20filing%20receipts.md), [queue](../System/Projects/Automatic%20routing%20queue.md) |
| Remaining implementation | [Roadmap](../IMPLEMENTATION.md) |
| Optional improvements and their concrete form | [Ideas](../ideas.md) |

## Using it

Continue giving work through chat. Name the project when useful. Ask the assistant to resume a project, retrieve a past decision with evidence, show pending filing, or explain a failure. Routine sync, filing, and verification are the assistant's responsibility within its available permissions.

Your projects stay in their existing vault folders and code repositories. This repository links to them and preserves their workflows. A reviewed project match is not a completed task; a delivery receipt means the destination was written and checked.

## Understanding freshness

The sync status and generated views have timestamps. Ordinary sync now checks behavior-file hashes, refreshes the skills inventory, and creates a snapshot when files change. A snapshot remains a dated copy: editing it does not alter the live app, activate a skill, or change a schedule.

The global Chief of Staff instruction reference was loaded into this conversation after installation. That verifies the reference is visible here; broader behavior still depends on the active agent, source access, and destination permissions. Ordinary ChatGPT and Muse do not inherit these local Codex instructions.

A saved active schedule or recorded run time does not prove completion. The native launch agent was disabled after macOS privacy blocked it. No computer security/privacy settings were weakened.

## Storage

Markdown/JSON conversations and the SQLite runtime database stay local. Skills, instructions, scripts, and documentation have local Git history. Private transcripts, imports, runtime logs, snapshots, and database backups are excluded from Git. No remote repository or external hosting is configured.

Database recovery has been tested into a new isolated directory. It restores conversation records/revisions and regenerates source files. Behavior snapshots and the project registry are separate recovery material. All current copies remain on this Mac, so this is not protection against losing the entire device.

## Coding preferences

Your [preferred coding style](/Users/zayan/.codex/skills/preferred-coding-style/SKILL.md) is installed with a global Codex instruction to apply it when writing, changing, reviewing, or illustrating code. The trigger loaded into the setup chat. You can explicitly invoke `$preferred-coding-style`; if a future session does not show the new skill, restart Codex. This configures Codex, not ordinary ChatGPT sessions.
