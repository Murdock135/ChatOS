"""Read-only source adapters. No browser sessions, credentials, or private APIs."""
from pathlib import Path
import json
import re
import sqlite3
import zipfile
from .core import timestamp
from .codex_lineage import SessionLineage

from .visibility import clean_text, origin_hint


def read_export_file(path, source):
    """Read one bounded export payload without extracting ZIP members to disk."""
    path=Path(path)
    if path.is_symlink():raise ValueError('Export inbox symlinks are not imported')
    maximum=128*1024*1024
    if path.suffix.lower()=='.zip':
        if source!='chatgpt':raise ValueError('Raw Muse ZIP export needs a verified schema adapter')
        with zipfile.ZipFile(path) as archive:
            members=[item for item in archive.infolist() if Path(item.filename).name=='conversations.json']
            if len(members)!=1:raise ValueError('ZIP must contain exactly one conversations.json payload')
            item=members[0]
            if item.file_size>maximum:raise ValueError('Export JSON exceeds the 128 MiB import bound')
            if item.flag_bits & 1:raise ValueError('Encrypted export requires a supported decoded export')
            with archive.open(item) as stream:
                raw=stream.read(maximum+1)
            if len(raw)>maximum:raise ValueError('Export JSON exceeds the import bound')
    else:
        if path.stat().st_size>maximum:raise ValueError('Export JSON exceeds the 128 MiB import bound')
        raw=path.read_bytes()
    data=json.loads(raw)
    if source=='chatgpt' and isinstance(data,list) and (not data or isinstance(data[0],dict) and 'mapping' in data[0]):
        return read_chatgpt_export(data)
    records=data if isinstance(data,list) else [data]
    if not all(isinstance(record,dict) for record in records):raise ValueError('Export records must be objects')
    return records


def read_codex(path, info=None):
    info = dict(info or {})
    messages, history, runs, warnings = [], [], [], []
    model, effort, turn_id = info.get('model'), info.get('reasoning_effort'), None
    meta, last_time = {}, None
    lineage = SessionLineage(info.get('id'))
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
                lineage.observe(payload)
                meta = lineage.metadata
            elif kind == 'turn_context':
                model = payload.get('model') or model
                effort = payload.get('effort') or payload.get('reasoning_effort') or effort
                turn_id = payload.get('turn_id')
                history.append({'turn_id': turn_id, 'timestamp': last_time, 'model': model, 'effort': effort, **lineage.origin()})
            elif kind == 'response_item' and payload.get('type') == 'message':
                role = payload.get('role')
                phase = payload.get('phase') or payload.get('channel')
                if role not in ['user','assistant'] or phase in ['analysis','reasoning','summary'] or payload.get('recipient') not in [None,'all']:
                    continue
                pieces = [p.get('text', '') for p in payload.get('content', [])
                          if p.get('type') in ['input_text','output_text','text']]
                text = '\n'.join(pieces)
                attachments = [dict(type=p.get('type'), reference=p.get('image_url') or p.get('image_path'))
                               for p in payload.get('content', []) if p.get('type') in ['input_image','image']]
                text = clean_text(role,text)
                if text is None:continue
                if not text and not attachments:
                    continue
                messages.append({'id': payload.get('id') or f'line-{line_number}', 'role': role,
                                 'phase': phase, 'text': text, 'timestamp': last_time, 'turn_id': turn_id,
                                 'model': model if role == 'assistant' else None,
                                 'reasoning_effort': effort if role == 'assistant' else None,
                                 'attachments': attachments, **origin_hint(role,text), **lineage.origin()})
            elif kind == 'event_msg' and payload.get('type') in ['task_complete','turn_aborted','task_started']:
                runs.append({'event': payload['type'], 'turn_id': payload.get('turn_id'),
                             'timestamp': last_time, 'started_at': payload.get('started_at'),
                             'completed_at': payload.get('completed_at'), **lineage.origin()})
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
        'evidence': {'path': str(Path(path).resolve()), 'parser': 'codex-jsonl-v1', 'warnings': warnings, **lineage.evidence()},
        'limits': ['Only visible messages retained in this local source file are included.',
                   'Attachment references are retained; remote media is not downloaded.'] +
                  (['Inherited fork messages retain their origin conversation ID; they were not newly authored in this fork.'] if lineage.evidence() else [])}


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
            if role not in ['user','assistant'] or channel in ['analysis','reasoning','summary'] or message.get('recipient') not in [None,'all']:
                continue
            parts=message.get('content',{}).get('parts',[])
            text = '\n'.join(p for p in parts if isinstance(p,str))
            attachments=[{'type':p['content_type'],'reference':p.get('asset_pointer')}
                         for p in parts if isinstance(p,dict) and p.get('content_type')=='image_asset_pointer']
            if not text and not attachments:
                continue
            metadata = message.get('metadata') or {}
            messages.append({'id': message.get('id') or node_id, 'export_node_id':node_id,'parent_id': node.get('parent'),
                             'role': role, 'phase': channel, 'text': text,
                             'timestamp': timestamp(message.get('create_time')),
                             'model': metadata.get('model_slug') if role=='assistant' else None,
                             'reasoning_effort':metadata.get('reasoning_effort') if role=='assistant' else None,
                             'attachments':attachments})
        by_id={m['id']:m for m in messages}
        current=conversation.get('current_node');branch=[];seen=set()
        while current in mapping and current not in seen:
            seen.add(current)
            node=mapping[current];message=node.get('message') or {}
            identity=message.get('id') or current
            if identity in by_id:branch.append(by_id[identity])
            current=node.get('parent')
        selected=next((m for m in branch if m.get('model')),None)
        if not selected:
            selected=max((m for m in messages if m.get('model')),key=lambda m:m.get('timestamp') or '',default=None)
        result.append({'source': 'chatgpt', 'id': conversation.get('id') or conversation.get('conversation_id'),
                       'title': conversation.get('title'), 'created_at': timestamp(conversation.get('create_time')),
                       'updated_at': timestamp(conversation.get('update_time')), 'workspace': None,
                       'model':selected['model'] if selected else None,
                       'provider': 'openai', 'messages': messages, 'capture': 'exported_visible_branches',
                       'evidence': {'parser': 'chatgpt-export-v2','current_node':conversation.get('current_node'),
                                    'model_basis':'active_branch' if any(m is selected for m in branch) else 'latest_timestamped_exported_assistant'},
                       'limits': ['Export snapshot, not live account synchronization.',
                                  'Branch parent IDs retained; parent-first rendering includes multiple branches.']})
    return result


def read_codex_history(home, info):
    """Recover projected visible messages when a retained rollout file is unavailable.

    The projection is incomplete evidence; model fields are thread-level fallback only.
    """
    home=Path(home);path=home/'thread_history_1.sqlite'
    if not path.is_file():return None
    connection=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)
    connection.row_factory=sqlite3.Row
    try:
        rows=connection.execute('''SELECT turn_id,item_id,rollout_ordinal,created_at_ms,item_json,item_type
             FROM thread_items WHERE thread_id=? AND item_type IN ('userMessage','agentMessage')
             ORDER BY rollout_ordinal,created_at_ms,item_id''',(info['id'],)).fetchall()
        if not rows:return None
        messages=[]
        for row in rows:
            item=json.loads(row['item_json'])
            if item.get('type')!=row['item_type']:raise ValueError('History projection item type mismatch')
            role='user' if row['item_type']=='userMessage' else 'assistant'
            phase=item.get('phase') if role=='assistant' else None
            if phase in ['analysis','reasoning','summary']:continue
            if role=='assistant':text=item.get('text','');attachments=[]
            else:
                text='\n'.join(p.get('text','') for p in item.get('content',[]) if p.get('type')=='text')
                attachments=[{'type':p.get('type'),'reference':p.get('path') or p.get('url')}
                             for p in item.get('content',[]) if p.get('type') in ['image','localImage']]
            text=clean_text(role,text)
            if text is None:continue
            if not text and not attachments:continue
            messages.append({'id':row['item_id'],'role':role,'phase':phase,'text':text,
                             'timestamp':timestamp(row['created_at_ms']),'turn_id':row['turn_id'],
                             'model':None,'reasoning_effort':None,'attachments':attachments,
                             'projection_ordinal':row['rollout_ordinal'],**origin_hint(role,text)})
        if not messages:return None
        runs=[{'turn_id':row['turn_id'],'status':row['status'],'started_at':timestamp(row['started_at']),
               'completed_at':timestamp(row['completed_at'])} for row in connection.execute('''
               SELECT turn_id,status,started_at,completed_at FROM thread_turns WHERE thread_id=?
               ORDER BY rollout_ordinal''',(info['id'],))]
    finally:connection.close()
    return {'source':'codex','id':info['id'],'title':info.get('title') or 'Untitled',
            'created_at':timestamp(info.get('created_at')),'updated_at':timestamp(info.get('updated_at')),
            'model':info.get('model'),'provider':info.get('model_provider'),
            'reasoning_effort':info.get('reasoning_effort'),'workspace':info.get('cwd'),
            'messages':messages,'model_history':[],'runs':runs,'capture':'partial_history_projection',
            'evidence':{'path':str(path),'table':'thread_items','parser':'codex-history-projection-v1',
                        'missing_rollout':info.get('rollout_path'),
                        'model_provenance':'Latest thread metadata only; per-message model and effort are unknown.'},
            'limits':['Recovered visible-message projection because the original rollout file is unavailable.',
                      'Projection coverage is not established as complete; hidden reasoning and tool payloads were not selected.',
                      'Thread-level model fallback is not per-turn evidence; attachment references are not downloaded.']}
