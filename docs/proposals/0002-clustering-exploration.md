# Rich clustering exploration

Date: 2026-10-24. Original status: future requirement, recorded only. Implementation was subsequently authorized for the October 25 overnight task; see the delivery note below.

Authority: Zayan requested, “for the clustering, i want the features you see in the image i attached. just note it for now”, in codex:01a16510-7f12-78b0-afa9-d5aee24d915b. The supplied screenshot is preserved privately at workspace/chief_of_staff/reference/Design references/2026-10-24-clustering-exploration.png; it is not distributed with the app.

## Requested experience

Use the screenshot as a reference for the conversation-clustering interface, alongside the existing Apple-inspired visual direction:

- A concept/search field above the map, filters, a content/source selector, visible result count, relevance sorting and a display/density control. The screenshot labels the latter “Balanced”; its exact behavior is not established by the image.
- An interactive two-dimensional scatter map with individually selectable items, distinct cluster colors and readable semantic topic names positioned over groups.
- A color-matched legend with cluster names and item counts, plus an expandable “more” control for additional clusters.
- Zoom and pan, fullscreen/expand, and visible layer/visibility controls. The screenshot shows these controls but does not establish what each layer or visibility option changes; confirm details when designing.
- Map download and result export affordances, distinguishing a visual export from the underlying selected records. Formats remain to be chosen.
- A result list accompanying the map, with cluster/category tags, titles, relevant metadata and short descriptions. For ChatOS, use conversations and their actual source/date/capture metadata rather than assuming a publications database.
- Let the user's existing assistant act as the clustering assistant: explain thematic directions and selected groups, compare relevant conversations, retrieve supporting passages and help refine exploration. Do not require a second assistant or side-by-side chat interface. Interpretations should be grounded in captured messages and disclose uncertainty.
- Provide an explicit handoff of the current exploration/selection to that assistant, rather than introducing a built-in chat service. The assistant should be able to retrieve the selected records and their evidence through ChatOS tools or a deliberate portable handoff.

The intended map, legend, explanation and results should work as a coordinated exploration surface. The screenshot alone does not prove specific click, hover, selection-linking or filtering behavior; define and verify those interactions during implementation rather than claiming they already exist.

## Scope and next design work

This records desired product behavior, not a choice of clustering algorithm, embedding model, external literature source or provider integration. Similarity remains a relevance suggestion, not proof of shared decisions or correct topic membership. Preserve provenance, original-record access, capture gaps and map freshness.

When resumed, compare these requirements with existing map capabilities; identify missing pieces and design their interactions before implementation. Retain useful existing controls. Evaluate meaningful cluster labels, topic quality and cross-view navigation with representative conversations; matching the screenshot's visual layout alone is insufficient.

## Clarification — use the user's existing assistant

Zayan clarified on October 24: “Don't need another side-by-side chat or assistant for that I think. Is there a way we can let the user's assistant use the information and act as the clustering-chat-ai ?” This supersedes the earlier screenshot-derived suggestion of a separate assistant pane.

Proposed connection: preserve an inspectable exploration snapshot or stable selection reference containing the query/filters, selected source-qualified conversation IDs, cluster labels/membership, generation time/method/freshness and cited evidence. The user's assistant reads that selection through the ChatOS skill and local commands, then responds in the user's existing chat. Authorized view changes could be passed back through explicit structured tool operations; historical text and assistant suggestions do not become approved edits automatically. Keep source records separate from exploration labels and view state.

Current basis: the bundled skill and CLI provide archive access, cited retrieval and explicitly selected portable bundles. A stable current-map/cluster selection handoff and tool operations for refining that exploration are future work, not shipped behavior. Local assistants need file/terminal access; a hosted assistant without that access needs a deliberately supplied bundle or another explicitly configured integration. Do not imply every assistant can access the browser's current state automatically. This clarification remains note-only.

## October 25 implementation

The overnight task in Codex chat `01a17120-0b72-7073-9847-ae25e24d509f` subsequently authorized implementation, local model downloads, derived-index rebuilds, local validation and scoped commits. The coordinated map/legend/results, content and semantic search, source/project/date filters, sorting, display controls, zoom/pan/expand, image/results exports and explicit existing-assistant selection handoff are implemented. See [the adopted design](../adr/0006-semantic-map-exploration.md) and [validation and limits](../verification/semantic-map-exploration.md).

The screenshot's ambiguous controls were defined as point-size presets, topic-label visibility and unclustered-item visibility. The map expands inside the app rather than requiring browser fullscreen. A local selection packet supports assistant explanation; a structured assistant-to-browser view-control protocol remains future work. These choices preserve the user's request to use their existing assistant without adding another chat pane.
