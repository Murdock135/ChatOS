# 0006 — Source-grounded semantic map exploration

Date: 2026-10-25. Status: implemented, awaiting user feedback.

The October 25 scheduled task authorized implementing the saved clustering exploration proposal. Earlier maps searched only titles, showed unlabeled points and plain title lists, and offered no coordinated selection handoff. Inspection of the actual archive also found imported browser-context and filesystem terms dominating some derived topic labels.

Use a concept search over captured content, explicit optional local semantic retrieval, a labeled map with a color-matched topic legend, coordinated conversation results, and explicit selection. Keep IDs internal to navigation and exports; the reader continues to hide them. Source/project/date filters and topic selection affect both views. The density presets change point radius; visibility controls toggle topic labels or unclustered records. Zoom/pan and an expanded view affect presentation, not clustering membership.

For pretrained maps, encode a title and up to twelve evenly spaced user-text samples using the configured local model. Remove recognized capture wrappers and filesystem paths from derived topic inputs; retain original records and exact source citations. Bound each sample and report fallback/coverage. HDBSCAN still clusters original cosine distances and UMAP provides geometry only. Use corpus-weighted distinctive source phrases for labels; they remain reviewable suggestions.

The explicit assistant handoff saves a validated, source-qualified selection with evidence and freshness into local state, then displays a copyable request and downloadable JSON. No built-in assistant, automatic upload or provider integration is added. Query mode, archive state and map generation are validated or disclosed; requests from a replaced map generation are rejected. A draft query does not replace the applied query in exported selection metadata.

Map image export is PNG; selected/visible results and assistant selections export JSON. Full transcripts use the existing portable bundle workflow. Rebuilding a semantic map is an explicit authenticated operation protected by the maintenance lock. Ordinary sync keeps saved pretrained maps and reports staleness.

Semantic search candidates are bounded and require separate passage indexing; clustering samples can miss topics, labels are English source phrases, and 2D geometry can distort relationships. No general quality guarantee or assistant-driven browser-control protocol is claimed. See [verification](../verification/semantic-map-exploration.md).
