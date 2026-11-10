# v2.1 — Sentence-case UI refinement

Date: 2026-11-06. Authority: the user's explicit preference against uppercase UI words, asking for capitalization similar to Google's style. Implemented as sentence case rather than automatic title casing. No claim is made that an external Google design specification was imported.

Changes cover hardcoded uppercase labels and CSS transforms: page breadcrumbs, Home title, central visualization labels, connection badges, registry categories, dialog kickers, settings metadata and table headings. Tracking is normalized for these labels. Proper nouns, acronyms, filenames, paths, source code, model IDs and captured conversation text retain their original casing.

## Rendered evidence

[Desktop Home](desktop-home.png) · [Phone Home](mobile-home.png) · [Directive reader](desktop-directive.png) · [Conversation headings](desktop-conversations.png)

Screenshots use the existing independent fictional fixture, not private workspace data. Desktop (1440px) and phone (390px) screenshots were visually inspected. The browser checked actual computed `text-transform` values, dynamic connection badges, dialog labels, Home heading, ChatGPT spelling, exact AGENTS.md filename preservation, conversation-column headings and health-table headings. No phone document overflow or script errors occurred.

Astro check/build and the existing Node browser regression passed. One existing beforeunload deprecation hint remains. This is a focused copy/style refinement, not another full accessibility or seven-screen responsive audit. Previous v2 evidence remains under its original version. No workflow, route, data or source content was changed.
