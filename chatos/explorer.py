"""Offline 2D browsing over the provisional local LSA representation."""
from collections import Counter
from pathlib import Path
import json
import math
from .core import atomic,digest,now
from .semantic import dot,normalize,clusters


def project(points):
    """Project centered, unit-length LSA vectors onto two principal components."""
    if not points:return [],0.0
    width=max(len(p) for p in points)
    if width==0:return [[0.0,0.0] for _ in points],0.0
    unit=[normalize(p+[0.0]*(width-len(p))) for p in points]
    mean=[sum(p[i] for p in unit)/len(unit) for i in range(width)]
    centered=[[p[i]-mean[i] for i in range(width)] for p in unit]
    covariance=[[sum(p[i]*p[j] for p in centered) for j in range(width)] for i in range(width)]
    axes=[];values=[]
    for component in range(2):
        v=normalize([math.sin((i+1)*(component+1)*1.618) for i in range(width)])
        for _ in range(100):
            nxt=[dot(row,v) for row in covariance]
            for axis in axes:
                overlap=dot(nxt,axis);nxt=[a-overlap*b for a,b in zip(nxt,axis)]
            nxt=normalize(nxt)
            if sum((a-b)**2 for a,b in zip(nxt,v))<1e-14:
                v=nxt;break
            v=nxt
        axes.append(v);values.append(max(0.0,dot(v,[dot(row,v) for row in covariance])))
    total=sum(covariance[i][i] for i in range(width))
    return [[dot(p,axis) for axis in axes] for p in centered],sum(values)/total if total>1e-12 else 0.0


def neighbor_retention(points,plane,k=5):
    count=len(points)
    if count<2:return None
    k=min(k,count-1);unit=[normalize(p) for p in points];total=0
    for i in range(count):
        original=sorted((j for j in range(count) if j!=i),key=lambda j:(-dot(unit[i],unit[j]),j))[:k]
        reduced=sorted((j for j in range(count) if j!=i),key=lambda j:(sum((a-b)**2 for a,b in zip(plane[i],plane[j])),j))[:k]
        total+=len(set(original)&set(reduced))/k
    return total/count


def payload(store,index):
    records=store.records();by_id={(r['source'],r['id']):r for r in records}
    points=index['coordinates'];plane,variance=project(points)
    groups=clusters(index)
    group_for={};labels={}
    for group in groups:
        identity=digest(sorted(index['documents'][i]['source']+':'+index['documents'][i]['id'] for i in group))[:10]
        weights=Counter()
        for i in group:weights.update(index['vectors'][i])
        labels[identity]=' / '.join(k for k,_ in weights.most_common(3))
        for i in group:group_for[i]=identity
    documents=[]
    for i,item in enumerate(index['documents']):
        record=by_id[(item['source'],item['id'])]
        neighbors=sorted((j for j in range(len(points)) if j!=i),
                         key=lambda j:-dot(normalize(points[i]),normalize(points[j])))[:5]
        documents.append({**item,'url':(store.root/item['path']).as_uri(),'x':plane[i][0],'y':plane[i][1],
                          'projects':record.get('projects',[]),'date':(record.get('updated_at') or record.get('created_at') or '')[:10],
                          'group':group_for[i],'neighbors':neighbors})
    return {'checked_at':now(),'documents':documents,'groups':labels,
            'variance_2d':variance,'neighbor_retention_5':neighbor_retention(points,plane),
            'method':'PCA of normalized local LSA vectors; groups use greedy cosine threshold 0.70.',
            'limits':'Exploratory English term co-occurrence from titles and sampled user messages. No pretrained embeddings. Map proximity and groups do not establish project ownership, truth, or decisions.'}


def refresh(store,index):
    saved=store.state/'dense-map.json'
    if saved.exists():
        data=json.loads(saved.read_text())
        if data.get('backend')=='qwen-umap-hdbscan-v1':
            data['freshness_note']=('Source records changed since this map was built; semantic refresh is pending.'
                                    if data.get('input_fingerprint')!=digest(store.records()) else 'Map matches current captured records.')
            write_page(store,data)
            return data
    data=payload(store,index)
    write_page(store,data)
    return data


def write_page(store,data):
    template=(store.root/'System/Templates/explorer.html')
    if not template.exists():
        template=Path(__file__).resolve().parents[1]/'System/Templates/explorer.html'
    serialized=json.dumps(data,ensure_ascii=False,allow_nan=False).replace('<','\\u003c')
    atomic(store.root/'Humans/explorer.html',template.read_text().replace('__EXPLORER_DATA__',serialized))
