# Feedback log

Record negative feedback Zayan expresses about the assistant's responses, actions, or results so recurring mistakes can be corrected. This is a record of observed feedback, not a judgment about Zayan's mood or personality.

## Recording rules

- Log explicit dissatisfaction, objections, frustration directed at assistant behavior, or corrections that clearly identify an unwanted response or action.
- For a plausible but ambiguous negative response, label the interpretation **uncertain** and state the observable evidence. Do not assert an emotion or motive.
- Neutral clarifications, added requirements, brief wording, disagreement about external subjects, and routine corrections alone do not establish negative feedback. This conversation's requests to include system files, scheduled tasks, and logs are scope additions, not evidence of dissatisfaction.
- Include the date/time when available, source chat or task link/ID when known, the relevant user wording, the preceding assistant behavior, interpretation and confidence, the adjustment made, and any unresolved follow-up. Preserve only the relevant excerpt; link to the conversation for context.
- Record feedback when observed in accessible conversations. Update the response or approach promptly within the user's authorized scope. Record later recovery or user confirmation without rewriting the original evidence. Do not claim the user is satisfied unless they say so.
- Review relevant prior feedback before repeating similar work. Repeated patterns may inform proposed guidance; do not turn one uncertain interpretation into a permanent user preference.
- Keep this log separate from technical failure events. Cross-link an incident in [[Event log]] if the feedback concerns a logged failure.
- Maintain quietly as part of the work. Surface an entry when it helps explain an adjustment or when Zayan asks. Do not interrupt work to ask the user to rate their sentiment.

## Coverage

Established on 2026-10-22. A bounded phrase-cue sweep of the captured archive produced six review candidates: five explicit feedback items (two already logged) and one neutral dashboard bug report. These were reviewed against source context. This is not an exhaustive historical audit or automatic sentiment monitor; unseen cross-app history remains uncovered. Candidate and review state is in the local runtime database, with generated views under System/State and System/Feedback.

## Entries

### 2026-10-22 — Ideas lacked implementation detail

- Source: [[2026-10-22 Chief of Staff and chat archive]], Codex ID `01a16442-0b52-7260-8019-a855dff30567`.
- User wording: “i don't understand the ideas. for example 'Decision history'. what is this?” and “are you proposing making a python script, a skill, an mcp, a new project structure for the repo? it's not clear”.
- Context: ideas.md listed benefits and small experiments without stating the software or file changes proposed.
- Interpretation: explicit negative feedback about clarity of the deliverable. No emotional state is inferred.
- Adjustment: rewrote the ideas with component types, proposed files, how each would be used, dependencies where relevant, and checks. Expanded Decision history into a concrete example of project-owned decision records maintained by the router.
- Outcome: document revision applied; user-confirmed resolution is pending.

### 2026-10-22 — Skill missing from the snapshot index

- Source: [[2026-10-22 Chief of Staff and chat archive]], Codex ID `01a16442-0b52-7260-8019-a855dff30567`.
- User wording: “you just created a new skill, which i don't see in the skills index of the latest snapshot. i wonder what other loopholes you have”.
- Context: project-router was created under workspace System/Skills, while snapshot discovery scanned only Codex skill roots. The system also lacked a live consolidated skills index and drift detection.
- Interpretation: explicit negative feedback identifying an omission and questioning system reliability; no additional emotional state is inferred.
- Adjustment: added shared skill discovery, a current inventory, workspace-inclusive snapshots, drift/integrity checks, concurrency protection for logs, and regression tests. Documented remaining gaps in the consistency audit.
- Outcome: repair applied and verification performed; user-confirmed resolution remains pending. No exhaustive reliability guarantee is implied.

<!-- For each new entry, append a dated entry using:
### YYYY-MM-DD — Short issue label
- Source: conversation/task link and ID when known; event time and timezone if available.
- User wording: a concise verbatim excerpt.
- Context: the assistant response/action being corrected.
- Interpretation: explicit negative feedback or uncertain interpretation, with evidence.
- Adjustment: what changed, or the planned next action if still open.
- Outcome: unresolved, change applied, or user-confirmed resolution; cite evidence.
Append later developments without overwriting the original feedback.
-->

<!-- feedback-review:4ab3ab45fbc57dad440cf809b0fb0b49cfdeccc1bdc38d3110c09254eb5ce5cd -->
### 2026-10-22 — From my repos, sparq and research-concerted_abduction, understand my coding style and add them into memory. Call it my preferred coding style.    Pick only the good parts. If any part of my code does not follow good coding practice, do not

- Source: [codex:01a16435-1257-7270-86dc-6f2708b70030](file:///Users/zayan/Documents/obsidian_vaults/chats/Conversations/2026/codex-01a16435-1257-7270-86dc-6f2708b70030.md); message msg_01a1643c-b6d0-7c60-a310-4d92d6c0438c
- User wording: you only opened 'repository documentation may be outdated'
- Interpretation: confirmed_feedback; The assistant said three files were queued; the user reported that only one was visible.
- Adjustment: Distinguish queued/open acknowledgments from verified visibility when presenting multiple artifacts.
- Outcome: Review recorded; user-confirmed resolution is unknown.

<!-- feedback-review:71fe6a978b9075d7603aeccb55abb6e0457ffef497651e5e795ae8c74abaf2c0 -->
### 2026-10-09 — Explain measured metrics

- Source: [codex:01a11f02-1ce9-7113-a7e1-e18a383889e4](file:///Users/zayan/Documents/obsidian_vaults/chats/Conversations/2026/codex-01a11f02-1ce9-7113-a7e1-e18a383889e4.md); message item-19
- User wording: i don't understand anything from the table you provided in manager_update.py
- Interpretation: confirmed_feedback; The user explicitly identified an assistant-produced metrics table as incomprehensible.
- Adjustment: On project resume, explain each metric, what was actually measured, and the limits of the experiment; historical code state is not revalidated here.
- Outcome: Review recorded; user-confirmed resolution is unknown.

<!-- feedback-review:3ba9ee1e6184a48588779edf1ce9872f6fdf61e56edef76731c97dcbdd670a56 -->
### 2026-08-07 — what is this project about

- Source: [codex:019fdd8b-262d-7712-b9e5-350ccecc8d69](file:///Users/zayan/Documents/obsidian_vaults/chats/Conversations/2026/codex-019fdd8b-262d-7712-b9e5-350ccecc8d69.md); message item-20
- User wording: i don't understand the JSON example form. why doesn't it follow the ExtractorOutput schema in [types.py](src/concerted_abduction/types.py)
- Interpretation: confirmed_feedback; The user pointed to an example that did not follow the declared output schema.
- Adjustment: Read the actual input/output schema and validate examples against it before claiming contract compliance; historical source state is not revalidated here.
- Outcome: Review recorded; user-confirmed resolution is unknown.

## Review mechanics

Ordinary sync produces a conservative [review queue](Feedback/Review%20queue.md). A cue remains unclassified until an agent checks its context. Confirmed/uncertain feedback can be recorded with the review-feedback command; neutral requests are dismissed without adding negative feedback. Stable source/message/text identities prevent repeated logging. No emotion or motive is inferred.

## 2026-10-22 — README audience was wrong

- Source: [conversation](../Conversations/2026/codex-01a16510-7f12-78b0-afa9-d5aee24d915b.md), codex:01a16510-7f12-78b0-afa9-d5aee24d915b.
- User wording: “it seems that you've written README for yourself. the README should be for new users”; followed by “you can move whatever you need somewhere else”.
- Context: README led with agent ownership, runtime internals, an undifferentiated command list, and recovery details.
- Interpretation: explicit correction of the assistant's documentation audience; high confidence. No emotional state inferred.
- Adjustment: rewrote README for first-time readers with purpose, entry points, example questions, basic sync/health commands, and source/privacy limits. Moved maintainer commands and recovery details to System/Runtime reference.md and linked it from the system index.
- Outcome: revision applied; local links, code fences, CLI command syntax, and diff whitespace verified. User-confirmed resolution remains unknown.
