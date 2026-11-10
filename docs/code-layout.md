# Code layout and responsibilities

Keep reusable implementation in the Python package, browser source in the frontend, and private information in the selected workspace. The existing `src/` layout separates importable code from checkout tools and data, consistent with [PyPA's source-layout guidance](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/). The responsibility boundaries below are this project's design choice.

```text
src/chatos/
├── __main__.py            python -m chatos entrypoint
├── core.py                canonical storage, identities and shared file primitives
├── workspace.py           versioned paths and source settings
├── visibility.py          capture text visibility rules
├── archive/               records, annotations, context, bundles and recovery
├── capture/               source adapters, import parsing and uploads
├── search/                lexical/dense retrieval, local models and evaluation
├── mapping/               representations, clustering, map layout and handoff
├── assistant/             project routing, feedback cues and assistant skill export
├── automation/            sync orchestration and scheduling
├── setup/                 independent initialization and onboarding
├── web/                   HTTP server, browser workflows and home integrations
├── cli/                   argument parsing and terminal presentation
├── experiments/           protocols, frozen inputs, execution and artifact checks
├── maintenance/           inventory, snapshots, logs and checkout tooling
├── templates/             maintained HTML templates
├── skills/                bundled assistant instructions
└── static/                compiled browser output
frontend/                  authored Astro, CSS, browser JavaScript and assets
scripts/                   thin checkout entrypoints
experiments/configs/       example experiment protocols
tests/                    regression tests using fictional temporary workspaces
docs/                     public guides, architecture, decisions and evidence
workspace/                 private records and generated artifacts, ignored by Git
```

## Import and resource rules

Use canonical package imports for new code, such as `chatos.capture.importers`, `chatos.search.retrieval`, `chatos.mapping.dense_map`, and `chatos.experiments.runner`. Cross-package imports are explicit; small relative imports are used inside the new experiment package. Shared storage and workspace paths remain independent of browser presentation.

The root `__main__.py`, `chatos.web` exports and `chatos.setup` initializer preserve existing entrypoints. Six small root aliases (`map_topics`, `search_models`, `semantic`, `dense_map`, `topic_map`, `evaluation`) preserve historical study imports and refer to the canonical module objects. They contain no duplicate implementation. Other internal imports now use their responsibility package.

Resolve static files, templates and bundled skills from the package root. Resolve personal records through `Workspace`/`workspace_path`, never through a source-module sibling. Checkout wrappers locate the repository; installed CLI commands work from outside it. The sync parser fingerprint hashes the actual adapter implementations after the move.

Keep `scripts/` small: command wrappers import a package `main()` and pass control to it. `app_control.py`, design archiving, the standalone topic-map builder and conversation metadata now have package implementations. Existing start/status/stop, archive and maintenance commands are retained.

## Experiments and historical evidence

New scientific runs use `chatos experiment PROTOCOL --output NEW_DIRECTORY`; details are in [Experiments](experiments.md). Application indexing and production map rebuilding remain separate commands. User-review UI work is deferred.

Private historical scripts were relocated byte-for-byte out of the active workspace into the ignored `experiments/archive/` tree. `workspace/chief_of_staff/reference/code-relocations.json` maps old paths to their retained code and hashes. Original results and manifests remain unchanged; use the relocation receipt when locating a historical source file. Frozen snapshots, downloaded dependencies and generated HTML are artifacts, not maintained source implementations.

The maintained source structure does not relocate records, database files, caches, backups, installed third-party integrations or design archives. Existing `workspace/app_data/state/` remains durable state. Do not delete it as cache.

## Development checks

Run the Python suite with `PYTHONPATH=src`, the Node browser-script tests, focused Ruff lint/format and scoped BasedPyright. Build a wheel and smoke-test it outside the checkout after changing package/resource locations. See [Contributing](../CONTRIBUTING.md). Frontend assets need rebuilding only when authored frontend files change.
