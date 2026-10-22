"""Conservative review cues for assistant feedback; never infer the user's mood."""
from pathlib import Path
import json
import re
from .core import atomic,write_json,digest,now,title,locked

CUES=re.compile(r"^(?:you (?:only|didn't|did not|missed|keep|just)|i (?:don't|do not) (?:understand|see)|(?:that's|that is|this is|you're|you are) (?:wrong|incorrect)|not what i (?:asked|meant)|why (?:did|are|do) you|stop (?:asking|doing)|don't (?:do|ask|use)|do not (?:do|ask|use))\b",re.I)


def candidates(store):
    reviews={row[0] for row in store.db.execute('SELECT identity FROM feedback_reviews')}
    pending=[]
    for record in store.records():
        for i,message in enumerate(record['messages']):
            text=message['text'].strip()
            if message['role']!='user' or message.get('origin_hint') or len(text)>1600 or not CUES.search(text):continue
            key=digest([record['source'],record['id'],message['id'],text])
            if key in reviews:continue
            before=next((m['text'] for m in reversed(record['messages'][:i]) if m['role']=='assistant'),None)
            pending.append({'key':key,'source':record['source'],'conversation_id':record['id'],
                            'message_id':message['id'],'timestamp':message.get('timestamp'),
                            'title':record['title'],'path':record['file_path'],'wording':text,
                            'preceding_assistant_excerpt':before[:1000] if before else None,
                            'classification':'review_needed'})
    return pending


def refresh(store):
    items=candidates(store)
    report={'checked_at':now(),'candidates':items,
            'limits':'Phrase cues only, not sentiment analysis or established negative feedback. Review source context; neutral clarifications and scope changes are not dissatisfaction. Long messages, quotes and unseen cross-app history are not comprehensively audited.'}
    write_json(store.state/'feedback-candidates.json',report)
    lines=['# Feedback review queue','',f'Last checked: {report["checked_at"]}','',report['limits'],'']
    for item in items:
        lines+=['## '+title(item['title']),'', 'Review key: '+item['key'],
                '[Source conversation]('+str((store.root/item['path']).as_uri())+')','',
                '> '+item['wording'].replace('\n','\n> '),'']
    if not items:lines+=['No unreviewed phrase cues in the captured records.']
    atomic(store.root/'System/Feedback/Review queue.md','\n'.join(lines)+'\n')
    return {'status':'review_queue','candidates':len(items),'checked_at':report['checked_at']}


def review(store,key,classification,reason,adjustment=None,already_logged=False):
    if classification not in ['confirmed_feedback','uncertain','not_feedback']:raise ValueError('Unknown review classification')
    if not reason.strip():raise ValueError('Review requires a source-grounded interpretation')
    with locked(store.state/'feedback.lock'):
        prior=store.db.execute('SELECT review_json FROM feedback_reviews WHERE identity=?',(key,)).fetchone()
        if prior:return {'status':'already_reviewed',**json.loads(prior[0])}
        item=next((item for item in candidates(store) if item['key']==key),None)
        if not item:raise ValueError('Unknown current feedback candidate')
        entry={**item,'classification':classification,'reviewed_at':now(),'reason':reason,
               'adjustment':adjustment,'outcome':'Review recorded; user-confirmed resolution is unknown.'}
        if already_logged:
            original=(store.root/'System/Feedback log.md').read_text()
            words=lambda text:' '.join(re.findall(r'\w+',text.lower()))
            if ' '.join(re.findall(r'\w+',item['wording'].lower())[:8]) not in words(original):
                raise ValueError('Existing log does not contain the candidate wording')
            entry['existing_log']='System/Feedback log.md'
        if classification!='not_feedback' and not already_logged:
            log=store.root/'System/Feedback log.md'
            original=log.read_text() if log.exists() else '# Feedback log\n'
            marker='<!-- feedback-review:'+key+' -->'
            if marker not in original:
                section=['',marker,'### '+(item['timestamp'] or entry['reviewed_at'])[:10]+' — '+title(item['title']),'',
                         '- Source: ['+item['source']+':'+item['conversation_id']+']('+str((store.root/item['path']).as_uri())+'); message '+str(item['message_id']),
                         '- User wording: '+item['wording'].replace('\n',' '),
                         '- Context: '+(item['preceding_assistant_excerpt'] or 'No preceding assistant response is captured.').replace('\n',' ')[:500],
                         '- Interpretation: '+classification+'; '+reason,
                         '- Adjustment: '+(adjustment or 'Pending source-context review and appropriate follow-through.'),
                         '- Outcome: '+entry['outcome'],'']
                atomic(log,original.rstrip()+'\n'+'\n'.join(section))
        with store.db:
            store.db.execute('INSERT INTO feedback_reviews VALUES(?,?)',(key,json.dumps(entry)))
        write_json(store.state/'feedback-reviews.json',{'reviews':[json.loads(row[0]) for row in store.db.execute('SELECT review_json FROM feedback_reviews')]})
        return {'status':'reviewed',**entry}
