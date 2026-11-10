# smriti interface style guide

Version: **v2.1 — Modern Dark, sentence case**  
Status: implemented and rendered-width verified; user review pending  
Date: 2026-11-06  
Authority: the user's supplied [Modern Dark specification](sources/modern-dark-v2.txt). Its authoritative tokens and design limits supersede the earlier Behance-informed graphite/mint palette. Earlier references and immutable archives remain historical evidence.

## Scope and product truth

Apply the visual system to the existing Astro/Tailwind frontend and Python-served application. Preserve copy, routes, source identity, data and existing behavior. This is a workspace, not a marketing landing page: do not add example charts, facts, photography, testimonials, metrics or new sections to satisfy illustrative patterns.

The ChatGPT core visualizes interfacing behavior and remains non-interactive. Other affordances retain real destinations: registry/categories expand, file rows read their sources, local mounts browse registered roots, and Conversation pool opens the clustering map. Workspace online does not claim a live model or provider connection.

## Authoritative sources

- [User specification](sources/modern-dark-v2.txt): retained verbatim from the supplied attachment.
- [Modern Dark CSS](../../frontend/src/styles/modern-dark.css): exact `--dp-*` tokens, locally hosted font aliases, current component styling, and responsive overrides. Imported last in the component layer.
- [Earlier compatibility styles](../../frontend/src/styles/design-system.css) and [tokens](../../frontend/src/styles/design-tokens.css): retain structural compatibility and prior design history. The v2 `--dp-*` roles override earlier presentation via mapped `--ds-*` roles.
- [Local font provenance and license](../../frontend/src/assets/fonts/README.md): upstream revision, asset URLs and SHA-256 identities. Original Geist binaries are unmodified.

When editing presentation, use the active `--dp-*` roles. Do not reintroduce the old mint-forward palette, colored glows, glass panels or heavy display type. New user instructions take precedence over the general Behance research convention; do not reinterpret an explicit design system through unrelated references.

## Identity and color

Near-black ground, opaque graphite surfaces, quiet grey reading text and bright white statements. Mint is a tiny live/selected signal with an accompanying label or state, not a general action or decorative color. Preserve the supplied recognizable smriti emblem/wordmark; do not recolor historical assets.

| Role | Authoritative token | Value |
| --- | --- | --- |
| Ground | `--dp-color-ground` | `#050505` |
| Panel | `--dp-color-panel` | `#0e0e0e` |
| Hairline | `--dp-color-hairline` | `#222222` |
| Stronger hairline | `--dp-color-hairline-2` | `#303030` |
| Bright statements/actions | `--dp-color-bright` | `#f2f2f2` |
| Reading text | `--dp-color-read` | `#a6a9ad` |
| Metadata | `--dp-color-meta` | `#8a8d91` |
| Live signal | `--dp-color-live` | `#3fd6c6` |
| Inverse action text | `--dp-color-inverse-ink` | `#0a0a0a` |
| Dim supporting text | `--dp-color-dim` | `#96999d` |

Ordinary reading areas remain flat. A static broad pool of white light may reveal the Home core; its material gradient is grey, opaque and non-animated. The map uses distinct greys, source/topic labels and explicit selected outlines; its coordinates, filtering and evidence are unchanged. Errors remain explicitly labeled and actionable rather than depending on a red fill.

## Capitalization

Use sentence case for app headings, navigation, buttons, badges, table headings, metadata labels and dialog kickers: “Autonomous agent hub”, “Control directives”, “Live directive”, “Local workspace”. Capitalize the first word and proper nouns; avoid all-caps labels and CSS `text-transform: uppercase` or automatic title casing. Do not use wide tracking as a substitute for hierarchy.

Keep the established spelling of smriti, ChatGPT, Gmail, Git and Obsidian. Preserve genuine technical acronyms such as API, JSON, PNG and SHA-256. Filenames, code, paths, model IDs and captured conversation text retain their source casing. The explicit user instruction to avoid uppercase UI words supersedes the earlier uppercase-label treatment; this is a sentence-case copy/style change, not a change to records or identifiers.

## Typography

Use **Geist** through `Modern Dark Grotesk` for display and reading, and **Geist Mono** through `Modern Dark Mono` for labels, dates, values, hashes and short notes. Both variable WOFF2 files are served locally; no runtime font CDN is used. The font license is included in source and published assets at `/geist-OFL.txt`.

Preserve the exact supplied stacks:

- `--dp-typography-face: "Modern Dark Grotesk", "Helvetica Neue", Arial, sans-serif`
- `--dp-typography-mono: "Modern Dark Mono", "SFMono-Regular", Menlo, monospace`

Display type is regular (400), tightly tracked, with leading near one. The existing Home opening scales from 44px to 92px inside the available workspace; it does not need to reach the illustrative 104px maximum. Existing app page/section headings are smaller, regular and precise. Reading is relaxed, with bright leading statements and readable grey supporting text. Do not reduce essential text opacity to create hierarchy. Canvas labels use the same regular Geist face.

## Layout, surfaces and motion

| Role | Token/value |
| --- | --- |
| Shared maximum | `--dp-spacing-max: 1360px` |
| Wide gutter | `--dp-spacing-gutter: 48px` |
| Gap | `--dp-spacing-gap: 24px` |
| Frame/panel radius | `--dp-radius-panel: 6px` |
| Button radius | `--dp-radius-pill: 999px` |
| Hairline width | `--dp-border-hairline: 1px` |
| Color transition | `--dp-motion-duration: 120ms` |
| Transition easing | `--dp-motion-ease: ease-out` |

Use a shared maximum and aligned column edges. Home's opening uses a twelve-column grid and left-aligned statement; retain its established registry/core/connections architecture beneath. Opaque panels use restrained hairlines. White filled primary actions and dark outlined secondary pill buttons are distinct from the 6px panel frames. Existing file/table rows remain functional rows rather than becoming decorative pills.

At 1180px, reduce gutters and allow the opening statement across the grid. Around 900px, simplify multi-column arrangements. At 560px, use a 20px gutter and single-column entries. Keep source order and all actions available; decorative elements must not cover text. Preserve wide-table containment and existing dialog scrolling.

Lighting is static. No pointer-following light, staged entrances, floating panels, decorative processing loops or animated charts. Brief control color changes use the supplied duration/easing; reduced-motion preference disables them.

## Components and accessibility

- **Navigation:** quiet grey rail, bright selected icon/label, tiny mint selected signal, accessible names and visible focus. Expanded navigation retains all destinations.
- **Home:** same copy, collapsible file registry and categories, live file readers, knowledge sources and tools. The central ChatGPT object has no click behavior or execution backend.
- **Search:** existing input, method selection, scope and disclosed filters. Selected controls have labeled state and small signals; mint does not fill controls.
- **Archive/readers:** exact captured text, clearly separated local annotations, source/model metadata and uncertainty. Reading areas are flat and neutral.
- **Context:** captured copies remain distinguishable from live directives. Source paths, read/capture times and hashes remain inspectable.
- **Map:** regular Geist labels, grayscale topic points, explicit selection, keyboard-accessible legend/results and unchanged data/export behavior.
- **Setup/settings/health:** retained copy and actions, regular headings, opaque panels, white primary buttons, readable structured details. No invented facts or app states.
- **Dialogs:** native modal semantics, visible close action, Escape, bounded scrolling, text-safe source content, meaningful account state. Existing authorization and source-access boundaries stay intact.

Buttons/forms/details/dialogs remain native and keyboard accessible. Use a visible offset white focus outline. Disabled controls remain recognizable and explicitly disabled. Do not remove focus to achieve a quieter aesthetic. Retain semantic labels, reading order and responsive behavior.

## Maintenance and archival contract

Before UI work, read this guide and [design provenance index](README.md). Follow the latest explicit user design source. For a materially new direction, update the guide, active stylesheet and [changelog](CHANGELOG.md), record rationale/authority and preserve superseded sources. Behance references can inform unspecified choices; they do not override authoritative supplied tokens.

Capture and inspect fictional-data screenshots at actual widths, including relevant open dialogs and selection states. Save evidence under a new version directory, never over a prior archive. Record tests and their limits. A token-only refinement without available visual capture must disclose that limitation and preserve earlier screenshots under their original version labels.

Create and verify a new immutable archive:

```bash
python3 scripts/archive_design.py --version v2 --source-ref 'codex:01a1b32b-dcb2-7823-bdb5-159c764aeb53' --summary 'Apply the supplied Modern Dark design system'
python3 scripts/archive_design.py --check v2
```

Archive public sources, exact supplied spec, local font provenance/license, guide, source-serving changes, screenshots and measurements. Exclude workspace data, credentials, runtime/provider logs and third-party inspiration artwork. Existing versions cannot be overwritten. Hash verification establishes retained file identity; it is not a complete accessibility audit or user acceptance.
