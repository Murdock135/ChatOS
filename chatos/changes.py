"""Count captured changes without confusing additions with revisions."""
import json
import re
from pathlib import Path


def snapshot_manifest(root: Path) -> dict:
    """Read the published snapshot manifest, or an empty initial baseline."""
    pointer = root / 'System/Latest snapshot.md'
    match = re.search(r'\]\((Snapshots/[^)]+/Index.md)\)', pointer.read_text()) if pointer.exists() else None
    return json.loads((pointer.parent / match.group(1)).with_name('manifest.json').read_text()) if match else {}


def count_changes(before: dict, after: dict) -> dict:
    """Compare stable identities and hashes, counting each identity once."""
    return {
        'new': len(after.keys() - before.keys()),
        'updated': sum(before[key] != after[key] for key in before.keys() & after.keys()),
        'removed': len(before.keys() - after.keys()),
        'total': len(after),
    }


def behavior_changes(before: dict, after: dict) -> dict:
    """Compare skill bundles and captured files against the previous snapshot."""
    groups = ['skills', 'memory', 'instructions', 'rules', 'automations', 'workspace', 'configuration']

    def identities(manifest):
        result = {group: {} for group in groups}
        files = manifest.get('files', [])
        for skill in manifest.get('skills', []):
            source = Path(skill['source'])
            # Include supporting files: changing a reference also updates its skill.
            bundle = sorted((file['source'], file['sha256']) for file in files
                            if source in Path(file['source']).parents)
            result['skills'][str(source)] = (skill['sha256'], bundle)
        for file in files:
            category = file['category']
            path = Path(file['source'])
            if category == 'workspace' and 'System/Memory' in path.as_posix():
                category = 'memory'
            if category in result and category != 'skills':
                result[category][file['source']] = file['sha256']
        if manifest.get('configuration_source_sha256') is not None:
            result['configuration']['config.toml'] = manifest['configuration_source_sha256']
        return result

    old, new = identities(before), identities(after)
    return {'initial_capture': not bool(before),
            **{group: count_changes(old[group], new[group]) for group in groups}}


def conversation_hashes(store) -> dict:
    return {(row['source'], row['id']): row['content_hash']
            for row in store.db.execute('SELECT source, id, content_hash FROM conversations')}
