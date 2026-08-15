import re
from .config import REFUSAL

FRIENDLY_NOT_FOUND='Não encontrei essa informação nas orientações disponíveis. Posso ajudar com serviços, preços, prazos ou pagamentos. 🙂'

def clean_line(line: str) -> str:
    return re.sub(r'^\s*[•\-*]+\s*','',line).strip()

def shorten_document_answer(answer: str, max_points: int = 4) -> str:
    """Keep factual answers short without truncating a sentence mid-way."""
    lines=[clean_line(x) for x in answer.splitlines() if clean_line(x)]
    if not lines:return answer.strip()
    headings={'informacao solicitada:','informacoes solicitadas:','informacoes relacionadas:'}
    if lines[0].lower() in headings:lines=lines[1:]
    lines=lines[:max_points]
    text='\n'.join('• '+line for line in lines)
    return text if text else answer.strip()

def style_result(result: dict, channel: str='web') -> dict:
    value={**result}
    if value.get('status')=='absent' or value.get('answer')==REFUSAL:
        value['answer']=FRIENDLY_NOT_FOUND
        value['evidence']=''
        return value
    # Gemini already writes prose. Local/fallback block dumps are condensed.
    if value.get('source') in {'document-engine','fallback'}:
        value['answer']=shorten_document_answer(value.get('answer',''),4 if channel=='web' else 3)
    # Final safety cap for conversational channels; preserve complete sentences when possible.
    limit=900 if channel=='web' else 700
    text=value.get('answer','').strip()
    if len(text)>limit:
        cut=text[:limit]
        stop=max(cut.rfind('.'),cut.rfind('!'),cut.rfind('?'))
        value['answer']=(cut[:stop+1] if stop>limit//2 else cut.rstrip())
    return value
