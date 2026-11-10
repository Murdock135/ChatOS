# Design history

## v2.2 — 2026-11-06 — Transparent vector branding

- Authority: user request to replace the image logo with a vector figure so it does not interfere with the background.
- Finding: the previous icon SVG embedded a PNG; expanded navigation used the PNG wordmark directly.
- Change: trace the supplied emblem and wordmark into path-only SVGs, use them in compact/expanded navigation, settings and favicon, and remove opaque/cropped logo containers. Preserve original artwork as historical source. No app runtime dependency is added.
- Verification: path-only XML/HTTP checks, alpha transparency checks, and desktop/mobile browser screenshots. Source/tracing provenance is retained in v2.2 evidence and a new immutable archive; earlier versions stay unchanged.

## v2.1 — 2026-11-06 — Sentence-case UI labels

- Authority: user instruction: “I don't like uppercase words. use capitalization instead in the UI, Much like Google's style”.
- Change: replace hardcoded uppercase UI strings, remove forced uppercase transforms, and normalize label tracking. Use sentence case for the Home title, core labels, badges, page breadcrumbs, table headings and dialog kickers.
- Boundaries: preserve proper nouns, acronyms, filenames, paths, code, model IDs and captured source records. No routes, actions or data change.
- Provenance: update the active guide and project instructions, record rendered checks in v2.1 evidence, and preserve earlier archives unchanged.

## v2 — 2026-11-06 — Supplied Modern Dark system

- Source: user attachment retained verbatim in [Modern Dark specification](sources/modern-dark-v2.txt); same Codex conversation.
- Authority: explicit user-supplied tokens, typefaces, components, design limits and responsive rules supersede earlier Behance-inspired color choices.
- Status: implemented and rendered-width verified; user visual acceptance pending.
- Change: near-black ground, opaque graphite surfaces, regular local Geist/Geist Mono, white primary pill controls, small mint status/selection marks, static white lighting, and grayscale topic presentation. Preserve existing copy, routes, data and behavior. No new sections or illustrative facts were added.
- Provenance: [font origin and license](../../frontend/src/assets/fonts/README.md), [v2 evidence](evidence/v2/README.md), [decision](../adr/0012-modern-dark-style.md), and independent immutable v2 archive. v1 and v1.1 remain unchanged.

## v1.1 — 2026-11-06 — Graphite & mint, informed by Behance

- Source: same Codex conversation, user instruction: “for designing, style and colors, go to behance and take inspiration from there”.
- Authority: Behance research explicitly requested; source selection and token adaptations are implementation choices. User visual acceptance remains pending.
- Direct visual evidence: inspected three public Behance project images. Full gallery access returned 403; indexed project descriptions were used only as metadata, not as a substitute for visual inspection. See [source observations](REFERENCES.md) and [image identity receipts](evidence/v1.1/reference-receipts.json).
- Change: graphite instead of blue-tinted general surfaces; softer mint primary states; lilac secondary identity; calmer map palette; subtle rounded-panel separation. Preserve the supplied branding, established dashboard arrangement, source contracts and all click destinations.
- Provenance: v1 remains immutable. New [v1.1 evidence](evidence/v1.1/README.md) distinguishes the selected palette from source image colors and records unavailable refreshed UI screenshots rather than reusing v1 images as new evidence.

## v1 — 2026-11-06 — Midnight workspace

- Source: Codex conversation `01a1b32b-dcb2-7823-bdb5-159c764aeb53`, user request: “make the design and UI of the entire app better; modern. create a style guide for yourself. maintain styleguides for future archival and just better provenance”.
- Authority: app-wide redesign and maintained guides explicitly requested; specific tokens, typography, layouts, and tooling are assistant implementation choices.
- Status: implemented; user review pending.
- Change: unify the dark architectural Home with all reading/management screens, introduce shared design tokens, improve text scale and hierarchy, restyle forms/navigation/overlays, and make the map renderer consume the same theme tokens.
- Behavior retained: source-preserving archive operations, clickable directive/source controls, Conversation pool opening clustering, and an inert ChatGPT center. No model execution or provider activation is added.
- Provenance: preserve the [observed earlier sources](archive/2026-11-06-pre-unification/README.md), then archive this guide, public sources, and [fictional-data evidence](evidence/v1/README.md) with SHA-256 hashes. No private data is an archive input.

## v2.3 — Modern Dark with color, 2026-11-06

User clarified that the supplied-guide implementation was liked except for monochrome color. Restored v2.2 Home, interaction code, navigation, type and geometry verbatim. Added a color-only stylesheet: lavender actions/selection/focus, semantic source colors and distinct map categories over the original near-black surfaces. Sentence case, vectors and inert core remain intact. The broader v3 exploration was rejected; its fictional screenshots are retained and explicitly labeled historical. ADR 0013 records the final decision.
