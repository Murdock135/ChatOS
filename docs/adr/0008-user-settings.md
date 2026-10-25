# Separate user settings

- Date: 2026-10-25
- Status: accepted and implemented
- Authority: Zayan requested a separate place for user settings, including Import chats, the local workspace path and sync controls, with Sync remaining in both places.

## Decision

Add a Settings destination in sidebar navigation. Move the import action/file input and workspace path there, and group sync, last-run information and local search-model configuration in that view. Keep the quick Sync action in the header. Both sync buttons invoke the same workflow, disable together during a request and share success/partial/error status. Setup & handoff retains source opt-in, assistant/context setup and portable handoff.

This changes navigation and presentation, not source access, import limits, model-download permission or workspace storage. Existing captured data, settings and annotations remain intact. Font changes remain deferred.

## Verification

The existing browser regression covers Settings navigation, its accessible name, view isolation, workspace path, import-picker activation and shared sync state. A separate fictional workspace verified visible Settings controls and successful/partial sync from the two entry points. All 124 Python tests and the Node regression pass. Astro check/build passes with one pre-existing deprecation hint and no errors/warnings. Browser assets were rebuilt. See the current library and semantic-search guides for the new locations.
