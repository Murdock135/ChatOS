# Set up your own workspace

This guide takes a new user from an empty folder to a searchable archive, reviewed context, an optional assistant workflow and a verified backup. It uses your own data and preferences. It does not install a global skill, scheduler, account connection or model.

## 1. Start independently

From the repository, with macOS and Python 3.9+:

```bash
./scripts/chatos init workspace
./scripts/chatos --root workspace setup-status --json
```

Initialization refuses a nonempty destination. If this checkout already has someone else's configured workspace, choose a new directory instead of copying their files. `setup-status` reports the current stages and next action; an empty archive is expected here. Obsidian is optional.

To try fictional material first, use `Demo` in place of `workspace` and copy `docs/examples/conversations.json` into `Demo/your_ais/chatgpt/imports/`. Keep demo folders separate from personal data and Git commits.

## 2. Choose your sources

For ChatGPT, open the app and supply a supported export through Import chats, then Sync workspace:

```bash
./scripts/chatos --root workspace serve --open
```

Keep the terminal running; stop with Ctrl+C. You can instead copy the export into `your_ais/chatgpt/imports/` inside your chosen workspace and run `sync`. There is no connected account merely because a platform folder exists.

Local Codex history is opt-in. For a new workspace, use `init DIRECTORY --codex-home /absolute/CODEX_DIRECTORY` instead of the first initialization command. For an existing version-2 workspace, edit its `chatos.json` Codex entry to `{"enabled": true, "path": "/absolute/CODEX_DIRECTORY"}` after choosing that source, then sync. Leave it disabled if you do not want local history scanned. Muse raw capture remains deferred.

Inspect what actually arrived:

```bash
./scripts/chatos --root workspace sync
./scripts/chatos --root workspace coverage --json
./scripts/chatos --root workspace search "a topic I discussed"
./scripts/chatos --root workspace retrieve "a specific question"
```

Open a cited record and verify its wording. Partial captures and unavailable replies are reported explicitly. A successful sync is not proof of full history. See [Source coverage](source-coverage.md).

## 3. Add only the context you want reused

Edit your own `shared_context/profile.md` and `preferences.md`, or follow [Context artifacts](context-artifacts.md) to ask your AI for an inspectable summary. Imported artifacts stay unreviewed until explicitly accepted. Check `setup-status` for pending IDs. Sync after accepting or retiring context so retrieval reflects the current selection.

Do not inherit another user's profile, project registry, accepted summaries or host skills. The fictional example is a format demonstration, not your preferences.

## 4. Choose how your assistant participates

Each new workspace contains `ASSISTANT.md` with paths and commands for that workspace. For an older initialized workspace, generate it:

```bash
./scripts/chatos --root workspace assistant-guide
```

The command preserves a user-authored ASSISTANT.md rather than overwriting it. After moving a workspace, regenerate the generated guide to refresh its paths.

Ask an assistant with local file/terminal access:

> Read the ASSISTANT.md file in my ChatOS workspace. Explain what you can access and what remains unavailable. Then help with my current task using cited source messages and reviewed context.

An ordinary chat application cannot read your local folder automatically. If the destination assistant cannot access local files, give it a [selected portable bundle](portable-bundles.md). This is an explicit handoff, not a background memory connection.

Projects are optional. When ready, add your own project entries in `chief_of_staff/projects/registry.json`, using `id`, `name`, `kind`, absolute `root`, and absolute `entrypoint`. Associate a chat through the app or `assign SOURCE ID PROJECT --reason "reviewed ownership"`. Associations do not move project files or establish commitments. External filing is separately restricted; configuring an assistant guide does not enable external writes.

## 5. Verify recovery and daily use

```bash
./scripts/chatos --root workspace doctor
./scripts/chatos --root workspace backup --fresh
./scripts/chatos --root workspace setup-status --json
```

A database backup preserves captured records, revisions and local annotations. It excludes the whole app, source attachments, authored context and configuration; back those up separately. Restore only into a new directory and inspect it before adoption. See [the library guide](chat-library.md) and [folder/recovery rules](reorganization.md).

Daily use is: open the local app, import or sync when you have new source material, inspect coverage when something is missing, and retrieve cited passages when resuming work. Scheduling and host integration are optional later choices.

## What the setup tests establish

Automated acceptance tests use two fictional users, distinct home/workspace paths, separate preferences, a source import and duplicate-free repeat, unreviewed/accepted context, assistant guides and portable export. They verify isolation and the documented review boundaries on the tested Mac. They do not establish a clean-machine install, every provider export schema, cross-platform operation, account connection or unattended reliability.
