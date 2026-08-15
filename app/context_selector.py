import json, re
from .business_config import load_business
from .text import normalize
STOP={'a','as','o','os','de','da','do','das','dos','e','em','por','para','qual','quais','como','um','uma','que'}
def _tokens(text): return {x for x in normalize(text).split() if len(x)>2 and x not in STOP}
def _parts():
    cfg=load_business(); parts=[]
    emp=cfg['empresa']
    parts += [('empresa',f"Nome: {emp.get('nome','')}. Descrição: {emp.get('descricao','')}. Missão: {emp.get('missao','')}. Visão: {emp.get('visao','')}. Valores: {', '.join(emp.get('valores',[]))}.")]
    parts += [(f"servico:{s.get('id',s['nome'])}",f"{s['nome']}. {s.get('descricao','')} Preço: {s['preco']}. Prazo: {s['prazo']}. {' '.join(s.get('observacoes',[]))}") for s in cfg['servicos']]
    a=cfg['atendimento']; parts.append(('atendimento',f"Atendimento: segunda a sexta {a['segunda_a_sexta']}; sábado {a['sabado']}; domingo e feriados {a['domingo_e_feriados']}; área {a['area']}."))
    p=cfg['pagamentos']; parts.append(('pagamentos',f"Pagamentos aceitos: {', '.join(p['formas_aceitas'])}. Não aceitos: {', '.join(p['formas_nao_aceitas'])}. Parcelamento: {p['parcelamento']}."))
    parts += [(f'politica:{k}',f"{k.replace('_',' ').title()}: {v}") for k,v in cfg['politicas'].items()]
    return parts
def select_context(question:str,limit:int=6):
    qt=_tokens(question); scored=[]
    synonyms={'diagnostico':{'diagnostico'},'visita':{'visita','tecnica'},'transparencia':{'orcamento','aprovacao','garantia','cancelamento'},'custos':{'preco','materiais','cancelamento'},'arquivos':{'formatacao','copia','backup'}}
    expanded=set(qt)
    for key,vals in synonyms.items():
        if key in qt: expanded|=vals
    for key,text in _parts():
        score=len(expanded & _tokens(key+' '+text))
        if score: scored.append((score,key,text))
    scored.sort(key=lambda x:(-x[0],x[1]))
    return [{'key':k,'text':t,'score':s} for s,k,t in scored[:limit]]
def context_text(items): return '\n'.join(f"[{x['key']}] {x['text']}" for x in items)
