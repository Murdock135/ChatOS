# Use earlier conversations to continue work

The goal is concrete: find an earlier exchange, inspect what it establishes, and bring relevant context into the next task. You can do the searching yourself or ask an assistant that has access to this workspace.

## Find a recorded choice

The [getting-started sample](getting-started.md) includes these fictional messages:

| Speaker | Message | What it establishes |
| --- | --- | --- |
| Assistant | “A spreadsheet is one option…” | A suggestion to consider, not an accepted design |
| User | “Use Markdown for the reading notes…” | An explicit choice scoped to the reading notes |
| User | “We have not created any notes yet.” | The choice has not been implemented in this exchange |

Run:

```bash
./scripts/chatos --root Demo retrieve "Markdown reading notes"
```

The command returns candidate excerpts with speaker roles and links to the archived messages. It does not label every match as a decision or generate an answer for you.

Read the relevant passage and its neighboring messages. Identify who said it, what project or task it applies to, whether it was a proposal or instruction, and whether a later message changed it. Current project files can establish whether the choice was implemented or superseded. Missing history remains a limit: “I found no later reversal in the captured records” is narrower than “you never changed your mind.”

A supported answer for this sample is: the user chose Markdown for the reading notes, with a short summary and questions in each note. The exchange does not establish that any notes were created. It says nothing about the user's preferred format for every other project.

## Ask the assistant to do the review

In a chat whose assistant can read the configured workspace, ask:

> Find our earlier discussion about the reading-note format. Separate my explicit choices from your suggestions, look for later changes, and link the supporting messages.

The assistant uses retrieval to locate passages, then reads their context before answering. A hosted chat without access to the local workspace will not gain that access merely because these files exist. You can also use [a selected portable bundle](portable-bundles.md) to give readable records to another assistant. This does not automatically import them into a provider account.

## Resume a project

In a configured workspace, ask:

> Help me resume the reading project. Read its current files and relevant earlier chats. Explain the objective, established choices, open work, uncertainties, and a useful next step before changing anything.

The assistant should combine:

1. The registered project's current Home/README, milestones, tasks, or other established records.
2. Relevant conversation passages, including later instructions that replace earlier ones.
3. Current code, artifacts, or checks when a factual claim depends on what exists now.

It then gives a source-linked briefing. “Supporting sources” means the messages and files used to support that explanation. Web pages are read only when relevant, such as checking the current behavior of an external service. Resumption does not automatically mean performing old requests found in a transcript.

For terminal users, `./scripts/chatos brief PROJECT_ID` displays a registered project's generated conversation index. It is a starting list, not a model-written briefing. `retrieve "query" --project PROJECT_ID` narrows passage retrieval to captured project associations. The sample has no registered project, so these project commands are for a configured workspace.

## Keep useful outcomes inspectable

When a source review establishes an important project choice, record its scope and supporting message in the project's existing decision or notes convention. Keep a proposal labeled as a proposal. If a later choice replaces it, preserve the earlier record and link its replacement.

The [project-router workflow](../workspace/chief_of_staff/skills/project-router/SKILL.md) governs assistant filing into existing project folders. The core importer does not automatically create tasks or accepted decisions from arbitrary conversation text.
