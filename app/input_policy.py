import re
from dataclasses import dataclass
from difflib import get_close_matches

from .document import load_document, normalize

MAX_INPUT_CHARS = 500

GREETINGS = {'oi', 'ola', 'bom dia', 'boa tarde', 'boa noite', 'e ai', 'eai', 'hello', 'hey'}
THANKS = {'obrigado', 'obrigada', 'valeu', 'agradeco', 'muito obrigado', 'muito obrigada'}
FAREWELLS = {'tchau', 'ate logo', 'ate mais', 'falou'}
ACKNOWLEDGEMENTS = {'ok', 'certo', 'entendi', 'beleza', 'perfeito', 'ta bom', 'esta bem'}

# Words that may express a valid short business query even when absent from one document revision.
CONVERSATION_WORDS = {
    'aceita', 'atende', 'atendimento', 'como', 'contato', 'custa', 'demora', 'dinheiro',
    'domingo', 'empresa', 'faz', 'fazem', 'garantia', 'gratis', 'horario', 'hoje', 'limpeza',
    'missao', 'onde', 'orcamento', 'pagamento', 'pagar', 'pix', 'prazo', 'preco', 'rede',
    'sabado', 'servico', 'servicos', 'telefone', 'telegram', 'tem', 'valor', 'valores',
    'visao', 'visita', 'voces', 'vcs', 'wifi', 'diagnostico', 'formatacao', 'cancelamento',
    'agendamento', 'cartao', 'credito', 'debito', 'parcelar', 'arquivos', 'documentos',
}
QUESTION_WORDS = {'como', 'qual', 'quais', 'quanto', 'quando', 'onde', 'porque', 'por que', 'quem', 'o que'}

@dataclass(frozen=True)
class InputDecision:
    valid: bool
    reply: str = ''
    normalized: str = ''
    corrected: str = ''


def _document_vocabulary() -> set[str]:
    try:
        words = set(normalize(load_document()).split())
    except Exception:
        words = set()
    return {word for word in words if len(word) >= 2} | CONVERSATION_WORDS | QUESTION_WORDS


def _looks_repetitive(compact: str) -> bool:
    return len(compact) >= 4 and (
        len(set(compact)) <= 2 or bool(re.fullmatch(r'(.{1,3})\1{2,}', compact))
    )


def _correct_tokens(tokens: list[str], vocabulary: set[str]) -> list[str]:
    corrected = []
    for token in tokens:
        if token in vocabulary or len(token) <= 2 or token.isdigit():
            corrected.append(token)
            continue
        match = get_close_matches(token, vocabulary, n=1, cutoff=0.84)
        corrected.append(match[0] if match else token)
    return corrected


def inspect_input(text: str) -> InputDecision:
    raw = (text or '').strip()
    normalized = normalize(raw)

    if not raw:
        return InputDecision(False, 'Escreva uma pergunta para eu ajudar. 🙂', normalized)
    if len(raw) > MAX_INPUT_CHARS:
        return InputDecision(False, 'Para eu entender melhor, envie até 500 caracteres. 🙂', normalized)
    if normalized in GREETINGS:
        return InputDecision(False, 'Olá! Que bom falar com você. 😊 Posso ajudar com serviços, preços, prazos ou atendimento.', normalized)
    if normalized in THANKS:
        return InputDecision(False, 'Por nada! Estou por aqui se precisar. 🙂', normalized)
    if normalized in FAREWELLS:
        return InputDecision(False, 'Até mais! Quando precisar, é só chamar. 🙂', normalized)
    if normalized in ACKNOWLEDGEMENTS:
        return InputDecision(False, 'Certo! Posso ajudar em mais alguma coisa? 🙂', normalized)
    if len(normalized) < 2:
        return InputDecision(False, 'Pode me contar um pouco mais? Exemplo: “Quanto custa o diagnóstico?”', normalized)

    compact = normalized.replace(' ', '')
    if not compact or not re.search(r'[a-z]', compact) or _looks_repetitive(compact):
        return InputDecision(False, 'Não consegui identificar uma pergunta. Tente: “Qual é o preço da limpeza?”', normalized)

    tokens = normalized.split()
    vocabulary = _document_vocabulary()
    corrected_tokens = _correct_tokens(tokens, vocabulary)
    recognized = [token for token in corrected_tokens if token in vocabulary]

    # A short unknown token or a short phrase with no recognizable intent is treated as noise.
    # This blocks strings such as abcd, afgi and nmgk without charging the AI.
    if not recognized and (len(tokens) <= 3 or len(compact) <= 18):
        return InputDecision(False, 'Não consegui identificar uma pergunta. Pode escrever sua dúvida em poucas palavras? 🙂', normalized)

    corrected = ' '.join(corrected_tokens)
    return InputDecision(True, normalized=normalized, corrected=corrected)
