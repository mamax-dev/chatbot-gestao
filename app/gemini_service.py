import asyncio,os,random,time
from enum import Enum
from google import genai
from google.genai import types
from pydantic import BaseModel,Field
from .cache import get_cached,set_cached
from .config import *
from .document import load_document, normalize
from .knowledge_engine import answer_local
from .prompt import SYSTEM_INSTRUCTION
from .query_analysis import analyze,TOPICS
from .retry_policy import is_retryable_error

class Status(str,Enum):answered='answered';absent='absent';ambiguous='ambiguous'
class ModelAnswer(BaseModel):
    status:Status
    answer:str=Field(min_length=1)
    evidence:list[str]=Field(default_factory=list)
    covered_topics:list[str]=Field(default_factory=list)
class ApiBusyError(RuntimeError):pass

def _required_topics(question):return list(analyze(question).topics)
def _validate(question,parsed,document):
    if parsed.status!=Status.answered:return False
    ev=' '.join(parsed.evidence).strip()
    if not ev:return False
    doc=normalize(document)
    if any(normalize(x) not in doc for x in parsed.evidence):return False
    required=set(_required_topics(question));covered=set(parsed.covered_topics)
    return required.issubset(covered)
def _call(client,question,document,revision=''):
    req=_required_topics(question)
    contents=f'''DOCUMENTO COMPLETO:\n---\n{document}\n---\nPERGUNTA: {question}\nTÓPICOS OBRIGATÓRIOS DETECTADOS: {req}\n{revision}\nResponda todos os tópicos e liste-os em covered_topics. evidence deve conter citações literais do documento.'''
    r=client.models.generate_content(model=GEMINI_MODEL,contents=contents,config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION,max_output_tokens=1400,response_mime_type='application/json',response_schema=ModelAnswer))
    return r.parsed or ModelAnswer.model_validate_json(r.text)
def _with_retry(fn):
    last=None
    for i in range(max(1,AI_RETRY_ATTEMPTS)):
        try:return fn()
        except Exception as e:
            last=e
            if not is_retryable_error(e) or i+1>=AI_RETRY_ATTEMPTS:break
            time.sleep(AI_RETRY_BASE_SECONDS*(2**i)+random.uniform(0,.4))
    if last and is_retryable_error(last):raise ApiBusyError(API_BUSY_MESSAGE) from last
    raise RuntimeError(TECHNICAL_MESSAGE) from last
def _fallback(question,document):
    a=analyze(question);blocks=[]
    from .knowledge_engine import select
    for t in a.topics:blocks+=select(document,TOPICS[t])
    if not blocks: return {'answer':REFUSAL,'evidence':'','status':'absent','cached':False,'source':'fallback','complete':True}
    unique=[]
    for b in blocks:
        if b not in unique:unique.append(b)
    return {'answer':'Informações relacionadas:\n'+'\n'.join('• '+b for b in unique),'evidence':' '.join(unique),'status':'answered','cached':False,'source':'fallback','complete':True}
def _generate_sync(question):
    local=answer_local(question)
    if local:return local
    cached=get_cached(question)
    if cached:return cached
    document=load_document();key=os.getenv('GEMINI_API_KEY')
    if not key:return _fallback(question,document)
    client=genai.Client(api_key=key)
    try:
        parsed=_with_retry(lambda:_call(client,question,document))
        if not _validate(question,parsed,document):
            parsed=_with_retry(lambda:_call(client,question,document,'REVISÃO: a resposta anterior ficou incompleta ou sem evidência literal. Corrija.'))
        if not _validate(question,parsed,document):return _fallback(question,document)
        out={'answer':parsed.answer.strip(),'evidence':' '.join(parsed.evidence),'status':'answered','cached':False,'source':'gemini','complete':True}
        set_cached(question,out);return out
    except Exception as exc:
        print(f'GeminiPipelineError type={type(exc).__name__} detail={str(exc)[:300]}')
        # Any model, validation, SDK, or transient failure degrades to a grounded document fallback.
        return _fallback(question,document)
async def generate_answer(question):return await asyncio.to_thread(_generate_sync,question.strip())
