"""Deliver source-linked context indexes, never inferred commitments or source code edits."""
from pathlib import Path
from urllib.parse import quote
import json
from .core import Store,ROOT,atomic,write_json,locked,now,title


def deliver(root=ROOT):
    store=Store(root)
    receipts=[];pending=[]
    try:
        records=store.records()
        for project in store.registry():
            matches=[r for r in records if project['id'] in r.get('projects',[])]
            certain=[r for r in matches if r.get('project_evidence') in ['workspace_path','reviewed_assignment']]
            pending += [{'project':project['id'],'source':r['source'],'id':r['id'],
                         'reason':'Title match needs ownership review','conversation':r['file_path']}
                        for r in matches if r not in certain]
            if not certain or project['id']=='chat-os':continue
            target_root=Path(project['root']).resolve()
            allowed=(Path('/Users/zayan/Documents/obsidian_vaults/academic_life').resolve(),store.root)
            if not any(p==target_root or p in target_root.parents for p in allowed):
                pending.append({'project':project['id'],'reason':'Outside registered delivery scope'});continue
            folder=target_root/('Notes' if project['kind']=='personal-project' else 'Scratch')
            destination=folder/'Chat OS conversations.md'
            marker='<!-- chatos-managed:'+project['id']+' -->'
            try:
                if not folder.is_dir():raise ValueError('Expected project note directory missing')
                # Do not follow substituted symlinks out of the verified project root.
                if target_root not in folder.resolve().parents:
                    raise ValueError('Project destination resolves outside project')
                if destination.is_symlink():raise ValueError('Refusing a symlink destination')
                if destination.exists() and not destination.read_text().startswith(marker):
                    raise ValueError('Existing note is not managed by chat-OS; left untouched')
                lines=[marker,'# Chat OS conversations','',
                       'Generated source-linked context for this project. It does not create accepted tasks or decisions.',
                       'The conversation archive contains the source messages; check them before acting.', '']
                for r in certain:
                    url=(store.root/r['file_path']).as_uri()
                    lines += ['## '+title(r['title']),'',f'[Source conversation]({url})',
                              '',f'Source: `{r["source"]}:{r["id"]}` · model: `{r.get("model") or "unknown"}`','']
                with locked(store.state/'routing.lock'):
                    # Recheck ownership inside the lock before replacing a managed view.
                    if destination.exists() and not destination.read_text().startswith(marker):
                        raise ValueError('Destination ownership changed; left untouched')
                    changed=atomic(destination,'\n'.join(lines))
                    if destination.read_text()!='\n'.join(lines):raise RuntimeError('Write verification failed')
                    index=folder/'00 Scratch Index.md'
                    if index.exists():
                        link='[[Chat OS conversations]]'
                        previous=index.read_text()
                        if link not in previous:
                            # Append one ordinary wikilink, preserving all authored text.
                            atomic(index,previous.rstrip()+'\n\n'+link+'\n')
                    receipts.append({'project':project['id'],'destination':str(destination),
                                     'conversations':len(certain),'status':'filed','changed':changed})
            except (OSError,ValueError,RuntimeError) as exc:
                pending.append({'project':project['id'],'destination':str(destination),
                                'reason':type(exc).__name__+': '+str(exc)})
        owned={(r['source'],r['id']) for r in records if r.get('projects')}
        pending += [{'source':r['source'],'id':r['id'],'conversation':r['file_path'],
                     'reason':'No registered owner inferred','title':r['title']}
                    for r in records if (r['source'],r['id']) not in owned]
        report={'checked_at':now(),'receipts':receipts,'pending':pending,
                'limits':'Exact-workspace or reviewed-assignment context indexes are delivered. Decisions/tasks require source review.'}
        write_json(store.state/'routing.json',report)
        lines=['# Automatic routing queue','',f'Last processed: {report["checked_at"]}',
               '', 'Pending items are not delivered. Read sources before assigning an owner or creating commitments.','']
        for item in pending:
            lines.append('- '+title(item.get('title') or item.get('project') or item.get('id'))+': '+title(item['reason']))
        if not pending:lines.append('No pending items in the captured records.')
        atomic(store.root/'System/Projects/Automatic routing queue.md','\n'.join(lines)+'\n')
        lines=['# Automatic filing receipts','',f'Last processed: {report["checked_at"]}','',
               'Verified context-index deliveries; these do not imply extracted decisions or task updates.','']
        for item in receipts:
            lines.append(f'- {item["project"]}: [{item["conversations"]} conversations]({Path(item["destination"]).as_uri()}) — filed, verified.')
        atomic(store.root/'System/Projects/Automatic filing receipts.md','\n'.join(lines)+'\n')
        return report
    finally:store.close()


def assign(root, source, identity, projects, reason):
    """Persist an evidence-backed ownership correction independently of imported content."""
    root=Path(root)
    if not reason.strip():raise ValueError('Assignment needs source evidence/reason')
    with locked(root/'System/State/sync.lock',blocking=False):
        store=Store(root)
        try:
            known={p['id'] for p in store.registry()}
            if not set(projects)<=known:raise ValueError('Unknown project owner')
            row=store.db.execute('SELECT record_json FROM conversations WHERE source=? AND id=?',
                                 (source,identity)).fetchone()
            if not row:raise ValueError('Conversation not captured')
            path=root/'System/Projects/overrides.json'
            state=json.loads(path.read_text()) if path.exists() else {'assignments':{}}
            entry={'projects':sorted(set(projects)),'reason':reason,'reviewed_at':now()}
            state['assignments'][source+':'+identity]=entry
            write_json(path,state)
            store.put(json.loads(row[0]))
            return {'source':source,'id':identity,**entry,
                    'delivery':'Ownership saved; run sync to refresh views and file-projects for external context indexes.'}
        finally:store.close()
