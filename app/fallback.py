import re
from .config import REFUSAL
from .query_analysis import TOPICS,analyze
LABELS={'agendamento':'Agendamento','cancelamento':'Cancelamento','pagamento':'Pagamento','orcamento':'Orçamento','garantia':'Garantia','materiais':'Materiais','formatacao':'Formatação','diagnostico':'Diagnóstico','limpeza':'Limpeza','rede':'Rede sem fio','visita':'Visita técnica','horario':'Horário','missao':'Missão','visao':'Visão','valores':'Valores'}
def first_sentences(text,maximum=2):
    parts=[x.strip() for x in re.split(r'(?<=[.!?])\s+',text) if x.strip()];return ' '.join(parts[:maximum])
def build_document_fallback(question,document):
    from .knowledge_engine import select
    a=analyze(question);lines=[];evidence=[]
    for topic in a.topics:
        blocks=select(document,TOPICS[topic])
        if blocks:
            lines.append(f"{LABELS.get(topic,topic.title())}: {first_sentences(' '.join(dict.fromkeys(blocks)))}");evidence+=blocks
    lines=list(dict.fromkeys(lines));evidence=list(dict.fromkeys(evidence))
    if not lines:return {'answer':REFUSAL,'evidence':'','status':'absent','cached':False,'source':'fallback','complete':True}
    return {'answer':'\n'.join('• '+x for x in lines),'evidence':' '.join(evidence),'status':'answered','cached':False,'source':'fallback','complete':True}
