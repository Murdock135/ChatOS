# Getting started

Use the sample below to see a conversation become a readable archive and a search result. It works in a cloned source checkout without connecting your chat accounts. All sample messages are fictional.

## What you need

The current implementation targets macOS. Use Python 3.9 or later with SQLite FTS5 support; the core commands use the standard library. Obsidian is optional. The generated HTML views can be opened in a browser, and Markdown files in an editor.

Run the commands below from the folder containing this repository's README. The checkout includes an `init` command that creates an independent version-2 workspace with an empty project registry and Codex capture disabled by default. Application code is also installable as a Python package; there is no native macOS app installer. General guided source/account setup remains incomplete. The private workspace used by the maintainer is excluded from Git.

## 1. Import the sample

```bash
./scripts/chatos init Demo
cp docs/examples/conversations.json Demo/your_ais/chatgpt/imports/conversations.json
./scripts/chatos --root Demo sync
```

`init Demo` creates a separate workspace inside this checkout. The following commands select it with `--root Demo`. Codex capture stays disabled, so sync does not scan your real Codex history. Only the supplied fictional ChatGPT export is imported. No account connection or schedule is installed. Initialization refuses an existing nonempty directory.

Expect one **new chat** and a total of one conversation. The first behavior inventory is labeled as an initial capture. Sample data belongs to `Demo/`, which is excluded from Git.

## 2. Open the conversation

Open `Demo/your_ais/chatgpt/chats/2026/chatgpt-chatos-demo-reading-plan.md` in your editor. It contains the question, the assistant's suggestion, and the user's later choice in order. The neighboring JSON file holds structured metadata. Model information is unknown because the sample does not provide it.

Start the dedicated chat library:

```bash
./scripts/chatos --root Demo serve --open
```

Keep the terminal running; stop with Ctrl+C. Select the sample chat. Expand Local title, notes & project to add a local note or archive/restore it. Find evidence returns cited passages; Import chats receives supported exports before sync; Health & sync reports coverage, checks health, and creates fresh database backups. See the [library guide](chat-library.md) for the full workflow. The server uses the demo configuration, which keeps Codex capture disabled.

You can also open the older `Demo/library/dashboard.html` in a browser. Filter for “reading” to find the chat, then follow its source link. This filter searches titles, project fields, and short previews; use the CLI for full transcript search.

## 3. Find the relevant passage

```bash
./scripts/chatos --root Demo search "reading notes"
./scripts/chatos --root Demo retrieve "Markdown reading notes"
```

Search returns conversations and snippets. Retrieval returns message passages with speaker roles and archived source locations. The sample contains both an assistant's suggestion and a user's choice; a result's relevance does not make every passage a decision. The [worked example](using-history.md) explains how to interpret them.

## 4. Check the sample's health

```bash
./scripts/chatos --root Demo status
./scripts/chatos --root Demo doctor
```

A successful run does not establish full source coverage. Source reports distinguish disabled Codex capture from export-based ChatGPT input and unavailable live connectors. Health checks inspect the local archive and report these distinctions.

Run `./scripts/chatos --root Demo sync` again without changing the sample file; do not rerun `init`. Expect zero new chats and zero updated chats. The existing conversation is retained, not duplicated.

## Using your own sources

The initializer can also create an empty workspace for your own records:

```bash
./scripts/chatos init /absolute/path/to/your-workspace
./scripts/chatos --root /absolute/path/to/your-workspace sync
```

The new workspace has its own `chatos.json`, blank profile/preferences, empty project registry, and no installed schedule or host skill. It does not copy the maintainer's private workspace. Add supported ChatGPT JSON/ZIP exports to `your_ais/chatgpt/imports/` inside the selected workspace, then sync. The ZIP importer expects one `conversations.json` payload and does not download media.

To opt into local Codex history during initialization, supply `--codex-home /absolute/path/to/your/.codex`. Review that source choice before the first sync. Subsequent commands should keep using `--root` for the selected workspace. The main checkout's configured workspace is a separate personal installation.

Chief of Staff project routing, external delivery destinations, host skill installation, and scheduled maintenance require separate configuration. Cloning or initializing does not connect accounts or install these integrations. A complete guided onboarding experience and broader new-user validation remain open. Muse has normalized-input support only; raw export work remains deferred. See [features and limits](features.md).

## Optional display and developer checks

Plain-text reports work without extra packages. For Rich tables and colors, an optional environment can be created with uv:

```bash
uv venv
uv pip install --python .venv/bin/python -e ".[terminal]"
.venv/bin/python -m chatos --root Demo status
```

Add `--json` to a command when another program needs structured output. This changes the presentation, not the stored records.

The repository's tests use synthetic fixtures:

```bash
PYTHONPATH=src python3 -B -m unittest discover -s tests -v
```

Optional semantic-search dependencies and model files are separate from the core walkthrough. The [runtime reference](../workspace/chief_of_staff/reference/Runtime%20reference.md) covers maintainer operations and recovery.

For real-user setup stages and optional assistant access, follow [Guided onboarding](onboarding.md). For asking your AI to prepare reusable context, use [Context artifacts](context-artifacts.md). Portable migration is documented in [Portable bundles](portable-bundles.md).
