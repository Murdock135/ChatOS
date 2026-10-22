# Project routing

The Chief of Staff is the entry point; project material should land in the workspace that owns it. Use [project-router](../Skills/project-router/SKILL.md) and the [registry](registry.json).

## Verified starting inventory

Inspected 2026-10-22: eight project/paper homes in `/Users/zayan/Documents/obsidian_vaults/academic_life`, plus this chat-OS workspace. This is an initial inventory, not all projects on disk or all app projects.

The currently existing work vault is `academic_life`. The older name `zayans_academic_life` was not present at inspection. Resolve paths against current files rather than recreating the old directory.

| ID | Owner | Routing boundary |
| --- | --- | --- |
| chat-os | Chief of Staff chat-OS | Conversation archive, sync, skills, system logs, and operating behavior here. |
| agentic-epidemiology | Agentic System For epidemiology | Shared SPARQ/epidemiology project work. |
| sparq-v1-jamia | SPARQ v1 JAMIA | JAMIA/v1 manuscript-specific material. |
| sparq-v2 | SPARQ v2 | Explicitly identified v2 paper material. |
| evidence-mas | Combination of Evidence in MASs | Shared evidence-combination research work. |
| purely-lm-pipeline | Purely language model pipeline | Material explicitly owned by this paper. |
| finding-a-job | Finding a job | Job-search decisions, actions, and notes. |
| american-history | Learning American History | Work owned by the existing history-learning project. |
| organizing-myself | Organizing Myself | Personal organization project; link chat-OS implementation rather than duplicating its system files. |

Home pages, project status, directory conventions, and repository README scopes were inspected. Aliases and repository relationships in the registry are initial routing aids; recheck specific ownership for the current item. Other repositories and PKM content need discovery before their own destinations can be registered.

## Destination conventions

The work vault's `System/How To Use.md` defines the filing convention: tasks in the owning Milestones, research progress in Research Log, substantial explorations in Scratch with index links, and personal notes in Notes. Manuscript-specific material belongs under Papers; shared infrastructure remains at project level. Shared resources remain in Library. Read the guide and destination before mutating them.

Project data currently sits outside this chat workspace's writable roots. Existing session permissions still apply: route the item and prepare a concrete draft here if a destination is unavailable; obtain required filesystem access through the supported permission mechanism before claiming delivery. Do not substitute a local topic link for a successful external write.

## Tracking

- [Routing log](Routing%20log.md): verified deliveries and their sources.
- [Routing queue](Routing%20queue.md): ambiguities, pending delivery, and drafts.

The skill is active through this workspace's AGENTS.md. Cross-app automatic routing, global skill installation, external project write access, and complete project discovery have not been established.
