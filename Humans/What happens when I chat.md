# What happens when I chat?

The repository is a local archive and working context for your Chief of Staff. Capture and assistant behavior are separate capabilities.

| Where you chat | What reaches this repository | What the assistant can use |
| --- | --- | --- |
| This Codex workspace | Retained visible messages are imported on the next successful sync, with observed model metadata. | Workspace instructions invoke routing, briefing, and archive retrieval. |
| Another Codex project on this Mac | Retained local conversation files are eligible for the same importer. | A global Chief of Staff reference now directs substantive project work to the shared router. The destination's own instructions and permissions still apply. |
| Ordinary ChatGPT | The first 31 recent/pinned chats have partial supported-tool capture. Hourly agent refresh is configured but unverified; missing replies and models require fuller exports. | Ordinary ChatGPT does not automatically read this local repository or receive its memory, skills, or search results. |
| Muse | Export capture is unfinished and explicitly deferred until you resume it. | No verified ongoing context or skill synchronization into Muse is installed. |

## Timing

The supported hourly Codex maintenance task is configured. Its first unattended successful execution still needs verification. Manual sync through Codex has succeeded. The Mac and app must be available; this is not an always-on remote service.

A sync imports source changes, collects runtime errors, refreshes the current schedule inventory, verifies skills/memory/instructions and snapshots changed behavior files, updates search/navigation, and verifies the daily database backup. It records its attempt and source coverage. See [timestamped status](../STATUS.md), not just the presence of files.

Project filing is an agent workflow. Reviewed project assignments survive later imports. Verified context-index deliveries are recorded separately; imported conversations do not automatically become accepted decisions or tasks.

## What you can ask

- “What did we decide about running this on my Mac?” The assistant retrieves evidence and answers with sources.
- “Resume the evidence-combination project.” It reads that project's current files and relevant captured history.
- “This conversation belongs to a different project.” It corrects the reviewed ownership and verifies any resulting filing.
- “What failed, and what remains unresolved?” It checks curated logs and current source health.

## Navigation

[Current state](../STATE.md) · [Conversation map](explorer.html) · [Dashboard](dashboard.html) · [Schedules](../System/Schedules/Index.md) · [Recorded decisions](../System/Decisions.md)

The map has an optional pretrained embedding/HDBSCAN/UMAP experiment, with a dated input snapshot and visible limitations. Cited passage retrieval uses local full-text ranking. The embedding experiment has not improved the first seven-question retrieval diagnostic and remains optional. The assistant generates grounded answers from the retrieved evidence; the retrieval command itself does not call an external model.
