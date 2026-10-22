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

Established on 2026-10-22. Applies to feedback actually visible during work in this vault. No historical feedback audit or automatic cross-app sentiment monitoring has been performed.

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
