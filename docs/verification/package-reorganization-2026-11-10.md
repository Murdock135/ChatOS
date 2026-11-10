# Package reorganization and experiment CLI verification

Date: November 10, 2026. Owner: chat-os. Source: current user requests for a scientific experiment CLI, repository reorganization and moving code out of workspace; conversation ID unavailable.

## Implemented scope

Moved 38 formerly flat modules into responsibility packages, retaining shared storage/path/visibility foundations and selected compatibility surfaces. Moved checkout tooling implementations into maintenance/experiments packages; checkout scripts remain thin wrappers. Added `experiment` and `experiment-check` commands with explicit protocols, frozen inputs and hashed bundles. Moved 29 historical study/maintenance/template source files out of active workspace folders to ignored private source history, verifying unchanged bytes in the relocation receipt. Private data and prior run artifacts were retained.

The in-app user-review interface remains deferred. No authored frontend changes or new visual-design claims are part of this refactor. Existing unrelated UI edits were preserved. The source `src/` layout follows PyPA's separation guidance; the individual responsibility packages are project design choices.

## Validation

The pre-change suite ran 153 tests: sandbox restrictions blocked the HTTP/socket and process-lifecycle cases. After the package moves, all 153 passed with permitted localhost/process access. After adding experiment and relocated-metadata regressions, the final full suite passed 161 tests. Five Node browser-script/theme/topic-map tests also passed. New tests cover frozen inputs, exact row identity, no-clustering null semantics, configuration validation, existing-output refusal, failure/interrupt status, manifest tampering/extra files/path traversal and metadata note scope/content preservation.

Focused Ruff lint/format and scoped BasedPyright passed for experiment code and the relocated metadata utility/tests. The immutable v4-serving design manifest still verifies 52 files. Python discovery/imports use canonical package paths; selected historical aliases share their canonical module objects.

A clean wheel includes the new package hierarchy, CLI, browser assets, skills and both HTML templates, and excludes workspace/private historical source. The first wheel inspection exposed obsolete implementations retained in an old generated `build/` tree. That tree was preserved outside the checkout; a clean build removed the stale modules. Fresh-process installed-package checks also exposed an onboarding/initializer import cycle that the original in-process suite had hidden. Workspace initialization is now lazy at the package boundary, its implementation has a distinct module name, and a fresh-import regression covers each service entrypoint. Installed-package smoke checks then passed from outside the checkout with no semantic dependencies: CLI help, independent workspace initialization, fictional import/sync/search, skill/resource access and experiment-bundle verification. The installed package does not rely on checkout-relative templates or private workspace state.

## Bounded local scientific runs

Two offline CLI runs reused the frozen November 9 pilot and the downloaded MiniLM model. One embedded 417 separate main/subtopic labels from 99 complete Astra responses, without clustering, then projected them with UMAP. The other embedded 100 raw conversations using sampled/averaged inputs, then ran HDBSCAN and UMAP. Both recorded seed 42 and completed with zero additional API calls. Their bundles passed `experiment-check`.

Topic representation: trustworthiness 0.96054 and five-neighbor retention 0.49880. Raw baseline: two clusters, six noise points, cosine silhouette 0.13004, trustworthiness 0.82420 and five-neighbor retention 0.42400. These are geometry diagnostics on different point units, not a semantic model ranking or accuracy comparison. The raw run uses sklearn min_samples=2; the older pilot used sklearn=3 after its self-count adjustment. The CLI now sets HDBSCAN copy explicitly to avoid a future-default warning observed in the first raw validation run.

Private paths, absent from fresh clones:

- `workspace/app_data/experiments/runs/2026-11-10-astra-topics/`
- `workspace/app_data/experiments/runs/2026-11-10-raw-hdbscan/`
- `workspace/chief_of_staff/reference/code-relocations.json`

Each run retains its own source snapshot and exact effective settings. Semantic accuracy is null because reviewed ground truth was not supplied. No new AWS calls, model downloads, production index replacement or semantic-faithfulness claims were made. Cross-platform execution and live browser appearance were not re-evaluated for this code-only change.
