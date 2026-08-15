import re
from dataclasses import dataclass
from .document import normalize

MAX_INPUT_CHARS = 500
GREETINGS = {'oi','ola','bom dia','boa tarde','boa noite','e ai','eai','hello','hey'}

@dataclass(frozen=True)
class InputDecision:
    valid: bool
    reply: str = ''
    normalized: str = ''


def inspect_input(text: str) -> InputDecision:
    raw = (text or '').strip()
    normalized = normalize(raw)
    if not raw:
        return InputDecision(False,'Escreva uma pergunta para eu ajudar. 🙂',normalized)
    if len(raw) > MAX_INPUT_CHARS:
        return InputDecision(False,f'Para eu entender melhor, envie até {MAX_INPUT_CHARS} caracteres. 🙂',normalized)
    if normalized in GREETINGS:
        return InputDecision(False,'Olá! Que bom falar com você. 😊 Posso ajudar com serviços, preços, prazos ou atendimento.',normalized)
    if len(normalized) < 2:
        return InputDecision(False,'Pode me contar um pouco mais? Exemplo: “Quanto custa o diagnóstico?”',normalized)
    compact = normalized.replace(' ','')
    if not compact or not re.search(r'[a-z]',compact):
        return InputDecision(False,'Não consegui entender. Pode escrever sua dúvida em poucas palavras? 🙂',normalized)
    # Repetitive noise: aaaaaa, 111111, abcabcabc and similar low-information input.
    if len(compact) >= 4 and (len(set(compact)) <= 2 or re.fullmatch(r'(.{1,3})\1{2,}',compact)):
        return InputDecision(False,'Não consegui identificar uma pergunta. Tente: “Qual é o preço da limpeza?”',normalized)
    return InputDecision(True,normalized=normalized)
