"""User-level macOS scheduler for deterministic sync, without model/API calls."""
from .workspace import workspace_path
from pathlib import Path
import os
import plistlib
import subprocess
import sys
from .core import ROOT,atomic,write_json,now

LABEL='local.chatos.sync'


def definition(root=ROOT, executable=None):
    root=Path(root).resolve()
    return {'Label':LABEL,'ProgramArguments':[executable or sys.executable,str(workspace_path(root, 'System/Scripts/run_sync.py'))],
            'WorkingDirectory':str(root),'StartInterval':300,'RunAtLoad':True,
            'ProcessType':'Background','Nice':10,'LowPriorityIO':True,'ThrottleInterval':60,
            'EnvironmentVariables':{'PYTHONDONTWRITEBYTECODE':'1'},
            'StandardOutPath':str(workspace_path(root, 'System/Logs/launchd.out.log')),
            'StandardErrorPath':str(workspace_path(root, 'System/Logs/launchd.err.log'))}


def service_status(root=ROOT):
    target=f'gui/{os.getuid()}/{LABEL}'
    result=subprocess.run(['/bin/launchctl','print',target],capture_output=True,text=True)
    return {'label':LABEL,'installed':result.returncode==0,
            'checked_at':now(),'details':result.stdout if result.returncode==0 else result.stderr.strip()}


def install(root=ROOT):
    root=Path(root).resolve()
    if sys.platform!='darwin':raise RuntimeError('macOS only')
    agent=Path.home()/'Library/LaunchAgents'/(LABEL+'.plist')
    spec=definition(root)
    if agent.exists():
        previous=plistlib.loads(agent.read_bytes())
        if previous.get('Label')!=LABEL or previous.get('WorkingDirectory')!=str(root):
            raise RuntimeError('Existing scheduler definition has another owner; left untouched')
    agent.parent.mkdir(parents=True,exist_ok=True)
    (workspace_path(root, 'System/Logs')).mkdir(parents=True,exist_ok=True)
    atomic(agent,plistlib.dumps(spec).decode())
    domain=f'gui/{os.getuid()}'
    if service_status(root)['installed']:
        subprocess.run(['/bin/launchctl','bootout',domain,str(agent)],capture_output=True,text=True,check=True)
    result=subprocess.run(['/bin/launchctl','bootstrap',domain,str(agent)],capture_output=True,text=True)
    if result.returncode:raise RuntimeError('launchctl bootstrap failed: '+result.stderr.strip())
    subprocess.run(['/bin/launchctl','kickstart',domain+'/'+LABEL],check=True,capture_output=True,text=True)
    status=service_status(root)
    write_json(workspace_path(root, 'System/State/scheduler.json'),status)
    return status


def remove(root=ROOT):
    root=Path(root).resolve()
    agent=Path.home()/'Library/LaunchAgents'/(LABEL+'.plist')
    if agent.exists():
        spec=plistlib.loads(agent.read_bytes())
        if spec.get('WorkingDirectory')!=str(root):raise RuntimeError('Definition belongs to another root')
        # Retain the exact definition before disabling our own service.
        backup=workspace_path(root, 'System/State/disabled-scheduler.plist')
        atomic(backup,agent.read_text())
        subprocess.run(['/bin/launchctl','bootout',f'gui/{os.getuid()}',str(agent)],capture_output=True,text=True)
        agent.unlink()
    status=service_status(root)
    write_json(workspace_path(root, 'System/State/scheduler.json'),status)
    return status
