"""Read scheduling evidence without executing tasks or copying private result bodies."""
from pathlib import Path
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
import json
import re
import sqlite3
from .core import write_json,atomic,now,title


def stamp(value):
    if value is None:return None
    return datetime.fromtimestamp(value/1000,timezone.utc).isoformat()


def scalar(text,key):
    match=re.search(r'^'+re.escape(key)+r'\s*=\s*(".*")\s*$',text,re.M)
    return json.loads(match.group(1)) if match else None


def collect(root,codex):
    root,codex=Path(root),Path(codex)
    definitions=[]
    for file in sorted((codex/'automations').glob('*/automation.toml')):
        if file.is_symlink() or file.parent.is_symlink():continue
        text=file.read_text()
        definitions.append({'id':scalar(text,'id') or file.parent.name,'name':scalar(text,'name'),
                            'status':scalar(text,'status'),'kind':scalar(text,'kind'),
                            'target_thread_id':scalar(text,'target_thread_id'),'path':str(file)})
    db=codex/'sqlite/codex-dev.db';tasks=[];runs=[]
    if db.is_file():
        connection=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True)
        connection.row_factory=sqlite3.Row
        try:
            tasks=[dict(row) for row in connection.execute('''SELECT id,name,status,kind,
                target_thread_id,last_run_at,next_run_at,updated_at FROM automations''')]
            runs=[dict(row) for row in connection.execute('''SELECT thread_id,automation_id,status,
                created_at,updated_at FROM automation_runs ORDER BY updated_at DESC LIMIT 500''')]
        finally:connection.close()
    for task in tasks:
        for key in ['last_run_at','next_run_at','updated_at']:task[key]=stamp(task[key])
    for run in runs:
        for key in ['created_at','updated_at']:run[key]=stamp(run[key])
    report={'checked_at':now(),'status':'metadata_read' if db.is_file() else 'definitions_only',
            'source_database':str(db) if db.is_file() else None,'definitions':definitions,
            'tasks':tasks,'observed_run_rows':runs,
            'limits':['Local Codex schedules only; ChatGPT and Muse tasks are not covered.',
                      'A saved active task or last_run_at is not proof of successful completion.',
                      'Heartbeat execution may not create automation_runs rows; absence of rows is unknown outcome.',
                      'Next-run timestamps are host-reported and may move while the target chat is busy.',
                      'Only 500 most recent run-metadata rows are retained in this current view; result bodies are excluded.']}
    write_json(root/'System/State/schedules.json',report)
    lines=['# Current Codex schedules','',f'Last checked: {report["checked_at"]}','',
           'Generated from local saved definitions and read-only scheduler metadata. No tasks are triggered by this collector.','',
           '| Task | Host state | Last recorded run | Host next-run time |',
           '| --- | --- | --- | --- |']
    def local(value):
        return datetime.fromisoformat(value).astimezone(ZoneInfo('America/Chicago')).strftime('%Y-%m-%d %H:%M %Z') if value else 'No timestamp recorded'
    for task in tasks:
        lines.append('| '+title(task['name'])+' | '+title(task['status'])+' | '+local(task['last_run_at'])+' | '+local(task['next_run_at'])+' |')
    if not tasks:lines+=['','No readable scheduler task rows. Saved definitions: '+str(len(definitions))+'.']
    lines+=['','## Observed run metadata','']
    if not runs:lines+=['No run rows in the inspected table. This does not establish that heartbeat tasks never ran.']
    for run in runs:
        lines+=['- '+title(run['automation_id'])+': host status '+title(run['status'])+'; '+local(run['updated_at'])+'; thread '+title(run['thread_id'])]
    lines+=['','## Saved definitions','']
    for item in definitions:
        lines+=['- ['+title(item['name'] or item['id'])+']('+Path(item['path']).as_uri()+') — '+title(item['status'])+'; target '+title(item['target_thread_id'] or 'unknown')]
    lines+=['','## Limits','']+['- '+item for item in report['limits']]
    atomic(root/'System/Schedules/Index.md','\n'.join(lines)+'\n')
    return {'status':report['status'],'checked_at':report['checked_at'],'tasks':len(tasks),
            'run_rows':len(runs),'detail':'Saved task state and host timestamps read; completion requires separate evidence.'}
