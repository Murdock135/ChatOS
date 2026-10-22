from pathlib import Path
import json
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from chatos.importers import read_codex_history
from chatos.runtime import sync
from chatos.core import Store
from chatos.visibility import clean_text,origin_hint


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve();self.home=self.root/'codex';self.home.mkdir()
        self.path=self.home/'thread_history_1.sqlite'
        self.info={'id':'missing-one','title':'Recovered test','model':'thread-fallback',
                   'cwd':str(self.root),'created_at':1792686423,'updated_at':1792686424,
                   'rollout_path':str(self.home/'missing.jsonl')}
        db=sqlite3.connect(str(self.path))
        db.executescript('''CREATE TABLE thread_items(thread_id,turn_id,item_id,rollout_ordinal,created_at_ms,item_json,item_type);
                            CREATE TABLE thread_turns(thread_id,turn_id,status,started_at,completed_at,rollout_ordinal);''')
        entries=[('u1','userMessage',{'type':'userMessage','content':[{'type':'text','text':'An earlier visible question'}]}),
                 ('secret','reasoning',{'type':'reasoning','text':'PRIVATE REASONING'}),
                 ('wrapper','userMessage',{'type':'userMessage','content':[{'type':'text','text':'<recommended_plugins>PRIVATE HARNESS</recommended_plugins><environment_context>generated</environment_context>'}]}),
                 ('a1','agentMessage',{'type':'agentMessage','phase':'final_answer','text':'An earlier visible answer'}),
                 ('tool','mcpToolCall',{'type':'mcpToolCall','text':'PRIVATE TOOL PAYLOAD'})]
        for ordinal,(identity,kind,item) in enumerate(entries):
            db.execute('INSERT INTO thread_items VALUES(?,?,?,?,?,?,?)',('missing-one','turn-one',identity,ordinal,1792686423000+ordinal,json.dumps(item),kind))
        db.execute('INSERT INTO thread_turns VALUES(?,?,?,?,?,?)',('missing-one','turn-one','completed',1792686423000,1792686424000,0))
        db.commit();db.close()

    def test_scheduled_markup_is_labeled_without_asserting_execution(self):
        text='<heartbeat><automation_id>job</automation_id><instructions>Run</instructions></heartbeat>'
        self.assertEqual(clean_text('user',text),text)
        self.assertEqual(origin_hint('user',text),{'origin_hint':'automation_markup','automation_id_observed':'job'})

    def test_read_only_visible_projection_with_unknown_turn_models(self):
        before=self.path.read_bytes();record=read_codex_history(self.home,self.info)
        self.assertEqual(self.path.read_bytes(),before)
        self.assertEqual([m['id'] for m in record['messages']],['u1','a1'])
        self.assertNotIn('PRIVATE',json.dumps(record))
        self.assertEqual(record['model'],'thread-fallback')
        self.assertIsNone(record['messages'][1]['model'])
        self.assertEqual(record['model_history'],[])
        self.assertEqual(record['capture'],'partial_history_projection')

    def test_sync_recovers_and_preserves_trimmed_projection_items(self):
        archive=self.root/'archive'
        source=[(self.info['rollout_path'],self.info)]
        with patch('chatos.runtime.codex_sources',return_value=source):
            first=sync(archive,self.home)
            self.assertEqual(first['status'],'ok')
            self.assertEqual(len(first['recovered_history']),1)
            self.assertEqual(first['unrecovered_history'],[])
            second=sync(archive,self.home)
            self.assertEqual(second['changed'],0)
            db=sqlite3.connect(str(self.path))
            db.execute("DELETE FROM thread_items WHERE item_id='u1'")
            item={'type':'agentMessage','phase':'final_answer','text':'Updated answer'}
            db.execute("UPDATE thread_items SET item_json=? WHERE item_id='a1'",(json.dumps(item),))
            db.commit();db.close()
            third=sync(archive,self.home)
            self.assertEqual(third['changed'],1)
        store=Store(archive)
        try:
            messages=store.records()[0]['messages']
            self.assertEqual([m['id'] for m in messages],['u1','a1'])
            self.assertEqual(messages[1]['text'],'Updated answer')
        finally:store.close()


if __name__=='__main__':unittest.main()
