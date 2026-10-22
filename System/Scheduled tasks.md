# Scheduled tasks

Scheduled tasks are part of this vault's operating system. Preserve their purpose, instructions, source app, schedule, enabled state, target chat or project, and available run evidence.

## Locally verified Codex definitions

Inspected on 2026-10-22. Both definitions were already included in the initial system snapshot, and their automation cards were opened through the app's supported view action.

| Task | Saved schedule | Saved state | Definition |
| --- | --- | --- | --- |
| Weekly AI Job Search | Fridays at 9:00 AM | Active | [Archived task definition](Snapshots/2026-10-22T15-40-43-657205Z/Automations/weekly-ai-job-search/automation.toml) |
| Create scheduled news digest | Every day at 9:00 AM | Active | [Archived task definition](Snapshots/2026-10-22T15-40-43-657205Z/Automations/create-a-scheduled-task-to-find-news-along-a-few-axes-axis-1-politics-1-news/automation.toml) |

These saved files do not specify a timezone. The user's timezone is America/Chicago; the scheduler's interpretation has not been independently verified. Enabled state does not establish successful execution. Last run, next run, delivery, and target health were not available in the inspected definitions.

## Chat-OS maintenance

**Maintain chat-OS** is configured as an active hourly Codex heartbeat targeting this chat. It runs the sync command, inspects evidence, reconciles skills/snapshots, and stays quiet on unchanged state. Its prompt defers agent work when the five-hour window has 30 percent or less remaining. First scheduled execution is not yet verified.

The native five-minute launch agent was blocked by macOS privacy and disabled. Its definition is retained under System/State for diagnosis. No security/privacy setting was weakened.

## Source and refresh

Live definitions: `/Users/zayan/.codex/automations/*/automation.toml`.

The [snapshot script](Scripts/snapshot_codex_state.py) preserves saved Codex task definitions on each manual refresh. Use [[Latest snapshot]] for the newest archive. This inventory records the initial inspection; reconcile it when tasks change. Modify live tasks through the supported automation tools, then refresh their vault records. Editing archived definitions does not change scheduled execution.

## Cross-app coverage

The intended scope also includes ChatGPT scheduled tasks and scheduled agent work in other chat apps. These sources have not been inventoried or connected here. The two rows above describe local Codex files only and do not establish a complete cross-app task list.
