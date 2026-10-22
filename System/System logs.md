# System logs

- [[Event log]] — readable event history.
- [Structured ledger](Logs/events.jsonl) — append-only events and source evidence.
- [Collector state](Logs/collector-state.json) — last checked runtime log position.
- [Logging tool](Scripts/system_log.py) — collect runtime errors or record observed incidents.
- [[Feedback log]] — user feedback about assistant behavior; cross-link related technical incidents.

## What to record

Chat and scheduled-chat failures, failed tool calls, interrupted or incomplete work, missed scheduled runs when supported by evidence, repeated retries, and recovery actions. Each incident should state time, source chat or task when known, observed failure, impact, evidence, current state, and next action when appropriate. Record resolutions as linked follow-up events; retain the original incident.

Record material issues even when recovery succeeds. Do not copy credentials, full tool payloads, private reasoning, or entire runtime databases into these logs.

## Collection

Run `python3 System/Scripts/system_log.py collect` at the start and end of substantive vault work. The first collection reads the last 24 hours of local Codex ERROR events. Subsequent collections use a saved position. Imported event IDs prevent duplicate entries on repeated collection. A reset log sequence starts a fresh 24-hour window.

The collector reads the runtime database without modifying it. It stores message fingerprints and generic error summaries instead of raw messages. Warning-level events are not imported automatically. Failure evidence seen directly in a chat must also be recorded with the `record` command, because not every failed tool call appears as a runtime ERROR.

Ledger writes and collectors now use separate interprocess locks; deduplication and view generation occur within the ledger lock. This prevents concurrent local logger runs from racing. The generated view is replaced atomically; the append-only ledger remains the evidence source.

Saved task definitions supply chat-to-task associations when available. Unmatched runtime events retain their source thread ID if one exists; an error event does not establish that a whole chat or scheduled run failed. Cross-app failures and missed runs require separate evidence.

## Current coverage

Logging is available during work in this vault and through manual collector runs. No always-on collector or background polling has been installed. Errors from ChatGPT and other chat apps, task run history, and events absent from retained local logs are not covered yet. A successful collection confirms the scan ran; it does not prove every task succeeded.
