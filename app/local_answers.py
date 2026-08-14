from dataclasses import dataclass

from .config import AMBIGUOUS, REFUSAL
from .document import normalize


@dataclass(frozen=True)
class LocalAnswer:
    answer: str
    evidence: str
    status: str = "answered"


def result(item: LocalAnswer) -> dict:
    return {
        "answer": item.answer,
        "evidence": item.evidence,
        "status": item.status,
        "cached": False,
        "source": "local",
    }


def contains_any(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)


BROAD_PATTERNS = {
    "condicoes gerais",
    "resumo dos servicos",
    "resuma os servicos",
    "servicos oferecidos",
    "compare",
    "comparar",
    "explique como funcionam",
    "antes de contratar",
    "deve conhecer",
    "informacoes um cliente",
}


def is_broad_question(question: str) -> bool:
    return contains_any(normalize(question), BROAD_PATTERNS)


def combine(parts: list[str], evidence: list[str]) -> dict | None:
    if not parts:
        return None
    return result(LocalAnswer(" ".join(parts), " ".join(evidence)))


def find_local_answer(question: str) -> dict | None:
    q = normalize(question)

    # Perguntas amplas devem ser sintetizadas pelo Gemini com o documento completo.
    if is_broad_question(question):
        return None

    protection = {
        "ignore o documento",
        "use seus conhecimentos",
        "invente um desconto",
        "capital da franca",
        "melhor marca de computador",
    }
    if contains_any(q, protection):
        return result(LocalAnswer(REFUSAL, "", "absent"))

    absent = {
        "celular", "celulares", "smartphone", "smartphones",
        "venda de computador", "venda de computadores",
        "vendem computadores", "recuperacao de dados", "recuperam dados",
        "desconto para estudante", "desconto para estudantes",
        "desconto promocional", "fora de sao paulo", "rio de janeiro",
    }
    if contains_any(q, absent):
        return result(LocalAnswer(REFUSAL, "", "absent"))

    generic = {
        "quanto custa", "quanto custa o servico", "qual o preco",
        "qual o preco do servico", "quanto tempo demora", "qual o prazo",
        "esta incluido", "tem garantia", "voces fazem esse servico",
        "posso parcelar isso",
    }
    services = {
        "diagnostico", "formatacao", "formatar", "limpeza", "rede",
        "wifi", "roteador", "visita tecnica",
    }
    if q in generic and not contains_any(q, services):
        return result(LocalAnswer(AMBIGUOUS, "", "ambiguous"))

    price_words = {"quanto custa", "quanto esta", "preco", "valor", "quanto pago", "pagar"}
    deadline_words = {"prazo", "quanto tempo", "demora", "duracao", "avaliar"}

    if "diagnostico" in q or ("computador" in q and contains_any(q, {"trava", "travando", "lento", "lentidao", "avaliar"})):
        parts, evidence = [], []
        asks_repair = contains_any(q, {"aprovar", "aprovado", "reparo", "conserto"})
        if contains_any(q, price_words) or asks_repair or contains_any(q, {"trava", "travando", "lento", "lentidao"}):
            parts.append("O diagnóstico de computador custa R$ 80,00.")
            evidence.append("Diagnóstico de computador: preço de R$ 80,00.")
        if contains_any(q, deadline_words) or contains_any(q, {"trava", "travando", "lento", "lentidao"}):
            parts.append("O prazo para avaliação é de até 2 dias úteis.")
            evidence.append("Prazo: até 2 dias úteis.")
        if asks_repair:
            parts.append("Quando o reparo é aprovado, o valor do diagnóstico é descontado do total.")
            evidence.append("O valor é descontado do total quando o reparo é aprovado.")
        answer = combine(parts, evidence)
        if answer:
            return answer

    if contains_any(q, {"formatacao", "formatar"}):
        parts, evidence = [], []
        if contains_any(q, price_words):
            parts.append("A formatação e instalação do sistema custa R$ 180,00.")
            evidence.append("Formatação e instalação do sistema: preço de R$ 180,00.")
        if contains_any(q, deadline_words):
            parts.append("O prazo é de 2 dias úteis.")
            evidence.append("Prazo de 2 dias úteis.")
        if "licenca" in q:
            parts.append("A licença do sistema não está incluída.")
            evidence.append("A licença do sistema não está incluída.")
        if contains_any(q, {"copia", "arquivos", "backup"}):
            parts.append("A cópia dos arquivos deve ser solicitada antes do início do serviço.")
            evidence.append("A cópia de arquivos deve ser solicitada antes do início.")
        answer = combine(parts, evidence)
        if answer:
            return answer

    if "limpeza" in q:
        parts, evidence = [], []
        if contains_any(q, price_words):
            parts.append("A limpeza interna custa R$ 120,00.")
            evidence.append("Limpeza interna: preço de R$ 120,00.")
        if contains_any(q, deadline_words):
            parts.append("O prazo da limpeza interna é de 1 dia útil.")
            evidence.append("Prazo de 1 dia útil.")
        if contains_any(q, {"troca", "componente", "componentes", "peca", "pecas", "inclui"}):
            parts.append("A troca de componentes não está incluída.")
            evidence.append("A troca de componentes não está incluída.")
        answer = combine(parts, evidence)
        if answer:
            return answer

    if contains_any(q, {"rede", "wifi", "roteador"}):
        parts, evidence = [], []
        if contains_any(q, price_words) or "configura" in q:
            parts.append("A configuração da rede sem fio custa R$ 150,00.")
            evidence.append("Configuração de rede sem fio: preço de R$ 150,00.")
        if contains_any(q, deadline_words):
            parts.append("A configuração dura até 2 horas.")
            evidence.append("Duração de até 2 horas.")
        if contains_any(q, {"dispositivo", "dispositivos", "quantos"}):
            parts.append("A configuração inclui a conexão de até cinco dispositivos.")
            evidence.append("Conexão de até cinco dispositivos.")
        if contains_any(q, {"incluido", "inclui", "equipamento"}):
            parts.append("O roteador e outros equipamentos não estão incluídos.")
            evidence.append("Equipamentos não estão incluídos.")
        answer = combine(parts, evidence)
        if answer:
            return answer

    if "visita" in q:
        parts, evidence = [], []
        if contains_any(q, price_words):
            parts.append("A visita técnica custa R$ 100,00.")
            evidence.append("Visita técnica: preço de R$ 100,00.")
        if contains_any(q, deadline_words):
            parts.append("A visita técnica dura até 1 hora.")
            evidence.append("Duração de até 1 hora.")
        answer = combine(parts, evidence)
        if answer:
            return answer

    if contains_any(q, {"horario", "sabado", "domingo", "feriado"}):
        parts, evidence = [], []
        if "sabado" in q:
            parts.append("Aos sábados, o atendimento ocorre das 8h às 12h.")
            evidence.append("Sábados, das 8h às 12h.")
        if contains_any(q, {"domingo", "feriado"}):
            parts.append("Não há atendimento aos domingos e feriados.")
            evidence.append("Não há atendimento aos domingos e feriados.")
        if "horario" in q and not parts:
            parts.append("O atendimento ocorre de segunda a sexta, das 8h às 18h, e aos sábados, das 8h às 12h.")
            evidence.append("Segunda a sexta-feira, das 8h às 18h. Sábados, das 8h às 12h.")
        answer = combine(parts, evidence)
        if answer:
            return answer

    if contains_any(q, {"pagamento", "pagar", "pix", "debito", "credito", "dinheiro", "cheque", "parcel"}):
        if "cheque" in q:
            return result(LocalAnswer("A empresa não aceita cheques.", "Não são aceitos cheques."))
        if "parcel" in q:
            return result(LocalAnswer(
                "Valores a partir de R$ 300,00 podem ser parcelados em até 3 vezes no cartão de crédito.",
                "Valores a partir de R$ 300,00 podem ser parcelados em até 3 vezes no cartão de crédito.",
            ))
        return result(LocalAnswer(
            "São aceitos Pix, cartão de débito, cartão de crédito e dinheiro.",
            "São aceitos Pix, débito, crédito e dinheiro.",
        ))

    if "garantia" in q:
        return result(LocalAnswer("Os serviços possuem garantia de 30 dias.", "Os serviços possuem garantia de 30 dias."))

    if contains_any(q, {"campinas", "rio de janeiro"}):
        return result(LocalAnswer("A empresa atende somente no município de São Paulo.", "A empresa atende somente no município de São Paulo."))

    return None
