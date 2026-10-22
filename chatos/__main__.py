from pathlib import Path
import argparse
import json
import sys
from .core import ROOT,Store
from .runtime import sync
from .terminal import print_report


def main():
    parser=argparse.ArgumentParser(description='Local Chief of Staff archive')
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--json', action='store_true', help='Print machine-readable JSON')
    commands=parser.add_subparsers(dest='command',required=True)
    cmd=commands.add_parser('sync');cmd.add_argument('--force',action='store_true');cmd.add_argument('--codex-home',type=Path)
    commands.add_parser('status')
    commands.add_parser('doctor')
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
    if args.command=='dense-map':
        from .dense_map import build
        from .core import locked
        with locked(args.root/'System/State/sync.lock',blocking=False):
            store=Store(args.root)
            try:emit(build(store))
            finally:store.close()
        return 0
    if args.command=='dense-build':
        from .dense import build
        from .core import locked
        if args.limit is not None and args.limit<0:parser.error('Limit must be nonnegative')
        if not 1<=args.batch_size<=16:parser.error('Batch size must be between 1 and 16')
        with locked(args.root/'System/State/sync.lock',blocking=False):
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
        with locked(args.root/'System/State/sync.lock',blocking=False):
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
        p=args.root/'System/State/status.json'
        emit(json.loads(p.read_text()) if p.exists() else {'status':'never_run'});return 0
    store=Store(args.root)
    try:
        if args.command=='search':
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
            emit((args.root/'Projects'/(args.project+'.md')).read_text())
    finally:
        store.close()
    return 0


if __name__=='__main__':
    raise SystemExit(main())
