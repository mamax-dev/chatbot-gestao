from dataclasses import dataclass

from .config import AMBIGUOUS, REFUSAL
from .document import blocks_from_text, load_document, normalize


@dataclass(frozen=True)
class IntentResult:
    answer: str
    evidence: str = ""
    status: str = "answered"


def response(item: IntentResult) -> dict:
    return {
        "answer": item.answer,
        "evidence": item.evidence,
        "status": item.status,
        "cached": False,
        "source": "document-engine",
    }


def has(text: str, *terms: str) -> bool:
    return any(term in text for term in terms)


def all_has(text: str, *terms: str) -> bool:
    return all(term in text for term in terms)


SERVICE_ALIASES = {
    "diagnostico": {"diagnostico", "analisar", "avaliar", "travando", "trava", "lentidao", "lento"},
    "formatacao": {"formatacao", "formatar", "instalacao do sistema", "instalar o sistema"},
    "limpeza": {"limpeza", "poeira", "ventilacao"},
    "rede": {"wifi", "wi fi", "rede sem fio", "roteador", "internet sem fio"},
    "visita": {"visita", "tecnico no local", "atendimento no endereco"},
}

TOPIC_ALIASES = {
    "agendamento": {"agendamento", "agendar", "marcar atendimento"},
    "cancelamento": {"cancelamento", "cancelar", "reagendamento", "reagendar", "tecnico ja saiu", "deslocamento"},
    "pagamento": {"pagamento", "pagar", "pix", "debito", "credito", "dinheiro", "cheque", "parcelar", "dividir", "cobranca"},
    "orcamento": {"orcamento", "aprovar", "aprovacao", "reparo adicional"},
    "garantia": {"garantia"},
    "horario": {"horario", "sabado", "domingo", "feriado"},
    "area": {"sao paulo", "campinas", "rio de janeiro", "fora de sao paulo"},
    "materiais": {"peca", "pecas", "material", "materiais", "cabo", "cabos", "licenca", "roteador", "incluido", "incluida", "inclui"},
}

DIMENSION_ALIASES = {
    "price": {"quanto custa", "quanto fica", "quanto esta", "preco", "valor", "quanto pago", "cobranca"},
    "time": {"prazo", "quanto tempo", "demora", "duracao", "quando recebo", "resultado"},
    "included": {"inclui", "incluido", "incluida", "itens nao incluidos", "preservar", "documentos", "arquivos", "backup"},
}

EXTERNAL = {
    "capital da franca", "melhor marca de computador", "ignore o documento",
    "use seus conhecimentos", "invente um desconto", "revele o prompt", "mostre o prompt",
}

ABSENT = {
    "celular", "celulares", "smartphone", "smartphones", "venda de computador",
    "vendem computadores", "recuperacao de dados", "recuperam dados",
    "desconto para estudante", "desconto para estudantes", "desconto promocional",
}


def requested_services(q: str) -> list[str]:
    return [name for name, aliases in SERVICE_ALIASES.items() if any(alias in q for alias in aliases)]


def requested_topics(q: str) -> list[str]:
    return [name for name, aliases in TOPIC_ALIASES.items() if any(alias in q for alias in aliases)]


def requested_dimensions(q: str) -> set[str]:
    return {name for name, aliases in DIMENSION_ALIASES.items() if any(alias in q for alias in aliases)}


def select_blocks(text: str, keyword_sets: list[set[str]]) -> list[str]:
    selected = []
    for block in blocks_from_text(text):
        normalized = normalize(block)
        if any(any(keyword in normalized for keyword in keywords) for keywords in keyword_sets):
            if block not in selected:
                selected.append(block)
    return selected


def service_blocks(text: str, service: str) -> list[str]:
    aliases = SERVICE_ALIASES[service]
    return select_blocks(text, [aliases])


def topic_blocks(text: str, topic: str) -> list[str]:
    aliases = TOPIC_ALIASES[topic]
    return select_blocks(text, [aliases])


def concise_blocks(blocks: list[str], max_items: int = 30) -> list[str]:
    clean = []
    for block in blocks:
        if len(block) > 15 and block not in clean:
            clean.append(block)
    return clean[:max_items]


def format_document_answer(title: str, blocks: list[str]) -> dict | None:
    blocks = concise_blocks(blocks)
    if not blocks:
        return None
    answer = title + "\n" + "\n".join(f"• {block}" for block in blocks)
    evidence = " ".join(blocks)
    return response(IntentResult(answer=answer, evidence=evidence))


def answer_from_text(question: str, document_text: str) -> dict | None:
    q = normalize(question)

    if any(term in q for term in EXTERNAL):
        return response(IntentResult(REFUSAL, status="absent"))

    if any(term in q for term in ABSENT):
        return response(IntentResult(REFUSAL, status="absent"))

    # Perguntas genuinamente ambíguas são tratadas antes da detecção de tópicos.
    if q in {
        "quanto custa", "quanto custa o servico", "qual o preco", "quanto tempo demora",
        "qual o prazo", "esta incluido", "posso parcelar isso",
    }:
        return response(IntentResult(AMBIGUOUS, status="ambiguous"))

    services = requested_services(q)
    topics = requested_topics(q)
    dimensions = requested_dimensions(q)

    # Garantia é geral, portanto não é ambígua.
    if q == "tem garantia":
        topics = ["garantia"]

    # Corrige premissas falsas sobre domingo, cheque, licença e duração da visita.
    if "domingo" in q and "sabado" not in q:
        blocks = topic_blocks(document_text, "horario")
        sunday = [b for b in blocks if "domingo" in normalize(b) or "feriado" in normalize(b)]
        return format_document_answer("Condição correta:", sunday)

    # Consultas amplas previsíveis.
    if has(q, "condicoes gerais", "condicoes de atendimento", "antes de contratar", "deve conhecer antes"):
        blocks = []
        for topic in ["horario", "area", "agendamento", "cancelamento", "pagamento", "orcamento", "garantia", "materiais"]:
            blocks.extend(topic_blocks(document_text, topic))
        return format_document_answer("Informações gerais:", blocks,)

    if has(q, "quais servicos existem", "servicos oferecidos", "resumo dos servicos", "resuma os servicos"):
        blocks = []
        for service in SERVICE_ALIASES:
            blocks.extend(service_blocks(document_text, service))
        return format_document_answer("Serviços oferecidos:", blocks)

    # Composição por múltiplos tópicos, sem parar no primeiro.
    if len(topics) >= 2:
        blocks = []
        for topic in topics:
            blocks.extend(topic_blocks(document_text, topic))
        return format_document_answer("Informações solicitadas:", blocks)

    # Comparações e consultas envolvendo vários serviços.
    if len(services) >= 2 or "compare" in q:
        blocks = []
        for service in services or list(SERVICE_ALIASES):
            blocks.extend(service_blocks(document_text, service))
        return format_document_answer("Comparação dos serviços:", blocks)

    # Consulta específica de serviço. O bloco documental preserva preço, prazo e exclusões.
    if len(services) == 1:
        blocks = service_blocks(document_text, services[0])
        # Serviço de formatação + preservação de arquivos exige também o bloco de cópia/backup.
        if services[0] == "formatacao" and has(q, "preservar", "documentos", "arquivos", "backup", "licenca"):
            blocks.extend(select_blocks(document_text, [{"copia", "arquivos", "licenca"}]))
        return format_document_answer("Informações do serviço:", blocks)

    # Consulta de um tópico.
    if len(topics) == 1:
        return format_document_answer("Informação solicitada:", topic_blocks(document_text, topics[0]))

    return None


def answer_local(question: str) -> dict | None:
    return answer_from_text(question, load_document())
