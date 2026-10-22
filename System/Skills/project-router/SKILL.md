---
name: project-router
description: Identify the owning project or paper for Zayan's discussions and file substantive decisions, tasks, research notes, and artifacts in its existing workspace, preserving source links and recording unresolved routing.
---

# Project router

Use this for substantive project work entering through the Chief of Staff chat, even when the user does not explicitly say “save this.” Keep ordinary small talk out of project files. The complete conversation stays in the conversation archive; useful project material belongs with its owner.

## Identify the owner

Read the live [project registry](../../Projects/registry.json) and relevant [routing guide](../../Projects/Project routing.md). The registry is a verified starting inventory, not an exhaustive list of Zayan's projects. Check that the destination still exists and read its Home/README, applicable AGENTS.md instructions, and existing conventions before writing.

Prefer the user's explicit project or file reference, then current project context and source evidence. A matching keyword is a candidate, not proof. Select the narrowest supported owner: manuscript-specific work belongs to that paper; shared work belongs to its parent project. Generic “SPARQ” does not select v1 versus v2, and generic “LLM” does not select a research project.

For multiple projects, split independently owned items or keep one canonical shared item and cross-link it. Record all relevant project IDs on the conversation. If ownership is ambiguous, preserve the item in the routing queue with candidates and ask one targeted question when needed. Do not create a new project or choose a stale path merely to avoid an unresolved item.

## File the useful result

Follow the destination's workflow, rather than inventing a second task or notes system:

- Decisions: record the decision and its scope, rationale where useful, and source. Distinguish user decisions, assistant proposals, and unresolved questions.
- Accepted project actions: update existing milestones/tasks in place; avoid duplicate checkboxes. Discussion alone is not commitment. Preserve explicit owner and due date; do not invent either.
- Research progress/results: use the owner's Research Log. Substantial drafts, derivations, or experiments belong in Scratch, with its scratch index updated as the vault convention requires.
- Personal-project notes: use that project's Notes folder and Milestones as appropriate.
- Code and artifacts: use the registered related repository or existing artifact location after checking its instructions and actual state. Do not infer branch, runtime, or repository ownership from a paper title.
- Shared resources: follow the vault's Library convention and link from projects rather than copying the same resource into each project.

Treat automatic filing as preserving relevant information, not authority to implement every idea mentioned. Do not change a manuscript, code behavior, schedule, or task completion state solely because it was discussed.

## Verify and leave a receipt

Before creating an entry, search for the existing source/item to make retries and repeated conversations update the same record. Preserve the source conversation ID or note link, source turn/time when available, item type, owner, and whether the content is proposed, accepted, or completed.

After writing, reopen the destination and verify the content and links. Add a concise receipt to [Routing log](../../Projects/Routing log.md): source, project ID(s), item, destination, and status. Only use `filed` for a verified write. A topic tag or local copy does not count as filing into an external project.

If access or permissions prevent the write, retain a reviewable draft in [Routing queue](../../Projects/Routing queue.md) with the exact intended destination and blocking reason. Use `pending` rather than claiming success. Resume delivery when access is available; preserve the receipt after resolving the queue item.

## Local activation

This skill is invoked by this vault's root AGENTS.md. It is not globally installed or an always-on router for other apps. Source synchronization must supply those conversations before they can be routed. Recheck the registry when paths or project identities change.
