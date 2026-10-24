from pathlib import Path
import argparse
import json
import sys
from .core import ROOT,Store
from .runtime import sync
from .terminal import print_report
from .workspace import workspace_path


def _main():
    parser=argparse.ArgumentParser(description='Local Chief of Staff archive')
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--json', action='store_true', help='Print machine-readable JSON')
    commands=parser.add_subparsers(dest='command',required=True)
    cmd=commands.add_parser('init',help='Create an independent visible workspace')
    cmd.add_argument('destination',type=Path);cmd.add_argument('--codex-home',type=Path)
    cmd=commands.add_parser('migrate',help='Verify a separate copy of a legacy workspace');cmd.add_argument('destination',type=Path)
    cmd=commands.add_parser('context-import');cmd.add_argument('file',type=Path)
    cmd=commands.add_parser('context-accept');cmd.add_argument('identity');cmd.add_argument('--review-note',required=True)
    cmd=commands.add_parser('context-retire');cmd.add_argument('identity');cmd.add_argument('--review-note',required=True)
    cmd=commands.add_parser('sync');cmd.add_argument('--force',action='store_true');cmd.add_argument('--codex-home',type=Path)
    commands.add_parser('status')
    commands.add_parser('coverage',help='Report captured records and known source gaps')
    cmd=commands.add_parser('evaluate',help='Evaluate labeled evidence retrieval');cmd.add_argument('cases',type=Path);cmd.add_argument('--limit',type=int,default=8);cmd.add_argument('--hybrid',action='store_true');cmd.add_argument('--output',type=Path)
    cmd=commands.add_parser('map-diagnostics');cmd.add_argument('--labels',type=Path)
    cmd=commands.add_parser('bundle-export',help='Write a selected portable local bundle');cmd.add_argument('destination',type=Path)
    selection=cmd.add_mutually_exclusive_group(required=True)
    selection.add_argument('--conversation',action='append');selection.add_argument('--project');selection.add_argument('--all',action='store_true')
    cmd.add_argument('--with-context',action='store_true')
    cmd=commands.add_parser('bundle-check');cmd.add_argument('directory',type=Path)
    commands.add_parser('setup-status')
    commands.add_parser('assistant-guide',help='Create or refresh the local assistant access guide')
    commands.add_parser('doctor')
    cmd=commands.add_parser('serve');cmd.add_argument('--port',type=int,default=8765);cmd.add_argument('--open',action='store_true');cmd.add_argument('--codex-home',type=Path)
    cmd=commands.add_parser('library');cmd.add_argument('source',choices=['codex','chatgpt','muse']);cmd.add_argument('identity');cmd.add_argument('--title');cmd.add_argument('--note')
    mode=cmd.add_mutually_exclusive_group();mode.add_argument('--archive',action='store_true');mode.add_argument('--restore',action='store_true')
    cmd=commands.add_parser('backup');cmd.add_argument('--fresh',action='store_true')
    cmd=commands.add_parser('restore');cmd.add_argument('backup',type=Path);cmd.add_argument('destination',type=Path)
    commands.add_parser('install-scheduler')
    commands.add_parser('scheduler-status')
    commands.add_parser('disable-scheduler')
    commands.add_parser('file-projects')
    cmd=commands.add_parser('search');cmd.add_argument('query');cmd.add_argument('--limit',type=int,default=15);cmd.add_argument('--semantic',action='store_true')
    cmd=commands.add_parser('brief');cmd.add_argument('project')
    cmd=commands.add_parser('assign');cmd.add_argument('source',choices=['codex','chatgpt','muse']);cmd.add_argument('identity');cmd.add_argument('projects',nargs='*');cmd.add_argument('--reason',required=True)
    cmd=commands.add_parser('retrieve');cmd.add_argument('query');cmd.add_argument('--project');cmd.add_argument('--limit',type=int,default=8);cmd.add_argument('--hybrid',action='store_true')
    cmd=commands.add_parser('dense-build');cmd.add_argument('--limit',type=int);cmd.add_argument('--batch-size',type=int,default=4)
    commands.add_parser('dense-map')
    cmd=commands.add_parser('feedback');cmd.add_argument('--limit',type=int,default=15)
    cmd=commands.add_parser('review-feedback');cmd.add_argument('key');cmd.add_argument('classification',choices=['confirmed_feedback','uncertain','not_feedback']);cmd.add_argument('--reason',required=True);cmd.add_argument('--adjustment');cmd.add_argument('--already-logged',action='store_true')
    for subparser in commands.choices.values():
        subparser.add_argument('--json', action='store_true', default=argparse.SUPPRESS,
                               help='Print machine-readable JSON')
    args=parser.parse_args()

    def emit(data):
        print_report(data, args.command, args.json)
    if args.command=='init':
        from .setup import initialize
        emit(initialize(args.destination,args.codex_home))
        return 0
    if args.command=='migrate':
        from .migration import migrate
        emit(migrate(args.root,args.destination));return 0
    if args.command=='context-import':
        from .context import import_artifact
        emit(import_artifact(args.root,args.file));return 0
    if args.command in ['context-accept','context-retire']:
        from .context import accept_artifact, retire_artifact
        operation=retire_artifact if args.command=='context-retire' else accept_artifact
        emit(operation(args.root,args.identity,args.review_note));return 0
    if args.command in ['setup-status','assistant-guide']:
        from .onboarding import setup_status, write_guide
        emit((setup_status if args.command=='setup-status' else write_guide)(args.root));return 0
    if args.command=='bundle-check':
        from .portable import check_bundle
        emit(check_bundle(args.directory));return 0
    if args.command=='serve':
        from .web import serve
        if not 0 <= args.port <= 65535:parser.error('Port must be between 0 and 65535')
        serve(args.root,args.port,args.open,args.json,args.codex_home)
        return 0
    if args.command=='library':
        from .library import get,update
        store=Store(args.root)
        try:
            changes={key:getattr(args,key) for key in ['title','note'] if getattr(args,key) is not None}
            if args.archive or args.restore:changes['archived']=args.archive
            emit(update(store,args.source,args.identity,changes) if changes else get(store,args.source,args.identity)[1])
        finally:store.close()
        return 0
    if args.command=='dense-map':
        from .dense_map import build
        from .core import locked
        with locked(workspace_path(args.root,'System/State/sync.lock'),blocking=False):
            store=Store(args.root)
            try:emit(build(store))
            finally:store.close()
        return 0
    if args.command=='dense-build':
        from .dense import build
        from .core import locked
        if args.limit is not None and args.limit<0:parser.error('Limit must be nonnegative')
        if not 1<=args.batch_size<=16:parser.error('Batch size must be between 1 and 16')
        with locked(workspace_path(args.root,'System/State/sync.lock'),blocking=False):
            store=Store(args.root)
            try:emit(build(store,args.limit,args.batch_size))
            finally:store.close()
        return 0
    if args.command in ['feedback','review-feedback']:
        from .feedback import candidates,review,refresh
        store=Store(args.root)
        try:
            if args.command=='feedback':emit(candidates(store)[:max(1,min(args.limit,100))])
            else:
                emit(review(store,args.key,args.classification,args.reason,args.adjustment,args.already_logged))
                refresh(store)
        finally:store.close()
        return 0
    if args.command=='backup':
        from .runtime import backup
        from .core import locked
        with locked(workspace_path(args.root,'System/State/sync.lock'),blocking=False):
            store=Store(args.root)
            try:emit(backup(store,args.fresh))
            finally:store.close()
        return 0
    if args.command=='doctor':
        from .recovery import doctor
        report=doctor(args.root);emit(report);return 0 if report['ok'] else 1
    if args.command=='restore':
        from .recovery import restore
        emit(restore(args.backup,args.destination));return 0
    if args.command=='assign':
        from .routing import assign
        emit(assign(args.root,args.source,args.identity,args.projects,args.reason));return 0
    if args.command=='retrieve':
        from .retrieval import retrieve,render
        if args.hybrid:
            from .dense import retrieve
        store=Store(args.root)
        try:
            evidence = retrieve(store,args.query,args.project,args.limit)
            emit(evidence if args.json else render(evidence))
        finally:store.close()
        return 0
    if args.command=='file-projects':
        from .routing import deliver
        report=deliver(args.root)
        emit({'filed':report['receipts'],'pending_count':len(report['pending'])});return 0
    if args.command in ['install-scheduler','scheduler-status','disable-scheduler']:
        from .scheduler import install,service_status,remove
        fn={'install-scheduler':install,'scheduler-status':service_status,'disable-scheduler':remove}[args.command]
        emit(fn(args.root));return 0
    if args.command=='sync':
        try:
            status=sync(args.root,args.codex_home,args.force)
        except BlockingIOError:
            emit({'status':'already_running'});return 0
        emit(status)
        return 0 if status['status']=='ok' else 1
    if args.command=='status':
        p=workspace_path(args.root,'System/State/status.json')
        emit(json.loads(p.read_text()) if p.exists() else {'status':'never_run'});return 0
    store=Store(args.root)
    try:
        if args.command=='bundle-export':
            from .portable import export_bundle
            emit(export_bundle(store,args.destination,args.conversation,args.project,args.all,args.with_context))
        elif args.command=='evaluate':
            from .evaluation import evaluate
            backend=None
            if args.hybrid:
                from .dense import retrieve as backend
            result=evaluate(store,args.cases,args.limit,backend)
            if args.output:
                from .core import write_json
                write_json(args.output,result)
            emit(result)
        elif args.command=='map-diagnostics':
            from .evaluation import map_diagnostics
            emit(map_diagnostics(store,args.labels))
        elif args.command=='coverage':
            from .coverage import report
            emit(report(store))
        elif args.command=='search':
            if args.semantic:
                from .semantic import query,refresh
                refresh(store)
                results=query(json.loads((store.state/'semantic.json').read_text()),args.query,args.limit)
            else:results=store.search(args.query,args.limit)
            emit(results)
        else:
            ids={p['id'] for p in store.registry()}
            if args.project not in ids:
                parser.error('Unknown project ID')
            emit((workspace_path(args.root,'Projects')/(args.project+'.md')).read_text())
    finally:
        store.close()
    return 0


def main():
    try:
        return _main()
    except (ValueError, OSError) as error:
        print_report({'status':'error','error':str(error)},'error','--json' in sys.argv)
        return 1


if __name__=='__main__':
    raise SystemExit(main())
