"""Compare lexical and optional hybrid retrieval on the same source-labeled questions."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from chatos.core import Store,write_json,atomic
from chatos.evaluation import evaluate
from chatos.dense import retrieve


def main():
    store=Store()
    try:
        cases=store.root/'System/Evaluations/retrieval-questions.json'
        lexical=evaluate(store,cases)
        hybrid=evaluate(store,cases,backend=retrieve)
        write_json(store.state/'retrieval-evaluation-lexical.json',lexical)
        write_json(store.state/'retrieval-evaluation-hybrid.json',hybrid)
        lines=['# Retrieval diagnostic','',f'Checked: {hybrid["checked_at"]}','','Seven hand-authored questions; exact supporting user message must appear in the top eight.','',
               '| Question | Lexical rank | Hybrid rank |','| --- | --- | --- |']
        for first,second in zip(lexical['cases'],hybrid['cases']):
            lines.append('| '+first['question']+' | '+str(first['first_relevant_rank'] or 'not found')+' | '+str(second['first_relevant_rank'] or 'not found')+' |')
        lines+=['','Lexical recall@8: '+str(round(lexical['recall_at_k']*100))+'%; hybrid recall@8: '+str(round(hybrid['recall_at_k']*100))+'%.',
                'Lexical MRR: '+str(round(lexical['mean_reciprocal_rank'],3))+'; hybrid MRR: '+str(round(hybrid['mean_reciprocal_rank'],3))+'.','',hybrid['limits'],'',
                'No answer generation or general factual accuracy is graded by this diagnostic. Broader evaluation remains required.','']
        atomic(store.root/'System/Evaluations/Latest.md','\n'.join(lines))
        import json
        print(json.dumps({'lexical_recall_at_8':lexical['recall_at_k'],'hybrid_recall_at_8':hybrid['recall_at_k'],
                          'lexical_mrr':lexical['mean_reciprocal_rank'],'hybrid_mrr':hybrid['mean_reciprocal_rank']},indent=2))
    finally:store.close()


if __name__=='__main__':main()
