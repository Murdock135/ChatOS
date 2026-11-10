# smriti interface style guide

Version: **v1 — Midnight workspace**  
Status: implemented; user review pending  
Date: 2026-11-06  
Authority: the user requested a modern design across the entire app and maintained style guides for archival and provenance. Palette and component decisions are delegated implementation choices. The earlier supplied dark dashboard reference informs this version; the ChatGPT center remains non-interactive by explicit user instruction.

## Purpose and hierarchy

smriti is a local conversation and context workspace. Design for finding a discussion, reading its exact source, and inspecting what an assistant can use. Keep capture provenance, annotation ownership, account authorization and uncertainty visible. A visual state must represent an actual state: workspace connectivity does not mean a model is running or a provider account is connected.

Use a persistent quiet navigation rail, a consistent page heading and sync action, then one clear task area. The dashboard may use its architectural composition; reading and management screens use calmer surfaces and familiar controls. Do not introduce fake activity, decorative metrics, or actions on the central ChatGPT visualization.

## Source of truth

- [Design tokens](../../frontend/src/styles/design-tokens.css): named colors, typography, spacing, radii, shadows, and canvas palette.
- [Shared components and presentation](../../frontend/src/styles/design-system.css): app-wide appearance. It is imported after the older structural styles and is the presentation authority for v1.
- [Dashboard structure](../../frontend/src/components/Home.astro), [behavior](../../frontend/src/scripts/home.ts), and [architecture layout](../../frontend/src/styles/home.css).
- Existing component IDs, API contracts, source identity, and supported workflows remain stable.

When a component needs a new color or dimension, reuse a token first. Introduce a new token only when the role is distinct; document it here. Do not create another disconnected palette in a component or the canvas renderer. Legacy structural styles are retained for compatibility; migrate them only as part of a scoped component change.

## Color

| Role | Token | Value | Use |
| --- | --- | --- | --- |
| Canvas | `--ds-canvas` | `#0b0e14` | Main workspace background |
| Sidebar | `--ds-sidebar` | `#0e131c` | Persistent navigation |
| Surface | `--ds-surface` | `#121923` | Cards, file registry, panels |
| Raised | `--ds-raised` | `#182230` | Menus, selected controls, secondary surfaces |
| Hover | `--ds-hover` | `#1d2b3c` | Interactive surface hover |
| Primary text | `--ds-text` | `#e6edf6` | Titles, body, file names |
| Secondary | `--ds-secondary` | `#b0bed0` | Supporting content |
| Muted | `--ds-muted` | `#879bb4` | Metadata and explanations |
| Border | `--ds-border` | `#27364a` | Containment and separators |
| Accent | `--ds-accent` | `#6dcfff` | Primary actions, focus, navigation |
| Knowledge | `--ds-teal` | `#50ddc3` | Grounded source identity |
| Context | `--ds-purple` | `#c3a1fa` | Vaults and user-role identity |
| Warning | `--ds-warning` | `#edc17c` | Conditions requiring attention |
| Danger | `--ds-danger` | `#ff9cb0` | Failed requests or destructive choices |

Use color with text/icons/state attributes; it must not be the only distinction. Borders distinguish containment, while surface fill distinguishes elevation. Avoid a border around every fragment of text. Preserve the supplied white smriti emblem and lowercase wordmark. No remote fonts or decorative images are required.

## Typography and spacing

Use the system sans-serif stack; use the shared monospace stack for source paths, hashes, and structured records. Page headings are 24–30 px, dashboard hero 32–58 px, section headings 16–20 px, body/rows 13–15 px, metadata 11–12 px. Uppercase labels are short and tracked; ordinary sentences use sentence case. Reading text has 1.8 line height and a comfortable line length. Do not shrink substantive content to fit a card; wrap or change the layout.

Use the 4/8/12/16/24/32/48 px spacing scale. Default control height is 36–40 px; navigation and primary mobile actions target 44 px. Small controls need a clear focus state. Use radii 7 px for controls, 12 px for panels, and 18 px for search and larger compositions. Modest shadows belong to overlays and elevated search panels; avoid glowing every element.

## Components and behavior

- **Navigation:** 76 px rail on desktop, 240 px expanded navigation; 64 px mobile rail with an expanded overlay. Accessible names remain available when visible labels are hidden. Selected destinations have both a surface treatment and `aria-pressed`.
- **Page header:** consistent breadcrumb, heading/description where useful, and a compact Sync control. Sync state comes from the actual workflow.
- **Search:** one prominent input, persistent method controls, source/project scope, and progressively disclosed filters. Show loading, zero results, and recoverable errors explicitly. The conversation list preserves source and model uncertainty.
- **Lists and tables:** predictable columns and gentle separators; hover highlights the entire clickable row. Long names wrap or truncate with a full title available. Small screens simplify columns rather than compress text.
- **Reading:** an independent conversation drawer with exact captured messages, role/model metadata, source provenance, and clearly separated local annotations. Do not restyle source text as an accepted system instruction.
- **Directives:** a clickable registry header, independently expandable categories, searchable live file rows, and a source reader with path, read time and hash. Archived context is labeled as captured context, distinct from live files.
- **Map:** same coordinates, filtering, selection, labels and provenance. Canvas colors come from design tokens; labels use a high-contrast fill and readable text. Color carries topic identity, not correctness. Keep legend/results available for keyboard access.
- **Setup/settings:** contained cards, readable explanations, explicit primary actions, persistent labels, and progressive disclosure of advanced controls. Avoid large decorative branding that displaces controls.
- **Health:** scan-friendly status cards and tables; distinguish a successful run from source completeness. Do not hide warnings in a success color.
- **Dialogs:** native modal semantics, visible close action, Escape dismissal, text-safe file rendering, bounded scrolling, and clear account state. Mounting a source does not authorize a hosted assistant to access it.
- **Connections:** show actual available sources and real connection state. Gmail is disconnected until its explicit authorization succeeds. Never include OAuth tokens in screenshots, style archives, or logs.

## Interaction and accessibility

Keep the ChatGPT center inert. Every other visual affordance must have a working destination/action or clearly communicate disabled/unavailable state. Use native buttons, forms, details, and dialogs wherever possible. Visible focus uses the focus token and is not removed to satisfy aesthetics. Hover must not be the only cue. Respect `prefers-reduced-motion`; avoid continual motion that looks like live work. Keep touch and keyboard flows usable. Do not use `!important` as the default way to solve component conflicts.

At desktop widths use generous whitespace and restrained panel grouping. At tablet widths wrap the dashboard, setup cards, and context browser. At phone widths keep the navigation rail, stack cards, simplify conversation rows, and allow horizontal scrolling inside a wide data table rather than the document. Verify at 390, 768, 1024 and 1440+ px. Check native dialogs separately from full-page screenshots.

## Maintenance and archival contract

Before changing UI, read this guide and `docs/design/README.md`. For a material visual change:

1. Record the user request or design decision and whether it is explicit or an implementation choice.
2. Update this guide and the shared tokens/component rules together; increment the version for a changed design system.
3. Add a dated entry to [CHANGELOG](CHANGELOG.md). Record supersession rather than rewriting old decisions.
4. Capture screenshots using fictional data in `docs/design/evidence/<version>/`; inspect them and record the checks in a README. Never put private workspace data into the public design archive.
5. After checks pass, create a new immutable snapshot with `python3 scripts/archive_design.py --version <version> --source-ref <source> --summary '<change>'`. Existing versions cannot be overwritten.
6. Verify it with `python3 scripts/archive_design.py --check <version>` and record the result. The archive manifest includes source hashes, working-tree Git provenance, authority and capture time; it does not imply user acceptance or complete test coverage.

Minor changes within this system can retain v1, with a dated changelog and verification record. Use a unique patch snapshot such as `v1.1` when new archival evidence is needed. Do not silently overwrite old archives. Do not update the user's external memory files as part of this workflow.
