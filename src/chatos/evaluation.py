"""Small source-labeled retrieval checks, not a general semantic quality benchmark."""
import json
from .core import now,write_json,atomic
from .retrieval import retrieve


def evaluate(store,cases_path,limit=8,backend=None):
    cases=json.loads(cases_path.read_text())['cases'];results=[]
    records={(r['source'],r['id']):r for r in store.records()}
    for case in cases:
        target=case['expected'];record=records.get((target['source'],target['conversation_id']))
        if not record:raise ValueError('Evaluation source is not captured: '+case['id'])
        messages=[m for m in record['messages'] if m['role']=='user' and target['contains'] in m['text']]
        if not messages:raise ValueError('Expected source wording is not present: '+case['id'])
        expected_ids={m['id'] for m in messages}
        packet=(backend or retrieve)(store,case['question'],case.get('project'),limit)
        hits=[i for i,p in enumerate(packet['passages'],1) if p['source']==target['source'] and
              p['id']==target['conversation_id'] and p.get('message_id') in expected_ids]
        results.append({'id':case['id'],'question':case['question'],'first_relevant_rank':min(hits) if hits else None,
                        'found':bool(hits),'returned':len(packet['passages'])})
    count=len(results)
    report={'checked_at':now(),'k':limit,'cases':results,'recall_at_k':sum(r['found'] for r in results)/count if count else None,
            'mean_reciprocal_rank':sum(1/r['first_relevant_rank'] if r['found'] else 0 for r in results)/count if count else None,
            'limits':'Hand-authored small in-vault diagnostic set with exact user-message labels. Not blinded, exhaustive, representative, or a model benchmark. Derived notes may support answers but do not count as exact-source hits here.'}
    return report
