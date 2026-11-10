# Design history

## v1 — 2026-11-06 — Midnight workspace

- Source: Codex conversation `01a1b32b-dcb2-7823-bdb5-159c764aeb53`, user request: “make the design and UI of the entire app better; modern. create a style guide for yourself. maintain styleguides for future archival and just better provenance”.
- Authority: app-wide redesign and maintained guides explicitly requested; specific tokens, typography, layouts, and tooling are assistant implementation choices.
- Status: implemented; user review pending.
- Change: unify the dark architectural Home with all reading/management screens, introduce shared design tokens, improve text scale and hierarchy, restyle forms/navigation/overlays, and make the map renderer consume the same theme tokens.
- Behavior retained: source-preserving archive operations, clickable directive/source controls, Conversation pool opening clustering, and an inert ChatGPT center. No model execution or provider activation is added.
- Provenance: preserve the [observed earlier sources](archive/2026-11-06-pre-unification/README.md), then archive this guide, public sources, and [fictional-data evidence](evidence/v1/README.md) with SHA-256 hashes. No private data is an archive input.
