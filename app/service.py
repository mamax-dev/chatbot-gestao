import asyncio,json,logging,uuid
from .answer_validator import validate_answer
from .business_config import load_business
from .cache import get,put
from .context_selector import context_text,select_context
from .contracts import BotReply,Source,Status
from .conversation import local_reply
from .faq import lookup
from .security import clean_input,injection_suspected
log=logging.getLogger('chatbot')
COMPLEX=('explique','por que','porque','resuma','compare','relacione','analise','interprete','justifique','sintetize')
def _emit(rid,state,**extra):log.info(json.dumps({'request_id':rid,'state':state,**extra},ensure_ascii=False))
def _reply(rid,answer,source,status='answered',evidence='',cached=False):return BotReply(answer=answer,source=source,status=status,evidence=evidence,cached=cached,request_id=rid).as_dict()
def is_open(q):
    n=q.lower();return any(x in n for x in COMPLEX)
def sync_answer(question):
    rid=uuid.uuid4().hex[:12];q=clean_input(question);_emit(rid,'RECEIVED',length=len(q))
    if injection_suspected(q):
        _emit(rid,'REJECTED',reason='prompt_injection');return _reply(rid,'Não posso atender a esse tipo de instrução. Faça uma pergunta sobre os serviços da empresa.',Source.LOCAL,Status.REJECTED)
    direct=local_reply(q)
    if direct:_emit(rid,'ROUTED_LOCAL');return _reply(rid,direct,Source.LOCAL)
    if not is_open(q):
        faq=lookup(q)
        if faq:_emit(rid,'ROUTED_FAQ');return {**faq,'request_id':rid}
    context=select_context(q)
    if not context:
        _emit(rid,'FAILED',reason='no_context');m=load_business()['conversa']['informacao_ausente'];return _reply(rid,m,Source.FALLBACK,Status.ABSENT)
    cached=get(q)
    if cached:_emit(rid,'CACHE_HIT');return {**cached,'request_id':rid}
    _emit(rid,'CONTEXT_FOUND',keys=[x['key'] for x in context])
    try:
        from .gemini import ask
        text=ask(q,context_text(context))
        if not text:raise ValueError('insufficient_context')
        valid,reason=validate_answer(q,text,context)
        if not valid:raise ValueError(f'answer_validation:{reason}')
        evidence='\n'.join(x['text'] for x in context)
        result=_reply(rid,text,Source.GEMINI,evidence=evidence)
        put(q,result);_emit(rid,'DELIVERED',source='gemini');return result
    except Exception as exc:
        _emit(rid,'FAILED',error=type(exc).__name__,reason=str(exc)[:160])
        m=load_business()['conversa']['indisponibilidade_ia'];return _reply(rid,m,Source.FALLBACK,Status.FAILED)
async def answer(question):return await asyncio.to_thread(sync_answer,question)
