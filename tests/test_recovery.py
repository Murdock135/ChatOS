from pathlib import Path
import json
import tempfile
import unittest
from chatos.core import Store
from chatos.runtime import backup
from chatos.recovery import restore,verify_backup,doctor


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'live'
        self.store=Store(self.root);self.addCleanup(self.store.close)
        self.record={'source':'muse','id':'recover-one','title':'Recover me','created_at':'2026-10-22',
                     'messages':[{'role':'user','id':'message-1','text':'A recorded commitment'}]}
        self.store.put(self.record)
        self.backup=Path(backup(self.store)['path'])

    def test_isolated_restore_preserves_live_source_and_regenerates_files(self):
        before=self.backup.read_bytes()
        destination=self.root.parent/'recovered'
        report=restore(self.backup,destination)
        self.assertEqual(report['restored_conversations'],1)
        self.assertEqual(self.backup.read_bytes(),before)
        recovered=Store(destination)
        try:
            record=recovered.records()[0]
            self.assertEqual(record['messages'],self.record['messages'])
            self.assertEqual(json.loads((destination/record['file_path']).with_suffix('.json').read_text()),record)
            self.assertIn('A recorded commitment',(destination/record['file_path']).read_text())
            self.assertEqual(recovered.db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
        finally:recovered.close()
        with self.assertRaises(FileExistsError):restore(self.backup,destination)
        self.assertEqual(len(self.store.records()),1)

    def test_corrupt_retained_backup_is_never_reported_healthy(self):
        with self.backup.open('ab') as stream:stream.write(b'corruption')
        with self.assertRaises(ValueError):verify_backup(self.backup)
        with self.assertRaises(ValueError):backup(self.store)
        self.assertFalse(doctor(self.root)['ok'])

    def test_doctor_detects_canonical_corruption_and_missing_files(self):
        record=self.store.records()[0];note=self.root/record['file_path']
        note.write_text('Changed generated source')
        note.with_suffix('.json').write_text('{broken')
        result=doctor(self.root)
        self.assertFalse(result['ok'])
        self.assertEqual(len(result['mismatched_canonical_files']),2)
        note.unlink()
        self.assertIn(str(note.resolve()),doctor(self.root)['missing_generated_files'])


if __name__=='__main__':unittest.main()
