"""Read-only source adapters. No browser sessions, credentials, or private APIs."""
from pathlib import Path
import json
import re
import sqlite3
from .core import timestamp

HARNESS = ('# AGENTS.md instructions', '<environment_context>', '<external_codex_apps_open_page>',
           '<permissions instructions>', '<collaboration_mode>', '<system_reminder>')


def read_codex(path, info=None):
    info = dict(info or {})
    messages, history, runs, warnings = [], [], [], []
    model, effort, turn_id = info.get('model'), info.get('reasoning_effort'), None
    meta, last_time = {}, None
    with Path(path).open() as f:
        for line_number, line in enumerate(f, 1):
            try:
                event = json.loads(line)
            except ValueError:
                warnings.append({'line': line_number, 'reason': 'incomplete_or_invalid_json'})
                continue
            kind, payload = event.get('type'), event.get('payload') or {}
            last_time = event.get('timestamp') or last_time
            if kind == 'session_meta':
                if info.get('id') and payload.get('id') != info['id']:
                    raise ValueError('Source conversation identity mismatch')
                meta = {k: payload.get(k) for k in ['id','timestamp','cwd','originator','cli_version','source','model_provider']}
            elif kind == 'turn_context':
                model = payload.get('model') or model
                effort = payload.get('effort') or payload.get('reasoning_effort') or effort
                turn_id = payload.get('turn_id')
                history.append({'turn_id': turn_id, 'timestamp': last_time, 'model': model, 'effort': effort})
            elif kind == 'response_item' and payload.get('type') == 'message':
                role = payload.get('role')
                phase = payload.get('phase') or payload.get('channel')
                if role not in ['user','assistant'] or phase in ['analysis','reasoning']:
                    continue
                pieces = [p.get('text', '') for p in payload.get('content', [])
                          if p.get('type') in ['input_text','output_text','text']]
                text = '\n'.join(pieces)
                attachments = [dict(type=p.get('type'), reference=p.get('image_url') or p.get('image_path'))
                               for p in payload.get('content', []) if p.get('type') in ['input_image','image']]
                if role == 'user' and text.lstrip().startswith(HARNESS):
                    continue
                if text.startswith('<send_user_message_question_reply>'):
                    try:
                        answers = json.loads(re.sub(r'</?send_user_message_question_reply>', '', text).strip())
                        text = '\n'.join(str(x.get('question','')) + '\n' + str(x.get('answer','')) for x in answers)
                    except (ValueError, TypeError):
                        pass
                if not text and not attachments:
                    continue
                messages.append({'id': payload.get('id') or f'line-{line_number}', 'role': role,
                                 'phase': phase, 'text': text, 'timestamp': last_time, 'turn_id': turn_id,
                                 'model': model if role == 'assistant' else None,
                                 'reasoning_effort': effort if role == 'assistant' else None,
                                 'attachments': attachments})
            elif kind == 'event_msg' and payload.get('type') in ['task_complete','turn_aborted','task_started']:
                runs.append({'event': payload['type'], 'turn_id': payload.get('turn_id'),
                             'timestamp': last_time, 'started_at': payload.get('started_at'),
                             'completed_at': payload.get('completed_at')})
    identity = info.get('id') or meta.get('id')
    if not identity:
        raise ValueError('Source session ID is missing')
    source_kind = info.get('source') or meta.get('source')
    if isinstance(source_kind, dict):
        source_kind = json.dumps(source_kind)
    if source_kind and 'subagent' in source_kind:
        return None
    return {'source': 'codex', 'id': identity, 'title': info.get('title') or next(
        (m['text'][:180] for m in messages if m['role']=='user'), 'Untitled'),
        'created_at': meta.get('timestamp') or timestamp(info.get('created_at')),
        'updated_at': last_time or timestamp(info.get('updated_at')),
        'model': model, 'provider': meta.get('model_provider') or info.get('model_provider'),
        'workspace': meta.get('cwd') or info.get('cwd'), 'client': meta.get('originator'),
        'client_version': meta.get('cli_version'), 'messages': messages, 'model_history': history,
        'runs': runs, 'capture': 'available_visible_messages',
        'evidence': {'path': str(Path(path).resolve()), 'parser': 'codex-jsonl-v1', 'warnings': warnings},
        'limits': ['Only visible messages retained in this local source file are included.',
                   'Attachment references are retained; remote media is not downloaded.']}


def codex_sources(home):
    home = Path(home)
    found = {}
    db = home / 'state_5.sqlite'
    if db.exists():
        connection = sqlite3.connect(db.as_uri() + '?mode=ro', uri=True)
        connection.row_factory = sqlite3.Row
        try:
            for row in connection.execute('SELECT id,title,source,model,model_provider,reasoning_effort,cwd,created_at,updated_at,rollout_path FROM threads'):
                info = dict(row)
                if 'subagent' not in info.get('source',''):
                    found[info['rollout_path']] = info
        finally:
            connection.close()
    for directory in ['sessions','archived_sessions']:
        for path in (home / directory).rglob('*.jsonl'):
            found.setdefault(str(path), {})
    # A session can occur in both live and archived trees. Prefer the most complete
    # retained file and do not let a shorter duplicate overwrite the same identity.
    grouped = {}
    for path, info in found.items():
        match = re.search(r'([0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})\.jsonl$', path)
        identity = info.get('id') or (match.group(1) if match else path)
        file = Path(path)
        rank = (file.stat().st_size, file.stat().st_mtime_ns) if file.exists() else (-1,-1)
        if identity not in grouped or rank > grouped[identity][0]:
            grouped[identity] = (rank, path, info)
    return sorted((p, i) for _, p, i in grouped.values())


def read_chatgpt_export(data):
    """Accept the user's downloaded conversations.json; preserve every visible branch node."""
    if not isinstance(data, list):
        raise ValueError('Expected a list of exported ChatGPT conversations')
    result = []
    for conversation in data:
        mapping = conversation.get('mapping')
        if not isinstance(mapping, dict):
            raise ValueError('Export conversation has no mapping')
        messages = []
        # Exports can contain missing timestamps and arbitrary mapping order.
        # Visit parents before children without assuming a single conversation branch.
        order, visited = [], set()
        for node_id in sorted(mapping, key=lambda k: timestamp((mapping[k].get('message') or {}).get('create_time')) or '9999'):
            chain, local, current = [], set(), node_id
            while current in mapping and current not in visited:
                if current in local:
                    raise ValueError('Conversation branch cycle in export')
                local.add(current);chain.append(current)
                current = mapping[current].get('parent')
            for key in reversed(chain):
                visited.add(key);order.append(key)
        for node_id in order:
            node=mapping[node_id]
            message = node.get('message')
            if not message:
                continue
            role = message.get('author',{}).get('role')
            channel = message.get('channel')
            if role not in ['user','assistant'] or channel in ['analysis','reasoning']:
                continue
            text = '\n'.join(p for p in message.get('content',{}).get('parts',[]) if isinstance(p,str))
            if not text:
                continue
            metadata = message.get('metadata') or {}
            messages.append({'id': message.get('id') or node_id, 'parent_id': node.get('parent'),
                             'role': role, 'phase': channel, 'text': text,
                             'timestamp': timestamp(message.get('create_time')),
                             'model': metadata.get('model_slug') if role=='assistant' else None})
        result.append({'source': 'chatgpt', 'id': conversation.get('id') or conversation.get('conversation_id'),
                       'title': conversation.get('title'), 'created_at': timestamp(conversation.get('create_time')),
                       'updated_at': timestamp(conversation.get('update_time')), 'workspace': None,
                       'model': next((m['model'] for m in reversed(messages) if m.get('model')),None),
                       'provider': 'openai', 'messages': messages, 'capture': 'exported_visible_branches',
                       'evidence': {'parser': 'chatgpt-export-v1'},
                       'limits': ['Export snapshot, not live account synchronization.',
                                  'Branch parent IDs retained; parent-first rendering includes multiple branches.']})
    return result
