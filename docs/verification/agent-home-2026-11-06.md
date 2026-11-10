# Home dashboard verification — 2026-11-06

The final homepage follows the user's supplied dark reference. Its ChatGPT center is non-interactive, per the user's explicit clarification. See [decision and boundaries](../adr/0010-agent-home-dashboard.md).

## Checks performed

- Astro check: no errors or warnings; one existing `beforeunload.returnValue` deprecation hint. Frontend build/publish succeeded.
- Existing Node browser regression, including Home navigation and real conversation-count handling: passed.
- Three new home unit tests: passed live revision reads, rejection of unregistered/symlinked directives, persisted mounts and directory boundaries, and Gmail profile/message mapping without token persistence.
- Two new HTTP tests plus existing compiled-asset and authorization tests: passed authentication/origin checks, live file reads, source mount/read/traversal behavior, and Gmail connect/disconnect state without exposing credentials.
- Ruff lint and formatting checks on new `home.py` and `test_home.py`: passed. Added web dispatch/test sections were range-formatted. Whole-file lint of the existing web module still reports its prior Optional/Union annotations, general exception handler and JSON boundary exception convention; these were not rewritten.
- Scoped BasedPyright on `home.py` and `web.py`: no errors or warnings.
- Headless Chrome against the actual Python server and fictional workspace, with no browser API-response mocking: passed directive reads, mounted repository README reads, Obsidian mount persistence and note reads, Gmail authorization-form rendering, navigation, and widths 1610, 1280, 1024, 768, and 390. No horizontal document overflow or browser script errors. Clicking the ChatGPT visualization generated no network request, and no task form is present.
- Desktop and mobile screenshots were visually inspected. The tablet connector-line overflow found during testing was fixed by hiding decorative cross-column lines when the layout wraps.
- The user's existing server was verified as this checkout's `chatos --root workspace serve` process, restarted on localhost:8765 with its existing authorization retained, and checked through the new API: HTTP 200, 596 available directives, 6 local sources, 412 conversations, Gmail disconnected. The served page contains the ChatGPT visualization and no task controls.

## Artifacts and limits

[Desktop](agent-home-2026-11-06/desktop.png) · [Mobile](agent-home-2026-11-06/mobile.png) · [Mobile sources](agent-home-2026-11-06/mobile-sources.png)

Screenshots contain fictional files and directories; private workspace data was not copied into public artifacts. Gmail profile/message calls were tested using mocked upstream responses, not the user's account. A real account requires a Google OAuth token with Gmail read-only scope. This is not a general accessibility audit, packaged OAuth setup, background agent, or account-wide connector integration.

## Primary API references read

Google's HTTP request, query parameter, response, and authorization sections for [users.getProfile](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users/getProfile), [users.messages.list](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list), and [users.messages.get](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get) were read directly to implement profile verification, bounded search, and metadata reads.

## Dashboard click destinations follow-up

The registry header is now a keyboard-accessible toggle with `aria-expanded` and an explicitly controlled content region. Category chevrons show their expand/collapse behavior. The Conversation pool card now opens conversation clustering instead of the flat chat list.

Astro check/build and the Node regression passed. A read-only Chrome check against the running user workspace passed registry mouse/keyboard toggling, category toggling, live file content display, Conversation pool → Conversation map navigation, and confirmation that clicking the ChatGPT center makes no request. No archive content or source configuration was changed by the check.
