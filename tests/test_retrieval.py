from pathlib import Path
import json
import tempfile
import unittest
from chatos.core import Store
from chatos.retrieval import retrieve
from chatos.routing import assign


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        folder=self.root/'System/Projects';folder.mkdir(parents=True)
        (folder/'registry.json').write_text(json.dumps({'projects':[
            {'id':'research','name':'Research','root':'/research','entrypoint':'/research/Home.md'},
            {'id':'personal','name':'Personal','root':'/personal','entrypoint':'/personal/Home.md'}]}))
        self.store=Store(self.root);self.addCleanup(self.store.close)
        self.record={'source':'codex','id':'one','title':'Combination protocol','workspace':'/research',
                     'created_at':'2026-10-22','capture':'available_visible_messages',
                     'messages':[{'id':'m1','role':'user','text':'We chose Yager combination for this experiment. '+('Evidence normalization matters. '*100)},
                                 {'id':'m2','role':'assistant','text':'I suggest an unapproved alternate fusion rule.'}]}
        self.store.put(self.record)
        self.store.put({'source':'muse','id':'one','title':'Personal shopping','workspace':'/personal',
                        'messages':[{'id':'p1','role':'user','text':'Yager book shopping cart.'}]})

    def test_exact_passage_offsets_citations_and_project_filter(self):
        packet=retrieve(self.store,'what did we choose for Yager experiment',project='research')
        self.assertTrue(packet['passages'])
        for item in packet['passages']:
            self.assertEqual(item['source'],'codex')
            message=self.record['messages'][item['message_index']]
            self.assertEqual(item['excerpt'],message['text'][item['start']:item['end']])
            line=Path(item['path']).read_text().splitlines()[item['line']-1]
            self.assertIn(item['message_id'],line)

    def test_edits_and_deletions_do_not_leave_old_evidence(self):
        self.assertTrue(retrieve(self.store,'normalization',project='research')['passages'])
        self.record['messages'][0]['text']='We revised the protocol.'
        self.store.put(self.record)
        self.assertFalse(retrieve(self.store,'normalization',project='research')['passages'])
        with self.store.db:
            self.store.db.execute("DELETE FROM conversations WHERE source='codex'")
        self.assertFalse(retrieve(self.store,'revised')['passages'])

    def test_project_assignment_survives_reimport_without_source_mutation(self):
        assign(self.root,'codex','one',['personal'],'User explicitly identified this as personal; test evidence')
        self.store.put(self.record)
        record=next(r for r in self.store.records() if r['source']=='codex')
        self.assertEqual(record['projects'],['personal'])
        self.assertEqual(record['project_evidence'],'reviewed_assignment')
        self.assertEqual(record['messages'],self.record['messages'])
        self.assertFalse(retrieve(self.store,'normalization',project='research')['passages'])
        self.assertTrue(retrieve(self.store,'normalization',project='personal')['passages'])

    def test_reimport_canonical_record_is_idempotent(self):
        canonical=next(r for r in self.store.records() if r['source']=='codex')
        self.assertFalse(self.store.put(canonical))

    def test_unknown_project_and_empty_query_are_explicit(self):
        with self.assertRaises(ValueError):retrieve(self.store,'question',project='missing')
        self.assertEqual(retrieve(self.store,'what is it')['passages'],[])


if __name__=='__main__':unittest.main()
