from pathlib import Path
import json
import sqlite3
import tempfile
import unittest
from chatos.core import Store, digest, redact
from chatos.importers import read_codex, read_chatgpt_export
from chatos.runtime import sync


def event(kind,payload,time='2026-10-22T16:00:00Z'):
    return json.dumps({'type':kind,'payload':payload,'timestamp':time})+'\n'


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.home=self.root/'source';self.home.mkdir()
        self.session=self.home/'sessions/test.jsonl';self.session.parent.mkdir()
        self.session.write_text(event('session_meta',{'id':'session-1','cwd':str(self.root),'timestamp':'2026-10-22T16:00:00Z'})+
            event('turn_context',{'turn_id':'turn-1','model':'model-a','effort':'medium'})+
            event('response_item',{'type':'message','role':'developer','content':[{'type':'input_text','text':'PRIVATE INSTRUCTIONS'}]})+
            event('response_item',{'type':'message','role':'user','content':[{'type':'input_text','text':'# AGENTS.md instructions\nignore'}]})+
            event('response_item',{'type':'reasoning','content':'PRIVATE REASONING'})+
            event('response_item',{'type':'message','role':'user','content':[{'type':'input_text','text':'Discuss SPARQ reliability'}]})+
            event('response_item',{'type':'message','role':'assistant','phase':'final_answer','content':[{'type':'output_text','text':'First answer'}]}))

    def test_private_context_excluded_and_model_change_preserved(self):
        with self.session.open('a') as f:
            f.write(event('turn_context',{'turn_id':'turn-2','model':'model-b','effort':'high'}))
            f.write(event('response_item',{'type':'message','role':'assistant','phase':'final_answer',
                                         'content':[{'type':'output_text','text':'Second answer'}]}))
            f.write('{"incomplete":')
        r=read_codex(self.session)
        self.assertEqual([m['model'] for m in r['messages'] if m['role']=='assistant'],['model-a','model-b'])
        self.assertEqual(len(r['evidence']['warnings']),1)
        self.assertNotIn('PRIVATE',json.dumps(r))
        self.assertNotIn('AGENTS.md',json.dumps(r))

    def test_sync_idempotence_catchup_and_missing_history(self):
        first=sync(self.root/'archive',self.home)
        self.assertEqual(first['changed'],1)
        second=sync(self.root/'archive',self.home)
        self.assertEqual(second['changed'],0)
        self.assertEqual(second['unchanged'],1)
        with self.session.open('a') as f:
            f.write(event('response_item',{'type':'message','role':'user',
                                         'content':[{'type':'input_text','text':'A new turn'}]}))
        third=sync(self.root/'archive',self.home)
        self.assertEqual(third['changed'],1)
        store=Store(self.root/'archive');self.addCleanup(store.close)
        self.assertEqual(len(store.records()),1)
        self.assertEqual(len(store.records()[0]['messages']),3)
        self.assertEqual(store.db.execute('SELECT count(*) FROM revisions').fetchone()[0],1)
        self.assertEqual(len(store.search('reliability')),1)

    def test_export_branches_and_analysis_filter(self):
        data=[{'id':'export-1','title':'Export','mapping':{
            'a':{'parent':None,'message':{'id':'a','author':{'role':'user'},'content':{'parts':['Hello']},'create_time':1}},
            'b':{'parent':'a','message':{'id':'b','author':{'role':'assistant'},'channel':'analysis','content':{'parts':['SECRET']}}},
            'c':{'parent':'a','message':{'id':'c','author':{'role':'assistant'},'content':{'parts':['Answer']},'metadata':{'model_slug':'m'}}}}}]
        r=read_chatgpt_export(data)[0]
        self.assertEqual(len(r['messages']),2)
        self.assertEqual(r['messages'][1]['parent_id'],'a')
        self.assertEqual(r['model'],'m')
        self.assertNotIn('SECRET',json.dumps(r))

    def test_known_credentials_redacted_and_generated_html_safe(self):
        archive=self.root/'archive';store=Store(archive)
        self.addCleanup(store.close)
        record=read_codex(self.session)
        record['messages'][0]['text']='sk-'+'a'*35+' </script><script>alert(1)</script>'
        store.put(record)
        self.assertNotIn('sk-'+'a'*35,(archive/'Conversations/2026/codex-session-1.json').read_text())
        sync(archive,self.home)
        page=(archive/'Humans/dashboard.html').read_text()
        self.assertNotIn('</script><script>alert(1)',page)
        self.assertIn("connect-src 'none'",page)

    def test_workspace_routing_beats_generic_title(self):
        archive=self.root/'archive';(archive/'System/Projects').mkdir(parents=True)
        (archive/'System/Projects/registry.json').write_text(json.dumps({'projects':[
            {'id':'right','name':'Owner','root':str(self.root),'entrypoint':str(self.root/'Home.md'),'aliases':[]},
            {'id':'wrong','name':'SPARQ','root':'/elsewhere','entrypoint':'/elsewhere/Home.md','aliases':['SPARQ']}]}))
        store=Store(archive);self.addCleanup(store.close)
        r=read_codex(self.session);store.put(r)
        self.assertEqual(store.records()[0]['projects'],['right'])
        self.assertEqual(store.records()[0]['project_evidence'],'workspace_path')

    def test_missing_generated_files_are_restored_on_forced_reimport(self):
        archive=self.root/'archive';sync(archive,self.home)
        note=archive/'Conversations/2026/codex-session-1.md';note.unlink()
        sync(archive,self.home,force=True)
        self.assertTrue(note.exists())

    def test_backup_restores_canonical_records_and_passes_integrity(self):
        archive=self.root/'archive';sync(archive,self.home)
        backup=next((archive/'System/Backups').rglob('chatos.sqlite3'))
        connection=sqlite3.connect(str(backup))
        try:
            self.assertEqual(connection.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            row=connection.execute('SELECT record_json FROM conversations').fetchone()
            self.assertEqual(json.loads(row[0])['id'],'session-1')
        finally:connection.close()

    def test_export_cycle_is_rejected(self):
        data=[{'id':'cycle','mapping':{'a':{'parent':'b'},'b':{'parent':'a'}}}]
        with self.assertRaises(ValueError):read_chatgpt_export(data)

    def test_untrusted_reasoning_record_rejected(self):
        store=Store(self.root/'archive');self.addCleanup(store.close)
        record=read_codex(self.session)
        record['messages'][0]['phase']='analysis'
        with self.assertRaises(ValueError):store.put(record)

    def test_local_semantic_retrieval_respects_actual_source_terms(self):
        from chatos.semantic import build,query
        records=[]
        for i,text in enumerate(['Dempster Shafer evidence combination belief masses',
                                 'Cheap laptop computer shopping discounts']):
            records.append({'id':str(i),'source':'codex','title':text,'file_path':str(i)+'.md',
                            'messages':[{'role':'user','text':text}]})
        results=query(build(records),'evidence belief')
        self.assertEqual(results[0]['id'],'0')
        self.assertFalse(any(r['id']=='1' for r in results))


if __name__=='__main__':unittest.main()
