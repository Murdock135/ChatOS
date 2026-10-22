from pathlib import Path
import json
import sqlite3
import tempfile
import unittest
from chatos.schedules import collect


class ScheduleTests(unittest.TestCase):
    def test_current_inventory_preserves_unknown_outcomes_and_excludes_result_bodies(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();codex=root/'codex';folder=codex/'sqlite';folder.mkdir(parents=True)
            db=sqlite3.connect(str(folder/'codex-dev.db'))
            db.executescript('''CREATE TABLE automations(id,name,status,kind,target_thread_id,last_run_at,next_run_at,updated_at,prompt);
                CREATE TABLE automation_runs(thread_id,automation_id,status,created_at,updated_at,archived_assistant_message);''')
            db.execute('INSERT INTO automations VALUES(?,?,?,?,?,?,?,?,?)',
                       ('test','Test task','ACTIVE','heartbeat','chat',None,1792690311000,1792686423545,'PRIVATE PROMPT'))
            db.execute('INSERT INTO automation_runs VALUES(?,?,?,?,?,?)',
                       ('run-chat','test','PENDING',1792686423545,1792686423545,'PRIVATE RESULT'))
            db.commit();db.close()
            summary=collect(root/'vault',codex)
            self.assertEqual(summary['tasks'],1)
            saved=(root/'vault/System/State/schedules.json').read_text()
            self.assertNotIn('PRIVATE',saved)
            record=json.loads(saved)['tasks'][0]
            self.assertIsNone(record['last_run_at'])
            self.assertEqual(record['status'],'ACTIVE')
            self.assertIn('No timestamp recorded',(root/'vault/System/Schedules/Index.md').read_text())


if __name__=='__main__':unittest.main()
