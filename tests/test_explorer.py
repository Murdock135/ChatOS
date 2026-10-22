import math
from pathlib import Path
import tempfile
import unittest
from chatos.core import Store
from chatos.semantic import build
from chatos.explorer import project,neighbor_retention,refresh


class ExplorerTests(unittest.TestCase):
    def test_empty_and_degenerate_projection_is_finite(self):
        self.assertEqual(project([]),([],0.0))
        plane,variance=project([[0,0],[0,0]])
        self.assertEqual(plane,[[0,0],[0,0]])
        self.assertEqual(variance,0)
        self.assertEqual(neighbor_retention([[1,0]],[[0,0]]),None)

    def test_planar_data_retains_variance_and_original_neighbors(self):
        points=[[math.cos(i*0.7),math.sin(i*0.7)] for i in range(8)]
        plane,variance=project(points)
        self.assertAlmostEqual(variance,1.0,places=6)
        self.assertAlmostEqual(neighbor_retention(points,plane,k=2),1.0,places=6)
        self.assertTrue(all(math.isfinite(x) for p in plane for x in p))

    def test_generated_page_has_real_sources_and_escaped_payload(self):
        with tempfile.TemporaryDirectory() as temp:
            store=Store(Path(temp));self.addCleanup(store.close)
            store.put({'source':'muse','id':'one','title':'Test','messages':[{'role':'user','text':'Research evidence belief'}]})
            store.put({'source':'codex','id':'two','title':'Other','messages':[{'role':'user','text':'Shopping books computer'}]})
            records=store.records();index=build(records)
            index['documents'][0]['title']='</script><script>alert(1)</script>'
            data=refresh(store,index)
            self.assertEqual(len(data['documents']),2)
            for item in data['documents']:
                self.assertEqual(item['url'],(store.root/item['path']).as_uri())
                self.assertEqual(len(item['neighbors']),1)
            page=(store.root/'Humans/explorer.html').read_text()
            self.assertNotIn('</script><script>alert(1)</script>',page)
            self.assertIn("connect-src 'none'",page)
            self.assertNotIn('__EXPLORER_DATA__',page)


if __name__=='__main__':unittest.main()
