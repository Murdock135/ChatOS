# Documentation verification record

Verification history: the original baseline was reviewed on 2026-10-22 (America/Chicago); dated 2026-10-23 follow-ups below cover packaging, layout cleanup and the current walkthrough. This records the evidence behind the [feature map](features.md), rather than treating earlier assistant descriptions as proof.

## Source review

The review covered the CLI command dispatch and sync lifecycle, and selected implementation sections for source adapters, visible-message filtering, record identity/revisions, search, passage retrieval, desktop normalization, project assignment/delivery, snapshots, change counts, health/recovery, feedback review, schedule evidence, and optional semantic retrieval/map generation. Relevant implementation and fixture links are attached to each feature in the map.

This was a documentation-focused review, not an exhaustive security audit, proof that every external app schema is supported, or verification of all semantic-model outputs. Large file reads were sampled where only a specific mechanism was needed; no claim that every repository file was read is made.

## Clean-copy checks

A temporary copy of committed source files was produced with `git archive HEAD`, outside the live workspace. It had no existing ignored archive, runtime database, imported exports, models, or virtual environment. It was on the same Mac and used the installed system Python; this is not a clean-machine or cross-platform installation test.

| Check | Observed result |
| --- | --- |
| CLI `--help` | Exited 0 and listed commands |
| `status --json` | Exited 0 with `never_run` |
| `doctor --json` on an empty copy | Exited 0, zero conversations; warned that no backup or sync evidence existed. Health does not imply setup is complete. |
| Baseline test suite in that copy | 57 tests passed with system Python |

The default source import was deliberately not run against the maintainer's real account from that copy. No assistant integration or scheduler was installed, and no external project filing was performed.

## Fictional first-use walkthrough

The documented `docs/examples/conversations.json` fixture was copied into a separate `Demo/` workspace in the temporary copy. Its source folder was explicitly empty. The current product docs and fixture are new documentation artifacts, not files claimed to have existed in the baseline commit.

| Step | Observed result |
| --- | --- |
| Initial demo sync | Status `ok`; one new chat, zero updated chats, total one |
| Behavior counts | Zero new skills or memory files; initial inventory labeled |
| Search for reading notes | Returned the fictional conversation |
| Retrieve Markdown reading notes | Included the exact user-choice message ID, `demo-choice` |
| Readable output | `Demo/Conversations/2026/chatgpt-chatos-demo-reading-plan.md` existed |
| Demo doctor | `ok`, with source-coverage warnings retained |
| Repeat sync without source edits | Zero new chats, zero updated chats, total still one |

These are local fixture results. They do not establish a live ChatGPT connection, broad export compatibility, or interpretation of arbitrary decisions.

## Checks on the documentation change

- The updated full suite passed 58 tests, including a new check that product documentation is included in workspace snapshot drift detection and capture.
- The system-Python consistency and terminal-report checks passed without Rich.
- Documentation links, code fences, SVG XML, and deterministic diagram regeneration are checked locally. Generated/private destinations are distinguished from files shipped in Git.
- The README and documentation navigation are inspected in Obsidian. Mermaid rendering encountered a vault-trust prompt; no trust setting was changed. Static SVG diagrams were supplied instead. Both static diagrams and the README navigation were visually inspected in Obsidian reading view. Two native scroll calls returned windowNotFoundAtPosition; keyboard page navigation recovered the inspection. No trust setting was changed.

That documentation baseline was followed by the user-requested local browser implementation below. Public setup and release remain separate from it.

## Dedicated local interface — 2026-10-23

The user selected a dedicated chat-management interface and Apple-inspired styling. The app was built over the existing core, using a loopback-only standard-library server and dependency-free browser assets.

- The full system-Python suite passed 72 tests, including HTTP access boundaries, context allowlisting/hash checks, source-preserving local annotations, local archive/restore, project assignment, upload validation, fresh backups and annotation recovery, map metadata, older-export protection, and project-filtered retrieval beyond 500 competing passages.
- New Python modules and tests were linted/formatted with isolated Ruff 0.14.1; new library/upload/server modules passed BasedPyright 1.31.7 in basic mode for Python 3.9. Browser assets were formatted/checked with Prettier 3.6.2 and JavaScript syntax checked with Node. This does not claim a full repository type-check or style migration.
- Browser fixture checks: read all three fictional messages; save local title/note; archive and restore; search/retrieve source passages and separately labeled annotations; receive the sample export with the file chooser; sync without an extra conversation; create a fresh verified database backup; assign a fictional registered project and filter the library.
- The repeated export changed provenance, so the browser sync reported zero new chats and one updated chat, total still one. No duplicate chat was created.
- The actual workspace loaded 254 chats; captured instruction previews and the older experimental 220-chat map rendered. These read-only checks did not change real chat annotations or project assignments. Desktop and narrow layouts were visually inspected.
- Initial HTTP tests required permission to open loopback sockets in the execution sandbox. The approved run passed; the server was not exposed to the network. A file-chooser test initially raced an old page and timed out/reset the browser tool; reloading the completed interface and selecting the fictional export succeeded. An unsaved-change confirmation triggered a driver timeout; its full dialog interaction remains inconclusive, rather than counted as a passed browser test.

The seven-question lexical diagnostic was rerun and still found exact supporting source messages in 4/7 cases. This is a small, unblinded diagnostic, not a general quality benchmark. The project-filter regression fixes scope correctness; it does not establish improved paraphrase recall. Optional semantic inference remains separate from ordinary sync.

No clean-machine installation, general-user setup, public release, comprehensive security audit, or cross-platform compatibility is established by these checks.

## Bounded optional-model refresh

At 05:30:57 UTC on October 23, the already-installed pinned Qwen model embedded 357 changed/new passages locally on CPU in 110.81 seconds, reaching 4,903/4,903 current vectors with zero remaining at that check. At 05:31:23 UTC, the rebuilt map represented 254/254 captured conversations, left 15 unclustered, and retained about 38.1% of its five-neighbor relationships. These are dated coverage/geometry observations, not evidence of answer accuracy or semantic grouping quality. Later captured records can require another refresh.

The same 72 tests also passed under the installed Python 3.13 environment. Selected text/action color pairs were checked numerically (white on the action blue: 4.70:1; secondary gray on white: 5.07:1). This is not a comprehensive accessibility audit.

## Final source-copy and reconnection checks

Committed source at `1e14970` was extracted into a new temporary directory without runtime data or a virtual environment. The system-Python suite passed all 72 tests; the documented fictional initial sync reported one new chat, and the unchanged repeat reported zero new/updated chats, total one. This is source-copy verification on the same Mac, not general-user initialization or a clean-machine test.

A later browser regression check restarted the fictional server on the same port, then opened its newly printed token URL in the already-open tab. The app reconnected without a page reload and retained access to the one-chat library. Map freshness is also checked against captured-record fingerprints at request time; current local titles/project associations are applied independently of the older coordinates. Map method/limits are available under About this map.

## 2026-10-23 — Reorganization acceptance

- Packaged source moved to `src/chatos/`; a wheel containing web assets and explorer template was built from cached setuptools and installed locally. An editable wheel was subsequently installed for development. Online build-isolation fetch was unavailable in this environment. `scripts/chatos` also runs independently of installation.
- All 259 existing conversations, revisions, checkpoints, annotations and feedback reviews matched exactly in a separate version-2 copy before activation. Two legacy title transformations were caught by the comparison; migration now updates only current projection paths and preserves historical record/revision bytes. Originals and failed staging remain retained.
- Post-activation manual sync ran through the existing System/Scripts wrapper, captured this continuation chat (260 total), and verified behavior files. Its one import failure is the pre-existing mixed parent/fork identity; no source identity validation was bypassed.
- 80 tests pass, including migration preservation and explicit repository-root selection. Loopback tests required authorized execution outside the restricted shell. Ruff lint/format and scoped BasedPyright checks pass for the migration/workspace modules.
- The browser app was opened against the active `workspace/` and visually verified to show 260 conversations. The library is left open. No new UI design or broad onboarding acceptance is claimed.
- Current behavior inventory and canonical-file/database health checks are repeated after maintained-note updates; known partial-source warnings remain. A fresh 260-record database backup verifies.

## 2026-10-23 — Visible folder cleanup acceptance

The earlier activation left legacy folders visible as aliases. User screenshots correctly showed that the root was still cluttered. This cleanup retires the aliases, updates active references, and groups recovery copies rather than deleting evidence.

- Visible root folders: docs, scripts, src, tests, workspace. Visible workspace folders: app_data, backups, chief_of_staff, library, shared_context, your_ais. No root migration-staging directories, Users directory, build output, or legacy folder aliases remain.
- Existing installed entry instructions and the active hourly maintenance prompt now use canonical paths; the task schedule, target and active state are preserved. This is configuration verification; manual run 57 verifies operation, not unattended execution after cleanup.
- 80 regression tests pass. The entry installer moved from the retired System namespace into the package. Migration/repeat-sync tests verify that legacy folders stay absent while records, revisions and annotations remain intact. Lint, format and scoped type checks pass for new migration, wrapper and installer code.
- README, Home, top-level product docs and active skills have no missing local Markdown link targets in the bounded link audit. Old absolute paths inside historical messages and snapshots remain original evidence; the migration receipt maps their current locations.
- A fresh 260-record database backup verifies. Final restored-database, inventory and doctor results are recorded in the operating state and cleanup receipt. The existing fork identity error still makes ordinary sync partial; no new capture-completeness claim is made.

## 2026-10-23 — Post-commit documentation consistency audit

A follow-up audit found stale prose even though the prior commit updated the main layout guide and commands: the docs index still said migration had not happened; the beginner guide denied the initializer it invoked and described a removed empty-source argument; the concepts and architecture pages retained old paths. These were corrected rather than treating changed filenames as evidence of documentation consistency.

The documentation now distinguishes the implemented basic initializer from incomplete guided onboarding. Package implementation links point to src/chatos/, and links to private configured records are identified as installation-specific. Historical verification results and the original structure proposal remain dated evidence.

In a temporary workspace, the actual checkout command initialized the fictional demo, imported one chat with Codex disabled, generated the documented canonical file, returned evidence passages, passed doctor, and imported again with zero new/updated chats. Local Markdown targets and code-fence balance were checked across README, CONTRIBUTING, and top-level docs pages. No application code changed; the 80-test result recorded above was not rerun for this prose-only correction.

## 2026-10-23 — README setup and usage revision

User feedback identified that the README still lacked a clear real-user setup and daily usage path. It now leads with prerequisites, workspace initialization, app startup, ChatGPT import, explicit opt-in Codex capture, and a separate fictional demo. The feature checklist and planned work follow usage. The optional pretrained backend is distinguished from model-free core operation, with a public semantic setup guide.

The README commands were exercised in temporary workspaces: empty initialization, refusal to overwrite a configured workspace, sample import, search, cited retrieval, health, fresh backup, duplicate-free repeat, and Codex configuration against an empty fictional source. A temporary loopback server served the initialized workspace. Initial test-helper comparisons treated macOS /var and /private/var aliases literally; checks were corrected to compare resolved paths and rerun successfully.

The previously reviewed model-data downloader is restored as a checkout helper with a packaged implementation, --root and --help. Tests use synthetic model bytes and a mocked download client to verify pinned-hash failure, accepted library-owned modules, rejected custom modules, canonical model paths and verification manifest publication. No model download, dependency installation, GPU inference or full embedding refresh was performed in this revision. Lint/format/scoped type checks pass; 82 regression tests pass. README and top-level documentation link/code-fence checks pass. Optional dependency installation on a fresh machine remains unverified.

## 2026-10-23 — Final reorganization check

The user resumed this chat to finish the reorganization and stop at that boundary. The live version-2 migration and folder cleanup were already committed; this pass inspected the actual checkout rather than repeating migration.

- All 82 regression tests passed on system Python, including migration preservation, workspace selection, recovery, imports and loopback API checks.
- No root-level System, Conversations, Humans, Projects or Topics aliases remain. Application code, maintenance commands, documentation and private records use the implemented layout.
- A bounded link audit covered 31 active entrypoints, guides, skills and top-level operational references. It found remaining renamed wiki links and a sync-status link pointing above the workspace. Those links now resolve directly to the canonical files; the repeated audit found no missing targets. Historical transcript and snapshot text was preserved.
- The initial health check found database integrity and generated conversation files intact, with behavior drift in three recently changed routing files. Manual sync run 64 reconciled those files, and inventory and doctor checks subsequently passed with 262 records. The existing mixed-identity fork import and partial source coverage remain separate limitations; this pass does not claim to repair them.

No application code, source connector, new onboarding feature or model inference was added in this final pass. The unrelated existing Home.md recap-link edit was left in place.

## 2026-10-23 — Source-coverage pass after migration

- Read-only inspection found that a rejected Codex file explicitly declared its fork owner and parent, then repeated parent metadata around inherited history. Added bounded ancestry validation rather than accepting arbitrary mismatched IDs. The parser retains the fork's own metadata and labels inherited messages, turn model history and run events with origin IDs. Readable records and retrieved evidence expose message origin.
- Synthetic tests cover wrong owners, undeclared identities, transitive ancestry, cyclic/conflicting relationships, source-file immutability, idempotent imports and citation provenance. Desktop tests cover every-page identity validation, narrower tool windows, retained missing-reply references and their removal only when matching message text becomes available. Coverage tests distinguish absent source files from histories already retained in the archive.
- All 90 tests passed on system Python. New lineage/coverage modules and tests passed Ruff lint/format; touched existing Python modules passed scoped F/E9 checks. The two new modules passed BasedPyright basic/Python 3.9 with zero errors/warnings. This is not a repository-wide type/style conversion.
- Manual sync run 65 completed with status ok and no errors, adding the rejected fork. It retained 230 Codex records and 33 partial ChatGPT records. The recovered fork has 13 visible messages: 11 inherited and two child messages. Comparison against 31 saved pre-update revisions found zero removed messages and zero changes to message text.
- Supported app reads still report missing source rollouts for the two known uncaptured Codex IDs. A bounded archived-ChatGPT listing returned zero entries. A prior cursor expired; a fresh read returned four turns with no next page. Existing captures retained all 113 visible ChatGPT messages and 38 unresolved reply references. No account-wide completeness or recovered missing replies are claimed.
- `coverage --json` reports observed records/capture types, inherited messages, missing-model metadata, absent rollout files and genuinely uncaptured IDs. It does not perform a source scan or infer a complete account denominator. Raw Muse capture remains deferred.

See [Source coverage](source-coverage.md) for interpretation and the supported fuller-export path.

Final follow-through: run 66 also completed with status ok and no errors. Doctor and behavior inventory checks passed, a fresh 263-record database backup verified, and the bounded 32-page active documentation/navigation audit found no missing targets. Source-completeness limitations above remain unchanged.

## 2026-10-24 — Evaluation, reviewed context and portable onboarding

The source suite passes 97 tests on system Python 3.9. New tests cover positive and negative retrieval cases, project scope, correct-message/wrong-passage distinction, map freshness and topic-pair diagnostics; independent fictional-user workspaces; context import/review failures; selected portable export, corruption, path/symlink rejection and an independent JSON reader. Browser tests require temporary loopback binding: the restricted run was blocked, then the authorized rerun passed. A first invocation without the documented PYTHONPATH failed import discovery and was corrected. These environmental failures are not passed tests.

A wheel was built with cached local setuptools, inspected to include the new modules/browser assets and exclude private workspace data, then installed offline without dependencies in a separate Python 3.9 environment. From outside the checkout, a fictional home and workspace whose path contains spaces and an apostrophe completed initialization, one-chat import, repeat sync, coverage, search, cited retrieval, the public three-case evaluation fixture, context import/accept/sync, assistant-guide generation, setup status, selected bundle export/check, fresh backup, isolated restore and doctor. Codex capture stayed disabled. The public fixture returned both expected passages and zero results for its one negative query. This tests a tiny instructional fixture, not general search quality or a clean-machine installation.

Ruff lint and format checks pass for the new/rewritten modules and tests; scoped basic/Python 3.9 BasedPyright reports zero errors and warnings. No browser assets changed in this phase, so no new visual-design verification is claimed. Source-text and local annotations remain separate; context is excluded from bundles by default and unreviewed artifacts remain excluded when context is selected.

On the private seven-question diagnostic, lexical retrieval found the expected passage for 3/7 questions (MRR 0.3571); hybrid retrieval found 4/7 (MRR 0.4048) after the already-installed pinned model reached 5,253/5,253 current passage vectors. CPU refresh embedded 369 passages in 79.78 seconds. No model download or remote inference was introduced. These source-specific assistant-authored questions are not blinded, representative or a general accuracy benchmark.

The rebuilt map represented 264/264 records at its check, with two clusters, 12 unclustered records and five-neighbor retention about 0.388. A five-record assistant-labeled convenience sample produced 2 related pairs grouped together and 8 unrelated pairs grouped together (precision 0.20, recall 1.0). That exposes false merges and leaves semantic quality unvalidated. These are dated corpus observations; later sync can make vectors and coordinates stale. See [evaluation methods and limits](search-evaluation.md).

The feasible requested workflows are implemented. Broader capture still needs accessible material for two unavailable Codex histories and missing ChatGPT reply bodies; the user has no export available. Muse remains deferred. Public positioning, independent real-user learning-path review, clean-machine/cross-platform validation, sustained maintenance reliability and destination-native import are not established by these checks.

## 2026-10-24 — Browser workflow completion after acceptance review

The earlier completion statement covered command-line mechanisms and missed essential access through the user-facing app. After the user's correction, Setup & handoff was implemented in the browser: empty-library orientation, explicit local source opt-in/disable before scanning, assistant-guide generation, context upload/inspection/acceptance/retirement and selected portable bundle creation. Human-readable context, sources, scope and review history appear before optional integrity metadata. Retiring a note preserves its source and prior reviews, removes it from active retrieval and future bundles, and permits a later explicit review. Existing bundles remain historical copies. A failed retirement-record write restores the published note rather than silently removing active context.

The full suite passes 101 tests with the existing interpreter. A source-only temporary checkout, separate fictional HOME, no private workspace and no virtual environment also ran 101 tests successfully, with one expected skip because optional NumPy was absent. In that copy, initialization, one-chat import, zero-change repeat, context acceptance/retirement, selected handoff/check and doctor passed. The fictional home acquired no Codex configuration. This is isolation on the same Mac, not evidence of another operating system or an independent person's usability review.

Browser acceptance in a separate fictional workspace visibly verified empty-library setup; file-picker ChatGPT import and sync; artifact source/scope inspection; acceptance; a one-chat bundle with three context files; retirement with retained accepted/retired review history; and a subsequent bundle with only the two user-authored context files. The narrow browser viewport was inspected. Local test uploads and bundles stayed in the fictional workspace. No real preference/source setting, host integration or external account was changed.

New API tests verify source choices do not scan immediately, user-authored guides remain protected, unreviewed/retired context stays out of retrieval and export, explicit selections exclude other chats, source records stay unchanged, and mutations retain authentication, origin and workspace-lock boundaries. Ruff lint/format, scoped basic/Python 3.9 BasedPyright, JavaScript syntax and Prettier checks passed. Product/setup/history guides were reconciled; a public assistant workflow guide now replaces reliance on private maintainer procedures. Missing source material, experimental semantic quality, independent real-user/cross-platform checks and long-term unattended reliability remain honestly bounded rather than treated as implemented guarantees.

Live-library acceptance found an additional startup race: an immediate navigation click could finish before the initial overview and be overwritten by its default view. Navigation now waits for initial startup. The actual app script passes a Node built-in regression using a deliberately delayed overview and a minimal DOM; no test-only runtime dependency was added. Immediate navigation was then verified against the live 265-chat library, including full handoff-selector pagination. The latest offline wheel includes the new backend module/assets and passes isolated imports/command discovery.
