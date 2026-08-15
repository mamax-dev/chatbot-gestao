from .config import AMBIGUOUS,REFUSAL
from .document import blocks_from_text,load_document,normalize
from .query_analysis import TOPICS,analyze

def result(answer,evidence='',status='answered'):
    return {'answer':answer,'evidence':evidence,'status':status,'cached':False,'source':'document-engine','complete':True}
def select(text,aliases):
    out=[]
    for b in blocks_from_text(text):
        n=normalize(b)
        if any(a in n for a in aliases) and b not in out:out.append(b)
    return out
def format_blocks(title,blocks):
    blocks=[b for i,b in enumerate(blocks) if len(b)>15 and b not in blocks[:i]]
    if not blocks:return None
    return result(title+'\n'+'\n'.join('• '+b for b in blocks),' '.join(blocks))
def answer_from_text(question,text):
    a=analyze(question);q=a.normalized
    if a.external:return result(REFUSAL,status='absent')
    if q in {'quanto custa','quanto custa o servico','qual o preco','quanto tempo demora','qual o prazo','esta incluido','posso parcelar isso'}:return result(AMBIGUOUS,status='ambiguous')
    # Complex/interpretive questions must never be partially answered by keyword extraction.
    if a.complex:return None
    if any(x in q for x in ['quem e a empresa','quem sao voces','fale sobre a empresa']):
        blocks=select(text,{'empresa ficticia','missao','visao','valores'})
        for aliases in list(TOPICS.values())[:5]:blocks+=select(text,aliases)
        return format_blocks('Sobre a empresa:',blocks)
    if any(x in q for x in ['o que a empresa faz','o que voces fazem','o que vcs fazem','o que vc fazem','atividade da empresa','servicos oferecidos']):
        blocks=[]
        for aliases in list(TOPICS.values())[:5]:blocks+=select(text,aliases)
        return format_blocks('A Solução Prática oferece:',blocks)
    if q in {'tem garantia'}:return format_blocks('Informação solicitada:',select(text,TOPICS['garantia']))
    if len(a.topics)==1:return format_blocks('Informação solicitada:',select(text,TOPICS[a.topics[0]]))
    if len(a.topics)==2:
        blocks=[]
        for t in a.topics:blocks+=select(text,TOPICS[t])
        return format_blocks('Informações solicitadas:',blocks)
    return None
def answer_local(question):return answer_from_text(question,load_document())
