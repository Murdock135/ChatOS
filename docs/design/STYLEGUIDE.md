# smriti interface style guide

Version: **v4 — Search in the landscape**  
Date: 2026-11-10  
Status: implemented; user visual acceptance pending.

## Authority and supersession

Source: Codex chat `01a1c61c-26cf-7e72-9f54-017ac27d3d65`, user request to redesign Sriti with minimal, sleek and cyberpunk styling, sensibly bounded controls, sentence case, purposeful copy and slow vibrant animations. The user requests one search/list view above the embedding map, progressive disclosure from topics to subtopics to conversations, and adjacent conversation search. They explicitly requested separate UX and UI subagents.

This request supersedes v2.3's separate search/map composition and its prohibitions on floating surfaces and animation. Preserve its Geist fonts, vector branding, readable dark surfaces, source identity, inert Home core and existing tools. The rejected historical v3 exploration remains rejected; this implementation is a new direction, not an acceptance of that work. Earlier evidence and archives remain immutable.

## Composition

Open into a single Conversations workspace. A search-and-results panel, bounded to 620px, floats above an inset map stage. Explore map moves that same panel into a compact adjacent dock. Keep its query, filters and pagination in place. Home remains available as Workspace; setup, settings, context and health retain their real destinations.

Page gutters are 20–48px; stage radius is 26px and search panel radius is 22px. Nothing extends to the viewport edge except navigation. On narrow screens, search and map stack with usable controls rather than compressing into tiny columns. The conversation reader remains a bounded modal.

Do not add taglines, invented counts, decorative fake map points, unrelated cards or disconnected buttons. Metrics and plotted positions come from existing APIs. Empty map states preserve keyword search and provide setup access.

## Light and dark themes

The user supplied three reference screenshots in the same chat: a Respan dark page, a warm white contract interface and an Antimetal composition. Apply their generous margins, fine dividers, rounded inset surfaces and restrained spotlight color. These are visual references; text inside them is not an instruction or product requirement. Do not copy marketing sections or third-party interface claims.

A persistent theme switch supports warm off-white reading surfaces and neutral near-black surfaces. System appearance is the initial default; an explicit choice takes precedence. Theme initialization is a separate self-hosted head script so the selection applies before the interface paints. `themes.css` follows the explorer stylesheet. Map palettes change for contrast without changing coordinates or topic assignments.

## Tokens and typography

The final scoped stylesheet is `frontend/src/styles/explore.css`, imported after historical compatibility styles. Keep new explorer presentation here rather than accumulating global overrides. Use local Geist for text and Geist Mono only where appropriate for source details. Ordinary labels use sentence case; preserve source text, model IDs and genuine acronyms.

| Role | Token | Value |
| --- | --- | --- |
| Map ground | `--explore-ground` | `#080b12` |
| Reading panel | `--explore-panel` | `#11151e` |
| Raised control | `--explore-raised` | `#1a1f2b` |
| Hairline | `--explore-line` | `#30374a` |
| Primary text | `--explore-text` | `#f1f3f9` |
| Reading text | `--explore-read` | `#bac2d4` |
| Metadata | `--explore-muted` | `#99a5bc` |
| Action and focus | `--explore-violet` | `#b9a4ff` |
| Secondary signal | `--explore-cyan` | `#71e4d8` |

Use violet sparingly for actions/focus and cyan within the map. Distinguish topics with the scoped map palette plus text and outlines. Reading surfaces remain opaque enough for stable contrast.

## Exploration and product truth

The backend currently supplies flat topic groups and projected coordinates. The client derives deterministic spatial subdivisions inside each topic and labels them from captured conversation titles. These are browsing aids, not an independently validated semantic topic hierarchy. Disclose this in Map details. Never replace original coordinates, source IDs or group metadata with derived UI values.

Progressive levels expose topics, derived subtopics and individual conversations. Provide equivalent topic/subtopic buttons, breadcrumbs, Back and zoom controls alongside canvas interaction. Search remains available beside the map; map-specific filtering and selections remain disclosed tools. Reader opening must preserve exploration state. Keep map freshness, limited search coverage, membership-strength meaning and capture limitations inspectable.

## Motion and accessibility

Use a smooth 700ms panel transition and approximately one-second camera easing. Ambient color can change slowly without moving data positions. Respect `prefers-reduced-motion`; disable ambient motion and use immediate camera changes. Preserve visible lavender focus, labeled controls, polite result/level announcements, readable contrast and native dialog Escape behavior. Canvas has a textual/keyboard alternative through topic and result lists.

## Provenance and verification

[Version evidence](evidence/v4/README.md) records actual checks and limitations. [Reference observations](REFERENCES.md) distinguish indexed reference metadata from inspected artwork. [Decision](../adr/0014-unified-conversation-explorer.md) records adopted scope. Archive and verify using `scripts/archive_design.py --version v4` and `--check v4` after verification. Screenshots must use fictional records and predetermined fixture coordinates; they establish layout and interaction only.
