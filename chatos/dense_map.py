"""Optional pretrained conversation map; cluster before the two-dimensional projection."""
from collections import Counter,defaultdict
import json
import os
from .core import digest,now,write_json
from .dense import passages,REVISION,MODEL


def build(store):
    os.environ['NUMBA_CACHE_DIR']=str(store.state/'numba-cache')
    os.environ['NUMBA_NUM_THREADS']='4'
    import numpy as np
    from sklearn.cluster import HDBSCAN
    from sklearn.metrics.pairwise import cosine_distances
    from umap import UMAP
    from .semantic import tokens
    from .explorer import neighbor_retention,write_page
    items=passages(store)
    cache={row[0]:np.frombuffer(row[1],dtype='<f4') for row in store.db.execute(
        'SELECT identity,vector FROM dense_vectors WHERE revision=?',(REVISION,))}
    records=store.records();groups=defaultdict(list);available=0
    for item in items:
        if item['identity'] in cache:
            groups[(item['source'],item['id'])].append(item);available+=1
    represented=[];vectors=[];assistant_fallback=0
    for record in records:
        parts=groups[(record['source'],record['id'])]
        users=[p for p in parts if p['role']=='user']
        if not users and parts:assistant_fallback+=1
        selected=users or parts
        if not selected:continue
        vector=np.mean([cache[p['identity']] for p in selected],axis=0)
        norm=np.linalg.norm(vector)
        if norm<1e-10:continue
        represented.append(record);vectors.append(vector/norm)
    if len(vectors)<6:raise ValueError('At least six conversations with current embeddings are required')
    matrix=np.asarray(vectors,dtype=np.float64)
    distances=np.maximum(cosine_distances(matrix),0);np.fill_diagonal(distances,0)
    labels=HDBSCAN(min_cluster_size=4,min_samples=2,metric='precomputed',n_jobs=1,copy=True).fit_predict(distances)
    plane=UMAP(n_neighbors=min(15,len(vectors)-1),n_components=2,min_dist=0.15,
               metric='cosine',random_state=42,n_jobs=1).fit_transform(matrix)
    group_labels={};group_for={}
    for label in sorted(set(labels)):
        indices=[i for i,value in enumerate(labels) if value==label]
        identity='unclustered' if label<0 else digest(sorted(represented[i]['source']+':'+represented[i]['id'] for i in indices))[:10]
        words=Counter()
        for i in indices:
            record=represented[i]
            # Limit each conversation's contribution so one long transcript does not name the group.
            words.update(set(tokens(record['title']+' '+' '.join(m['text'][:500] for m in record['messages'][:4] if m['role']=='user'))))
        group_labels[identity]='Unclustered' if label<0 else ' / '.join(w for w,_ in words.most_common(3))
        for i in indices:group_for[i]=identity
    documents=[]
    for i,record in enumerate(represented):
        neighbors=np.argsort(distances[i]).tolist();neighbors=[j for j in neighbors if j!=i][:5]
        documents.append({'source':record['source'],'id':record['id'],'title':record['title'],
                          'path':record['file_path'],'url':(store.root/record['file_path']).as_uri(),
                          'projects':record.get('projects',[]),'date':(record.get('updated_at') or record.get('created_at') or '')[:10],
                          'x':float(plane[i,0]),'y':float(plane[i,1]),'group':group_for[i],'neighbors':neighbors})
    data={'checked_at':now(),'backend':'qwen-umap-hdbscan-v1','model':MODEL,'revision':REVISION,
          'input_fingerprint':digest(records),'documents':documents,'groups':group_labels,'variance_2d':None,
          'neighbor_retention_5':neighbor_retention(matrix.tolist(),plane.tolist()),
          'coverage':{'represented_conversations':len(represented),'total_conversations':len(records),
                      'current_vectors':available,'current_passages':len(items),'assistant_fallback':assistant_fallback},
          'method':'Mean normalized user-passage Qwen3-Embedding-0.6B vectors; HDBSCAN on original cosine distances (min cluster 4, min samples 2); UMAP 2D (15 neighbors, min distance 0.15, seed 42). Topic labels are frequent source terms.',
          'limits':'Experimental local pretrained representation. HDBSCAN may leave conversations unclustered; labels and clusters need human/agent review. UMAP can distort distance and density. Groups and map proximity do not establish ownership, truth, or accepted decisions. Averages can blur multi-topic conversations; assistant passages are used only if no user passage is available. Embedding text has a 512-token cap per passage.'}
    write_json(store.state/'dense-map.json',data);write_page(store,data)
    return {'checked_at':data['checked_at'],'coverage':data['coverage'],
            'clusters':len([k for k in group_labels if k!='unclustered']),
            'unclustered':int(sum(label<0 for label in labels)),'neighbor_retention_5':data['neighbor_retention_5'],
            'path':str(store.root/'Humans/explorer.html')}
