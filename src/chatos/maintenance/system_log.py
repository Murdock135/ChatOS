"""Append observed incidents and collect local Codex runtime errors, read-only.

Examples:
  python3 scripts/system_log.py collect
  python3 scripts/system_log.py record --kind chat --summary 'Tool failed' --status open
Recovery is a new record with --related EVENT_ID; earlier evidence is retained.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import sqlite3
import time
import uuid
import fcntl
from contextlib import contextmanager

from ..workspace import default_root, workspace_path
ROOT = default_root()
LOGS = workspace_path(ROOT, 'System/Logs')
LEDGER = LOGS / 'events.jsonl'
CODEX = Path.home() / '.codex'


def now():
    return datetime.now(timezone.utc).isoformat()


def load_events():
    if not LEDGER.exists():
        return []
    return [json.loads(line) for line in LEDGER.read_text().splitlines() if line.strip()]


@contextmanager
def exclusive(name):
    LOGS.mkdir(parents=True, exist_ok=True)
    with (LOGS / name).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def save(events):
    with exclusive('events.lock'):
        return _save_locked(events)


def _save_locked(events):
    LOGS.mkdir(parents=True, exist_ok=True)
    existing = load_events()
    ids = {e['id'] for e in existing}
    added = []
    for event in events:
        if event['id'] not in ids:
            added.append(event)
            ids.add(event['id'])
    with LEDGER.open('a') as f:
        for event in added:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
    all_events = existing + added
    lines = ['# System event log', '',
             'Append-only evidence ledger: [events.jsonl](events.jsonl). Times below are UTC.', '',
             'Runtime errors are unreviewed observations; they do not establish chat failure.', '',
             '| Time (UTC) | Kind | State | Observation | Evidence ID |',
             '| --- | --- | --- | --- | --- |']
    for event in sorted(all_events, key=lambda e: e['observed_at'], reverse=True):
        clean = lambda s: str(s).replace('|', '\\|').replace('\n', ' ')
        lines.append('| ' + ' | '.join(clean(event.get(k, '')) for k in
                     ['observed_at', 'kind', 'status', 'summary', 'id']) + ' |')
    view = LOGS / 'Event log.tmp'
    view.write_text('\n'.join(lines) + '\n')
    view.replace(LOGS / 'Event log.md')
    return len(added)


def collect():
    with exclusive('collector.lock'):
        return _collect_locked()


def _collect_locked():
    LOGS.mkdir(parents=True, exist_ok=True)
    checkpoint = LOGS / 'collector-state.json'
    state = json.loads(checkpoint.read_text()) if checkpoint.exists() else {}
    db = CODEX / 'logs_2.sqlite'
    connection = sqlite3.connect(db.as_uri() + '?mode=ro', uri=True)
    connection.execute('PRAGMA query_only=ON')
    try:
        connection.execute('BEGIN')
        high = connection.execute('SELECT coalesce(max(id),0) FROM logs').fetchone()[0]
        last = state.get('last_id')
        if last is None or last > high:
            rows = connection.execute(
                "SELECT id,ts,target,thread_id,feedback_log_body FROM logs "
                "WHERE ts>=? AND upper(level)='ERROR' AND id<=? ORDER BY id",
                (int(time.time()) - 86400, high)).fetchall()
        else:
            rows = connection.execute(
                "SELECT id,ts,target,thread_id,feedback_log_body FROM logs "
                "WHERE id>? AND id<=? AND upper(level)='ERROR' ORDER BY id",
                (last, high)).fetchall()
    finally:
        connection.close()
    tasks = {}
    for p in (CODEX / 'automations').glob('*/automation.toml'):
        text = p.read_text()
        target = re.search(r'^target_thread_id\s*=\s*"([^"]+)"', text, re.M)
        if target:
            tasks[target.group(1)] = p.parent.name
    events = []
    for row_id, ts, target, thread_id, body in rows:
        raw = body or ''
        lower = raw.lower()
        if 'timed out' in lower or 'timeout' in lower:
            summary = 'Runtime request timed out; task outcome unknown.'
        elif 'transport channel closed' in lower:
            summary = 'Tool transport channel closed; task outcome unknown.'
        elif 'failed to refresh available models' in lower:
            summary = 'Available-model refresh failed; task outcome unknown.'
        elif 'fail to delete session' in lower:
            summary = 'Session cleanup request failed; task outcome unknown.'
        else:
            summary = 'Runtime error recorded; message retained only in source database.'
        task = tasks.get(thread_id)
        events.append({'id': 'codex-runtime-' + str(row_id) + '-' + hashlib.sha256(
                           (str(ts) + raw).encode()).hexdigest()[:12],
                       'observed_at': datetime.fromtimestamp(ts, timezone.utc).isoformat(),
                       'recorded_at': now(), 'kind': 'scheduled-task' if task else 'runtime',
                       'status': 'unreviewed', 'summary': summary,
                       'source': {'path': str(db), 'table': 'logs', 'row_id': row_id,
                                  'target': target, 'body_sha256': hashlib.sha256(raw.encode()).hexdigest()},
                       'thread_id': thread_id, 'task_id': task,
                       'impact': 'Unknown; error-level log evidence only.', 'related': None})
    count = save(events)
    temp = checkpoint.with_suffix('.tmp')
    temp.write_text(json.dumps({'last_id': high, 'checked_at': now(),
                               'source': str(db), 'initial_window_hours': 24}, indent=2) + '\n')
    temp.replace(checkpoint)
    print(json.dumps({'added': count, 'observed_errors': len(rows), 'last_id': high}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('collect')
    record = sub.add_parser('record')
    record.add_argument('--kind', choices=['chat', 'scheduled-task', 'runtime', 'recovery'], required=True)
    record.add_argument('--summary', required=True)
    record.add_argument('--status', choices=['open', 'unreviewed', 'resolved', 'blocked'], default='open')
    record.add_argument('--evidence', default='Observed in current conversation')
    record.add_argument('--impact', default='Not assessed')
    record.add_argument('--related')
    record.add_argument('--thread-id')
    record.add_argument('--task-id')
    args = parser.parse_args()
    if args.command == 'collect':
        collect()
    else:
        event = {'id': str(uuid.uuid4()), 'observed_at': now(), 'recorded_at': now(),
                 'kind': args.kind, 'status': args.status, 'summary': args.summary,
                 'source': {'evidence': args.evidence}, 'impact': args.impact,
                 'related': args.related, 'thread_id': args.thread_id, 'task_id': args.task_id}
        save([event])
        print(json.dumps({'id': event['id'], 'status': event['status']}))


if __name__ == '__main__':
    main()
