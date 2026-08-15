import asyncio,os,random,time
from enum import Enum
from google import genai
from google.genai import types
from pydantic import BaseModel,Field
from .cache import get_cached,set_cached
from .config import *
from .document import load_document,normalize
from .fallback import build_document_fallback
from .input_policy import inspect_input
from .knowledge_engine import answer_local
from .prompt import SYSTEM_INSTRUCTION
from .query_analysis import analyze
from .response_style import style_result
from .retry_policy import is_retryable_error
class Status(str,Enum):answered='answered';absent='absent';ambiguous='ambiguous'
class ModelAnswer(BaseModel):
    status:Status;answer:str=Field(min_length=1);evidence:list[str]=Field(default_factory=list);covered_topics:list[str]=Field(default_factory=list)
def call(client,q,doc,revision=''):
    req=list(analyze(q).topics)
    content=f'DOCUMENTO:\n{doc}\nPERGUNTA:{q}\nTÓPICOS OBRIGATÓRIOS:{req}\n{revision}\nUma frase curta por tópico; não omita tópicos.'
    r=client.models.generate_content(model=GEMINI_MODEL,contents=content,config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION,max_output_tokens=1200,response_mime_type='application/json',response_schema=ModelAnswer))
    return r.parsed or ModelAnswer.model_validate_json(r.text)
def retry(fn):
    last=None
    for i in range(max(1,AI_RETRY_ATTEMPTS)):
        try:return fn()
        except Exception as e:
            last=e
            if not is_retryable_error(e) or i+1>=AI_RETRY_ATTEMPTS:break
            time.sleep(AI_RETRY_BASE_SECONDS*(2**i)+random.uniform(0,.4))
    raise last
def valid(q,p,doc):
    if p.status!=Status.answered or not p.evidence:return False
    if any(normalize(e) not in normalize(doc) for e in p.evidence):return False
    return set(analyze(q).topics).issubset(set(p.covered_topics))
def generate_sync(q):
    decision=inspect_input(q)
    if not decision.valid:return {'answer':decision.reply,'evidence':'','status':'answered','cached':False,'source':'input-policy','complete':True}
    routed_question = decision.corrected or q
    local=answer_local(routed_question)
    if local:return style_result(local)
    cached=get_cached(routed_question)
    if cached:return style_result(cached)
    doc=load_document();key=os.getenv('GEMINI_API_KEY')
    if not key:return style_result(build_document_fallback(routed_question,doc))
    try:
        client=genai.Client(api_key=key);parsed=retry(lambda:call(client,routed_question,doc))
        if not valid(routed_question,parsed,doc):parsed=retry(lambda:call(client,routed_question,doc,'REVISE: resposta incompleta.'))
        if not valid(routed_question,parsed,doc):return style_result(build_document_fallback(routed_question,doc))
        out={'answer':parsed.answer.strip(),'evidence':' '.join(parsed.evidence),'status':'answered','cached':False,'source':'gemini','complete':True};set_cached(routed_question,out);return style_result(out)
    except Exception as exc:
        print(f'GeminiPipelineError type={type(exc).__name__} detail={str(exc)[:300]}');return style_result(build_document_fallback(routed_question,doc))
async def generate_answer(q,channel='web'):return await asyncio.to_thread(generate_sync,q.strip())
