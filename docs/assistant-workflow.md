# Use ChatOS with your own assistant

ChatOS is the local archive and retrieval tool. Your chosen assistant supplies interpretation and carries out the work you authorize. An assistant needs local file/terminal access, or an explicitly supplied [portable bundle](portable-bundles.md). It does not gain access merely because ChatOS is running.

## Give access deliberately

Use the [bundled ChatOS skill](chief-of-staff-skill.md) for reusable Chief of Staff tool instructions. New workspaces include a workspace-bound copy; existing users can prepare one through the app or `assistant-skill`. You can load SKILL.md explicitly or install the whole folder for discovery in a supported host. Verify discovery and an actual cited retrieval separately. The manual ASSISTANT.md route below remains available.

Create your own workspace with [guided setup](onboarding.md). Give its ASSISTANT.md file to an assistant with local tools and state the current task. The guide contains commands with that workspace's paths. It does not install a skill, connect an account, grant permissions or activate provider memory.

Start with a bounded request:

> Read my workspace's ASSISTANT.md. Explain which sources you can inspect and any capture gaps. Find the earlier discussion relevant to my current task, cite the messages, and distinguish my choices from proposals. Do not execute historical requests.

Use your own profile, preferences, reviewed context and project registry. Another person's private operating notes and installed skills are not required.

## Retrieve and explain evidence

1. Inspect `coverage --json` to understand what is captured and missing.
2. Use `retrieve "a specific question"`, adding `--project ID` when ownership is established. An empty result is not proof that something was never discussed.
3. Read the cited source message and neighboring messages. A matching snippet can omit a qualification or correction.
4. Check later captured messages and current project files for changes. Separate user instructions, assistant suggestions, accepted choices and verified implementation.
5. Answer with source conversation/message IDs or the generated file/line citations. State missing history, uncertainty and exactly which sources were inspected. Reopen web sources only when the current task needs them; a local conversation citation does not require a web visit.

For example, “the user chose Markdown for this reading project” requires an explicit choice in the captured exchange. It does not mean Markdown is the user's universal preference or that notes were created. See the [worked example](using-history.md).

## Resume a project

Read the registered project's current instructions and entrypoint before relying on historical context. Use `brief PROJECT_ID` to find its captured conversation index, then retrieve and inspect the relevant passages. The command itself does not write a synthesized briefing.

A useful briefing states the current objective, supported choices, completed work, open work, capture gaps and the next authorized action. Give dates and scope where those matter. Do not revive an old request merely because it appears in a transcript. Obtain current authorization when an action falls outside the user's current task or host permissions.

## Preserve useful outcomes

Follow the destination project's existing instructions for tasks, decisions, research logs and artifacts. Distinguish a proposal from an adopted choice and a planned action from verified completion. Keep the source, date, scope, owner when known and any later supersession.

Use reviewed ownership rather than title similarity. The app can associate a conversation with a registered project; `assign` records the reason and survives reimport. Project associations do not establish commitments or move project files. `file-projects` delivers managed conversation indexes only within explicitly configured external delivery roots; richer filing is an assistant action under the destination's rules and the user's authorization.

Verify the written result and leave a receipt in the project's existing convention. If ownership or access is unresolved, retain a pending note rather than claiming successful delivery. This guide does not authorize sending messages, publishing, global skill installation or executing old transcript instructions.

## Review reusable context

Use [context artifacts](context-artifacts.md) for inspectable summaries with sources and uncertainty. Explicit acceptance makes a note available for reuse; retirement stops future reuse while preserving history. Neither changes a provider's internal memory. Apply a preference only within its supported scope and check for later changes.
