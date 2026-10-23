# Core concepts

These terms distinguish what the system has captured from what a person or assistant concludes from it.

## Workspace

The visible data folder containing the readable chat archive, configuration, generated views, and operating records. The default is `workspace/` inside the repository; application code lives separately in `src/chatos/`. A selected workspace can be opened as an Obsidian vault. Keeping the workspace together makes its different kinds of records inspectable.

Source applications and live installed skills can remain outside this folder. The workspace may contain their captured records or dated copies. “One workspace” does not mean that every external source is physically moved into it.

## Source and capture

A **source** is the original conversation or file supplied by an application. A **capture** is the portion chat-OS obtained from it.

A conversation ID is stored together with the source app, so two applications using the same ID do not become the same chat. Available timestamps, message IDs, model information, and attachment references are retained where supplied. Missing values remain unknown.

A captured conversation can be partial: the source file may be missing, a desktop tool may omit replies, or an export may represent one point in time. A file existing in the archive does not establish that the entire original chat was captured. Attachment references also do not establish that the image or other media bytes were saved.

## Record, view, and index

- A **record** is the structured captured conversation stored in the database and written as JSON, with a readable Markdown rendering.
- A **view** is a generated way to browse records, such as a conversation index or dashboard. It can be regenerated.
- An **index** is a structure optimized for finding records or passages. Search indexes are not new evidence about what happened.

The running application reads its conversation state from SQLite. The original application remains the source for what it supplied; archived records preserve that available evidence. Markdown and JSON conversation files are generated from stored records. Editing them by hand does not change the source conversation and may be overwritten by sync. Keep annotations in authored notes with links to the source.

## Retrieval and evidence

**Search** returns matching conversations and snippets. **Passage retrieval** returns specific message excerpts with roles, identifiers, offsets, and links to their archived locations. The default ranking uses words in the query and the indexed text.

A relevant match is a candidate to read, not a verified answer. An assistant can use the passages as evidence, but must inspect context, distinguish speakers, and check later changes. Retrieval itself does not call a language model or load web pages.

## Decision, proposal, and completion

Suppose an assistant writes “We could use method A,” and you later write “Use method B for this experiment.” The first statement is a proposal; the second supports a scoped decision. Neither proves that method B was implemented.

A maintained decision note records the choice, scope, source, status, and any replacement. It is not an automatic log of every life decision. A task's completion needs evidence of the action or result, not just a matching discussion.

## Project and filing

A **project** is an identified owner of work, with a registered folder and existing notes or task conventions. Workspace paths and reviewed assignments provide stronger ownership evidence than a title keyword.

**Filing** means placing useful context or an accepted outcome with the project that owns it. The current `file-projects` command writes source-linked conversation indexes into configured project folders. It does not automatically extract decisions, create commitments, or complete tasks. An active assistant can do substantive filing after reading the sources and the destination's rules.

## Memory, instructions, and skills

**Memory** here means maintained or captured files containing preferences and useful context. It is not a claim that a model permanently remembers every chat.

**Instructions** tell the active assistant how to behave. A **skill** is a reusable instruction document, sometimes with supporting resources. The host must make it available and the assistant must apply it; a skill file does not run itself.

The workspace inventories accessible skills and memory and can archive dated copies. A live installed skill affects an assistant only through its host's loading behavior. Editing an archived copy does not update the installed skill. Human inspection of these records is independent of whether a host activates them.

## Sync, snapshot, and backup

**Sync** imports accessible source changes and refreshes local indexes, views, reports, and operating-file checks. It is not universal live synchronization with every chat application.

A **snapshot** is a dated copy of accessible behavior files, such as skills, instructions, and memory. A **database backup** preserves conversation state, revisions, and related database tables. They have different recovery scopes; neither automatically backs up every attachment or every source application.

A **scheduled run** needs a configured trigger and an available host. An enabled schedule does not establish that work completed. See [how it works](how-it-works.md) for the actual components and data flow.

## Local library annotations

A local title, note, or archive flag is your own annotation, stored separately from captured messages. The app keeps the original title and source ID visible. Generated copies in `workspace/your_ais/<source>/annotations/` are readable views of database state. Use the library or CLI to edit them. Archive hides a chat from the active library; it does not delete it, change the source app, or remove it from evidence search or the map. See the [library guide](chat-library.md).
