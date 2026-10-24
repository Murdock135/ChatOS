# Check source coverage

A successful sync means the accessible inputs were processed without import errors. It does not mean every conversation, reply, attachment or model detail has been captured.

From the repository, run:

```bash
./scripts/chatos --root workspace coverage --json
./scripts/chatos --root workspace doctor
```

`coverage` combines the current archive counts with the most recent source scan. It does not connect an account or scan new sources. `doctor` checks local integrity and reports coverage warnings separately.

## Read the counts

| Report field | Meaning |
| --- | --- |
| `records` | Distinct captured source conversation IDs; not the number of chats in the account |
| `capture_types` | How those records were obtained, such as retained visible messages, partial history projections or export snapshots |
| `visible_messages` | Retained user/assistant messages; tool payloads and private reasoning are excluded |
| `unavailable_rollout_files_last_scan` | Enumerated Codex files absent during the last scan; some have earlier retained captures or partial projections |
| `known_uncaptured_history_ids` | Enumerated Codex IDs absent from the archive for which the scan found neither a retained rollout nor a usable history projection |
| `unavailable_message_references` | Known ChatGPT replies returned as references without usable message text |
| `fork_records` / `inherited_messages` | Declared Codex fork relationships and messages explicitly marked as inherited from an observed ancestor |

No account-wide completeness percentage is calculated: the available tools do not establish a complete denominator. Model fields can also be missing; a record's thread-level model does not establish the model for every historical turn.

## Codex: retained files and partial history

The adapter reads local retained rollout files and observed thread metadata. If a rollout is absent, it can recover available user/assistant text from the supported local history projection, labeled `partial_history_projection`. It preserves earlier richer captures when the projection is smaller. A missing file is therefore different from an uncaptured conversation.

Fork files can contain their own header and inherited parent history. The importer accepts only the owning ID and explicitly declared ancestry, rejects unrelated IDs and conflicting/cyclic relationships, and retains the owning conversation's metadata. Inherited messages, model-history entries and run events carry `origin_conversation_id` and `inherited`; readable records and retrieval citations expose message origin. Shared history can appear in both parent and fork, so aggregate message counts are not counts of uniquely authored text.

An unavailable history stays unavailable when both the retained source and supported app read fail. Restore accessible source material or supply a supported export when available. A summary is not a replacement transcript.

## ChatGPT: exports and bounded desktop captures

Supported exports are snapshots of visible exported branches. The local import accepts JSON or a ZIP containing one `conversations.json`, with the documented 128 MiB payload limit. It does not download attachments or connect a live account. See [Getting started](getting-started.md).

Assistant-mediated desktop capture is explicitly partial. Recent/pinned listing limits, per-page and per-item caps, and unavailable reply bodies bound coverage. No next cursor means the tool returned no next page; it does not prove the complete original conversation was supplied. Stored cursors can expire, and a later read can expose fewer turns. Earlier captured messages and unresolved reply references are retained when that happens.

The normalizer checks the source ID on every supplied page. An unresolved reply reference is removed only when actual text for that same message ID becomes available. Archived-list results describe that tool's listing, not a proof of all historical account contents.

For broader history or missing replies, a supported user-provided export is the next ingestion path. New captures never turn reference markers into reply text or invent unavailable model information.

## Muse and remaining boundaries

Normalized Muse input has a limited adapter. General raw Muse export and ongoing capture remain deferred in the current installation. Enabling a source setting is not evidence that it is captured.

[Features and limits](features.md) explains capability scope. The configured installation's [current state](../workspace/STATE.md) and [source notes](../workspace/chief_of_staff/reference/Sync%20sources.md) record dated observations; those private records are absent from a fresh clone.
