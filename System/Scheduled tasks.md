# Scheduled tasks

Scheduled tasks are part of this vault's operating system. Preserve their purpose, instructions, source app, schedule, enabled state, target chat or project, and available run evidence.

**Current generated view:** [Codex schedules](Schedules/Index.md) reads saved definitions and host-reported timing/run metadata on each sync. The original inspection below is historical.

## Locally verified Codex definitions

Inspected on 2026-10-22. Both definitions were already included in the initial system snapshot, and their automation cards were opened through the app's supported view action.

| Task | Saved schedule | Saved state | Definition |
| --- | --- | --- | --- |
| Weekly AI Job Search | Fridays at 9:00 AM | Active | [Archived task definition](Snapshots/2026-10-22T15-40-43-657205Z/Automations/weekly-ai-job-search/automation.toml) |
| Create scheduled news digest | Every day at 9:00 AM | Active | [Archived task definition](Snapshots/2026-10-22T15-40-43-657205Z/Automations/create-a-scheduled-task-to-find-news-along-a-few-axes-axis-1-politics-1-news/automation.toml) |

These saved files do not specify a timezone. The user's timezone is America/Chicago; the scheduler's interpretation has not been independently verified. Enabled state does not establish successful execution. Last run, next run, delivery, and target health were not available in the inspected definitions.

## Chat-OS maintenance

**Maintain chat-OS** is configured as an active hourly Codex heartbeat targeting this chat. It runs the sync command, inspects evidence, reconciles skills/snapshots, and stays quiet on unchanged state. Its prompt defers agent work when the five-hour window has 30 percent or less remaining. The first triggered core sync and a later bounded desktop refresh have been verified; see the dated evidence below.

The native five-minute launch agent was blocked by macOS privacy and disabled. Its definition is retained under System/State for diagnosis. No security/privacy setting was weakened.

## Source and refresh

Live definitions: `/Users/zayan/.codex/automations/*/automation.toml`.

The [snapshot script](Scripts/snapshot_codex_state.py) preserves saved Codex task definitions when ordinary sync detects changed behavior files. Use [[Latest snapshot]] for the newest archive. This inventory records the initial inspection; reconcile it when tasks change. Modify live tasks through the supported automation tools, then refresh their vault records. Editing archived definitions does not change scheduled execution.

## Cross-app coverage

The intended scope also includes ChatGPT scheduled tasks and scheduled agent work in other chat apps. These sources have not been inventoried or connected here. The two rows above describe local Codex files only and do not establish a complete cross-app task list.

## 2026-10-22 — Maintenance update and target failure

The hourly maintenance prompt now includes bounded ChatGPT desktop refresh, usage checks between phases, and explicit Muse deferral. Optional embedding builds are not automatic. At this historical update its first unattended result remained unverified; later evidence follows.

The daily news digest target (01a10c46-e763-76b2-826c-b1a68da0f92f) returned a missing-source-rollout history error through read_thread. No fallback visible-history rows were available for that ID. This is a verified history/target access problem; delivery/execution remains unknown. The incident is recorded in the event ledger. No replacement target was invented.

## 2026-10-22 — First triggered core sync

The maintain-chat-os heartbeat arrived at 18:30:09 UTC. With 32 percent of the five-hour allowance remaining, the agent ran only the bounded core sync. run_sync.py exited 0; run 12 completed at 18:30:23 UTC with status ok. This verifies this triggered core phase, not full source capture, desktop refresh, or recurring reliability. Existing partial-history and deferred Muse coverage remain unchanged.

## 2026-10-22 — Bounded desktop refresh verified

At 11:19 PM America/Chicago, heartbeat maintenance read two changed ChatGPT chats through supported tools and refreshed the partial inbox. Run 33 exited 0: 254 total conversations, 32 partial ChatGPT captures, no parse errors. The capture contains 90 available messages and 38 unavailable message-body references. No remaining changed listed chats were pending. A subsequent doctor check detected a live memory file disappearing after snapshot verification; reconciliation was required. This is execution evidence for this bounded refresh only, not full history coverage or a guarantee of recurring execution.

## 2026-10-23 — One-time development continuation

User requested a 4:16 AM allowance check and continuation after going to sleep. Created and reopened the active heartbeat **Resume chatOS after allowance refresh** (`resume-chatos-after-allowance-refresh`), targeting codex:01a16510-7f12-78b0-afa9-d5aee24d915b, with a single scheduled occurrence at 4:16 AM October 23 in the local America/Chicago context. The saved definition and prompt were read back. The account's 300-minute reset was reported as October 23 4:15:36 AM CDT.

It checks actual allowance before resuming unfinished essential development, preserves the later public-setup requirements, and stays quiet on unchanged/non-actionable state. This explicit development run may use the available allowance; it does not alter the separate Maintain chat-OS reserve. No future execution or successful refresh is claimed. Local file work needs the Mac and app running.

Execution evidence, 2026-10-23: this heartbeat arrived at 09:16:10.976Z (4:16:10 AM America/Chicago). The live account check reported 1 percent used in the 300-minute window, next reset 9:16:15 AM local, and 32 percent used in the weekly window. No reset credit was used. The assistant resumed work with the user's newer structure-design and README-checklist instructions taking precedence. This confirms this single scheduled wakeup and allowance check; general-user initialization is still planned.
