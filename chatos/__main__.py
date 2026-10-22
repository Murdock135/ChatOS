from pathlib import Path
import argparse
import json
import sys
from .core import ROOT,Store
from .runtime import sync


def main():
    parser=argparse.ArgumentParser(description='Local Chief of Staff archive')
    parser.add_argument('--root',type=Path,default=ROOT)
    commands=parser.add_subparsers(dest='command',required=True)
    cmd=commands.add_parser('sync');cmd.add_argument('--force',action='store_true');cmd.add_argument('--codex-home',type=Path)
    commands.add_parser('status')
    commands.add_parser('install-scheduler')
    commands.add_parser('scheduler-status')
    commands.add_parser('disable-scheduler')
    commands.add_parser('file-projects')
    cmd=commands.add_parser('search');cmd.add_argument('query');cmd.add_argument('--limit',type=int,default=15);cmd.add_argument('--semantic',action='store_true')
    cmd=commands.add_parser('brief');cmd.add_argument('project')
    args=parser.parse_args()
    if args.command=='file-projects':
        from .routing import deliver
        report=deliver(args.root)
        print(json.dumps({'filed':report['receipts'],'pending_count':len(report['pending'])},indent=2));return 0
    if args.command in ['install-scheduler','scheduler-status','disable-scheduler']:
        from .scheduler import install,service_status,remove
        fn={'install-scheduler':install,'scheduler-status':service_status,'disable-scheduler':remove}[args.command]
        print(json.dumps(fn(args.root),indent=2));return 0
    if args.command=='sync':
        try:
            status=sync(args.root,args.codex_home,args.force)
        except BlockingIOError:
            print(json.dumps({'status':'already_running'}));return 0
        print(json.dumps({'run_id':status['run_id'],'status':status['status'],
                          'changed':status['changed'],'unchanged':status['unchanged'],
                          'errors':len(status['errors']), 'unavailable_history':len(status.get('unavailable_history',[])),
                          'sources':status['sources']},indent=2));return 0 if status['status']=='ok' else 1
    if args.command=='status':
        p=args.root/'System/State/status.json'
        print(p.read_text() if p.exists() else json.dumps({'status':'never_run'}));return 0
    store=Store(args.root)
    try:
        if args.command=='search':
            if args.semantic:
                from .semantic import query,refresh
                refresh(store)
                results=query(json.loads((store.state/'semantic.json').read_text()),args.query,args.limit)
            else:results=store.search(args.query,args.limit)
            print(json.dumps(results,indent=2,ensure_ascii=False))
        else:
            ids={p['id'] for p in store.registry()}
            if args.project not in ids:
                parser.error('Unknown project ID')
            print((args.root/'Projects'/(args.project+'.md')).read_text())
    finally:
        store.close()
    return 0


if __name__=='__main__':
    raise SystemExit(main())
