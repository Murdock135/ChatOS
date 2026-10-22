"""Archive accessible Codex behavior files without changing their live sources.

Run manually with Python 3. Creates a new dated snapshot on every run.
Never copies authentication, session transcripts, runtime databases, or logs.
Configuration values are limited to an explicit allowlist.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib
import json
import re
from system_inventory import discover_skills, workspace_files, refresh

VAULT = Path(__file__).resolve().parents[2]
SOURCE = Path('/Users/zayan/.codex')
STAMP = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H-%M-%S-%fZ')
DEST = VAULT / 'System' / 'Snapshots' / STAMP
DEST.mkdir(parents=True, exist_ok=False)
SKIP = {'.git', 'node_modules', '__pycache__', '.venv', '.DS_Store'}
records = []
skipped = []


def copy_file(source, relative, category):
    if source.is_symlink():
        skipped.append({'source': str(source), 'reason': 'symlink'})
        return
    content = source.read_bytes()
    target = DEST / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    records.append({'source': str(source), 'snapshot': str(relative),
                    'category': category, 'bytes': len(content),
                    'sha256': hashlib.sha256(content).hexdigest()})


def copy_tree(source, relative, category):
    for item in sorted(source.rglob('*')):
        rel = item.relative_to(source)
        if set(rel.parts) & SKIP:
            continue
        if item.is_file():
            copy_file(item, relative / rel, category)


copy_file(SOURCE / 'AGENTS.md', Path('Instructions/Global instructions.md'), 'instructions')
for name in ['memories', 'memories_v2']:
    copy_tree(SOURCE / name, Path('Memory') / name, 'memory')
copy_tree(SOURCE / 'rules', Path('Rules'), 'rules')
for source in sorted((SOURCE / 'automations').glob('*/automation.toml')):
    copy_file(source, Path('Automations') / source.parent.name / source.name, 'automations')

skills = discover_skills(VAULT, SOURCE)
for skill in skills:
    if skill['scope'] != 'workspace':
        copy_tree(Path(skill['source']), Path(skill['snapshot']), 'skills')
for source in workspace_files(VAULT):
    copy_file(source, Path('Workspace') / source.relative_to(VAULT), 'workspace')

# Retain setting names and a few non-secret preferences; omit all other values.
safe = {'model', 'model_reasoning_effort', 'model_verbosity', 'approval_policy',
        'sandbox_mode', 'personality', 'web_search'}
settings = []
section = ''
for line in (SOURCE / 'config.toml').read_text().splitlines():
    stripped = line.strip()
    if stripped.startswith('['):
        section = stripped
    match = re.match(r'^([A-Za-z_][A-Za-z0-9_-]*)\s*=\s*(.*)$', stripped)
    if match:
        key, value = match.groups()
        item = {'section': section, 'key': key, 'value': '[omitted]'}
        if not section and key in safe and re.fullmatch(r'"[A-Za-z0-9_. -]+"', value):
            item['value'] = value[1:-1]
        settings.append(item)
(DEST / 'Configuration').mkdir()
(DEST / 'Configuration/settings-inventory.json').write_text(json.dumps({
    'source': str(SOURCE / 'config.toml'),
    'note': 'Inventory only; not a loadable configuration. Non-allowlisted values omitted.',
    'settings': settings}, indent=2) + '\n')

manifest = {'captured_at_utc': STAMP, 'source_root': str(SOURCE), 'workspace_root': str(VAULT),
            'configuration_source_sha256': hashlib.sha256((SOURCE / 'config.toml').read_bytes()).hexdigest(),
            'files': records, 'skills': skills, 'skipped': skipped,
            'exclusions': ['auth.json and credentials', 'runtime databases',
                           'session transcripts and history', 'logs and caches outside skill bundles',
                           'non-allowlisted configuration values', 'symlinks and development dependencies']}
(DEST / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
lines = ['# Codex and workspace system snapshot', '', f'Captured at {STAMP} (UTC).', '',
         'Copies of accessible local files; not automatically loaded or synchronized.', '',
         '## Contents', '']
for category, count in sorted(Counter(x['category'] for x in records).items()):
    lines.append(f'- {category}: {count} files')
lines += ['', '## Memory', '',
          '- [Memory registry](Memory/memories/MEMORY.md)',
          '- [Memory summary](Memory/memories/memory_summary.md)',
          '- [Second memory store summary](Memory/memories_v2/memory_summary.md)', '',
          '## Skills', '',
          'Discovered on disk; presence does not establish availability in every chat.', '']
for skill in skills:
    lines.append(f'- [{skill["name"]}]({skill["snapshot"]}/SKILL.md) — {skill["scope"]}; {skill["activation"]}.')
lines += ['', '## Workspace-owned behavior files', '',
          '- [Workspace instructions](Workspace/AGENTS.md)',
          '- [Working memory](Workspace/System/Memory/Working%20memory.md)',
          '- [Project registry](Workspace/System/Projects/registry.json)',
          '- [Operating guidance](Workspace/System/Operating%20guidance.md)',
          '', 'Workspace scripts, skills, guidance, and project-routing data are preserved in Workspace/.',
          'Conversations, operational event data, generated live index files, and previous snapshots are excluded.',
          'This is a behavior-file archive, not a standalone executable workspace.']
lines += ['', '## Provenance and limits', '',
          'See [manifest](manifest.json) for original paths, hashes, exclusions, and skipped files.',
          'See [configuration inventory](Configuration/settings-inventory.json) for setting names and selected preferences.',
          'Memory may contain stale facts or unconfirmed inferences. Verify consequential claims against live sources.',
          'Original absolute paths inside archived skills still refer to the live installation.',
          'This snapshot is not a complete runtime backup or a dump of platform instructions.', '']
(DEST / 'Index.md').write_text('\n'.join(lines))
(VAULT / 'System/Latest snapshot.md').write_text(
    '# Latest system snapshot\n\n'
    '[Current skills inventory](Skills/Index.md)\n\n'
    f'[Open snapshot index](Snapshots/{STAMP}/Index.md)\n\n'
    f'Captured at {STAMP} (UTC). Includes Codex and workspace-owned behavior files.\n\n'
    'This is a dated copy, not live synchronization. Run '
    '`python3 System/Scripts/system_inventory.py --check` to detect unindexed skills or workspace snapshot drift.\n')
refresh(VAULT, SOURCE)
print(json.dumps({'snapshot': str(DEST), 'copied_files': len(records),
                  'skill_bundles': len(skills), 'bytes': sum(x['bytes'] for x in records),
                  'skipped': len(skipped)}))
