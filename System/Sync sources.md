# Sync sources and runtime

## Confirmed scope

On 2026-10-22, Zayan confirmed using Muse and chose to run the chat-OS on the Mac for now. Earlier source scope includes Codex and ChatGPT.

| Source | Verified access | Sync readiness |
| --- | --- | --- |
| Codex | Local session files, thread metadata, saved automation definitions, and error logs | Some metadata/error collectors exist; visible-message ingestion works; supported hourly scheduling is configured but first-run verification is pending. |
| ChatGPT | No export or ongoing ingestion mechanism established in this workspace | Pending source-access verification. |
| Muse | Installed Mac application and readable live chat/library/activity interface | Programmatic export and incremental sync are unverified. |

## Muse identity

Verified from the installed application on 2026-10-22:

- App: `/Applications/Muse.app`
- Bundle identifier: `com.meta.endo`
- Version: `8.0`, build `1093405488`
- Live app surface: `muse.ai`, with chat, side chats, Library, and activity.
- No `muse` or `allume` command was found on the inspected shell PATH. The installed app's `Contents/MacOS` directory contains `Muse` and `EndoCrashpadHandler`; no bundled CLI helper was observed there.

Some older integration notes associate Muse with Allume. Do not use Allume's MCP/CLI documentation as evidence for this installed app. A similarly named product or Muse Code is not a verified integration for `com.meta.endo`.

## Runtime requirements

- The initial sync runner and stored archive will remain on this Mac. No always-on remote host is requested.
- Regular incremental synchronization is required; the proposed five-minute cadence has not yet been configured.
- Resume and reconcile after sleep, downtime, and failed scans using saved checkpoints; prevent overlapping runs and duplicate records.
- Keep sync health visible per source: last attempt, last success, checkpoint, pending work where measurable, and latest failure.
- Start with source-to-archive ingestion. Define deliberate publication rules before writing archived memory, skills, or instructions back into an app.
- Preserve the existing Obsidian-compatible files while the repository/VS Code interface remains under consideration.

An active hourly Codex maintenance heartbeat is configured; first scheduled execution is unverified. Native launchd sync was privacy-blocked and disabled. The next implementation milestone is incremental Codex conversation ingestion; Muse needs its own verified data-access path before automatic capture can be promised.
