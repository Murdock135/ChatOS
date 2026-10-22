"""CLI reports preserve machine output, literal source text, and honest change counts."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from chatos import terminal
from chatos.__main__ import main
from chatos.changes import behavior_changes


class ReportTests(unittest.TestCase):
    def report(self):
        return {'run_id': 17, 'status': 'partial', 'errors': [{'error': '[red]literal error[/red]'}],
                'sources': {'codex': {'status': 'partial', 'detail': '[red]unreadable[/red]'}},
                'changes': {'chats': {'new': 2, 'updated': 3, 'removed': 0, 'total': 8}}}

    def test_metadata_precedes_changes_and_source_details_remain_visible(self):
        for renderer in [terminal.Console, None]:
            with self.subTest(rich=renderer is not None), patch.object(terminal, 'Console', renderer):
                stream = io.StringIO()
                terminal.print_report(self.report(), 'sync', stream=stream)
                text = stream.getvalue()
                self.assertLess(text.index('Errors: 1'), text.index('Changes captured this run'))
                self.assertLess(text.index('Changes captured this run'), text.index('Sources'))
                self.assertIn('[red]unreadable[/red]', text)
                self.assertIn('[red]literal error[/red]', text)
                self.assertIn('Behavior-file changes unavailable', text)
                self.assertIn('Uncaptured Codex histories: unknown', text)

    def test_json_is_complete_and_unadorned(self):
        stream = io.StringIO()
        terminal.print_report(self.report(), 'sync', as_json=True, stream=stream)
        self.assertEqual(json.loads(stream.getvalue()), self.report())

    def test_older_status_does_not_invent_change_counts(self):
        stream = io.StringIO()
        terminal.print_report({'status': 'ok'}, 'status', stream=stream)
        self.assertIn('Change counts unavailable', stream.getvalue())
        self.assertNotIn('Changes captured this run', stream.getvalue())

    def test_cli_accepts_json_before_or_after_command(self):
        with tempfile.TemporaryDirectory() as root:
            for flags in [['--json', 'status'], ['status', '--json']]:
                stream = io.StringIO()
                with patch('sys.argv', ['chatos', '--root', root, *flags]), contextlib.redirect_stdout(stream):
                    self.assertEqual(main(), 0)
                self.assertEqual(json.loads(stream.getvalue()), {'status': 'never_run'})

    def test_failed_sync_retains_exit_code_and_unknown_behavior_counts(self):
        with tempfile.TemporaryDirectory() as root:
            stream = io.StringIO()
            args = ['chatos', '--root', str(Path(root) / 'archive'), 'sync',
                    '--codex-home', str(Path(root) / 'missing'), '--json']
            with patch('sys.argv', args), contextlib.redirect_stdout(stream):
                self.assertEqual(main(), 1)
            report = json.loads(stream.getvalue())
            self.assertEqual(report['status'], 'failed')
            self.assertTrue(report['errors'])
            self.assertEqual(report['changes']['chats']['new'], 0)
            self.assertNotIn('skills', report['changes'])

    def test_skill_supporting_files_and_memory_have_distinct_counts(self):
        before = {'skills': [{'source': '/skills/a', 'sha256': 'same'}],
                  'files': [{'source': '/skills/a/reference.md', 'sha256': 'old', 'category': 'skills'},
                            {'source': '/memory/old.md', 'sha256': 'old', 'category': 'memory'},
                            {'source': '/vault/System/Memory/Working memory.md', 'sha256': 'old', 'category': 'workspace'}]}
        after = {'skills': [{'source': '/skills/a', 'sha256': 'same'}, {'source': '/skills/b', 'sha256': 'new'}],
                 'files': [{'source': '/skills/a/reference.md', 'sha256': 'new', 'category': 'skills'},
                           {'source': '/memory/new.md', 'sha256': 'new', 'category': 'memory'},
                           {'source': '/vault/System/Memory/Working memory.md', 'sha256': 'new', 'category': 'workspace'}]}
        changes = behavior_changes(before, after)
        self.assertEqual(changes['skills'], {'new': 1, 'updated': 1, 'removed': 0, 'total': 2})
        self.assertEqual(changes['memory'], {'new': 1, 'updated': 1, 'removed': 1, 'total': 2})
        self.assertFalse(changes['initial_capture'])
        self.assertTrue(behavior_changes({}, after)['initial_capture'])
        self.assertEqual(behavior_changes(after, after)['skills']['updated'], 0)
