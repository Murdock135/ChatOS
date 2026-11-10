# v2 — Modern Dark rendered evidence

Date: 2026-11-06. Status: implemented and verified at actual widths; user visual acceptance pending.

Authority: [the user's exact supplied specification](../../sources/modern-dark-v2.txt). [Source receipt](source-receipt.json) retains its SHA-256. [Font provenance](../../../../frontend/src/assets/fonts/README.md) records the pinned official Geist repository, unmodified binaries and license.

## Screens inspected

All screenshots use an independent fictional workspace with 18 authored conversations, fixed illustrative map coordinates, fictional source roots, and captured context samples. No personal conversation content, emails, credentials or workspace files appear. Temporary paths belong to that fictional fixture. Screenshot coverage is by viewport, not every scroll position.

| View | Desktop, 1440px | Phone, 390px |
| --- | --- | --- |
| Home | [Opening and architecture](desktop-home.png) | [Single-column opening](mobile-home.png) |
| Conversations | [Search and list](desktop-chats.png) | [Mobile list](mobile-chats.png) |
| Clustering | [Map](desktop-map.png) | [Mobile map](mobile-map.png) |
| Skills & memory | [Captured context](desktop-context.png) | [Stacked context](mobile-context.png) |
| Health & sync | [Status and coverage](desktop-health.png) | [Mobile health](mobile-health.png) |
| Setup & handoff | [Setup cards](desktop-setup.png) | [Mobile setup](mobile-setup.png) |
| Settings | [Settings](desktop-settings.png) | [Mobile settings](mobile-settings.png) |

Additional inspected states: [conversation reader](desktop-reader.png), [search filter menu](desktop-search-filters.png), [expanded navigation](desktop-navigation.png), [live directive dialog](desktop-directive-dialog.png).

## Validation

- Astro check: 0 errors/warnings; one existing `beforeunload.returnValue` deprecation hint. Build and publish succeeded.
- Existing Node startup/search/settings/sync regression and JavaScript syntax check passed.
- Scoped type checking for the asset server and archive tool passed. Archive-tool lint/format checks and two archive integrity/boundary tests passed.
- Three focused server tests passed: both local WOFF2 assets return correct MIME/signature, the published font license is available, missing/traversal paths remain rejected, existing compiled assets work, and token/host/origin access boundaries remain intact.
- Headless Chrome against the real Python server with a fictional workspace: all seven destinations loaded without script errors. Verified both local font aliases load. Checked each destination at 1180, 900, 768, 560 and 390px (35 responsive checks), with no horizontal document overflow. The 1440px screenshots and phone screenshots were visually inspected.
- Preserved interactions: conversation reader and Escape, filters, expanded navigation, keyboard-accessible registry/category toggles, live directive content, repository file browsing, Conversation pool → clustering, and map zoom/fit.
- Verified clicking the ChatGPT center produces no request. No execution backend was introduced.
- A separate read-only browser pass against the user's existing localhost:8765 app passed font/token activation, live file inspection, registry keyboard controls, clustering navigation and inert-center checks after restarting the same local server with font support. Existing browser authorization was retained.

## Selected contrast measurements

[Measurements](contrast.json) use the standard sRGB relative-luminance calculation:

| Pair | Ratio |
| --- | --- |
| Bright / ground | 18.21:1 |
| Reading text / panel | 8.18:1 |
| Metadata / panel | 5.79:1 |
| Inverse text / white primary action | 17.68:1 |

These are selected token-pair checks, not a complete accessibility audit. Focus/reduced-motion rules are implemented; screen-reader behavior and every possible imported transcript are not exhaustively audited.

## Provenance and limits

The v2 stylesheet is the final presentation authority and maps earlier component roles to the supplied `--dp-*` tokens. It preserves the stack, copy, routes and functional views. No example facts, photography, charts or new product sections were added. Existing branding remains recognizable. Earlier v1 and v1.1 archives still verify unchanged; they are not relabeled as current screenshots.

The separate operating-workspace inventory still reports previously logged path/plugin/configuration drift, with no snapshot-integrity errors. It is not represented as repaired by this design work. The new public design archive is independently verified. Existing unrelated working-tree edits remain; no clean-tree or commit claim is made.
