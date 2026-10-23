# Features and limits

This is a map of the current implementation, not a list of promises for a future public app. “Implemented” means the mechanism exists; source coverage and installation setup can still be limited. Verification scope and fresh-checkout results are recorded in [verification](verification.md).

## Capture and preserve conversations

| Capability | How you use it | Status and limits | Implementation |
| --- | --- | --- | --- |
| Import local Codex history | `sync` on a configured source folder | Implemented. Reads retained session files and observed local metadata; missing files may have explicitly partial history-cache recovery. Local schema compatibility matters. | [Adapters](../chatos/importers.py), [runner](../chatos/runtime.py) |
| Import ChatGPT exports | Import chats in the app, or supply JSON/ZIP in `System/Imports/chatgpt/`, then `sync` | Implemented for supported formats, including exported branch relationships. Export snapshots are not live account sync. JSON payload size is bounded to 128 MiB. The app also bounds the uploaded file to 128 MiB and validates before publishing. Known older source update times cannot supersede a newer exported snapshot. | [Export parser](../chatos/importers.py), [export tests](../tests/test_exports.py) |
| Capture available desktop ChatGPT messages | Active assistant uses supported desktop tools and the capture procedure | Agent-assisted. Normalizer preserves available text and marks unavailable reply bodies; neither complete history nor a source subscription. Cloning does not connect the host tools. | [Normalizer](../chatos/desktop_capture.py), [capture skill](../System/Skills/desktop-chat-capture/SKILL.md) |
| Import normalized Muse records | Supply supported normalized input | Limited adapter exists. General raw Muse export and ongoing capture are deferred. | [Importer](../chatos/importers.py) |
| Preserve readable records and revisions | Open `Conversations/YYYY/`; inspect stored metadata | Implemented. Source+ID identity prevents duplicate chats; changed database records retain prior versions. Not every possible source schema or attachment is covered. | [Store](../chatos/core.py), [import tests](../tests/test_chatos.py) |

## Find and organize chats

| Capability | How you use it | Status and limits | Implementation |
| --- | --- | --- | --- |
| Browse a chat library | `serve --open`, generated indexes, or `Humans/dashboard.html` | Dedicated local app with transcript/annotation search, source/project filters, pagination, and transcript reader. Older static dashboard searches previews only. | [Library guide](chat-library.md), [server](../chatos/web.py) |
| Annotate and archive locally | Open Local title, notes & project, or use `library` | Local title/note and reversible archive state are separate from source messages. Annotations participate in cited retrieval and database backup/restore. Archiving does not exclude evidence/map results. | [Annotations](../chatos/library.py), [operation tests](../tests/test_web.py) |
| Search transcript text | `search "query"` | Implemented local full-text search with snippets. Lexical matching can miss paraphrases. | [Search](../chatos/core.py) |
| Retrieve cited passages | `retrieve "query"`, optionally `--project ID` | Implemented. Returns excerpts with speaker, IDs, offsets, and source links; it does not produce a model answer. Indexed material is captured conversations plus selected workspace notes. | [Retrieval](../chatos/retrieval.py), [citation tests](../tests/test_retrieval.py) |
| Associate chats with projects | Workspace matching or `assign SOURCE ID PROJECT_ID --reason "evidence"` | Implemented. Reviewed assignments survive reimport. Title matches remain candidates; a project match is not a task or decision. | [Ownership](../chatos/core.py), [assignment](../chatos/routing.py) |
| Explore related chats on a map | Conversation map in the app or generated `Humans/explorer.html` | Experimental. Local term-based and optional pretrained representations exist. Similarity is not agreement or ownership; maps can be stale and some chats unclustered. | [Explorer](../chatos/explorer.py), [pretrained map](../chatos/dense_map.py) |
| Use optional semantic ranking | `search --semantic` or configured `retrieve --hybrid` | Experimental. These are different backends: term-co-occurrence ranking versus local pretrained hybrid retrieval. The latter requires dependencies, pinned model files, and current vectors. Core sync does not build them. | [Term model](../chatos/semantic.py), [hybrid retrieval](../chatos/dense.py) |

## Use the archive with an assistant

| Capability | How you use it | Status and limits | Implementation |
| --- | --- | --- | --- |
| Explain earlier choices with evidence | Ask an active assistant to review retrieved passages and later changes | Agent-assisted. A proposal, explicit user instruction, and completed action require different evidence. No general automatic decision extractor exists. | [Retrieval procedure](../System/Skills/archive-retrieval/SKILL.md) |
| Resume a project | Ask for a briefing using current project files and captured history | Agent-assisted. `brief ID` itself only displays a generated conversation index. Source/file access and interpretation are still needed. | [Briefing procedure](../System/Skills/project-briefing/SKILL.md) |
| File conversation context into project folders | `file-projects` after verified ownership | Implemented narrow delivery of managed context indexes. It writes externally and currently has personal path restrictions. Richer filing of decisions/tasks is an assistant workflow. | [Delivery](../chatos/routing.py), [routing procedure](../System/Skills/project-router/SKILL.md) |
| Inspect skills, memory, and instructions | Skills & memory in the app, skills inventory, or dated behavior snapshots | Implemented for accessible configured roots. A discovered file is not proof of host activation; archived copies do not update live installed resources. | [Inventory](../System/Scripts/system_inventory.py), [snapshots](../System/Scripts/snapshot_codex_state.py) |

## Inspect operations and recover

| Capability | How you use it | Status and limits | Implementation |
| --- | --- | --- | --- |
| See run health and changes | `status`, `doctor`, sync reports; `--json` for structured output | Implemented. Separate new/updated chat counts and behavior-file counts; missing coverage remains visible even when core checks pass. | [Reports](../chatos/terminal.py), [counts](../chatos/changes.py), [doctor](../chatos/recovery.py) |
| Back up and restore conversations | Back up now in the app; sync verifies the daily backup; `restore BACKUP NEW_DIRECTORY` | Implemented and fixture-tested. New destination required. Database restoration does not restore the entire app, all original sources, skills, or attachments. Current backups are local. | [Backup](../chatos/runtime.py), [recovery](../chatos/recovery.py) |
| Inspect schedules and runtime errors | Generated schedule inventory and curated event log | Implemented for accessible local Codex evidence. Collectors do not trigger tasks. Error logs or timestamps alone cannot establish a whole task's outcome. | [Schedules](../chatos/schedules.py), [error collector](../System/Scripts/system_log.py) |
| Review possible negative feedback | `feedback`, then explicit classification with `review-feedback` | Phrase-cue queue and persistent review state implemented. Human/agent interpretation is required; it is not comprehensive sentiment analysis. | [Feedback](../chatos/feedback.py) |
| Run maintenance periodically | Configure a host automation separately | Deployment-specific. The current Codex heartbeat has bounded execution evidence; it is not installed by cloning. Native launchd code exists but was disabled on this installation. | [Schedule record](../System/Scheduled%20tasks.md), [native scheduler](../chatos/scheduler.py) |

## Future requirements, not current features

- A public onboarding/initialization flow independent of the maintainer's configuration.
- Public packaging and new-user verification of the implemented local browser interface.
- Migration of selected chats and useful context into another chat application.
- Wider verified source coverage and improved semantic discovery, evaluated on actual use cases.

Deletion, renaming, sending replies, and synchronizing labels back into every source application are not implemented here. The local HTTP API serves the browser app; no generic assistant API/MCP server or built-in AI reply service is shipped. See [product choices still open](product.md#what-must-be-resolved-before-a-public-release) and the [roadmap](../IMPLEMENTATION.md).
