# 0014: Unify conversation search and embedding exploration

Date: 2026-11-10. Status: adopted implementation; user visual acceptance pending.

Authority: Codex chat `01a1c61c-26cf-7e72-9f54-017ac27d3d65`. The user requested minimal/sleek cyberpunk styling, bounded layouts, sentence case, purposeful text, slow vibrant motion, and a single search/list foreground over a progressively disclosed embedding map with adjacent conversation search. UX and UI implementation were assigned separately at the user's request.

Replace separate primary Conversations and Conversation map destinations with one Conversations explorer. Search mode centers a bounded reading panel above the map; map mode moves the same panel aside. Preserve queries, filters, pagination, source IDs, original projected coordinates and reader behavior. Keep the prior Home dashboard accessible as Workspace and retain its inert visualization.

The existing map API has flat groups. Derive deterministic spatial subdivisions in the browser, name them from source titles, and disclose that these are provisional browsing aids. No backend clustering-quality improvement or validated semantic hierarchy is claimed. Map/model failures must not block ordinary keyword search.

This supersedes the separate-view composition in 0013 and v2.3 where inconsistent with the new request. It does not retroactively approve the rejected historical v3 exploration. Retain prior archives unchanged; capture new fictional-data evidence and an immutable v4 source snapshot. See `docs/design/STYLEGUIDE.md` and `docs/design/evidence/v4/README.md` for implementation and validation limits.
