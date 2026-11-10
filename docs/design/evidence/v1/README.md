# v1 interface evidence — 2026-11-06

Status: implemented and checked; user visual review pending. These artifacts document the Midnight workspace style guide, not a claim of user acceptance.

## Screenshot inventory

All screenshots use an independent fictional workspace with 18 authored conversations, fixed illustrative map coordinates, three captured context samples, and fictional Git/vault roots. No personal workspace records, account tokens, emails or real project files are included. Temporary filesystem paths visible in screenshots belong to that fictional fixture. Map geometry and labels are interface test data, not a clustering-quality result.

| Destination | Desktop | Phone |
| --- | --- | --- |
| Home | [1440 px](desktop-home.png) | [390 px](mobile-home.png) |
| Conversations | [1440 px](desktop-chats.png) | [390 px](mobile-chats.png) |
| Conversation map | [1440 px](desktop-map.png) | [390 px](mobile-map.png) |
| Skills & memory | [1440 px](desktop-context.png) | [390 px](mobile-context.png) |
| Health & sync | [1440 px](desktop-health.png) | [390 px](mobile-health.png) |
| Setup & handoff | [1440 px](desktop-setup.png) | [390 px](mobile-setup.png) |
| Settings | [1440 px](desktop-settings.png) | [390 px](mobile-settings.png) |

Additional inspected states: [conversation reader](desktop-reader.png), [search filters](desktop-search-filters.png), [expanded navigation](desktop-navigation.png), and [live directive dialog](desktop-directive-dialog.png). Screenshots show a viewport rather than claiming every scroll position is represented.

## Verification performed

- Astro check: 0 errors, 0 warnings, one existing `beforeunload.returnValue` deprecation hint. Frontend build/publish passed.
- `node --check frontend/public/app.js` and the existing Node browser regression passed, preserving navigation, Home count, search recovery, Settings/import controls and sync status behavior.
- Headless Chrome against the real Python server with the fictional workspace: all seven views loaded without script errors. At 1024, 768 and 390 px, each view had no horizontal document overflow (21 responsive checks). Desktop and phone screenshots were visually inspected, including reading, filter, context and setup surfaces.
- Interaction checks passed for reading a captured conversation, Escape dismissal, filters, expanded navigation, registry mouse/keyboard control, a live directive reader, repository file browsing, Conversation pool → map navigation, and map zoom/fit. The center remains a static ChatGPT visualization with no execution backend.
- A tablet-width intrinsic grid overflow, inherited light search-field fill, and inherited low-contrast headings/map metadata were found during inspection and corrected before the final screenshot set.
- New archival tool/tests passed Ruff lint and formatting checks and scoped BasedPyright. Two tests verify preserved source copies, private/hidden/data-file exclusion, refusal to overwrite an existing version, invalid-version rejection and tamper detection.
- Source diff whitespace checks passed for the edited frontend, guide and archival-tool files. The repository already contains unrelated uncommitted work; no commit or clean-working-tree claim is made.

## Contrast measurements

[Recorded token-pair measurements](contrast.json) use the standard sRGB relative-luminance contrast calculation:

| Pair | Ratio |
| --- | --- |
| Primary text / canvas | 16.38:1 |
| Secondary text / surface | 9.35:1 |
| Muted text / surface | 6.20:1 |
| Accent text / accent background | 7.44:1 |
| Map label text / label surface | 13.48:1 |

These are selected token-pair checks, not a complete accessibility audit. Native focus and reduced-motion rules are implemented; screen-reader behavior, every state and every possible source transcript were not exhaustively audited.

## Separate workspace inventory finding

The project-required `system_inventory.py --check` reported unresolved skill/snapshot/configuration drift, including older `chats` paths and changed plugin versions. That operating-workspace inventory is separate from this design archive and was not represented as current or repaired by the UI work. Its follow-up is retained in the private project record. The versioned design manifest has its own independent file-integrity check.

## Archival scope

The archive preserves this report, 18 screenshots, the contrast measurements, the active guide/change log, the relevant public frontend source tree, supplied branding, project design instructions and the archival tool/test. Hash verification proves retained file identity only. It does not imply complete app testing, authenticated Gmail coverage, provider-memory activation, or autonomous execution.
