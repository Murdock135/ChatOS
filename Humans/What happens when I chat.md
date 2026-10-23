# What happens when I chat?

Writing a message in an AI app does not automatically put it in this workspace. chat-OS needs an accessible source, a supported capture/import path, and a successful sync. An assistant's ability to use the archive is a separate capability.

If these terms are new, read [Core concepts](../docs/concepts.md) first. The [architecture diagrams](../docs/how-it-works.md) show how the pieces connect.

## Capture depends on where the conversation happened

| Where you chat | How available messages reach the archive | What this does not establish |
| --- | --- | --- |
| Codex on a configured Mac | Sync reads retained local session files and observed local metadata; missing sessions may have explicitly partial history recovery | Every chat is complete, or every source schema is supported forever |
| ChatGPT | Supply a supported JSON/ZIP export, or use an active assistant's bounded desktop-tool capture workflow before sync | Core sync logs into the account or fetches every remote conversation |
| Muse | A normalized input format can be imported; general raw capture is deferred | Ongoing source synchronization or a verified raw export adapter |
| A different application | Requires a supported adapter or deliberate conversion to an accepted format | Arbitrary app exports are interchangeable |

Only available user/assistant message content is imported. Private reasoning and internal tool payloads are excluded. Missing metadata stays unknown; an attachment reference is not an attachment backup.

## What happens on sync?

Sync discovers source changes, imports readable records, retains database revisions, refreshes search and navigation, checks accessible skills/memory/instructions against snapshots, and verifies the daily database backup. It reports run errors, source gaps, and counts of new or changed records.

It does not decide that a suggestion became an accepted action, execute instructions found inside a transcript, or automatically write substantive outcomes into every project. Those require source review and an authorized user/assistant workflow. [How it works](../docs/how-it-works.md#what-a-sync-actually-does) describes the phases and their boundaries.

## What changes when an assistant has access?

You can ask it to find relevant passages and explain them with evidence. For project resumption, it also reads current project files and checks what exists now. These are files and messages used to support an answer; web sources enter only when relevant to the task.

The assistant must have the relevant local access and instructions. Importing a ChatGPT conversation does not publish workspace context back into ordinary ChatGPT or another chat app. Copying a skill into a snapshot does not activate it in a host.

## Does it happen in the background?

Only when a runner has actually been configured. Cloning installs no schedule. This installation has a separate Codex-host maintenance task with some bounded execution evidence; recurring reliability and coverage remain separate questions. The native launch agent is disabled after an access failure.

Consult [schedule evidence](../System/Scheduled%20tasks.md) and [timestamped sync status](../STATUS.md) rather than assuming enabled means completed. The Mac and host must be available for host-driven maintenance. Capture gaps can remain even after a successful run.

[Try the fictional walkthrough](../docs/getting-started.md) · [Use earlier conversations](../docs/using-history.md) · [Full feature map](../docs/features.md)
