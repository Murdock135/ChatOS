# smriti branding — October 26, 2026

User-approved rename from ChatGrep to lowercase smriti, using the supplied artwork. The original PNG is retained unchanged in `frontend/public/smriti-brand.png`; the SVG icon frames its emblem using embedded original pixels. No external assets or fonts are requested.

Navigation uses the emblem when compact and the supplied wordmark when expanded. The rail uses navy/blue; existing light content surfaces and search layout remain. The browser title/favicon, Settings artwork, product-facing messages, current documentation and bundled assistant skill use the new name. Technical `chatos` identifiers, compatibility routes and old search aliases remain. Historical verification reports, ADRs and proposals keep their original wording.

## Verification

- Astro check: no errors/warnings; existing `beforeunload` deprecation hint remains.
- Astro production build: passes; compiled assets published to `src/chatos/static/`.
- Node startup regression: 1 test passes.
- Python: 19 web tests (including brand asset routes), 3 assistant-skill tests, 2 search-review tests, 9 map-exploration tests pass.
- Scoped BasedPyright: 0 errors/warnings for web, setup and assistant-skill modules.
- Ruff format: passes for changed web/setup/assistant-skill modules and web tests. Scoped lint reports 12 existing findings; compared diagnostic codes/messages against HEAD and found no additions.
- Browser inspection with a temporary fictional workspace: compact/expanded navigation, Settings artwork and 431px mobile layout verified. Settings sizing moved from inline styling into the stylesheet to respect the existing Content Security Policy.
- Screenshots: [desktop](smriti-branding-2026-10-26/desktop.png), [mobile](smriti-branding-2026-10-26/mobile.png), [Settings](smriti-branding-2026-10-26/settings.png).

## Limits and continuity

Existing unrelated search/navigation working-tree changes were preserved. No commit, publication or workspace data migration was performed. The web suite initially could not bind temporary loopback servers in the sandbox; rerunning with loopback access passed.

The workspace inventory check reported pre-existing dated snapshot drift in routing records and provider-managed memory files. It was not represented as synchronized. The metadata-refresh script referenced by the workspace guide is absent; the partial chat summary retains unknown model/timestamps as null. Product naming was recorded as COS-2026-007, in the project registry and STATE.md. No full archive sync or snapshot refresh was performed for this branding change.

## Live-server follow-up

The user reported the logo missing. The existing app on port 8765 returned 404 for the new emblem route because its Python process predated the branding changes. Restarted that server against the same workspace and port, then verified the emblem and expanded wordmark in the live browser. The earlier verification used a fresh temporary server and did not catch this deployment-state mismatch.
