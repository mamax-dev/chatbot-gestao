from .business_config import load_business
from .text import normalize
def reply(answer,evidence=''):return {'answer':answer,'evidence':evidence,'status':'answered','cached':False,'source':'faq'}
def _service(service):
    return reply(f"{service['nome']}: {service['preco']}; prazo {service['prazo']}. {' '.join(service['observacoes'])}".strip(),str(service))
def lookup(question):
    cfg=load_business();q=normalize(question)
    if any(normalize(x) in q for x in cfg['fora_do_escopo']):return {'answer':cfg['conversa']['informacao_ausente'],'evidence':'','status':'absent','cached':False,'source':'faq'}
    if any(x in q for x in ['o que a empresa faz','o que voces faz','quais servicos','atividade da empresa']):return reply('Oferecemos '+', '.join(s['nome'] for s in cfg['servicos'])+'.',str(cfg['servicos']))
    if 'quem e a empresa' in q:return reply(f"A {cfg['empresa']['nome']} é uma {cfg['empresa']['natureza']} voltada a {cfg['empresa']['descricao']}.",str(cfg['empresa']))
    for key,label in [('missao','Missão'),('visao','Visão'),('valores','Valores')]:
        if key in q:
            value=cfg['empresa'][key];value=', '.join(value) if isinstance(value,list) else value
            return reply(f'{label}: {value}',value)
    matched=[]
    for service in cfg['servicos']:
        if any(normalize(v) in q for v in service['variacoes']):matched.append(service)
    if len(matched)==1:return _service(matched[0])
    if len(matched)>1:return reply('\n'.join(f"{s['nome']}: {s['preco']}; prazo {s['prazo']}." for s in matched),str(matched))
    if any(x in q for x in ['dinheiro','pix','pagamento','pagar','cartao','parcelar','cheque']):
        p=cfg['pagamentos'];return reply(f"Aceitamos {', '.join(p['formas_aceitas'])}. {p['parcelamento']}. Não aceitamos {', '.join(p['formas_nao_aceitas'])}.",str(p))
    if any(x in q for x in ['horario','sabado','domingo','feriado']):
        a=cfg['atendimento'];return reply(f"Segunda a sexta: {a['segunda_a_sexta']}; sábado: {a['sabado']}; domingo e feriados: {a['domingo_e_feriados']}. Atendimento {a['area']}.",str(a))
    pol=cfg['politicas'];mapping={'agend':'agendamento','cancel':'cancelamento','desloc':'deslocamento','orcamento':'orcamento','validade':'validade_orcamento','garantia':'garantia','pecas':'materiais','cabos':'materiais','materiais':'materiais'};selected=[]
    for term,key in mapping.items():
        if term in q and key not in selected:selected.append(key)
    if selected:return reply(' '.join(pol[k] for k in selected),' '.join(pol[k] for k in selected))
    if any(x in q for x in ['gratis','tem que pagar','precisa pagar']):return reply('Os serviços são pagos. Diga qual serviço procura e eu informo o preço.','serviços pagos')
    if all(x in q for x in ['custos','arquivos']):return reply(f"{pol['cancelamento']} {pol['orcamento']} {pol['materiais']} A cópia de arquivos deve ser solicitada antes da formatação.",str(pol))
    return None
