"""Offline latent semantic analysis. Similarity is not confidence or ownership."""
from collections import Counter
import math
import re
from .core import write_json,atomic,digest,title

STOP=set('the a an and or is are was were be been to of in on for from by with this that these those it its i you your me my we our they their as at how what why when where can could would should do does did have has had not but if then than about into using use want need please also just all some any so which will more'.split())

def tokens(text):
    return [w for w in re.findall(r'[a-z][a-z0-9_-]{2,}',text.lower()) if w not in STOP]

def dot(a,b):return sum(x*y for x,y in zip(a,b))

def normalize(v):
    norm=math.sqrt(dot(v,v))
    return [x/norm for x in v] if norm>1e-12 else [0.0 for x in v]

def sparse_dot(a,b):
    if len(a)>len(b):a,b=b,a
    return sum(v*b.get(k,0) for k,v in a.items())

def build(records,dimensions=12):
    documents=[]
    for r in records:
        excerpts=[m['text'][:1800] for m in r['messages'] if m['role']=='user']
        documents.append(Counter(tokens((r['title']+' ')*3+' '.join(excerpts[:4]+excerpts[-4:]))))
    count=len(documents)
    df=Counter(k for d in documents for k in d)
    idf={k:math.log((count+1)/(v+1))+1 for k,v in df.items()}
    vectors=[]
    for d in documents:
        weights={k:(1+math.log(v))*idf[k] for k,v in d.items()}
        norm=math.sqrt(sum(v*v for v in weights.values())) or 1
        vectors.append({k:v/norm for k,v in weights.items()})
    matrix=[[sparse_dot(a,b) for b in vectors] for a in vectors]
    eigen=[]
    for component in range(min(dimensions,count)):
        v=normalize([math.sin((i+1)*(component+1)*1.618) for i in range(count)])
        for _ in range(60):
            updated=[dot(row,v) for row in matrix]
            for _,previous in eigen:
                overlap=dot(updated,previous)
                updated=[x-overlap*y for x,y in zip(updated,previous)]
            updated=normalize(updated)
            if sum((a-b)**2 for a,b in zip(updated,v))<1e-12:
                v=updated
                break
            v=updated
        value=dot(v,[dot(row,v) for row in matrix])
        if value<1e-9:break
        eigen.append((value,v))
    coordinates=[[math.sqrt(value)*v[i] for value,v in eigen] for i in range(count)]
    return {'backend':'local-lsa-v1','documents':[{'source':r['source'],'id':r['id'],'title':r['title'],'path':r['file_path']} for r in records],
            'idf':idf,'vectors':vectors,'eigen':eigen,'coordinates':coordinates,
            'limits':'English term co-occurrence; no pretrained embeddings. Similarity does not verify ownership or factual support.'}

def query(index,text,limit=15):
    counts=Counter(tokens(text))
    q={k:(1+math.log(v))*index['idf'][k] for k,v in counts.items() if k in index['idf']}
    if not q:return []
    qnorm=math.sqrt(sum(v*v for v in q.values())) or 1
    similarities=[sparse_dot(q,d)/qnorm for d in index['vectors']]
    coordinate=normalize([dot(similarities,v)/math.sqrt(value) for value,v in index['eigen']])
    scored=[]
    for i,point in enumerate(index['coordinates']):
        latent=dot(coordinate,normalize(point))
        # Pure low-rank scores were too broad in live checks. Anchor experimental
        # retrieval in actual source terms rather than returning unrelated neighbors.
        lexical=similarities[i]
        score=0.75*lexical+0.25*max(0,latent)
        if lexical>=0.04:
            scored.append(dict(index['documents'][i],similarity=score,latent_similarity=latent,term_similarity=lexical))
    return sorted(scored,key=lambda r:r['similarity'],reverse=True)[:limit]

def clusters(index):
    groups=[]
    for i,point in enumerate(index['coordinates']):
        best=max([(dot(normalize(point),normalize(index['coordinates'][g[0]])),g) for g in groups],
                 key=lambda pair:pair[0],default=(-1,None))
        if best[0]>=0.70:best[1].append(i)
        else:groups.append([i])
    return groups


def refresh(store):
    records=store.records()
    signature=digest(['lsa-v2',records])
    target=store.state/'semantic.json'
    if signature==store.signature('maintenance','semantic') and target.exists():return
    index=build(records)
    write_json(target,index)
    groups=clusters(index)
    lines=['# Suggested semantic groups','','Local latent semantic analysis over conversation titles and sampled user text.',
           'Exploratory co-occurrence groups, not verified project assignments or pretrained-model interpretations.','']
    for group in sorted(groups,key=len,reverse=True):
        weights=Counter()
        for i in group:weights.update(index['vectors'][i])
        lines+=['## '+' / '.join(k for k,_ in weights.most_common(3)),'']
        for i in group:
            r=index['documents'][i]
            lines.append(f'- [{title(r["title"])}](../{r["path"]})')
        lines.append('')
    atomic(store.root/'Topics/Semantic groups.md','\n'.join(lines)+'\n')
    store.checkpoint('maintenance','semantic',signature)
