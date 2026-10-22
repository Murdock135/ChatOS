from pathlib import Path
import tempfile
import unittest
from chatos.core import Store
from chatos.feedback import candidates,review,refresh


class FeedbackTests(unittest.TestCase):
    def test_cues_require_review_and_do_not_classify_scope_or_scheduled_text(self):
        with tempfile.TemporaryDirectory() as temp:
            store=Store(Path(temp));self.addCleanup(store.close)
            store.put({'source':'codex','id':'one','messages':[
                {'role':'user','id':'scope','text':'Scheduled tasks as well'},
                {'role':'assistant','id':'a','text':'I opened three documents.'},
                {'role':'user','id':'critique','text':'you only opened one document'},
                {'role':'user','id':'trigger','text':'<heartbeat><instructions>You only need to run this.</instructions></heartbeat>'}]})
            items=candidates(store)
            self.assertEqual(len(items),1)
            self.assertEqual(items[0]['classification'],'review_needed')
            self.assertFalse((store.root/'System/Feedback log.md').exists())
            key=items[0]['key'];reason='Explicit correction of the visible opening result.'
            review(store,key,'confirmed_feedback',reason,'Verify displayed documents before claiming success.')
            original=(store.root/'System/Feedback log.md').read_text()
            self.assertEqual(candidates(store),[])
            self.assertEqual(review(store,key,'confirmed_feedback',reason)['status'],'already_reviewed')
            self.assertEqual((store.root/'System/Feedback log.md').read_text(),original)
            self.assertEqual(refresh(store)['candidates'],0)

    def test_neutral_bug_report_can_be_dismissed_without_negative_log(self):
        with tempfile.TemporaryDirectory() as temp:
            store=Store(Path(temp));self.addCleanup(store.close)
            store.put({'source':'muse','id':'two','messages':[{'role':'user','text':"i don't see progress in this old dashboard"}]})
            key=candidates(store)[0]['key']
            review(store,key,'not_feedback','Initial bug report without a preceding assistant action or explicit dissatisfaction.')
            self.assertFalse((store.root/'System/Feedback log.md').exists())
            self.assertEqual(candidates(store),[])


if __name__=='__main__':unittest.main()
