from pathlib import Path
import tempfile
import unittest
from chatos.desktop_capture import normalize,merge,write_inbox,CAPTURE


def capture(identity='one',text='A visible question'):
    return {'listing':{'id':identity,'title':'Desktop','projectId':'known-source-project'},'pages':[{
        'thread':{'id':identity,'kind':'chatgpt','title':'Desktop','createdAt':1,'updatedAt':2},
        'page':{'hasMore':False},'turns':[{'id':'turn','startedAt':1,'items':[
            {'type':'userMessage','id':'u','content':[{'type':'text','text':text}]},
            {'type':'agentMessage','id':'a','text':'::chatgpt-content-reference{index="0"}'},
            {'type':'reasoning','id':'secret','text':'PRIVATE REASONING'}]}]}]}


class DesktopTests(unittest.TestCase):
    def test_references_never_become_assistant_text_or_invented_models(self):
        record=normalize(capture())
        self.assertEqual(len(record['messages']),1)
        self.assertEqual(record['messages'][0]['text'],'A visible question')
        self.assertIsNone(record['model'])
        self.assertEqual(record['capture'],CAPTURE)
        self.assertEqual(len(record['evidence']['unavailable_message_text']),1)
        self.assertEqual(record['source_app_project_id'],'known-source-project')

    def test_full_export_is_preserved_and_incremental_inbox_keeps_earlier_sources(self):
        full={'capture':'exported_visible_branches','messages':[{'id':'a','text':'Full reply'}]}
        self.assertEqual(merge(full,normalize(capture())),full)
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            write_inbox(root,{'captures':[capture('one')]})
            report=write_inbox(root,{'captures':[capture('two')]})
            self.assertEqual(report['conversations'],2)
            self.assertEqual(report['captured_this_attempt'],1)

    def test_truncated_update_does_not_erase_longer_captured_text(self):
        old=normalize(capture(text='A visible question with more context'))
        new=normalize(capture(text='A visible question'))
        self.assertEqual(merge(old,new)['messages'][0]['text'],'A visible question with more context')

    def test_every_page_requires_matching_identity(self):
        value=capture()
        value['pages'].append(capture('another')['pages'][0])
        with self.assertRaises(ValueError):normalize(value)

    def test_narrower_tool_window_retains_old_messages_and_unresolved_replies(self):
        old=normalize(capture())
        fresh=capture()
        fresh['pages'][0]['turns'][0]['items']=[{'type':'userMessage','id':'new','content':[{'type':'text','text':'Newer question'}]}]
        merged=merge(old,normalize(fresh))
        self.assertEqual({m['id'] for m in merged['messages']},{'u','new'})
        self.assertEqual([gap['id'] for gap in merged['evidence']['unavailable_message_text']],['a'])
        full=capture()
        full['pages'][0]['turns'][0]['items'][1]['text']='An actually available answer'
        merged=merge(merged,normalize(full))
        self.assertEqual(merged['evidence']['unavailable_message_text'],[])
        self.assertIn('new',{m['id'] for m in merged['messages']})

    def test_oldest_returned_page_determines_remaining_pagination(self):
        first=capture();first['pages'][0]['page']={'hasMore':True}
        last=capture()['pages'][0];last['turns']=[]
        first['pages'].append(last)
        self.assertFalse(normalize(first)['evidence']['tool_has_more'])


if __name__=='__main__':unittest.main()
