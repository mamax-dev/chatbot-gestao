import re
from .business_config import load_business
from .text import normalize
GREET={'oi','ola','bom dia','boa tarde','boa noite','e ai'}
THANKS={'obrigado','obrigada','valeu'}
BYE={'tchau','ate mais','ate logo'}
ACK={'ok','certo','entendi','beleza','perfeito'}
KNOWN={'quanto','qual','quais','como','onde','quem','empresa','servico','servicos','preco','prazo','diagnostico','formatacao','limpeza','wifi','rede','visita','pagamento','dinheiro','pix','cartao','horario','sabado','domingo','garantia','orcamento','cancelamento','agendamento','arquivos','documentos','gratis','pagar','missao','visao','valores','voces','faz','atendente','humano','compare','explique','resuma','cuidados','posso','cancelar','validade'}
def local_reply(text):
    cfg=load_business();msg=cfg['conversa'];raw=(text or '').strip();q=normalize(raw);compact=q.replace(' ','')
    if not raw:return msg['entrada_invalida']
    if len(raw)>500:return 'Para eu entender melhor, envie até 500 caracteres.'
    if q in GREET:return msg['saudacao']
    if q in THANKS:return msg['agradecimento']
    if q in BYE:return msg['despedida']
    if q in ACK:return 'Certo! Posso ajudar em mais alguma coisa?'
    handoff=cfg.get('transferencia_simulada',{})
    if handoff.get('ativa') and any(normalize(x) in q for x in handoff.get('gatilhos',[])):return handoff['mensagem']
    if len(q)<2 or not re.search('[a-z]',q):return msg['entrada_invalida']
    if len(compact)>=4 and (len(set(compact))<=2 or re.fullmatch(r'(.{1,3})\1{2,}',compact)):return msg['entrada_invalida']
    if len(q.split())<=3 and not any(word in KNOWN for word in q.split()):return msg['entrada_invalida']
    return ''
