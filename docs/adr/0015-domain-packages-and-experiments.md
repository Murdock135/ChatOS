# 0015: Organize implementation by responsibility and keep experiment code out of workspace

Date: 2026-11-10. Status: implemented locally.

Authority: the current user requested a CLI script for embedding/clustering experiments, asked to reorganize the chaotic repository using established practices, and clarified that application code should not live inside workspace. The current source conversation ID is unavailable. The user separately deferred the in-app review interface; that deferral remains in force.

Keep the existing `src/` package, authored `frontend/`, compiled `static/`, and private workspace boundaries. Group Python implementation into `archive`, `capture`, `search`, `mapping`, `assistant`, `automation`, `setup`, `web`, `cli`, `experiments` and `maintenance`. Retain shared storage/path/visibility foundations at package root. Cross-package imports name the responsible package. This is a responsibility refactor, not a new application architecture or UI redesign.

Retain `python -m chatos`, installed `chatos`, checkout scripts and start/status/stop commands. Keep small aliases for historical experiment imports where needed; do not duplicate their implementations. Resolve templates, skills and static assets from the package root, and data through the selected workspace. Update parser fingerprints to hash the moved source adapters. Build and test the wheel outside the checkout to catch packaging/resource regressions.

Reusable experiment code is versioned in `src/chatos/experiments`. `chatos experiment PROTOCOL --output NEW_DIRECTORY` freezes data and exact embedding inputs, records effective settings/model hashes/source evidence/library versions, runs CPU embeddings and optional original-space HDBSCAN/UMAP, and saves results, geometry diagnostics, status and timings. `experiment-check` verifies relative-path artifact integrity without model inference. Existing runs cannot be overwritten; failures and interruptions retain their status. No remote inference or implicit model download is introduced.

Raw conversations use the current sampled/averaged baseline. Saved structured subjects/subtopics remain separate source-linked points, with invalid/missing outputs excluded and coverage disclosed. Different point units and sklearn HDBSCAN min_samples conventions must remain explicit when comparing studies. Semantic accuracy remains unmeasured without reviewed reference labels. The standalone HTML map remains available through a thin wrapper and a packaged template.

Remove runnable study and duplicate maintenance scripts from active workspace locations. Retain 29 original source files byte-for-byte under the ignored private `experiments/archive/` tree and record source-path/hash relocations alongside the study records. Private source evidence is not copied into public examples or package data. Downloaded third-party environments, frozen snapshots and generated visualizations remain workspace artifacts. Datasets, results, existing manifests, records, durable state, backups and immutable design archives keep their locations/content.

[Code layout](../code-layout.md) documents boundaries and compatibility. [Experiments](../experiments.md) defines protocols, outputs and limitations. [Verification](../verification/package-reorganization-2026-11-10.md) records tests, packaging and bounded local execution evidence.
