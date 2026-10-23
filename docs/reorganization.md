# Where things live

The repository contains the application. Your visible `workspace/` contains your information:

```text
chats/
├── README.md
├── CONTRIBUTING.md
├── pyproject.toml
├── src/chatos/                 application and bundled browser assets
├── scripts/chatos             checkout command
├── tests/
├── docs/                      guides, concepts, reference, ADRs and proposals
└── workspace/                 private; not distributed in the package
    ├── chatos.json             layout version and source settings
    ├── your_ais/
    │   ├── codex/chats/        source-specific readable conversations
    │   ├── chatgpt/imports/    supplied export inbox
    │   └── muse/              retained source material; raw capture deferred
    ├── shared_context/        reviewed cross-app context, when supplied
    ├── chief_of_staff/        guidance, memory, skills, projects and feedback
    ├── library/               generated cross-app navigation
    ├── app_data/              database, logs, snapshots and rebuildable cache
    └── backups/               verified conversation database backups
```

`chief_of_staff/reference/` retains existing operational notes that do not fit a narrower category. Platform `context/` indexes point to dated snapshot evidence; they do not claim that every platform exports memory or skills. `app_data/state/` contains durable records and must not be deleted as a cache.

From the repository, run `./scripts/chatos serve --open` or `./scripts/chatos doctor`. The checkout command works without installation. An installed package provides `chatos`; use `--root /absolute/workspace` when running outside the checkout. `CHATOS_WORKSPACE` is an explicit override.

The old root-level and workspace-level `System/`, `Conversations/`, `Projects/`, `Topics/`, and `Humans/` aliases have been retired. Active instructions, schedules, documentation and maintenance commands use canonical paths. Historical absolute file links keep their original source text; use `workspace/app_data/migration.json` to find their current destinations. Retained alias trees live in `workspace/app_data/legacy-paths/` for diagnosis. Start in `workspace/Home.md` or the browser app.

## Migration and recovery

Migration creates a separate version-2 copy, uses an online SQLite backup, compares source records and durable side tables, then verifies canonical files. It does not reimport source chats or activate a new host integration. `workspace/app_data/migration.json` records the source, path mapping and verification. Historical snapshot and backup payloads remain unchanged.

Original directories and both failed staging copies are consolidated under `workspace/backups/layout-migration/`, with a README explaining each. These are recovery evidence rather than active data. Do not delete them automatically. Rollback requires stopping the browser/sync process, preserving post-migration changes, disabling activated workspace selection, and restoring the retained originals. This is a local rollback copy, not off-device protection.

Layout changes do not repair unavailable histories or the existing mixed-identity fork-import issue. Public-user onboarding and context-artifact setup remain a separate phase.

## Local assistant shortcuts

Optional shortcuts to the capability summary, sync report and roadmap are grouped under `.chief_of_staff/`, keeping them out of the visible repository root. Their actual files remain in workspace/. README links go directly to those files, and the application does not depend on the shortcuts. Authored Chief of Staff guidance continues to live in workspace/chief_of_staff/.
