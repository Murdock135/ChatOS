"""Absolute-path entry point for launchd, independent of its Python import path."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from chatos.runtime import sync

if __name__=='__main__':
    import argparse
    from chatos.terminal import print_report
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true')
    options = parser.parse_args()
    try:
        result=sync()
        print_report(result, 'sync', options.json)
        raise SystemExit(0 if result['status']=='ok' else 1)
    except BlockingIOError:
        print_report({'status': 'already_running'}, 'sync', options.json)
