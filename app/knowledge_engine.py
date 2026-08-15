import re
from .config import AMBIGUOUS,REFUSAL
from .document import load_document,normalize,sections_from_text
from .query_analysis import TOPICS,analyze

def result(answer,evidence='',status='answered'):return {'answer':answer,'evidence':evidence,'status':status,'cached':False,'source':'document-engine','complete':True}
def select(text,aliases):
    aliases={normalize(a) for a in aliases}
    def match(value):
        n=normalize(value);return any(re.search(r'(^| )'+re.escape(a)+r'($| )',n) for a in aliases)
    out=[]
    for heading,paragraphs in sections_from_text(text):
        candidates=paragraphs if match(heading) else [p for p in paragraphs if match(p)]
        for p in candidates:
            if p not in out:out.append(p)
    return out
def service_blocks(text):
    for heading,paragraphs in sections_from_text(text):
        if normalize(heading)=='servicos':return paragraphs
    return []
def answer_from_text(question,text):
    a=analyze(question);q=a.normalized
    if a.external:return result(REFUSAL,status='absent')
    if q in {'quanto custa','qual o preco','quanto tempo demora','qual o prazo','esta incluido'}:return result(AMBIGUOUS,status='ambiguous')
    if q in {'e gratis','gratis','tem que pagar','precisa pagar'}:return result('Os serviços são pagos. Diga qual serviço procura e eu informo o preço. 🙂','SERVIÇOS')
    if q in {'dinheiro','aceita dinheiro','posso pagar em dinheiro'}:
        b=select(text,{'dinheiro'});return result('Sim. Aceitamos dinheiro, Pix, débito e crédito. 🙂',' '.join(b)) if b else None
    if a.complex:return None
    if any(x in q for x in ['o que a empresa faz','o que voces fazem','o que vcs fazem','o que vc fazem','atividade da empresa']):return result('Oferecemos diagnóstico, formatação, limpeza interna, configuração de rede sem fio e visita técnica. 🙂',' '.join(service_blocks(text)))
    if len(a.topics)==1:
        b=select(text,TOPICS[a.topics[0]])
        return result(b[0],' '.join(b)) if b else None
    if len(a.topics)==2:
        lines=[]
        for t in a.topics:lines+=select(text,TOPICS[t])
        lines=list(dict.fromkeys(lines));return result('\n'.join('• '+x for x in lines),' '.join(lines)) if lines else None
    return None
def answer_local(question):return answer_from_text(question,load_document())
