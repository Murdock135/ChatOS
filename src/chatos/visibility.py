"""Separate visible conversation text from recognized source-generated context wrappers."""
import json
import re

HARNESS = ('# AGENTS.md instructions','<environment_context>','<external_codex_apps_open_page>',
           '<permissions instructions>','<collaboration_mode>','<system_reminder>',
           '<recommended_plugins>','<skills_instructions>','<app-context>','<turn_aborted>')


def clean_text(role,text):
    if role!='user':return text
    if text.lstrip().startswith(HARNESS):return None
    if text.lstrip().startswith('<send_user_message_question_reply>'):
        try:
            answers=json.loads(re.sub(r'</?send_user_message_question_reply>','',text).strip())
            return '\n'.join(str(x.get('question',''))+'\n'+str(x.get('answer','')) for x in answers)
        except (ValueError,TypeError):pass
    return text


def origin_hint(role,text):
    if role!='user':return {}
    if text.lstrip().startswith('<heartbeat>'):
        match=re.search(r'<automation_id>([^<]+)</automation_id>',text)
        return {'origin_hint':'automation_markup','automation_id_observed':match.group(1) if match else None}
    if text.lstrip().startswith(('## Referenced ChatGPT conversation:','## Prior conversation with Codex:')):
        return {'origin_hint':'referenced_context'}
    return {}
