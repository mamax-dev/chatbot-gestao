from .config import AMBIGUOUS,REFUSAL
from .document import blocks_from_text,load_document,normalize,sections_from_text
from .query_analysis import TOPICS,analyze
import re

def result(answer,evidence='',status='answered'):
    return {'answer':answer,'evidence':evidence,'status':status,'cached':False,'source':'document-engine','complete':True}
def select(text, aliases):
    """Return complete relevant sections, never a heading without its content."""
    aliases = {normalize(alias) for alias in aliases}
    def matches(value):
        normalized = normalize(value)
        return any(re.search(r'(^| )' + re.escape(alias) + r'($| )', normalized) for alias in aliases)
    output = []
    for heading, paragraphs in sections_from_text(text):
        heading_match = matches(heading)
        matching_paragraphs = [paragraph for paragraph in paragraphs if matches(paragraph)]
        if heading_match:
            # A matched heading brings its complete section.
            candidates = paragraphs
        else:
            candidates = matching_paragraphs
        for paragraph in candidates:
            if paragraph not in output:
                output.append(paragraph)
    return output


def service_blocks(text):
    """Return only the content under SERVIÇOS, excluding later policies."""
    for heading, paragraphs in sections_from_text(text):
        if normalize(heading) == 'servicos':
            return list(paragraphs)
    blocks = []
    for aliases in list(TOPICS.values())[:5]:
        blocks.extend(select(text, aliases))
    return list(dict.fromkeys(blocks))

def format_blocks(title,blocks):
    blocks=[b for i,b in enumerate(blocks) if len(b)>15 and b not in blocks[:i]]
    if not blocks:return None
    return result(title+'\n'+'\n'.join('• '+b for b in blocks),' '.join(blocks))
def answer_from_text(question,text):
    a=analyze(question);q=a.normalized
    if a.external:return result(REFUSAL,status='absent')
    if q in {'quanto custa','quanto custa o servico','qual o preco','quanto tempo demora','qual o prazo','esta incluido','posso parcelar isso'}:return result(AMBIGUOUS,status='ambiguous')
    if q in {'e gratis','gratis','tem que pagar','precisa pagar'}:
        return result('Os serviços são pagos. Diga qual serviço você procura e eu informo o preço. 🙂',status='answered',evidence='SERVIÇOS')
    if q in {'dinheiro','aceita dinheiro','posso pagar em dinheiro'}:
        blocks=select(text,{'dinheiro'})
        return result('Sim. Aceitamos dinheiro, Pix, débito e crédito. 🙂',' '.join(blocks)) if blocks else None
    # Complex/interpretive questions must never be partially answered by keyword extraction.
    if a.complex:return None
    if any(x in q for x in ['quem e a empresa','quem sao voces','fale sobre a empresa']):
        blocks=select(text,{'empresa ficticia','missao','visao','valores'})
        blocks += service_blocks(text)
        return format_blocks('Sobre a empresa:',blocks)
    if any(x in q for x in ['o que a empresa faz','o que voces fazem','o que vcs fazem','o que vc fazem','atividade da empresa','servicos oferecidos']):
        return format_blocks('A Solução Prática oferece:',service_blocks(text))
    if q in {'tem garantia'}:return format_blocks('Informação solicitada:',select(text,TOPICS['garantia']))
    if len(a.topics)==1:return format_blocks('Informação solicitada:',select(text,TOPICS[a.topics[0]]))
    if len(a.topics)==2:
        blocks=[]
        for t in a.topics:blocks+=select(text,TOPICS[t])
        return format_blocks('Informações solicitadas:',blocks)
    return None
def answer_local(question):return answer_from_text(question,load_document())
