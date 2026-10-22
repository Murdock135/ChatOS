"""Normalize supported desktop chat-tool responses without inventing unavailable replies."""
import json
from .core import timestamp,write_json,now
from .visibility import clean_text,origin_hint

CAPTURE='partial_desktop_tool_capture'


def normalize(capture,text_cap=20000):
    listing=capture['listing'];pages=capture['pages']
    if not pages:raise ValueError('Desktop capture has no pages')
    thread=pages[0]['thread']
    if thread.get('kind')!='chatgpt' or thread['id']!=listing['id']:
        raise ValueError('Desktop conversation identity/source mismatch')
    messages=[];unavailable=[]
    turns=[turn for page in pages for turn in page.get('turns',[])]
    turns.sort(key=lambda turn:timestamp(turn.get('startedAt')) or '')
    for turn in turns:
        for ordinal,item in enumerate(turn.get('items',[])):
            kind=item.get('type');role='user' if kind=='userMessage' else 'assistant' if kind=='agentMessage' else None
            if not role:continue
            if role=='user':text='\n'.join(p.get('text','') for p in item.get('content',[]) if p.get('type')=='text')
            else:text=item.get('text','')
            if '::chatgpt-content-reference{' in text:
                unavailable.append({'id':item.get('id'),'role':role,'reason':'Source tool supplied a content reference, not message text'})
                continue
            text=clean_text(role,text)
            if text is None or not text:continue
            if item.get('phase') in ['analysis','reasoning','summary']:continue
            messages.append({'id':item.get('id') or 'desktop-'+turn['id']+'-'+str(ordinal),
                             'role':role,'text':text,'phase':item.get('phase'),
                             'timestamp':timestamp(turn.get('startedAt')),'turn_id':turn['id'],
                             'source_item_index':ordinal,'model':None,'reasoning_effort':None,
                             **origin_hint(role,text)})
    return {'source':'chatgpt','id':thread['id'],'title':thread.get('title') or listing.get('title'),
            'created_at':timestamp(thread.get('createdAt')),'updated_at':timestamp(thread.get('updatedAt') or listing.get('updatedAt')),
            'source_app_project_id':listing.get('projectId'),'model':None,'provider':'openai',
            'messages':messages,'model_history':[],'capture':CAPTURE,
            'evidence':{'adapter':'supported-desktop-list_threads/read_thread','text_cap_per_item':text_cap,
                        'pages_read':len(pages),'tool_has_more':any(page.get('page',{}).get('hasMore') for page in pages),
                        'unavailable_message_text':unavailable},
            'limits':['Partial desktop tool capture, not a full transcript or live source subscription.',
                      'Assistant content references are recorded as unavailable; they are never substituted for real replies.',
                      'Models, effort and message details not exposed by these tools remain unknown.',
                      'Recent/pinned listing and per-item/page limits bound coverage, even when a tool reports no next page.']}


def merge(previous,incoming):
    if previous.get('capture')!=CAPTURE:
        return previous  # A partial tool view must never replace a richer export/source capture.
    by_id={message['id']:message for message in previous['messages']}
    for message in incoming['messages']:
        old=by_id.get(message['id'])
        if old and len(old['text'])>len(message['text']) and old['text'].startswith(message['text']):continue
        by_id[message['id']]=message
    incoming['messages']=sorted(by_id.values(),key=lambda m:(m.get('timestamp') or '',m.get('source_item_index',0),m['id']))
    return incoming


def write_inbox(root,envelope):
    records=[normalize(item,envelope.get('text_cap_per_item',20000)) for item in envelope['captures']]
    scanned=len(records)
    target=root/'System/Imports/chatgpt/desktop-partial.json'
    previous=json.loads(target.read_text()) if target.exists() else []
    by_id={record['id']:record for record in previous}
    for record in records:
        by_id[record['id']]=merge(by_id[record['id']],record) if record['id'] in by_id else record
    records=list(by_id.values());write_json(target,records)
    report={'checked_at':envelope.get('checked_at') or now(),'listing_limit':envelope.get('listing_limit'),
            'conversations':len(records),'captured_this_attempt':scanned,'visible_messages':sum(len(r['messages']) for r in records),
            'unavailable_message_text':sum(len(r['evidence']['unavailable_message_text']) for r in records),
            'errors':envelope.get('errors',[]),'capture':CAPTURE,'inbox':str(target)}
    write_json(root/'System/State/desktop-capture-status.json',report)
    return report
