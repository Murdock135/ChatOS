# Chief of Staff system

[Human orientation guide](../Humans/Start%20here.md)

[Current state](../STATE.md) — maintained by the Chief of Staff for human inspection.

- [Implementation roadmap](../IMPLEMENTATION.md) — operational requirements and delivery order.
- [Ideas](../ideas.md) — optional improvements and experiments.

- [Runtime reference](Runtime%20reference.md) — maintainer commands, storage, and recovery.
- [[Operating guidance]] — responsibilities, ownership, and runtime boundaries.
- [[Working memory]] — vault-owned durable notes requested by Zayan.
- [[Scheduled tasks]] — schedules, saved state, task instructions, and cross-app coverage.
- [[System logs]] — failures, evidence, recovery, and operational follow-up.
- [[Feedback log]] — negative user feedback, context, and resulting adjustments.
- [[Conversation metadata]] — model, source, timestamps, provenance, and model history.
- [[Sync sources]] — confirmed apps, local runtime, and integration readiness.
- [[Project routing]] — project owners, filing conventions, verified delivery, and pending items.
- [Project router skill](Skills/project-router/SKILL.md) — retrieve and file project context at the point of entry.
- [Current skills inventory](Skills/Index.md) — all configured skill roots, separated by scope.
- [Consistency audit](Audits/2026-10-22%20consistency%20audit.md) — identified gaps, repairs, and regression checks.
- [[Latest snapshot]] — archived skills, memory, instructions, rules, automations, and configuration inventory.
- [Snapshot script](Scripts/snapshot_codex_state.py) — manually refresh the system archive.

The vault's active entry point is its root `AGENTS.md`. Imported system files are reference snapshots. This vault does not yet replace the live Codex installation or provide automatic cross-app ingestion.
