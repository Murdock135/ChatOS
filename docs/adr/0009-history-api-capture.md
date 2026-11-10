# 0009: Opt-in API history capture with retained local evidence

Status: adopted, 2026-10-28.

Codex's partial direct database projection can omit persisted turns. ChatGPT desktop capture can omit reply bodies, and repeated manual account exports are cumbersome. Add the official local Codex app-server history API and an explicit wrapper around a user-supplied chatgpt-history checkout. Keep manual JSON/ZIP imports and retained local Codex sources available.

Use separate capture commands to stage snapshots, then import them through ordinary sync. An opt-in workspace setting permits incremental Codex API reads within sync. Request full turn items, exhaust pagination, enumerate active/archived non-subagent sources, and publish a snapshot only after all of its history pages succeed. Capture failures are reported and keep previous snapshots. Do not start/resume chats or execute server-initiated actions.

Normalize only visible messages and supported metadata. Reconcile Codex source IDs/text in order, retaining unmatched evidence and disclosing uncertain order. Do not equate thread-level model metadata with historical per-message evidence. Retain ChatGPT branches and active-node membership. Authentication belongs in an explicit private local file; normal sync does not extract browser credentials or authenticate to ChatGPT. No new schedule is created.

chatgpt-history is an optional external dependency, reviewed at commit `b2683b4043523115258ed293f1136cf019e00e0b`, rather than a core package dependency. Its private API and discovery/media gaps remain limitations. Its completion summary must be checked because individual failures can accompany exit code zero.

Validation and actual capture outcomes are recorded separately from these design choices. See [capture workflow and limits](../history-capture.md).
