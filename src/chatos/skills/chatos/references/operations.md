# ChatOS operations

Use the command prefix and actual paths in connection.md. `chatos --root WORKSPACE --help` lists supported commands. Commands accept `--json` for structured results.

## Organize and preserve

- `search "topic"` finds conversations; `retrieve "question" [--project ID]` returns cited passages. Open the original context, not just a search snippet. Lexical search may miss paraphrases; optional hybrid retrieval requires an installed model and current vectors.
- `library SOURCE ID --note "local note"` updates separate annotations; `--archive` and `--restore` change local visibility without deleting source messages. Do not describe these as edits in the provider app.
- `assign SOURCE ID PROJECT_ID --reason "verified ownership"` persists reviewed ownership. Read `chief_of_staff/projects/registry.json` and the destination's current instructions first. A title match is only a candidate.
- `file-projects` delivers managed conversation indexes to explicitly configured external roots. It does not file arbitrary tasks or decisions. Use it only within current authorization; verify destination files and retain a delivery receipt.

## Maintain when needed

- `status`, `coverage --json` and `doctor` separate run health from source availability. Check actual errors before retrying. Do not repeatedly retry unchanged inaccessible history.
- `sync` ingests available configured sources and supplied exports, refreshes lexical indexes/views and verifies a daily database backup. It does not download models, connect accounts or imply complete coverage. Respect the workspace lock; an operation already running should finish before another starts.
- `backup --fresh` creates a verified current conversation-database backup. It excludes authored context/configuration, original attachment bytes and the whole app. `restore BACKUP NEW_DIRECTORY` is isolated recovery; never overwrite the live workspace.
- Pretrained embeddings/maps are optional explicit maintenance (`dense-build`, `dense-map`). Their freshness/geometry and search evaluations are diagnostics, not proof that groups are semantically correct. Do not download a model or expand source access merely to make a report look complete.

## Review reusable context

`context-import FILE` retains an artifact as unreviewed data. Inspect its body, provenance, scope and uncertainty before explicit `context-accept ID --review-note "what was verified"`. Do not claim the human reviewed something merely because you ran the command. `context-retire ID --review-note "why reuse ended"` preserves the source/review history while stopping future reuse. Command-line changes require sync for retrieval freshness; browser acceptance/retirement refreshes it immediately. Acceptance is not installation as a host rule or provider memory.

## Handoff deliberately

`bundle-export NEW_DIRECTORY --conversation SOURCE:ID` exports one selected chat; repeat that option, choose one `--project ID`, or explicitly `--all`. Optional `--with-context` includes user-authored profile/preferences and accepted summaries with review provenance. Unreviewed/retired context is excluded. `bundle-check DIRECTORY` verifies integrity. Source text, local annotations and capture gaps remain distinct. Creating a local bundle does not authorize uploading it; native provider import and attachment bytes are outside this format.
