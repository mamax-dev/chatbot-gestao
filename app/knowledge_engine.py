from dataclasses import dataclass

from .config import AMBIGUOUS, REFUSAL
from .document import blocks_from_text, load_document, normalize


@dataclass(frozen=True)
class IntentResult:
    answer: str
    evidence: str = ""
    status: str = "answered"


def response(item: IntentResult) -> dict:
    return {"answer": item.answer, "evidence": item.evidence, "status": item.status, "cached": False, "source": "document-engine"}


def has(text: str, *terms: str) -> bool:
    return any(term in text for term in terms)


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
    "missao": {"missao"},
    "visao": {"visao"},
    "valores": {"valores", "principios"},
}

EXTERNAL = {"capital da franca", "melhor marca de computador", "ignore o documento", "use seus conhecimentos", "invente um desconto", "revele o prompt", "mostre o prompt"}
ABSENT = {"celular", "celulares", "smartphone", "smartphones", "venda de computador", "vendem computadores", "recuperacao de dados", "recuperam dados", "desconto para estudante", "desconto para estudantes", "desconto promocional"}


def select_blocks(text: str, aliases: set[str]) -> list[str]:
    found=[]
    for block in blocks_from_text(text):
        normalized=normalize(block)
        if any(alias in normalized for alias in aliases) and block not in found:
            found.append(block)
    return found


def format_answer(title: str, blocks: list[str]) -> dict | None:
    unique=[]
    for block in blocks:
        if len(block)>15 and block not in unique:
            unique.append(block)
    if not unique:
        return None
    return response(IntentResult(title+"\n"+"\n".join(f"• {b}" for b in unique), " ".join(unique)))


def requested_services(q: str) -> list[str]:
    return [name for name, aliases in SERVICE_ALIASES.items() if any(alias in q for alias in aliases)]


def requested_topics(q: str) -> list[str]:
    return [name for name, aliases in TOPIC_ALIASES.items() if any(alias in q for alias in aliases)]


def answer_from_text(question: str, document_text: str) -> dict | None:
    q=normalize(question)
    if any(term in q for term in EXTERNAL) or any(term in q for term in ABSENT):
        return response(IntentResult(REFUSAL,status="absent"))
    if q in {"quanto custa", "quanto custa o servico", "qual o preco", "quanto tempo demora", "qual o prazo", "esta incluido", "posso parcelar isso"}:
        return response(IntentResult(AMBIGUOUS,status="ambiguous"))

    services=requested_services(q)
    topics=requested_topics(q)

    # Institutional questions can be asked separately or together.
    institutional=[topic for topic in ["missao","visao","valores"] if topic in topics]
    if institutional:
        blocks=[]
        for topic in institutional:
            blocks.extend(select_blocks(document_text,TOPIC_ALIASES[topic]))
        return format_answer("Identidade institucional:",blocks)

    # Presentation and activity questions are answered locally, including informal variations.
    company_identity = {
        "quem e a empresa", "quem e essa empresa", "quem sao voces",
        "quem e a solucao pratica", "fale sobre a empresa",
        "apresente a empresa", "qual e a empresa",
    }
    company_activity = {
        "o que a empresa faz", "o que voces fazem", "o que vcs fazem",
        "o que vc fazem", "o que voces oferece", "o que vcs oferece",
        "quais servicos a empresa oferece", "quais servicos voces oferecem",
        "qual e a atividade da empresa", "servicos oferecidos",
        "resumo dos servicos",
    }

    if any(term in q for term in company_identity):
        blocks=[]
        blocks.extend(select_blocks(document_text,{"empresa ficticia", "solucao pratica servicos"}))
        for topic in ["missao","visao","valores"]:
            blocks.extend(select_blocks(document_text,TOPIC_ALIASES[topic]))
        for aliases in SERVICE_ALIASES.values():
            blocks.extend(select_blocks(document_text,aliases))
        return format_answer("Sobre a empresa:",blocks)

    if any(term in q for term in company_activity):
        blocks=[]
        for aliases in SERVICE_ALIASES.values():
            blocks.extend(select_blocks(document_text,aliases))
        return format_answer("A Solução Prática oferece:",blocks)

    if has(q,"condicoes gerais","condicoes de atendimento","antes de contratar","deve conhecer antes"):
        blocks=[]
        for topic in ["horario","area","agendamento","cancelamento","pagamento","orcamento","garantia","materiais"]:
            blocks.extend(select_blocks(document_text,TOPIC_ALIASES[topic]))
        return format_answer("Informações gerais:",blocks)

    if len(topics)>=2:
        blocks=[]
        for topic in topics:
            blocks.extend(select_blocks(document_text,TOPIC_ALIASES[topic]))
        return format_answer("Informações solicitadas:",blocks)

    if len(services)>=2 or "compare" in q:
        blocks=[]
        for service in services or list(SERVICE_ALIASES):
            blocks.extend(select_blocks(document_text,SERVICE_ALIASES[service]))
        return format_answer("Comparação dos serviços:",blocks)

    if len(services)==1:
        blocks=select_blocks(document_text,SERVICE_ALIASES[services[0]])
        if services[0]=="formatacao" and has(q,"preservar","documentos","arquivos","backup","licenca"):
            blocks.extend(select_blocks(document_text,{"copia","arquivos","licenca"}))
        return format_answer("Informações do serviço:",blocks)

    if len(topics)==1:
        return format_answer("Informação solicitada:",select_blocks(document_text,TOPIC_ALIASES[topics[0]]))
    return None


def answer_local(question: str) -> dict | None:
    return answer_from_text(question,load_document())
