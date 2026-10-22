"""Shared discovery for live skill inventory, snapshots, and consistency checks."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import quote
import argparse
import hashlib
import json
import re
import os

VAULT = Path(__file__).resolve().parents[2]
CODEX = Path('/Users/zayan/.codex')
SKIP = {'.git', 'node_modules', '__pycache__', '.venv', '.DS_Store'}


def sensitive_name(path):
    name=path.name.lower()
    return (name=='.env' or name.startswith('.env.') or
            name in {'auth.json','credentials','credentials.json','id_rsa','id_ed25519'} or
            path.suffix.lower() in {'.pem','.key','.p12','.pfx'})


def walk_files(root, excluded=()):
    """Prune archives/dependencies before descent; never follow directory symlinks."""
    root = Path(root)
    if root.is_symlink():
        return
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP and not (Path(base)/d).is_symlink()
                         and (Path(base)/d).relative_to(root).as_posix() not in excluded)
        for name in sorted(files):
            item = Path(base)/name
            if name not in SKIP and not item.is_symlink() and not sensitive_name(item):
                yield item


def skill_roots(vault=VAULT, codex=CODEX):
    return [(vault / 'System/Skills', 'workspace'), (codex / 'skills', 'local'),
            (codex.parent / '.agents/skills', 'user'),
            (codex / 'plugins/cache', 'plugins'), (codex / 'memories/skills', 'memory-skills')]


def discover_skills(vault=VAULT, codex=CODEX):
    instructions = (vault / 'AGENTS.md').read_text() if (vault / 'AGENTS.md').exists() else ''
    global_path=codex/'AGENTS.override.md' if (codex/'AGENTS.override.md').exists() else codex/'AGENTS.md'
    global_instructions=global_path.read_text() if global_path.exists() else ''
    result = []
    for root, scope in skill_roots(vault, codex):
        for entry in sorted(p for p in walk_files(root) if p.name == 'SKILL.md'):
            if entry.is_symlink() or set(entry.relative_to(root).parts) & SKIP:
                continue
            raw = entry.read_bytes()
            match = re.search(r'^name:\s*[\'"]?([a-z0-9-]+)', raw.decode(), re.M)
            relative = entry.relative_to(vault) if scope == 'workspace' else None
            snapshot = (Path('Workspace') / relative if relative else
                        Path('Skills') / scope / entry.relative_to(root))
            result.append({'name': match.group(1) if match else entry.parent.name,
                           'scope': scope, 'source': str(entry.parent),
                           'entrypoint': str(entry), 'snapshot': str(snapshot.parent),
                           'sha256': hashlib.sha256(raw).hexdigest(),
                           'activation': ('referenced by workspace AGENTS.md' if relative and str(relative) in instructions
                                          else 'referenced by global instructions' if str(entry) in global_instructions
                                          else 'not verified by this inventory')})
    return result


def workspace_files(vault=VAULT):
    """Behavior/config/docs only: exclude archives, event data, and generated indexes."""
    excluded = {'System/Snapshots', 'System/Logs', 'System/State', 'System/Imports', 'System/Backups', 'System/Models'}
    generated = {'System/Latest snapshot.md', 'System/Skills/Index.md', 'System/Skills/inventory.json',
                 'STATUS.md', 'Humans/dashboard.html','Humans/explorer.html','System/Projects/Automatic routing queue.md',
                 'System/Projects/Automatic filing receipts.md', 'System/Schedules/Index.md', 'System/Feedback/Review queue.md'}
    dependency_files=[p for pattern in ['requirements*.in','requirements*.txt','requirements*.lock','pyproject.toml','uv.lock'] for p in vault.glob(pattern)]
    candidates = (list(vault.glob('*.md')) + dependency_files + list(walk_files(vault / 'Humans')) +
                  list(walk_files(vault / 'System', {'Snapshots','Logs','State','Imports','Backups','Models'})) +
                  list(walk_files(vault / 'tests')) + list(walk_files(vault / 'chatos')) + list(walk_files(vault / '.vscode')) +
                  ([vault/'.gitignore'] if (vault/'.gitignore').exists() else []))
    result = set()
    for p in candidates:
        rel = p.relative_to(vault)
        name = rel.as_posix()
        if (not p.is_file() or p.is_symlink() or set(rel.parts) & SKIP or name in generated or
                any(name == prefix or name.startswith(prefix + '/') for prefix in excluded)):
            continue
        result.add(p)
    return sorted(result)


def codex_files(vault=VAULT, codex=CODEX):
    candidates = [codex / 'AGENTS.md',codex / 'AGENTS.override.md']
    for name in ['memories', 'memories_v2', 'rules']:
        candidates.extend(walk_files(codex / name))
    candidates.extend((codex / 'automations').glob('*/automation.toml'))
    for skill in discover_skills(vault, codex):
        if skill['scope'] != 'workspace':
            candidates.extend(walk_files(skill['source']))
    return sorted({p for p in candidates if p.is_file() and not p.is_symlink()
                   and not set(p.parts) & SKIP})


def refresh(vault=VAULT, codex=CODEX):
    skills = discover_skills(vault, codex)
    target = vault / 'System/Skills'
    target.mkdir(parents=True, exist_ok=True)
    checked = datetime.now(timezone.utc).isoformat()
    (target / 'inventory.json').write_text(json.dumps({
        'checked_at': checked, 'roots': [str(p) for p, _ in skill_roots(vault, codex)],
        'skills': skills, 'limits': 'Discovered files; runtime availability is not established.'}, indent=2) + '\n')
    lines = ['# Current skills inventory', '', f'Last scanned: {checked} (UTC).', '',
             'This is a generated inventory of configured file roots, not automatic background discovery.',
             'Run `python3 System/Scripts/system_inventory.py` to refresh, or `--check` to detect drift.',
             'Cached/imported files are not proof that a skill is installed or available in a chat.', '']
    for scope in ['workspace', 'local', 'user', 'plugins', 'memory-skills']:
        group = [s for s in skills if s['scope'] == scope]
        lines += [f'## {scope} — {len(group)}', '']
        for s in group:
            entry = Path(s['entrypoint'])
            link = quote(str(entry.relative_to(target)) if target in entry.parents else str(entry), safe='/')
            lines.append(f'- [{s["name"]}]({link}) — {s["activation"]}.')
        lines.append('')
    (target / 'Index.md').write_text('\n'.join(lines))
    return skills


def check(vault=VAULT, codex=CODEX):
    actual = discover_skills(vault, codex)
    index = vault / 'System/Skills/inventory.json'
    saved = json.loads(index.read_text()).get('skills', []) if index.exists() else []
    key = lambda s: s['entrypoint']
    old, new = {key(s): s for s in saved}, {key(s): s for s in actual}
    report = {'live_index_missing': sorted(set(new) - set(old)),
              'live_index_removed': sorted(set(old) - set(new)),
              'live_index_changed': sorted(k for k in set(old) & set(new) if old[k] != new[k]),
              'snapshot_missing': [], 'snapshot_changed': [], 'snapshot_removed': [],
              'snapshot_integrity_errors': [], 'snapshot_workspace_missing': [],
              'snapshot_workspace_changed': [], 'snapshot_workspace_removed': []}
    pointer = vault / 'System/Latest snapshot.md'
    match = re.search(r'\]\((Snapshots/[^)]+/Index.md)\)', pointer.read_text()) if pointer.exists() else None
    manifest_path = pointer.parent / match.group(1) if match else None
    if manifest_path:
        manifest_path = manifest_path.parent / 'manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path and manifest_path.exists() else {}
    captured = {str(Path(s['source']) / 'SKILL.md'): s for s in manifest.get('skills', [])}
    report['snapshot_missing'] = sorted(set(new) - set(captured))
    report['snapshot_removed'] = sorted(set(captured) - set(new))
    snapshot_root = manifest_path.parent if manifest_path and manifest_path.exists() else None
    for k in sorted(set(new) & set(captured)):
        p = snapshot_root / captured[k]['snapshot'] / 'SKILL.md'
        if captured[k]!=new[k] or not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != new[k]['sha256']:
            report['snapshot_changed'].append(k)
    current = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in workspace_files(vault)}
    previous = {f['source']: f for f in manifest.get('files', []) if f['category'] == 'workspace'}
    report['snapshot_workspace_missing'] = sorted(set(current) - set(previous))
    report['snapshot_workspace_removed'] = sorted(set(previous) - set(current))
    report['snapshot_workspace_changed'] = sorted(k for k in set(current) & set(previous)
                                                   if current[k] != previous[k]['sha256'])
    for item in manifest.get('files', [])+manifest.get('derived_files',[]):
        p = snapshot_root / item['snapshot']
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != item['sha256']:
            report['snapshot_integrity_errors'].append(item['snapshot'])
    sources = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in codex_files(vault, codex)}
    old_sources = {f['source']: f for f in manifest.get('files', []) if f['category'] != 'workspace'}
    report['snapshot_source_missing'] = sorted(set(sources) - set(old_sources))
    report['snapshot_source_removed'] = sorted(set(old_sources) - set(sources))
    report['snapshot_source_changed'] = sorted(k for k in set(sources) & set(old_sources)
                                                if sources[k] != old_sources[k]['sha256'])
    config = codex / 'config.toml'
    report['configuration_changed'] = ((hashlib.sha256(config.read_bytes()).hexdigest() if config.is_file() else None)
                                       != manifest.get('configuration_source_sha256'))
    report['ok'] = bool(manifest) and index.exists() and not any(report.values())
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        result = check()
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result['ok'] else 1)
    print(json.dumps({'indexed_skills': len(refresh())}))
