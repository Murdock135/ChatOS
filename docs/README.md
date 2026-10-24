# Understand and use chat-OS

chat-OS keeps captured AI conversations and related context in a visible local workspace. You can browse and search the records yourself. An assistant with access to the workspace can also use them to help you continue earlier work.

Start with the problem and product, then follow a conversation through the system:

| Read | What you will learn |
| --- | --- |
| [Product and purpose](product.md) | Who this serves, what it offers, and the difference between today's prototype and the intended app |
| [Getting started](getting-started.md) | What a fresh clone can do, what needs configuration, and the everyday commands |
| [Core concepts](concepts.md) | Sources, captures, memory, skills, projects, and the Chief of Staff role |
| [Features and limits](features.md) | Which capabilities are implemented, which need an assistant, and which remain future work |
| [How it works](how-it-works.md) | Architecture, data flow, storage, and the interfaces used by people and assistants |
| [Your own assistant](assistant-workflow.md) | How a new user gives access, gets cited briefings and preserves project outcomes without private maintainer skills |
| [Using earlier conversations](using-history.md) | A worked example of finding a recorded choice and resuming a project with evidence |

These pages explain the product. The [runtime reference](../workspace/chief_of_staff/reference/Runtime%20reference.md) contains maintainer commands and recovery procedures. [Current state](../workspace/STATE.md) and the generated `STATUS.md` report describe this particular installation; they are not prerequisites or promises about a new installation.

The [implementation roadmap](../workspace/IMPLEMENTATION.md) tracks incomplete work. The [verification record](verification.md) states what was inspected and tested for this documentation pass.

[Chat-library guide](chat-library.md) — browse, annotate, archive/restore, inspect context, and check health in the local browser app.

[Source coverage](source-coverage.md) — inspect capture counts, inherited fork history, unavailable replies, and the limits of a successful sync.

[Repository and workspace layout](reorganization.md) — the implemented source/workspace split, canonical folders, local assistant shortcuts, and recovery locations. The [original proposal](proposals/0001-repository-and-workspace-layout.md) is retained as design history.

Links into `workspace/` describe a configured installation and are absent from a fresh clone. The public guides and fictional walkthrough do not require those private records.

[Optional semantic setup](semantic-search.md) — embedding-model and dependency installation, indexing, hybrid retrieval, clustering and map freshness.

## Complete your own workflow

1. [Source coverage](source-coverage.md): understand accessible records and missing evidence.
2. [Search and clustering evaluation](search-evaluation.md): measure exact passages, scope, negatives and labeled map pairs.
3. [Context artifacts](context-artifacts.md): ask your AI for scoped context, inspect it and record explicit review.
4. [Guided onboarding](onboarding.md): initialize independently, inspect readiness, choose assistant access and verify backup.
5. [Portable bundles](portable-bundles.md): select local records/context for a different assistant without automatic transmission.
