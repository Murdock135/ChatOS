---
type: ideas
project: chat-os
updated: 2026-10-22
status: exploratory
---
# Ideas for improving the chat-OS

Each proposal below says **what we would build, where it would live, and how you would use it**. Paths are proposed locations, not files that already exist. These ideas are not approved implementation tasks; required work is in [IMPLEMENTATION.md](IMPLEMENTATION.md).

Current progress: a project-briefing skill, offline dashboard, keyword/experimental LSA topic views, VS Code tasks, and local sync/retry checks now exist. These are bounded initial implementations; the descriptions below remain proposals for their fuller versions. Decision-history records and a new MCP server have not been built.

## What the implementation terms mean

- **Markdown/JSON records:** information stored in files, with a defined format.
- **Skill:** instructions that tell the assistant how to perform a recurring kind of work. A skill needs an active agent to carry it out; the file does not run by itself.
- **Python script:** code for repeatable operations such as importing, comparing, validating, or summarizing structured records.
- **Scheduled job:** a configured trigger that starts work periodically. It needs a script or agent workflow to run.
- **UI:** a human interface, such as a local status page or a VS Code action, over the underlying records and commands.
- **MCP server:** an integration exposing operations to compatible clients. It would be useful if several apps needed the same controlled project/search tools. A new MCP server is not the initial implementation proposed for any item below.

An improvement can combine these. Use files and agent instructions first when they are sufficient; add code where deterministic or unattended execution is needed. A folder name alone does not implement a feature.

## 1. Decision history

**Proposed form: project-owned Markdown records + an extension to the project-router skill.**

This means keeping a readable record of explicit decisions so we can answer “what did we choose, and what changed?” without reconstructing every chat.

**What we would build:** agree on a small decision-entry format: stable ID, date, decision, status, source conversation, reason if stated, and a link to any decision it supersedes. Store entries in an existing suitable project note, or introduce a `Decisions.md` within that project if needed. Extend the router to maintain those entries when it encounters an explicit decision. Keep the conversation as the original evidence.

**Example:** you have chosen to run the chat-OS on your Mac for now. Its decision entry would link to that message. If you later choose an always-on server, add a new entry linked to the previous one and mark the earlier choice as superseded. Do not silently erase the earlier choice or invent your reason.

**How you use it:** “Why are we running this only on my Mac?” or “What did we decide about deployment?” I read the decision entries and their supporting conversations.

**First implementation:** a record format and a router instruction change. No standalone Python script, MCP server, or wholesale project restructuring is needed. Later, a validator could check source links and supersession references.

**Check:** record a decision, explicitly revise it, then verify that both the old and current choices can be retrieved with the right source. A suggestion must not become an accepted decision automatically.

## 2. Project context packs

**Form:** a new project-briefing skill producing a Markdown brief on demand.

**Build:** `System/Skills/project-briefing/SKILL.md`, reading the project registry, current tasks, decision records, artifacts, and relevant conversations. Start by returning the brief in chat; save a copy only when useful.

**Use:** “Resume SPARQ v1 JAMIA.” I return the current objective, established decisions, open tasks, blockers, and useful files, each backed by sources.

**Check:** a fresh session can resume a project accurately from the brief. Later code could assist retrieval, but it is not required for the first version.

## 3. What changed since last time?

**Form:** saved project checkpoints + a comparison script, presented through the briefing skill.

**Build:** `System/State/project-checkpoints/` for the last reviewed record IDs/hashes, and a script such as `System/Scripts/project_changes.py` to identify changed tasks, decisions, and artifacts. The agent explains those changes using source evidence.

**Use:** “What changed in Concerted Abduction since our last review?”

**Check:** new changes appear once; unchanged material is not described as new. This needs stable records and checkpoints first.

## 4. Handoff bundles

**Form:** an agent handoff skill + an optional Markdown output file.

**Build:** `System/Skills/project-handoff/SKILL.md`. It assembles the objective, relevant sources, current state, constraints, open questions, and authorized next action. Retain one local handoff record when needed.

**Use:** “Prepare a handoff so I can continue this in Muse.” I create a brief you can transfer. Automatic delivery would require a separately verified integration and authorization.

**Check:** the receiving session can identify what to do and what remains undecided without being given the entire chat history.

## 5. Project dependencies

**Form:** explicit relationship records in the project registry + a generated diagram.

**Build:** add verified dependency edges, such as one project's experiment depending on a library change. Initially render a Mermaid diagram from those records; add a generator only when manual maintenance becomes repetitive.

**Use:** “What is blocking this paper?” I show its recorded dependencies and the evidence for their current state.

**Check:** related projects are not called dependencies unless one actually relies on the other. No new top-level project hierarchy is required.

## 6. Memory freshness

**Form:** a memory-entry schema + a review script/agent workflow.

**Build:** add source, last-verified date, and review conditions to selected vault-owned memory records. A future script such as `System/Scripts/memory_review.py` lists entries needing review; an agent verifies them or leaves them explicitly unresolved. Imported snapshots remain historical evidence.

**Use:** “Which assumptions about my projects may be stale?”

**Check:** a dated assumption is flagged for verification, not automatically treated as false or silently rewritten. This initially applies to a bounded set of consequential entries, not every archived file.

## 7. Feedback-driven guidance changes

**Form:** an extension to the existing feedback-review workflow, producing a proposed instruction edit.

**Build:** add a procedure that reads relevant feedback entries, identifies a supported recurring problem, and drafts a narrow change to the appropriate skill or operating file. Link the proposed change to its evidence and retain the outcome.

**Use:** “We keep having this problem; update how you handle it.” I show and apply the authorized correction in the right active file.

**Check:** one ambiguous reaction does not become a universal preference. No separate sentiment-analysis service or MCP is proposed.

## 8. Inspect the evidence behind an answer

**Form:** source references in generated records, with a small navigation UI later.

**Build:** first ensure summaries, decisions, and project notes link to their supporting conversation/message IDs. Once those references are reliable, optionally add a local page or VS Code command that opens the cited record.

**Use:** “Where did you get that?” I show the source wording and context.

**Check:** the cited record actually supports the claim. The first version is a data/linking convention, not a new MCP server.

## 9. Project vocabulary

**Form:** a data update to the existing project registry + router examples.

**Build:** maintain confirmed aliases in `System/Projects/registry.json` and add examples of confusing names to routing checks. Keep related names distinct when they identify different papers or repositories.

**Use:** say “the JAMIA paper” and have it resolve to the verified owner; say only “SPARQ” and have the router use context or leave ambiguity visible.

**Check:** aliases improve matching without merging SPARQ v1 and v2. No new script is required initially.

## 10. Filing previews and reviewable changes

**Form:** an extension to the project-router skill + a draft change or diff.

**Build:** for uncertain ownership or consequential overwrites, produce the proposed destination, supporting evidence, and exact file change before applying it. Store unresolved drafts in the existing routing queue. Ordinary unambiguous filing can proceed within the authorized scope.

**Use:** “Where would this go?” I show the actual destination and content, not just a topic label.

**Check:** correcting a proposed route changes the target without leaving duplicate records. This combines the earlier “Where does this belong?” and “Reviewable filing changes” ideas.

## 11. VS Code actions

**Form:** workspace task configuration first; a custom extension only if needed later.

**Build:** after the underlying commands work, expose sync and status through `.vscode/tasks.json`. Add simple navigation to the routing queue and briefing workflow. A true custom command-palette UI may require an extension; it is a separate later choice.

**Use:** run a named workspace task rather than remembering a Python command.

**Check:** the action runs the same tested command and surfaces its actual exit status. This does not itself build sync, retrieval, or scheduling.

## 12. Local dashboard

**Form:** a read-only local web UI, backed by existing structured state.

**Build:** a small `ui/` application showing source freshness, project activity, pending deliveries, and incidents. Start with read-only views over sync/task records. Its serving mechanism and UI framework would be chosen at implementation time.

**Use:** open one local page to see what needs attention and follow links to the underlying records.

**Check:** unavailable or stale data is visible; an attractive page must not imply healthy sync. This depends on the operational records in the roadmap.

## 13. Semantic map with a time view

**Form:** a visualization over the retrieval index, with topic links retained in files.

**Build:** once semantic indexing works, add a graph/list view to the local UI with time filters and source links. Render clusters from indexed data rather than inferring them from folder names alone.

**Use:** explore conversations related to a research idea across dates and apps.

**Check:** topic groups are useful on representative imported chats, and a conversation can appear in several groups. An interactive map is optional; core semantic organization remains required work in the roadmap.

## 14. Conversation-to-artifact trail

**Form:** provenance fields on artifact records + a generated view.

**Build:** record which conversation/turn produced a note, experiment, manuscript revision, or code artifact. Use those relationships to render a timeline or linked list. Start with ordinary file links; add a script when repeated rendering justifies it.

**Use:** “Show me how we got from that discussion to this result.”

**Check:** the trail points to actual outputs and delivery receipts, and distinguishes a draft from an implemented result.

## 15. Weekly portfolio review

**Form:** a portfolio-review skill + a scheduled agent run once on-demand review works.

**Build:** `System/Skills/portfolio-review/SKILL.md`, reading project status, commitments, blockers, and pending deliveries. Configure a periodic trigger separately and retain its run result. The weekly cadence is a proposal, not an existing schedule.

**Use:** receive a concise review of real open loops and useful next actions, with links to the projects involved.

**Check:** the review finds supported issues and advances already authorized work without inventing priorities, deadlines, or new commitments.

## 16. Dependency-triggered follow-up

**Form:** persisted dependency/action state + a check in the scheduled agent workflow.

**Build:** record a specific blocker, how to verify it, and the authorized action to take once resolved. The runner checks that condition and records an action receipt before treating the follow-up as delivered.

**Use:** “When that experiment finishes, update the project note with its result.”

**Check:** the condition is actually met, and retries do not apply the same external action twice. This needs durable task state and a functioning runner.

## 17. Notification budget

**Form:** notification policy + persistent delivery state in the runner.

**Build:** group related actionable events, remember what was already reported, and suppress unchanged routine checks. Define what should still interrupt promptly, such as a failure requiring action.

**Use:** receive a useful consolidated update instead of repeated unchanged messages.

**Check:** deduplication reduces noise without hiding unresolved actionable failures. No new chat app or MCP service is required.

## 18. Failure-pattern review

**Form:** a grouping/report script + an agent review procedure.

**Build:** read the existing event ledger, group similar symptoms, and generate a report with representative event IDs. The agent checks whether shared symptoms really have the same cause before proposing a fix.

**Use:** “What keeps failing, and what should we fix first?”

**Check:** the report distinguishes observed errors, unknown impact, and verified causes. It does not declare a whole chat failed from one low-level error.

## 19. Replayable sync audit

**Form:** per-run JSON manifests + an import/replay command.

**Build:** retain source record identities/hashes, parser version, outputs, skips, and failures for a sync run. Test replay against retained fixtures or a consistent source snapshot in an isolated directory, without repeating external side effects.

**Use:** “What did yesterday's sync change?” or “Can we reproduce this import?”

**Check:** the same input produces the expected records with no duplicates. This extends the sync audit trail; it is not a full copy of the Mac or a new MCP server.

## 20. Adapter compatibility checks

**Form:** non-sensitive source fixtures + automated tests in `tests/`.

**Build:** small representative examples for each importer and tests for edits, model changes, missing fields, and malformed records. Run them when adapters or dependencies change.

**Use:** there is no new user interface; this gives us evidence that sync still works after a change.

**Check:** a source schema change causes a meaningful test failure or explicit unsupported-field report rather than silent data loss.

## What to try first

After the first working import/sync, start with **decision records**, **project briefings**, and **filing previews**. These can improve everyday use with small changes to files and skills. Dashboard/graph work should follow reliable underlying data.

When promoting any idea into the implementation backlog, specify its component type, affected files, invocation/trigger, dependencies, and acceptance check. Do not describe a benefit alone as if it were an implementable feature.
