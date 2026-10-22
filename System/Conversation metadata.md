# Conversation metadata

Every archived conversation should carry metadata in its YAML properties and a structured sidecar when source detail is available. Record observed values and their evidence; use `null` for unavailable values. A model name from global configuration is not evidence of the model used in a particular conversation.

## Required properties

- `source_app`, `source_id`, and `source_url` when available.
- `created_at`, `last_activity_at`, `metadata_checked_at`, and the source timestamps' timezone/offset. Use ISO 8601; retain UTC in structured records. Display dates in America/Chicago when presenting them to Zayan.
- `model`, `model_provider`, and `reasoning_effort`, based on conversation or turn records. Identify the internal model ID as such; do not invent a UI display name or infer the user's manual selection from execution records.
- `capture`: full, partial, or summary. A metadata-only refresh does not improve transcript completeness.
- Topic links and related project/workspace when known.
- A link to metadata evidence and model history where available.

## Additional evidence when available

Preserve turn IDs, per-turn models and effort, client/version, source export path, scheduled-task association, parent/fork relationships, attachments, tool use, outcomes, and incident/feedback references. Add these as evidence is captured; do not infer missing relationships or mark a task successful from an enabled schedule.

Usage counters and cost are optional. Store only validated usage with its scope and source; do not confuse local counters with account-wide billing, or estimate a monetary cost without verified pricing and usage.

## Model changes

The main `model` property describes the latest observed conversational turn, with database fallback if no turn metadata is available. The JSON sidecar keeps all observed per-turn model and effort values. Keep reviewer or subagent models associated with their own IDs, separate from the user-facing conversation.

## Local Codex extraction

Use the verified conversation ID, never just the most recently updated chat in a directory:

```bash
python3 System/Scripts/conversation_metadata.py --thread-id CONVERSATION_ID --note 'Conversations/YYYY/Conversation title.md'
```

The extractor reads local state and only metadata-bearing session events. It writes YAML properties and a `.metadata.json` sidecar next to the existing conversation note, retaining other properties and note content. It does not import transcripts, change source files, or establish automatic capture. Refresh when working on or importing a conversation. For other apps, use the same fields with provenance from their exports or supported APIs; unavailable model details remain unknown.
