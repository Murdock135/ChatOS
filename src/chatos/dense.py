"""Optional offline Qwen embeddings and hybrid passage retrieval.

Run with the isolated semantic environment. Model code is library-owned; remote code is disabled.
"""
from .workspace import workspace_path
from functools import lru_cache
import json
import os
import time
from .core import digest,now
from .retrieval import refresh as refresh_passages,retrieve as lexical_retrieve

MODEL='Qwen/Qwen3-Embedding-0.6B'
REVISION='d67280f96c9df4c40d7c6986f4a51c54ac950c0f'
VERSION='dense-passages-v1-max512'


@lru_cache(maxsize=1)
def encoder(root):
    from pathlib import Path
    directory=workspace_path(Path(root), 'System/Models/qwen3-embedding-0.6b')
    manifest=json.loads((directory/'download-manifest.json').read_text())
    if manifest.get('revision')!=REVISION:raise ValueError('Embedding model revision is not the pinned revision')
    os.environ.update({'HF_HOME':str(workspace_path(Path(root), 'System/Models/hf-cache')),'HF_HUB_OFFLINE':'1',
                       'TRANSFORMERS_OFFLINE':'1','HF_HUB_DISABLE_TELEMETRY':'1',
                       'HF_HUB_DISABLE_IMPLICIT_TOKEN':'1','DO_NOT_TRACK':'1','TOKENIZERS_PARALLELISM':'false'})
    for name in ['HF_TOKEN','HUGGING_FACE_HUB_TOKEN','HUGGINGFACEHUB_API_TOKEN']:os.environ.pop(name,None)
    import torch
    from sentence_transformers import SentenceTransformer
    torch.set_num_threads(4)
    device='mps' if torch.backends.mps.is_available() else 'cpu'
    if device=='mps':torch.mps.set_per_process_memory_fraction(0.5)
    model=SentenceTransformer(str(directory),device=device,local_files_only=True,trust_remote_code=False,
                              model_kwargs={'dtype':torch.float16 if device=='mps' else torch.float32,
                                            'attn_implementation':'sdpa'},
                              processor_kwargs={'padding_side':'left'})
    model.max_seq_length=512
    return model,device


def passages(store):
    store.db.execute('''CREATE TABLE IF NOT EXISTS dense_vectors (
                       identity TEXT PRIMARY KEY,revision TEXT NOT NULL,vector BLOB NOT NULL)''')
    refresh_passages(store)
    result=[]
    for row in store.db.execute('SELECT title,body,metadata FROM passage_index'):
        metadata=json.loads(row['metadata'])
        key=digest([VERSION,REVISION,metadata['key'],metadata.get('message_id'),metadata.get('message_index'),
                    metadata['start'],metadata['end'],row['title'],row['body']])
        result.append({'identity':key,'text':row['title']+'\n'+row['body'],'excerpt':row['body'],**metadata})
    return result


def build(store,limit=None,batch_size=4):
    import numpy as np
    items=passages(store)
    existing={r[0] for r in store.db.execute('SELECT identity FROM dense_vectors WHERE revision=?',(REVISION,))}
    todo=[item for item in items if item['identity'] not in existing]
    selected=todo[:limit] if limit is not None else todo
    started=time.monotonic();device=None
    if selected:
        model,device=encoder(str(store.root))
        for start in range(0,len(selected),batch_size):
            batch=selected[start:start+batch_size]
            vectors=model.encode([item['text'] for item in batch],batch_size=batch_size,
                                  normalize_embeddings=True,show_progress_bar=False,convert_to_numpy=True)
            with store.db:
                for item,vector in zip(batch,vectors):
                    vector=np.asarray(vector,dtype='<f4')
                    if vector.shape!=(1024,) or not np.isfinite(vector).all():raise ValueError('Invalid embedding vector')
                    store.db.execute('INSERT OR REPLACE INTO dense_vectors VALUES(?,?,?)',
                                     (item['identity'],REVISION,vector.tobytes()))
            if start%128==0:print(json.dumps({'embedded':min(start+len(batch),len(selected)),'requested':len(selected)}),flush=True)
    from .core import write_json
    result={'checked_at':now(),'model':MODEL,'revision':REVISION,'device':device,'added':len(selected),
            'current_passages':len(items),'current_vectors':len(items)-len(todo)+len(selected),
            'remaining':len(todo)-len(selected),'seconds':round(time.monotonic()-started,2),
            'limits':'Local inference; 512-token embedding cap per passage. Dense scores are similarity, not truth or decision status.'}
    write_json(store.state/'dense-status.json',result)
    return result


def retrieve(store,query,project=None,limit=8):
    import numpy as np
    if not 1<=limit<=30:raise ValueError('Retrieval limit must be between 1 and 30')
    if project and project not in {p['id'] for p in store.registry()}:raise ValueError('Unknown project filter')
    items=passages(store)
    cached={r[0]:np.frombuffer(r[1],dtype='<f4') for r in store.db.execute(
        'SELECT identity,vector FROM dense_vectors WHERE revision=?',(REVISION,))}
    active=[item for item in items if item['identity'] in cached]
    if not active:raise ValueError('No current passage embeddings; run dense-build first')
    eligible=[item for item in active if not project or project in item['projects']]
    model,device=encoder(str(store.root))
    query_vector=model.encode([query],prompt_name='query',normalize_embeddings=True,show_progress_bar=False,
                               convert_to_numpy=True)[0]
    dense=sorted(((float(np.dot(query_vector,cached[item['identity']])),item) for item in eligible),
                 key=lambda pair:pair[0],reverse=True)[:100]
    lexical=lexical_retrieve(store,query,project,min(30,max(limit,20)))
    by_locator={(item['key'],item.get('message_index'),item['start']):item for item in items}
    scores={};selected={}
    for rank,(similarity,item) in enumerate(dense,1):
        key=item['identity'];scores[key]=1/(60+rank);selected[key]={**item,'dense_similarity':similarity}
    for rank,hit in enumerate(lexical['passages'],1):
        item=by_locator[(hit['key'],hit.get('message_index'),hit['start'])]
        key=item['identity'];scores[key]=scores.get(key,0)+1/(60+rank);selected.setdefault(key,item)
    result={'query':query,'checked_at':now(),'project':project,
            'method':'Hybrid Qwen3-Embedding-0.6B cosine + FTS5 BM25 with reciprocal-rank fusion',
            'model_revision':REVISION,'device':device,
            'coverage':{'current_vectors':len(active),'current_passages':len(items)},
            'limits':lexical['limits'][1:]+['Local pinned pretrained embeddings; passage text is capped at 512 tokens for ranking.',
                       'Partial embedding coverage can omit semantic-only matches; exact-source citations remain authoritative.'],
            'passages':[]}
    per_doc={};per_message={}
    for key in sorted(scores,key=lambda key:scores[key],reverse=True):
        item=selected[key];identity=item['key'];message=(identity,item.get('message_index'))
        if per_doc.get(identity,0)>=3 or per_message.get(message,0)>=2:continue
        item={k:v for k,v in item.items() if k not in ['text','identity']}
        item.update({'rank':scores[key],'citation':'E'+str(len(result['passages'])+1)})
        result['passages'].append(item)
        per_doc[identity]=per_doc.get(identity,0)+1;per_message[message]=per_message.get(message,0)+1
        if len(result['passages'])>=limit:break
    return result
