"""Absolute-path entry point for launchd, independent of its Python import path."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from chatos.runtime import sync

if __name__=='__main__':
    import json
    try:
        result=sync()
        print(json.dumps({k:result[k] for k in ['run_id','status','changed','unchanged','finished_at']}))
        raise SystemExit(0 if result['status']=='ok' else 1)
    except BlockingIOError:
        print('{"status":"already_running"}')
