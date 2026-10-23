"""Bounded local sync. Source reads are read-only; output stays in the workspace."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import quote
import html
import json
import re
import subprocess
import sys
import time
import traceback
from .core import ROOT, Store, atomic, write_json, locked, now, digest, title
from .importers import codex_sources, read_codex, read_export_file, read_codex_history


def sync_system(root, codex_home):
    """Reconcile every accessible behavior file, and verify the resulting archive."""
    from System.Scripts.system_inventory import refresh, check
    from System.Scripts.snapshot_codex_state import create_snapshot
    if not codex_home.is_dir():
        raise FileNotFoundError('Codex source root unavailable: ' + str(codex_home))
    from .changes import snapshot_manifest, behavior_changes
    previous = snapshot_manifest(root)
    refresh(root, codex_home)
    before = check(root, codex_home)
    captured = create_snapshot(root, codex_home) if not before['ok'] else None
    after = check(root, codex_home) if captured else before
    if not after['ok']:
        raise RuntimeError('Behavior archive changed during capture or failed integrity check; retry sync')
    return {'status': 'verified', 'checked_at': now(), 'snapshot_created': bool(captured),
            'snapshot': captured['snapshot'] if captured else None,
            'changes': behavior_changes(previous, snapshot_manifest(root)),
            'detail': 'Skills, memory, instructions, rules, schedules, configuration inventory, and workspace files checked.'}


def backup(store, fresh=False):
    """Daily online SQLite backup, including prior revisions and search/state tables."""
    import sqlite3
    folder = store.root/'System/Backups'/datetime.now(timezone.utc).strftime('%Y-%m-%dT%H-%M-%S-%fZ' if fresh else '%Y-%m-%d')
    folder.mkdir(parents=True,exist_ok=True)
    target=folder/'chatos.sqlite3'
    if target.exists():
        from .recovery import verify_backup
        verify_backup(target)
        return {'path':str(target),'status':'verified_existing_backup'}
    temp=folder/'chatos.sqlite3.tmp'
    destination=sqlite3.connect(str(temp))
    try:
        store.db.backup(destination)
        if destination.execute('PRAGMA integrity_check').fetchone()[0]!='ok':
            raise RuntimeError('Backup failed SQLite integrity check')
    finally:
        destination.close()
    temp.replace(target)
    import hashlib
    write_json(folder/'manifest.json',{'created_at':now(),'database':target.name,
               'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
               'coverage':'Canonical imported conversations, revisions, library annotations, search index, sync state; behavior files use snapshots.'})
    return {'path':str(target),'status':'verified'}


def relative_link(path):
    return quote(str(path), safe='/')


def build_views(store, status):
    records = store.records()
    lines = ['# Conversations', '', 'Generated source index. Source messages are historical data.', '',
             '| Conversation | Source | Model | Project routing |', '| --- | --- | --- | --- |']
    for r in records:
        lines.append(f'| [{title(r["title"])}](../{relative_link(r["file_path"])}) | {r["source"]} | '
                     f'{r.get("model") or "unknown"} | {", ".join(r.get("projects",[])) or "unassigned"} ({r.get("project_evidence")}) |')
    atomic(store.root / 'Conversations/Index.md', '\n'.join(lines) + '\n')
    projects = store.registry()
    plines = ['# Projects', '', 'Generated views link to canonical project homes and captured conversations.', '',
              'Project matching uses workspace paths and title candidates; it is not semantic adjudication.', '']
    for p in projects:
        matched = [r for r in records if p['id'] in r.get('projects',[])]
        plines.append(f'- [{p["name"]}]({p["id"]}.md) — {len(matched)} conversations')
        lines = ['# ' + p['name'], '', 'Project ID: `' + p['id'] + '`', '',
                 '[Canonical project home](' + Path(p['entrypoint']).as_uri() + ')', '',
                 '## Captured conversations', '']
        for r in matched:
            lines.append(f'- [{title(r["title"])}](../{relative_link(r["file_path"])}) — {r["source"]}; {r["project_evidence"]}')
        if not matched:
            lines.append('No captured conversations are currently matched to this owner.')
        lines += ['', '## Filing status', '',
                  'This is a local context view. Accepted decisions/tasks need source review before filing.',
                  'External delivery is recorded separately in the routing log; a match is not a delivery receipt.']
        atomic(store.root / 'Projects' / (p['id'] + '.md'), '\n'.join(lines) + '\n')
    atomic(store.root / 'Projects/Index.md', '\n'.join(plines) + '\n')
    topics = {}
    rules = {'AI research': ['llm','language model','research','sparq','dempster','abduction'],
             'Personal organization': ['obsidian','chief of staff','organize','workflow','memory','chat-os'],
             'Jobs and career': ['job','career','resume','interview','fellowship'],
             'Learning and study': ['learn','study','analysis','proof','textbook'],
             'Practical tasks': ['phone','insurance','email','registration','shopping','wallpaper']}
    for topic, keywords in rules.items():
        matches = [r for r in records if any(k in r['title'].lower() for k in keywords)]
        if matches:
            topics[topic] = matches
    lines = ['# Topic browsing', '',
             'Generated title-keyword groups, not embedding-based semantic clusters. Groups may overlap.', '']
    for topic, matches in topics.items():
        lines += ['## ' + topic, '']
        lines += [f'- [{title(r["title"])}](../{relative_link(r["file_path"])})' for r in matches]
        lines.append('')
    lines += ['[Suggested latent-semantic groups](Semantic%20groups.md)', '']
    atomic(store.root / 'Topics/Index.md', '\n'.join(lines) + '\n')
    lines = ['# Live sync status', '', 'Generated by the local sync runner; check the timestamp.', '',
             '- Last attempt: ' + status['finished_at'],
             '- Outcome: ' + status['status'],
             '- Local conversations: ' + str(len(records)),
             '- Changed records this run: ' + str(status.get('changed',0)),
             '- Skipped unchanged source files: ' + str(status.get('unchanged',0)), '',
             '## Sources', '', '| Source | State | Details |', '| --- | --- | --- |']
    for source, health in status['sources'].items():
        lines.append(f'| {source} | {health["status"]} | {title(health.get("detail",""))} |')
    behavior = status.get('system_sync', {})
    lines += ['', '## Behavior files', '',
              '- Verification: ' + behavior.get('status', 'not reached'),
              '- Checked: ' + behavior.get('checked_at', 'unavailable'),
              '- New snapshot this run: ' + str(behavior.get('snapshot_created', False)),
              '- [Current skills](System/Skills/Index.md) and [latest snapshot](System/Latest%20snapshot.md)', '']
    lines += ['', '## Browse', '', '[Conversations](Conversations/Index.md) · [Projects](Projects/Index.md) · '
              '[Topics](Topics/Index.md) · [Skills](System/Skills/Index.md) · [State](STATE.md)', '',
              '## Problems', '']
    retrieval=status.get('retrieval')
    if retrieval:
        lines[-2:-2]=['## Retrieval and map','',
                     '- Indexed passages: '+str(retrieval['passages']),
                     '- Current optional embedding vectors: '+str(retrieval['optional_current_vectors']),
                     '- Map computed: '+retrieval['map_checked_at'],
                     '- Map freshness: '+retrieval['map_freshness'],
                     '- Optional model inference is an explicit maintenance step; core sync does not require it.','']
    lines += [f'- {title(e.get("source"))}: {title(e.get("error"))}' for e in status.get('errors',[])] or ['None reported by this run.']
    atomic(store.root / 'STATUS.md', '\n'.join(lines) + '\n')
    # Single offline HTML file: no server, external scripts, tracking, or remote assets.
    data = [{'title': r['title'], 'source':r['source'], 'model':r.get('model'), 'projects':r.get('projects',[]),
             'url':(store.root/r['file_path']).as_uri(), 'preview':next((m['text'][:300] for m in r['messages'] if m['role']=='user'),'')}
            for r in records]
    payload = json.dumps(data, ensure_ascii=False).replace('<','\\u003c')
    cards = ''.join('<li><b>' + html.escape(k) + '</b>: ' + html.escape(v['status']) + ' — ' +
                    html.escape(v.get('detail','')) + '</li>' for k,v in status['sources'].items())
    document = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'none'; img-src 'none'">
<title>Chief of Staff</title><style>
body{font:16px/1.55 system-ui;margin:0;background:#f5f3ec;color:#232c27}main{max-width:1050px;margin:auto;padding:40px 24px}
h1{font-size:38px;margin-bottom:6px}h2{margin-top:32px}a{color:#21604b}input{font:inherit;padding:12px;width:95%;border:1px solid #aaa;border-radius:8px}
article{background:white;padding:18px;margin:12px 0;border-radius:10px}small{color:#5a665f}nav a{margin-right:18px}#count{margin:14px 0}
</style></head><body><main><h1>Chief of Staff</h1><p>Agent-managed workspace · local reference</p><nav>'''
    for label,path in [('State','STATE.md'),('Memory','System/Memory/Working memory.md'),('Skills','System/Skills/Index.md'),
                       ('Logs','System/Logs/Event log.md'),('Projects','Projects/Index.md'),('Map','Humans/explorer.html'),('Roadmap','IMPLEMENTATION.md')]:
        document += '<a href="' + html.escape((store.root/path).as_uri(),quote=True) + '">' + label + '</a>'
    document += '</nav><h2>Sync health</h2><p>' + html.escape(status['finished_at']) + ' · ' + html.escape(status['status']) + \
                '</p><ul>' + cards + '</ul><h2>Conversations</h2><p>Filter titles, projects, and previews. Full transcript search is available through the local search command.</p><input id="q" placeholder="Find a conversation…"><div id="count"></div><section id="results"></section>'
    document += '<script type="application/json" id="data">' + payload + '''</script><script>
const data=JSON.parse(document.getElementById('data').textContent); const q=document.getElementById('q');
function render(){const words=q.value.toLowerCase().split(/\\s+/).filter(Boolean);const matches=data.filter(r=>words.every(w=>JSON.stringify(r).toLowerCase().includes(w)));document.getElementById('count').textContent=matches.length+' conversations';const out=document.getElementById('results');out.replaceChildren();for(const r of matches.slice(0,100)){const card=document.createElement('article');const link=document.createElement('a');link.href=r.url;link.textContent=r.title;const meta=document.createElement('small');meta.textContent=r.source+' · '+(r.model||'model unknown')+' · '+(r.projects.join(', ')||'unassigned');const p=document.createElement('p');p.textContent=r.preview;card.append(link,document.createElement('br'),meta,p);out.append(card)}}q.addEventListener('input',render);render();
</script></main></body></html>'''
    atomic(store.root / 'Humans/dashboard.html', document)


def sync(root=ROOT, codex_home=None, force=False):
    root = Path(root).resolve()
    codex_home = Path(codex_home or Path.home()/'.codex').resolve()
    with locked(root/'System/State/sync.lock', blocking=False):
        store = Store(root)
        from .changes import conversation_hashes, count_changes
        previous_chats = conversation_hashes(store)
        start = now()
        # Holding sync.lock means a previous 'running' row can only be an interrupted run.
        store.db.execute("UPDATE runs SET status='interrupted' WHERE status='running'")
        checkpoint=store.db.execute("SELECT checked_at FROM checkpoints WHERE source='maintenance' AND identity='reconcile'").fetchone()
        daily_reconcile = not checkpoint or time.time()-datetime.fromisoformat(checkpoint[0]).timestamp()>86400
        force = force or daily_reconcile
        cursor = store.db.execute('INSERT INTO runs(started_at,status) VALUES(?,?)',(start,'running'))
        run_id = cursor.lastrowid
        store.db.commit()
        status = {'run_id': run_id,'started_at':start,'codex_home':str(codex_home),'status':'ok','changed':0,'unchanged':0,'errors':[],
                  'sources': {'codex':{'status':'checking'},'chatgpt':{'status':'export_required','detail':'No live account adapter; export drop-folder supported.'},
                              'muse':{'status':'export_required','detail':'Normalized export import supported; live source access unverified.'}}}
        try:
            if not codex_home.is_dir():
                raise FileNotFoundError('Codex source root unavailable: ' + str(codex_home))
            sources = codex_sources(codex_home)
            unavailable = []
            recovered_history=[]
            unrecovered_history=[]
            warnings = []
            parser_fingerprint=digest([Path(__file__).with_name(name).read_text() for name in ['importers.py','visibility.py']])
            routing_files=[root/'System/Projects/registry.json',root/'System/Projects/overrides.json',Path(__file__).with_name('core.py')]
            routing_fingerprint=digest([p.read_text() if p.exists() else None for p in routing_files])
            for name, info in sources:
                path = Path(name)
                if not path.exists():
                    unavailable.append({'id': info.get('id'), 'path': str(path)})
                    try:
                        record=read_codex_history(codex_home,info)
                        if record:
                            existing=store.db.execute('SELECT record_json FROM conversations WHERE source=? AND id=?',('codex',record['id'])).fetchone()
                            if existing:
                                previous_record=json.loads(existing[0])
                                if previous_record.get('capture')!='partial_history_projection':
                                    recovered_history.append({'id':record['id'],'status':'previous_source_capture_preserved'})
                                    continue
                                # A projection may trim old rows. Retain earlier captured visible messages,
                                # replacing an item only when the same stable ID has updated source text.
                                prior={m['id']:m for m in previous_record['messages']}
                                prior.update({m['id']:m for m in record['messages']})
                                record['messages']=sorted(prior.values(),key=lambda m:(m.get('projection_ordinal',0),m.get('timestamp') or '',m['id']))
                            signature=digest([record,parser_fingerprint,routing_fingerprint])
                            if not force and store.signature('codex-history',record['id'])==signature:
                                status['unchanged']+=1
                            else:
                                status['changed']+=int(store.put(record))
                                store.checkpoint('codex-history',record['id'],signature)
                            recovered_history.append({'id':record['id'],'status':'partial_projection'})
                        else:unrecovered_history.append({'id':info.get('id'),'path':str(path)})
                    except Exception as exc:
                        unrecovered_history.append({'id':info.get('id'),'path':str(path)})
                        status['errors'].append({'source':'codex-history','identity':info.get('id'),
                                                 'error':type(exc).__name__+': '+str(exc)})
                    continue
                try:
                    stat = path.stat()
                    signature = digest([stat.st_size,stat.st_mtime_ns,info.get('title'),info.get('model'),parser_fingerprint,routing_fingerprint])
                    if not force and store.signature('codex',name) == signature:
                        status['unchanged'] += 1
                        continue
                    record = read_codex(path,info)
                    if record:
                        status['changed'] += int(store.put(record))
                    if record and record.get('evidence',{}).get('warnings'):
                        warnings.append({'id': record['id'], 'path': str(path),
                                         'warnings': record['evidence']['warnings']})
                        # Retry incomplete sources next run even if their stat is unchanged.
                    else:
                        store.checkpoint('codex',name,signature)
                except Exception as exc:
                    status['errors'].append({'source':'codex','identity':info.get('id'),
                                             'path':str(path),'error':type(exc).__name__ + ': ' + str(exc)})
            status['unavailable_history'] = unavailable
            status['recovered_history']=recovered_history
            status['unrecovered_history']=unrecovered_history
            status['source_warnings'] = warnings
            status['sources']['codex'] = {
                'status': 'partial' if status['errors'] or warnings else ('partial_history' if unavailable else 'ok'),
                'detail': f'{len(sources)-len(unavailable)} files checked; {len(unavailable)} rollout files unavailable, with {len(recovered_history)} partial cache recoveries and {len(unrecovered_history)} uncaptured; {len(warnings)} parse warnings.'}
            # Exports are user-provided files; nothing is requested from remote services.
            for source in ['chatgpt','muse']:
                folder = root/'System/Imports'/source
                folder.mkdir(parents=True,exist_ok=True)
                imported = 0
                prior_errors=len(status['errors'])
                for file in sorted(p for p in folder.iterdir() if p.suffix.lower() in ['.json','.zip']):
                    try:
                        if file.is_symlink():raise ValueError('Export inbox symlinks are not imported')
                        import hashlib
                        fingerprint=hashlib.sha256()
                        with file.open('rb') as stream:
                            for block in iter(lambda:stream.read(1024*1024),b''):fingerprint.update(block)
                        signature = digest([fingerprint.hexdigest(),parser_fingerprint,routing_fingerprint])
                        if not force and store.signature(source,str(file)) == signature:
                            continue
                        records = read_export_file(file,source)
                        for record in records:
                            if record.get('source') != source:
                                raise ValueError('Export source does not match drop-folder')
                            if record.get('capture')=='partial_desktop_tool_capture':
                                from .desktop_capture import merge
                                existing=store.db.execute('SELECT record_json FROM conversations WHERE source=? AND id=?',(source,record['id'])).fetchone()
                                if existing:
                                    before=json.loads(existing[0]);record=merge(before,record)
                                    if before.get('capture')!='partial_desktop_tool_capture':continue
                            if source == 'chatgpt' and record.get('capture') == 'exported_visible_branches':
                                existing = store.db.execute(
                                    'SELECT record_json FROM conversations WHERE source=? AND id=?',
                                    (source, record['id'])).fetchone()
                                previous = json.loads(existing[0]) if existing else None
                                if previous and previous.get('capture') == 'exported_visible_branches':
                                    try:
                                        old_time = datetime.fromisoformat(previous['updated_at']).timestamp()
                                        new_time = datetime.fromisoformat(record['updated_at']).timestamp()
                                    except (KeyError, TypeError, ValueError):
                                        old_time = new_time = None
                                    # Inbox filenames do not establish which source snapshot is newer.
                                    if old_time is not None and new_time is not None and new_time < old_time:
                                        status.setdefault('retained_newer_exports', []).append(
                                            {'source': source, 'id': record['id'], 'older_export': str(file)})
                                        continue
                            record.setdefault('evidence',{})['export_path'] = str(file)
                            status['changed'] += int(store.put(record))
                            imported += 1
                        store.checkpoint(source,str(file),signature)
                    except Exception as exc:
                        status['errors'].append({'source':source,'path':str(file),
                                                 'error':type(exc).__name__ + ': ' + str(exc)})
                count = store.db.execute('SELECT count(*) FROM conversations WHERE source=?',(source,)).fetchone()[0]
                if count:
                    status['sources'][source] = {'status':'export_snapshot','detail':f'{count} captured; updates need source exports.'}
                    partial=store.db.execute("SELECT count(*) FROM conversations WHERE source=? AND json_extract(record_json,'$.capture')='partial_desktop_tool_capture'",(source,)).fetchone()[0]
                    if partial:
                        status['sources'][source]={'status':'partial_app_capture','detail':f'{count} captured, including {partial} partial desktop-tool captures; unavailable replies/models require fuller exports.'}
                if len(status['errors'])>prior_errors:
                    status['sources'][source]={'status':'partial','detail':f'{count} captured; one or more inbox exports failed and will retry.'}
            # Shared scripts retain their own locks and logs. Never execute source-provided commands.
            for script in ['system_log.py']:
                path = root/'System/Scripts'/script
                if path.exists():
                    args = [sys.executable,str(path)] + (['collect'] if script=='system_log.py' else [])
                    result = subprocess.run(args,cwd=str(root),capture_output=True,text=True,timeout=60)
                    if result.returncode:
                        status['errors'].append({'source':'maintenance','error':script + ' failed',
                                                 'detail':result.stderr[-500:]})
            try:
                from .schedules import collect as collect_schedules
                status['schedules']=collect_schedules(root,codex_home)
            except Exception as exc:
                status['errors'].append({'source':'schedules','error':type(exc).__name__ + ': ' + str(exc)})
            try:
                status['system_sync'] = sync_system(root, codex_home)
            except Exception as exc:
                status['system_sync'] = {'status':'failed','checked_at':now()}
                status['errors'].append({'source':'system_sync','error':type(exc).__name__ + ': ' + str(exc)})
            status['status'] = 'partial' if status['errors'] or warnings else 'ok'
            from .semantic import refresh as refresh_semantic
            refresh_semantic(store)
            from .explorer import refresh as refresh_explorer
            map_data=refresh_explorer(store,json.loads((store.state/'semantic.json').read_text()))
            from .dense import passages as indexed_passages, REVISION
            items=indexed_passages(store)
            cached={row[0] for row in store.db.execute('SELECT identity FROM dense_vectors WHERE revision=?',(REVISION,))}
            status['retrieval']={'passages':len(items),'optional_current_vectors':sum(item['identity'] in cached for item in items),
                                 'optional_model_installed':(root/'System/Models/qwen3-embedding-0.6b/download-manifest.json').is_file(),
                                 'map_backend':map_data.get('backend','local-lsa-pca'),'map_checked_at':map_data['checked_at'],
                                 'map_freshness':map_data.get('freshness_note','Current captured records'),
                                 'limits':'Ordinary sync refreshes lexical evidence; optional model inference/map rebuild is explicit agent maintenance.'}
            from .feedback import refresh as refresh_feedback
            status['feedback_review']=refresh_feedback(store)
            if status['status']=='ok' and daily_reconcile:
                store.checkpoint('maintenance','reconcile',start)
            status['backup']=backup(store)
        except Exception as exc:
            status['status'] = 'failed'
            if status['sources']['codex']['status']=='checking':
                status['sources']['codex']={'status':'failed','detail':'Source scan did not complete; see problems.'}
            status['errors'].append({'source':'sync','error':type(exc).__name__ + ': ' + str(exc)})
        finally:
            status['changes'] = {'chats': count_changes(previous_chats, conversation_hashes(store))}
            status['changes'].update(status.get('system_sync', {}).get('changes', {}))
            status['finished_at'] = now()
            previous_path = root/'System/State/status.json'
            previous = json.loads(previous_path.read_text()) if previous_path.exists() else {}
            for source,health in status['sources'].items():
                before = previous.get('sources',{}).get(source,{})
                health['last_attempt'] = status['finished_at']
                health['last_success'] = status['finished_at'] if health['status'] in ['ok','partial_history','export_snapshot','partial_app_capture'] else before.get('last_success')
            # Generated files follow the committed canonical records. Failed rendering leaves the run failed.
            try:
                build_views(store,status)
            except Exception as exc:
                status['status'] = 'failed'
                status['errors'].append({'source':'views','error':type(exc).__name__ + ': ' + str(exc)})
            write_json(previous_path,status)
            with store.db:
                store.db.execute('UPDATE runs SET finished_at=?,status=?,report_json=? WHERE id=?',
                                 (status['finished_at'],status['status'],json.dumps({k:v for k,v in status.items() if k!='unavailable_history'}),run_id))
            # One JSONL entry per actual run. Protected by the global sync lock.
            runlog=root/'System/Logs/sync-runs.jsonl'
            runlog.parent.mkdir(parents=True,exist_ok=True)
            with runlog.open('a') as f:
                f.write(json.dumps({k:v for k,v in status.items() if k!='unavailable_history'})+'\n')
            store.close()
        return status
