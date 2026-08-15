import re
from .text import normalize
GREET={'oi','ola','bom dia','boa tarde','boa noite','e ai'};THANKS={'obrigado','obrigada','valeu'};BYE={'tchau','ate mais','ate logo'};ACK={'ok','certo','entendi','beleza','perfeito'}
KNOWN={'quanto','qual','quais','como','onde','quem','servico','servicos','preco','prazo','empresa','diagnostico','formatacao','limpeza','wifi','rede','visita','pagamento','dinheiro','pix','cartao','horario','sabado','domingo','garantia','orcamento','cancelamento','agendamento','arquivos','documentos','gratis','pagar','missao','visao','valores','voces','faz'}
def local_reply(text):
    raw=(text or '').strip();q=normalize(raw);compact=q.replace(' ','')
    if not raw:return 'Escreva uma pergunta para eu ajudar. 🙂'
    if len(raw)>500:return 'Para eu entender melhor, envie até 500 caracteres. 🙂'
    if q in GREET:return 'Olá! Que bom falar com você. 😊 Posso ajudar com serviços, preços, prazos ou atendimento.'
    if q in THANKS:return 'Por nada! Estou por aqui se precisar. 🙂'
    if q in BYE:return 'Até mais! Quando precisar, é só chamar. 🙂'
    if q in ACK:return 'Certo! Posso ajudar em mais alguma coisa? 🙂'
    if len(q)<2 or not re.search('[a-z]',q):return 'Pode me contar um pouco mais? Exemplo: “Quanto custa o diagnóstico?”'
    if len(compact)>=4 and (len(set(compact))<=2 or re.fullmatch(r'(.{1,3})\1{2,}',compact)):return 'Não consegui identificar uma pergunta. Pode escrever sua dúvida em poucas palavras? 🙂'
    if len(q.split())<=3 and not any(w in KNOWN for w in q.split()):return 'Não consegui identificar uma pergunta. Pode escrever sua dúvida em poucas palavras? 🙂'
    return ''
