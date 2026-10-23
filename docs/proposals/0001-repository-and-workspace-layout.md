# Separate application code from a visible user workspace

Status: implemented on 2026-10-23; the initial compatibility aliases were subsequently retired after user review. This preserves the original design proposal; see [the adopted decision](../adr/0002-versioned-visible-workspace.md) and [actual layout](../reorganization.md). The implementation uses chatos.json rather than the illustrative TOML filename below.

Source: user messages in codex:01a16510-7f12-78b0-afa9-d5aee24d915b requesting conventional project organization, meaningful `your_ais/<platform>/` folders, a possible Chief of Staff folder, and a README feature checklist. This refines the adopted direction to keep chats, skills, memory, and related records together and inspectable; it does not supersede it.

## Problem in the current layout

The current root mixes distributable software (`chatos/`, `tests/`, `docs/`) with private conversations, project context, personal operating instructions, and several navigation pages. `System/` contains scripts, settings, user memory, skills, logs, imports, snapshots, backups, and durable database state. These have different audiences, privacy, and recovery needs but look like one category. `Humans/` describes an audience rather than what its files contain.

The application currently uses a flat Python package, `chatos/`, with no `pyproject.toml`. `chatos/core.py` derives its default workspace from the checkout and stores the database in `System/State/`. Stored record paths, citation links, generated pages, scripts, and host entry instructions depend on existing names. Some scripts also contain personal absolute paths. A directory rename alone would break behavior.

## Recommended repository layout

```text
chatos/                         # repository root; name is illustrative
├── README.md                   # purpose, features, first use, documentation links
├── CONTRIBUTING.md             # development setup and contribution checks
├── AGENTS.md                   # instructions for agents developing the app
├── pyproject.toml              # package, CLI entry point, dependency/tool settings
├── src/
│   └── chatos/                 # installable Python package and bundled web assets
├── tests/
├── docs/
│   ├── README.md               # learning path
│   ├── guides/                 # setup, daily use, recovery
│   ├── concepts/               # sources, capture, context, Chief of Staff role
│   ├── reference/              # commands, configuration, formats, architecture
│   ├── adr/                    # adopted software/design decisions
│   └── proposals/              # designs still under discussion
├── examples/                   # fictional workspaces and context artifacts only
├── scripts/                    # developer tooling; no user-specific configuration
└── workspace/                  # visible, private user data; not shipped in package
```

Use `src/chatos/`, rather than `chatos/src/` inside the repository, for the importable package. The [Python Packaging User Guide](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) explains the distinction and the required installation step. Developer setup would use an editable installation; fresh-install checks must exercise the built package, including its web assets. This is a proposed packaging change, not a command supported by the current checkout.

Keep ADRs and proposals under `docs/` so explanatory material has one home. Add `bin/` only if real executable wrappers are needed: the installed `chatos` command should come from the package entry point, without a second implementation in shell scripts. Keep current modules intact initially; do not reorganize every Python module while changing storage.

## Recommended user workspace

```text
workspace/
├── README.md                   # where your information lives; editing rules
├── Home.md                     # generated navigation across your library
├── chatos.toml                 # workspace version, enabled sources, local settings
├── your_ais/
│   ├── codex/
│   │   ├── chats/2026/         # readable records with stable source identities
│   │   ├── imports/            # explicitly supplied source material
│   │   └── context/            # dated captured skills, memory, instructions + index
│   ├── chatgpt/                # same categories when supported by the source
│   └── muse/                   # optional; not an implication that capture works
├── shared_context/
│   ├── profile.md              # user-reviewed cross-app context
│   ├── preferences.md          # user-reviewed preferences
│   ├── skills/                 # shared authored skills, not automatically installed
│   └── inbox/                  # unreviewed AI-prepared artifacts and provenance
├── chief_of_staff/
│   ├── instructions.md         # role and authorized workflow
│   ├── memory.md               # working context for that role
│   ├── skills/                 # role-specific procedures
│   ├── projects/               # registry, overrides, routing queue and receipts
│   ├── decisions/              # recorded user/project choices, not software ADRs
│   └── feedback/               # reviewed interaction feedback
├── library/                    # generated cross-platform project/topic views
├── app_data/
│   ├── state/                 # durable database, revisions, annotations, checkpoints
│   ├── logs/                  # sync and incident evidence
│   ├── snapshots/             # dated workspace snapshots and capture manifests
│   └── cache/                 # rebuildable derived files/models only
└── backups/                    # verified backups with explicit recovery scope
```

Create source folders when enabled or supplied, rather than presenting empty folders as connected services. The same source categories do not imply equal capabilities: a provider may expose chats but no skills, or only a partial desktop capture. `your_ais` groups applications/platforms; source and observed model metadata identify the actual provider/model.

This gives a person four useful questions: **Which app did this come from?** → `your_ais/`; **What context do I want to reuse?** → `shared_context/`; **How does my organizing assistant operate?** → `chief_of_staff/`; **Where can I browse everything together?** → the browser app or `library/`. Ordinary use should not require opening `app_data/`.

Keep the default workspace visibly inside the checkout for the current installation. Support choosing another visible directory later through explicit configuration; do not force hidden OS data directories. The application must resolve its code/resources independently of the selected workspace. Opening the workspace as an Obsidian vault should remain possible without exposing all developer files as notes.

## Ownership and editing rules

- **One current record per source and conversation ID.** Platform `chats/` holds the readable current projection. The database retains structured records, revisions and local annotations. Cross-app views link to those records rather than producing another editable transcript. Original exports retain source evidence.
- **Source text and local edits remain separate.** Local titles, notes and archive flags belong to annotations, survive reimport, and do not imply changes in the source app. Explain which readable files are generated before encouraging direct editing.
- **Captured context is evidence, not activation.** Platform `context/` contains dated accessible copies. Live host configuration remains at its actual host location unless the user explicitly installs/updates it. Shared skills and Chief of Staff skills have separate scope and explicit activation.
- **Avoid duplicating captured files.** A platform context index can reference immutable files in a dated snapshot. New snapshot manifests should distinguish platform captures, workspace captures and source paths; keep old snapshot payloads and their hashes intact during migration.
- **Shared user context and role memory differ.** A general preference can apply across apps; the Chief of Staff's working memory is specific to that workflow. Unreviewed AI-generated context stays in the inbox with source and uncertainty, without silently becoming an instruction.
- **Durable state is not cache.** Never tell users that deleting `app_data/` is harmless. The database includes non-rebuildable revisions and annotations. Only specifically identified derived material belongs in `cache/`; model downloads can be replaced, subject to availability and cost.
- **Private workspace and distributable app differ.** Ignore the private workspace in Git and exclude it from package builds. Some private records are already tracked: ignore rules alone do not remove them or sanitize existing Git history. No publication or history rewrite is authorized by this proposal.

## Mapping from today's directories

| Current location | Proposed ownership |
| --- | --- |
| `chatos/` | `src/chatos/`, with package metadata and bundled resources |
| `System/Scripts/` | Runtime operations into the package; developer-only tools into `scripts/`; inspect each script before moving |
| `Conversations/YYYY/` | `workspace/your_ais/<source>/chats/YYYY/`, preserving source+ID identity |
| `Conversations/Annotations/` | Generated annotation views alongside the corresponding source records; authoritative state stays in the database |
| `System/Imports/` | `workspace/your_ais/<source>/imports/` |
| `System/Skills/`, `System/Memory/`, operating guidance | Classify into platform captures, shared authored context, and Chief of Staff procedures; no blanket move based on filename |
| `System/Projects/`, decisions, feedback | `workspace/chief_of_staff/`; generated browse views in `workspace/library/` |
| `Projects/`, `Topics/`, generated human HTML | `workspace/library/` or application-generated views; one clear Home |
| `System/State/`, `System/Logs/` | `workspace/app_data/state/`, `workspace/app_data/logs/` |
| `System/Snapshots/`, `System/Models/`, `System/Backups/` | Snapshots, cache/models, and backups respectively, with recovery scope retained |
| Root onboarding and runtime prose | Public explanations in `docs/`; personal operating state in the workspace |

## Safe implementation sequence

1. Define a versioned workspace manifest and a single path resolver. Explicitly select legacy versus new layout; do not guess by folder presence or silently redirect an existing default workspace. Remove personal paths from distributable defaults without altering this user's preferences.
2. Add package metadata and installable source layout, including runtime scripts/resources needed by sync. Test CLI and web assets from a built package outside the checkout.
3. Initialize independent fictional workspaces, with no copied personal registry, memory, schedule, or automatic source scanning. Document context-artifact provenance and review before activation.
4. Build a dry-run migration manifest. Back up database **and** authored context/configuration; inventory counts, identities, hashes, permissions and source gaps. Acquire the workspace lock and stop competing writers. Preserve the original workspace until verification succeeds.
5. Migrate an isolated copy first. Update database file paths, generated links, retrieval paths, snapshot pointers, inventories, schedules and installed entrypoint references through explicit handling. Historical transcripts and immutable snapshot source evidence must not be rewritten as though old paths never existed; use a migration map for resolving old links.
6. Verify counts/identities, revisions, annotations, search/citations, import idempotence, project routing, map freshness, context browsing, backup/restore and rollback. Test spaces in paths, different fictional home directories, interrupted migration and already-migrated inputs. Only then migrate the live installation as a separately reported operation.

The main choice to settle before live migration is the user-facing workspace naming and ownership model. The proposal recommends one visible `workspace/` containing `your_ais/`, rather than scattering private folders among the source files. This design remains open for review; this document does not authorize a migration or promise that onboarding is already complete.
