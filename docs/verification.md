# Documentation verification record

Reviewed on 2026-10-22 (America/Chicago). This records the evidence behind the [feature map](features.md), rather than treating earlier assistant descriptions as proof.

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
