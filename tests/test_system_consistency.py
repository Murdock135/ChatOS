"""Regression checks for missing skills, stale snapshots, and concurrent logging."""
from pathlib import Path
import hashlib
import importlib.util
import json
import multiprocessing
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'System/Scripts'
sys.path.insert(0, str(SCRIPTS))
import system_inventory as inventory


def load_logger():
    spec = importlib.util.spec_from_file_location('log_test', SCRIPTS / 'system_log.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_event(root, event):
    logger = load_logger()
    logger.LOGS = Path(root)
    logger.LEDGER = logger.LOGS / 'events.jsonl'
    logger.save([event, event])


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.vault, self.codex = self.root / 'vault', self.root / 'codex'
        self.vault.mkdir()
        (self.vault / 'AGENTS.md').write_text('Read System/Skills/router/SKILL.md\n')
        self.add_skill('router')
        self.capture()

    def add_skill(self, name):
        p = self.vault / f'System/Skills/{name}/SKILL.md'
        p.parent.mkdir(parents=True)
        p.write_text(f'---\nname: {name}\ndescription: Test\n---\n# Skill\n')

    def capture(self):
        inventory.refresh(self.vault, self.codex)
        self.snapshot = self.vault / 'System/Snapshots/test'
        self.snapshot.mkdir(parents=True, exist_ok=True)
        records = []
        for p in inventory.workspace_files(self.vault):
            rel = Path('Workspace') / p.relative_to(self.vault)
            target = self.snapshot / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            data = p.read_bytes()
            target.write_bytes(data)
            records.append({'source': str(p), 'snapshot': str(rel), 'category': 'workspace',
                            'sha256': hashlib.sha256(data).hexdigest()})
        (self.snapshot / 'manifest.json').write_text(json.dumps({
            'skills': inventory.discover_skills(self.vault, self.codex), 'files': records}))
        (self.snapshot / 'Index.md').write_text('# Snapshot\n')
        (self.vault / 'System/Latest snapshot.md').write_text('[Index](Snapshots/test/Index.md)\n')

    def test_workspace_skill_is_captured_and_indexed(self):
        report = inventory.check(self.vault, self.codex)
        self.assertTrue(report['ok'], report)
        self.assertIn('router', (self.vault / 'System/Skills/Index.md').read_text())

    def test_new_skill_cannot_silently_disappear_from_indexes(self):
        self.add_skill('new-skill')
        report = inventory.check(self.vault, self.codex)
        self.assertFalse(report['ok'])
        self.assertEqual(len(report['live_index_missing']), 1)
        self.assertEqual(len(report['snapshot_missing']), 1)
        inventory.refresh(self.vault, self.codex)
        self.assertEqual(inventory.check(self.vault, self.codex)['live_index_missing'], [])
        self.assertEqual(len(inventory.check(self.vault, self.codex)['snapshot_missing']), 1)

    def test_instruction_changes_are_detected(self):
        (self.vault / 'AGENTS.md').write_text('Changed instructions\n')
        report = inventory.check(self.vault, self.codex)
        self.assertFalse(report['ok'])
        self.assertIn(str(self.vault / 'AGENTS.md'), report['snapshot_workspace_changed'])

    def test_corrupted_snapshot_is_detected(self):
        (self.snapshot / 'Workspace/AGENTS.md').write_text('Corrupted\n')
        self.assertIn('Workspace/AGENTS.md', inventory.check(
            self.vault, self.codex)['snapshot_integrity_errors'])

    def test_removed_skill_is_detected(self):
        (self.vault / 'System/Skills/router/SKILL.md').unlink()
        report = inventory.check(self.vault, self.codex)
        self.assertEqual(len(report['live_index_removed']), 1)
        self.assertEqual(len(report['snapshot_removed']), 1)

    def test_new_supporting_file_is_detected_without_entrypoint_change(self):
        p = self.codex / 'skills/example/SKILL.md'
        p.parent.mkdir(parents=True)
        p.write_text('---\nname: example\ndescription: Test\n---\n')
        resource = p.parent / 'reference.txt'
        resource.write_text('New reference\n')
        report = inventory.check(self.vault, self.codex)
        self.assertIn(str(resource), report['snapshot_source_missing'])

    def test_credential_named_support_files_are_excluded(self):
        secret=self.vault/'System/Skills/router/.env'
        secret.write_text('SECRET VALUE')
        self.assertNotIn(secret,inventory.workspace_files(self.vault))
        self.assertNotIn(secret,list(inventory.walk_files(secret.parent)))

    def test_configuration_view_corruption_is_detected(self):
        from snapshot_codex_state import create_snapshot
        self.codex.mkdir()
        result=create_snapshot(self.vault,self.codex)
        settings=Path(result['snapshot'])/'Configuration/settings-inventory.json'
        settings.write_text('Corrupted settings view')
        self.assertIn('Configuration/settings-inventory.json',inventory.check(self.vault,self.codex)['snapshot_integrity_errors'])

    def test_failed_snapshot_preserves_published_pointer(self):
        from snapshot_codex_state import create_snapshot
        self.codex.mkdir()
        pointer=self.vault/'System/Latest snapshot.md'
        original=pointer.read_text()
        read=Path.read_bytes
        def fail(path):
            if path==self.vault/'AGENTS.md':
                raise OSError('Simulated read failure')
            return read(path)
        with patch.object(Path,'read_bytes',fail):
            with self.assertRaises(OSError):
                create_snapshot(self.vault,self.codex)
        self.assertEqual(pointer.read_text(),original)
        self.assertFalse(list((self.vault/'System/Snapshots').glob('.staging-*')))

    def test_discovery_does_not_follow_symlinked_directories(self):
        external=self.root/'private';external.mkdir()
        (external/'SKILL.md').write_text('Never archive this')
        (self.vault/'System/Skills/linked').symlink_to(external,target_is_directory=True)
        self.assertFalse(any('linked' in str(p) for p in inventory.workspace_files(self.vault)))
        self.assertFalse(any('linked' in s['entrypoint'] for s in inventory.discover_skills(self.vault,self.codex)))


class LogTests(unittest.TestCase):
    def test_concurrent_retries_produce_one_ledger_event(self):
        with tempfile.TemporaryDirectory() as temp:
            event = {'id': 'same-event', 'observed_at': '2026-10-22T16:00:00Z',
                     'kind': 'chat', 'status': 'open', 'summary': 'Example'}
            context = multiprocessing.get_context('spawn')
            processes = [context.Process(target=write_event, args=(temp, event)) for _ in range(4)]
            for p in processes:
                p.start()
            for p in processes:
                p.join(15)
                self.assertEqual(p.exitcode, 0)
            rows = [json.loads(line) for line in (Path(temp) / 'events.jsonl').read_text().splitlines()]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['id'], event['id'])
            self.assertIn('same-event', (Path(temp) / 'Event log.md').read_text())


if __name__ == '__main__':
    unittest.main()
