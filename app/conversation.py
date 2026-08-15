import re

from .business_config import load_business
from .text import normalize

GREET = {'oi', 'ola', 'bom dia', 'boa tarde', 'boa noite', 'e ai'}
THANKS = {'obrigado', 'obrigada', 'valeu', 'agradeco'}
BYE = {'tchau', 'ate mais', 'ate logo'}
ACK = {'ok', 'certo', 'entendi', 'beleza', 'perfeito', 'sim', 'nao'}
HELP = {'ajuda', 'menu', 'opcoes', 'opcao'}

KNOWN = {
    'quanto', 'qual', 'quais', 'como', 'onde', 'quem', 'empresa', 'servico',
    'servicos', 'preco', 'precos', 'prazo', 'diagnostico', 'formatacao',
    'limpeza', 'wifi', 'rede', 'visita', 'pagamento', 'dinheiro', 'pix',
    'cartao', 'horario', 'sabado', 'domingo', 'garantia', 'orcamento',
    'cancelamento', 'agendamento', 'arquivos', 'documentos', 'gratis',
    'pagar', 'missao', 'visao', 'valor', 'valores', 'principios', 'voces',
    'faz', 'atendente', 'humano', 'compare', 'explique', 'resuma', 'cuidados',
    'tabela', 'custam', 'oferecem', 'formas', 'atendem', 'aceita', 'licenca',
    'pecas', 'cabos', 'roteador', 'dispositivos', 'desconto', 'validade',
    'aprovar', 'aprovacao', 'reagendar', 'reagendamento', 'deslocamento',
}


def local_reply(text):
    cfg = load_business()
    messages = cfg['conversa']
    raw = (text or '').strip()
    question = normalize(raw)
    compact = question.replace(' ', '')

    if not raw:
        return messages['entrada_invalida']
    if len(raw) > 500:
        return 'Para eu entender melhor, envie até 500 caracteres.'
    if question in GREET:
        return messages['saudacao']
    if question in THANKS:
        return messages['agradecimento']
    if question in BYE:
        return messages['despedida']
    if question in ACK:
        return 'Certo! Posso ajudar em mais alguma coisa?'
    if question in HELP:
        return 'Posso informar serviços, preços, prazos, horários, pagamentos, políticas, missão, visão e valores.'

    handoff = cfg.get('transferencia_simulada', {})
    if handoff.get('ativa') and any(
        normalize(trigger) in question for trigger in handoff.get('gatilhos', [])
    ):
        return handoff['mensagem']

    if len(question) < 2 or not re.search(r'[a-z]', question):
        return messages['entrada_invalida']
    if len(compact) >= 4 and (
        len(set(compact)) <= 2 or re.fullmatch(r'(.{1,3})\1{2,}', compact)
    ):
        return messages['entrada_invalida']
    if len(question.split()) <= 3 and not any(word in KNOWN for word in question.split()):
        return messages['entrada_invalida']
    return ''
