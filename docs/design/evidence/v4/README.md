# v4 — Search in the landscape

Date: 2026-11-10. Implemented; user visual acceptance pending.

## Source and scope

Codex chat `01a1c61c-26cf-7e72-9f54-017ac27d3d65`: user specified minimal/sleek cyberpunk styling, bounded search/content, sentence case, purposeful text, slow vibrant motion, unified search/list foreground over an embedding map, progressive topic/subtopic/conversation disclosure and adjacent chat search. Separate UX and UI agents were explicitly requested. Subsequent user screenshots and Aether reference inform warm white and quiet dark themes; their embedded text is reference content, not instructions.

Search opens above an inset real-data map and moves to a compact adjacent panel for exploration. Topic/derived-subtopic navigation has breadcrumbs, Back, zoom and keyboard alternatives. Reader opening preserves exploration; map failures preserve keyword search. A persistent theme switch follows system appearance until explicitly changed. Existing tools/Home remain available. Prior v2.3/v3 evidence is historical and unchanged.

## Verification

- Astro check: zero errors/warnings, one existing deprecated `returnValue` hint. Frontend build passes and publishes bundled Python-served assets.
- Node startup/integration regression passes, including unified visibility/query persistence, derived navigation and original source-coordinate preservation. Theme tests cover stored preference, accessible toggle state and blocked storage.
- Design archive tests: immutable creation/exclusions/tamper checks pass. Python syntax compilation passes with a temporary cache prefix.
- Headless Chrome fictional-data checks: bounded center and adjacent panel geometry; topic → subtopic → conversation navigation; Back; point preview; reader Escape without leaving exploration; keyword recovery after model failure; empty-map search; persistent light theme after reload; no page errors.
- Ten responsive states across1180,900,768,560,390px check page overflow, panel/list widths, compact map controls and mobile search/map order. Both theme variants are captured on desktop and phone. Desktop captures use settled viewport screenshots with animations disabled: full-page screenshot viewport resizing previously produced misleading transition frames and those captures were replaced.
- Screenshots are actually inspected. See browser-checks.json for fixture measurements. No full accessibility/assistive-technology audit is claimed.

Screenshots use108 fictional conversations and predetermined projection coordinates. They establish interface behavior, not embedding quality, real-account completeness or validated semantic labels. Subtopics are deterministic spatial subdivisions labeled from captured titles, explicitly disclosed in Map details. No private workspace record, export, credential, external reference artwork or live model call is part of this evidence.

## Reproduce

Build the frontend, then run `node --test tests/browser_startup.test.cjs tests/theme.test.cjs`. The optional browser fixture uses an installed `playwright-core` and Chrome: `CHATOS_PLAYWRIGHT_PATH=/path/to/playwright-core CHATOS_CHROME_PATH=/path/to/chrome node tests/explorer-browser.cjs`. It serves only built public files on temporary loopback and intercepts every API request with fictional fixtures.
