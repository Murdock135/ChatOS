"""Verify retained backups and restore into a new isolated workspace, never over live data."""
from pathlib import Path
import hashlib
import json
import sqlite3
from .core import Store,now,write_json,atomic


def verify_backup(path):
    path=Path(path).resolve()
    manifest_path=path.parent/'manifest.json'
    manifest=json.loads(manifest_path.read_text())
    if manifest.get('database')!=path.name:
        raise ValueError('Backup manifest names a different database')
    if hashlib.sha256(path.read_bytes()).hexdigest()!=manifest.get('sha256'):
        raise ValueError('Backup hash mismatch; retained backup was not modified')
    db=sqlite3.connect(path.as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':
            raise ValueError('Backup failed SQLite integrity check')
        count=db.execute('SELECT count(*) FROM conversations').fetchone()[0]
    finally:db.close()
    return {'status':'verified','path':str(path),'conversations':count,'created_at':manifest.get('created_at')}


def restore(backup,destination):
    """Require a new directory, regenerate canonical files, and retain provenance."""
    backup=Path(backup).resolve();destination=Path(destination).resolve()
    report=verify_backup(backup)
    # mkdir(exist_ok=False) prevents an accidental overwrite of a live/test archive.
    destination.mkdir(parents=True,exist_ok=False)
    state=destination/'System/State';state.mkdir(parents=True)
    source=sqlite3.connect(backup.as_uri()+'?mode=ro&immutable=1',uri=True)
    target=sqlite3.connect(str(state/'chatos.sqlite3'))
    try:source.backup(target)
    finally:target.close();source.close()
    store=Store(destination)
    try:
        records=store.records()
        for record in records:
            path=destination/record['file_path']
            # A backup is data, never authority to write outside its new root.
            if destination not in path.resolve().parents:
                raise ValueError('Unsafe canonical path in backup')
            write_json(path.with_suffix('.json'),record)
            store.render(record)
        from .library import restore_annotations
        restore_annotations(store)
        with store.db:
            store.db.execute("UPDATE runs SET status='interrupted' WHERE status='running'")
        report.update({'restored_at':now(),'destination':str(destination),
                       'restored_conversations':len(records),
                       'limits':'Conversation database, revisions, checkpoints, library annotations and regenerated source files only. Behavior snapshots and project registry need separate recovery. No scheduler installed or sync triggered.'})
        write_json(destination/'RESTORE.json',report)
        atomic(destination/'README.md','# Isolated recovery\n\n'+report['limits']+'\n\nSee RESTORE.json for provenance.\n')
    finally:store.close()
    return report


def doctor(root):
    root=Path(root).resolve()
    report={'checked_at':now(),'errors':[],'warnings':[]}
    store=Store(root)
    try:
        report['database_integrity']=store.db.execute('PRAGMA integrity_check').fetchone()[0]
        if report['database_integrity']!='ok':report['errors'].append('Runtime database integrity failed')
        report['conversations']=len(store.records())
        missing=[];mismatched=[]
        for record in store.records():
            path=root/record['file_path']
            if root not in path.resolve().parents:
                report['errors'].append('Canonical path escapes workspace');continue
            for file in [path,path.with_suffix('.json')]:
                if not file.is_file():missing.append(str(file))
            if path.is_file() and path.read_text()!=store.render(record,write=False):
                mismatched.append(str(path))
            if path.with_suffix('.json').is_file():
                try:matches=json.loads(path.with_suffix('.json').read_text())==record
                except ValueError:matches=False
                if not matches:
                    mismatched.append(str(path.with_suffix('.json')))
        report['missing_generated_files']=missing
        report['mismatched_canonical_files']=mismatched
        if missing or mismatched:report['errors'].append('Canonical files differ from database; force sync can regenerate source files')
        backups=sorted((root/'System/Backups').glob('*/chatos.sqlite3'))
        if backups:
            try:report['latest_backup']=verify_backup(backups[-1])
            except (OSError,ValueError,sqlite3.Error) as exc:report['errors'].append('Latest backup verification failed: '+str(exc))
        else:report['warnings'].append('No database backup found')
        status=root/'System/State/status.json'
        if status.exists():
            saved=json.loads(status.read_text());report['last_sync']={k:saved.get(k) for k in ['finished_at','status','system_sync','sources']}
            if saved.get('codex_home'):
                from System.Scripts.system_inventory import check
                try:
                    report['behavior_files']=check(root,Path(saved['codex_home']))
                    if not report['behavior_files']['ok']:report['errors'].append('Behavior-file archive/index drift detected; run sync to reconcile')
                except (OSError,ValueError,KeyError) as exc:
                    report['errors'].append('Behavior archive verification failed: '+str(exc))
            from datetime import datetime,timezone
            age=(datetime.now(timezone.utc)-datetime.fromisoformat(saved['finished_at'])).total_seconds()
            report['sync_age_seconds']=round(age)
            if age>7200:report['warnings'].append('Last completed sync is more than two hours old')
            if saved.get('status')!='ok':report['warnings'].append('Last sync did not report ok')
            for name,health in saved.get('sources',{}).items():
                if health.get('status')!='ok':report['warnings'].append(name+': '+health.get('status','unknown'))
        else:report['warnings'].append('No sync execution evidence')
        report['ok']=not report['errors']
        return report
    finally:store.close()
