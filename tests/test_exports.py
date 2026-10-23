from pathlib import Path
import json
import tempfile
import unittest
import zipfile
from chatos.importers import read_export_file
from chatos.runtime import sync


class ExportTests(unittest.TestCase):
    def test_zip_payload_imports_without_extracting_any_archive_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);archive=root/'export.zip'
            data=[{'id':'export-test','title':'Test','mapping':{
                'a':{'parent':None,'message':{'id':'a','author':{'role':'user'},'content':{'parts':['Exported visible question']}}}}}]
            with zipfile.ZipFile(archive,'w') as out:
                out.writestr('conversations.json',json.dumps(data))
                out.writestr('../do-not-extract.txt','Never write this member')
            records=read_export_file(archive,'chatgpt')
            self.assertEqual(records[0]['messages'][0]['text'],'Exported visible question')
            self.assertFalse((root.parent/'do-not-extract.txt').exists())
            self.assertEqual(list(root.iterdir()),[archive])

    def test_ambiguous_payload_and_unverified_muse_zip_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            archive=Path(temp)/'export.zip'
            with zipfile.ZipFile(archive,'w') as out:
                out.writestr('conversations.json','[]');out.writestr('other/conversations.json','[]')
            with self.assertRaises(ValueError):read_export_file(archive,'chatgpt')
            with self.assertRaises(ValueError):read_export_file(archive,'muse')

    def test_active_branch_model_and_tool_recipient_exclusion(self):
        from chatos.importers import read_chatgpt_export
        data=[{'id':'branched','current_node':'chosen','mapping':{
          'u':{'parent':None,'message':{'id':'u','author':{'role':'user'},'content':{'parts':['Question']}}},
          'chosen':{'parent':'u','message':{'id':'chosen','author':{'role':'assistant'},'create_time':1,'content':{'parts':['Chosen answer']},'metadata':{'model_slug':'active-model'}}},
          'other':{'parent':'u','message':{'id':'other','author':{'role':'assistant'},'create_time':2,'content':{'parts':['Other branch']},'metadata':{'model_slug':'other-model'}}},
          'tool':{'parent':'chosen','message':{'id':'tool','author':{'role':'assistant'},'recipient':'python','content':{'parts':['PRIVATE TOOL CODE']}}}}}]
        record=read_chatgpt_export(data)[0]
        self.assertEqual(record['model'],'active-model')
        self.assertEqual(record['evidence']['model_basis'],'active_branch')
        self.assertNotIn('PRIVATE TOOL CODE',json.dumps(record))
        self.assertTrue(all('export_node_id' in m for m in record['messages']))

    def test_older_uploaded_export_cannot_replace_a_newer_source_snapshot(self):
        from chatos.core import Store
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'archive'
            home = Path(temp) / 'source'
            home.mkdir()
            inbox = root / 'System/Imports/chatgpt'
            inbox.mkdir(parents=True)
            def export(updated, text):
                return [{'id': 'stable-chat', 'title': 'Reading notes', 'update_time': updated,
                         'mapping': {'m': {'parent': None, 'message': {'id': 'm',
                             'author': {'role': 'user'}, 'content': {'parts': [text]}}}}}]
            (inbox / 'a-newer.json').write_text(json.dumps(export(200, 'Latest source text')))
            (inbox / 'z-older.json').write_text(json.dumps(export(100, 'Older source text')))
            report = sync(root, home)
            self.assertEqual(len(report['retained_newer_exports']), 1)
            store = Store(root)
            try:
                self.assertEqual(len(store.records()), 1)
                self.assertEqual(store.records()[0]['messages'][0]['text'], 'Latest source text')
            finally:
                store.close()
            self.assertEqual(sync(root, home, force=True)['status'], 'ok')

    def test_bad_update_does_not_advance_source_success(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'archive';home=Path(temp)/'source';home.mkdir()
            inbox=root/'System/Imports/chatgpt';inbox.mkdir(parents=True)
            export=inbox/'data.json';export.write_text(json.dumps([{'source':'chatgpt','id':'one','title':'Captured',
                'messages':[{'role':'user','text':'A real source message'}]}]))
            first=sync(root,home)
            self.assertEqual(first['sources']['chatgpt']['status'],'export_snapshot')
            success=first['sources']['chatgpt']['last_success']
            export.write_text('{bad json')
            second=sync(root,home)
            self.assertEqual(second['sources']['chatgpt']['status'],'partial')
            self.assertEqual(second['sources']['chatgpt']['last_success'],success)
            self.assertEqual(second['status'],'partial')


if __name__=='__main__':unittest.main()
