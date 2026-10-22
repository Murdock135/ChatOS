"""Install one reversible Codex entry skill and a bounded global instruction reference."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import os
import tempfile

VAULT=Path(__file__).resolve().parents[2]
BEGIN='<!-- chat-os-entry:start -->'
END='<!-- chat-os-entry:end -->'


def atomic(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    descriptor,name=tempfile.mkstemp(prefix='.'+path.name,dir=str(path.parent))
    try:
        with os.fdopen(descriptor,'w') as stream:stream.write(text)
        os.replace(name,path)
    finally:
        if os.path.exists(name):os.unlink(name)


def install(vault=VAULT,codex=Path.home()/'.codex',skills=Path.home()/'.agents/skills'):
    vault,codex,skills=map(Path,(vault,codex,skills))
    instructions=codex/'AGENTS.md'
    if (codex/'AGENTS.override.md').exists():
        raise ValueError('Global override is present; reconcile instruction precedence before installation')
    target=skills/'chief-of-staff-entry/SKILL.md'
    source=vault/'System/Skills/chief-of-staff-entry/SKILL.md'
    for path in [instructions,target,skills,skills/'chief-of-staff-entry']:
        if any(p.is_symlink() for p in [path]+list(path.parents)):
            raise ValueError('Refusing symlinked installation destination')
    content=source.read_text()
    original=instructions.read_text() if instructions.exists() else ''
    block=BEGIN+'\n## Chief of Staff project continuity\n\n'+\
        '- For substantive project work, read '+str(source)+' and use its routing/briefing workflow. '+\
        'Preserve project instructions and source evidence; keep ambiguous or blocked filing pending. '+\
        'Small self-contained requests do not need an archive scan.\n'+END
    if target.exists() and target.read_text()!=content:
        raise ValueError('Existing entry skill differs; review it rather than overwriting')
    if BEGIN in original:
        if block not in original:raise ValueError('Managed global instructions differ; review before replacing')
        changed=False
    else:
        if END in original:raise ValueError('Malformed existing entry marker')
        stamp=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H-%M-%S-%fZ')
        backup=vault/'System/Backups/entrypoint-install'/stamp
        backup.mkdir(parents=True)
        atomic(backup/'AGENTS.original.md',original)
        atomic(backup/'manifest.json',json.dumps({'source':str(instructions),'sha256':hashlib.sha256(original.encode()).hexdigest()},indent=2)+'\n')
        changed=True
    atomic(target,content)
    if changed:atomic(instructions,original.rstrip()+'\n\n'+block+'\n')
    report={'installed_at':datetime.now(timezone.utc).isoformat(),'skill':str(target),
            'canonical_skill':str(source),'global_instructions':str(instructions),'instructions_changed':changed,
            'skill_sha256':hashlib.sha256(content.encode()).hexdigest(),
            'activation':'Files installed and global reference verified; loading in a fresh session still needs host verification.'}
    atomic(vault/'System/State/entrypoint-install.json',json.dumps(report,indent=2)+'\n')
    if target.read_text()!=content or block not in instructions.read_text():raise RuntimeError('Installation verification failed')
    return report


if __name__=='__main__':
    print(json.dumps(install(),indent=2))
