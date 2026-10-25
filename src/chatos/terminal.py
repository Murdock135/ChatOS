"""Readable CLI reports with optional Rich formatting and explicit JSON output."""
import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.table import Table
    from rich.text import Text
except ImportError:
    Console = None


class Report:
    def __init__(self, stream=None):
        self.stream = stream or sys.stdout
        self.console = Console(file=self.stream, markup=False, highlight=False) if Console else None

    def text(self, value: str, style: str = ''):
        if self.console:
            self.console.print(Text(value, style=style))
        else:
            print(value, file=self.stream)

    def table(self, title: str, columns: list[str], rows: list):
        self.text('\n' + title, 'bold cyan')
        if not rows:
            self.text('  None')
        elif self.console:
            table = Table(*columns, header_style='bold', expand=False)
            for row in rows:
                table.add_row(*(Text(str(cell)) for cell in row))
            self.console.print(table)
        else:
            values = [[str(cell) for cell in row] for row in [columns, *rows]]
            widths = [max(len(row[i]) for row in values) for i in range(len(columns))]
            for row in values:
                self.text('  ' + '  '.join(cell.ljust(width) for cell, width in zip(row, widths)))

    def details(self, data):
        """Render remaining structured fields without interpreting source text as markup."""
        if isinstance(data, dict):
            for key, value in data.items():
                label = key.replace('_', ' ').capitalize()
                if isinstance(value, (dict, list)):
                    self.text('\n' + label, 'bold')
                    self.details(value)
                else:
                    self.text(f'  {label}: {value if value is not None else "unknown"}')
        elif isinstance(data, list):
            if not data:
                self.text('  None')
            for item in data:
                if isinstance(item, (dict, list)):
                    self.details(item)
                    self.text('')
                else:
                    self.text('  • ' + str(item))
        else:
            self.text(str(data))


def local_time(value):
    if not value:
        return 'unknown'
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(
        ZoneInfo('America/Chicago')).strftime('%Y-%m-%d %I:%M:%S %p %Z')


def print_report(data, command: str, as_json: bool = False, stream=None):
    """Print run metadata first, captured changes next, and supporting detail last."""
    output = Report(stream)
    if as_json:
        print(json.dumps(data, indent=2, ensure_ascii=False), file=output.stream)
        return
    output.text('ChatGrep · ' + command, 'bold')
    if isinstance(data, str):
        if output.console:
            output.console.print(Markdown(data))
        else:
            output.text(data)
        return
    if command in ['sync', 'status'] and isinstance(data, dict):
        state = data.get('status', 'unknown')
        if state in ['already_running', 'never_run']:
            output.text('Status: ' + state, 'yellow')
            return
        output.text(f'Run ID: {data.get("run_id", "unknown")}   Status: {state}',
                    'green' if state == 'ok' else 'yellow')
        output.text(f'Errors: {len(data.get("errors", []))}   Parse warnings: {len(data.get("source_warnings", []))}')
        output.text('Started:  ' + local_time(data.get('started_at')))
        output.text('Finished: ' + local_time(data.get('finished_at')))
        changes = data.get('changes')
        if changes:
            labels = {'chats': 'Chats', 'skills': 'Skills', 'memory': 'Memory files',
                      'instructions': 'Instruction files', 'rules': 'Rule files',
                      'automations': 'Schedule definitions', 'workspace': 'Workspace files',
                      'configuration': 'Configuration files'}
            output.table('Changes captured this run', ['Item', 'New', 'Updated', 'Removed', 'Total'],
                         [(label, *(changes[key][field] for field in ['new', 'updated', 'removed', 'total']))
                          for key, label in labels.items() if key in changes])
            output.text('Skills count bundles; memory and other behavior rows count files.', 'dim')
            if changes.get('initial_capture'):
                output.text('Initial behavior inventory: New means newly captured, not newly installed.', 'dim')
            if 'skills' not in changes:
                output.text('Behavior-file changes unavailable: verification did not complete.', 'yellow')
        else:
            output.text('Change counts unavailable for this saved run; run sync to record them.')
        output.table('Sources', ['Source', 'State', 'Details'],
                     [(name, value['status'], value.get('detail', '')) for name, value in data.get('sources', {}).items()])
        output.details({key: data[key] for key in ['errors', 'source_warnings'] if data.get(key)})
        output.details({key: data[key] for key in ['backup', 'retrieval', 'feedback_review'] if key in data})
        unavailable = len(data['unrecovered_history']) if 'unrecovered_history' in data else 'unknown'
        output.text(f'Uncaptured Codex histories: {unavailable}. Source coverage is separate from run success.')
    elif command == 'doctor' and isinstance(data, dict):
        output.text('Health: ' + ('OK' if data.get('ok') else 'FAILED'),
                    'green' if data.get('ok') else 'red')
        output.text(f'Errors: {len(data.get("errors", []))}   Warnings: {len(data.get("warnings", []))}')
        output.text('Checked: ' + local_time(data.get('checked_at')))
        behavior = data.get('behavior_files', {})
        output.table('Checks', ['Check', 'Result'], [
            ('Database integrity', data.get('database_integrity', 'unknown')),
            ('Conversations', data.get('conversations', 'unknown')),
            ('Missing conversation files', len(data.get('missing_generated_files', []))),
            ('Mismatched conversation files', len(data.get('mismatched_canonical_files', []))),
            ('Behavior archive', 'verified' if behavior.get('ok') else 'not verified'),
            ('Sync age (seconds)', data.get('sync_age_seconds', 'unknown')),
        ])
        output.details({key: data[key] for key in ['errors', 'warnings', 'latest_backup'] if key in data})
        problems = {key: value for key, value in behavior.items() if value and key != 'ok'}
        if problems:
            output.details({'behavior_file_problems': problems})
    elif command == 'search' and isinstance(data, list):
        for index, item in enumerate(data, 1):
            output.text(f'\n{index}. {item.get("title", "Untitled")}', 'bold cyan')
            identity = item.get('conversation_id') or item.get('id', 'unknown')
            output.text(f'  {item.get("source", "unknown")} · {identity}')
            output.text(item.get('excerpt') or item.get('preview') or item.get('file_path', ''))
        if not data:
            output.text('No matching conversations.')
    else:
        output.details(data)
