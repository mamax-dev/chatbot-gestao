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


def find_local_answer(question: str) -> dict | None:
    q = normalize(question)

    absent = {
        "celular", "celulares", "smartphone", "smartphones",
        "venda de computador", "venda de computadores",
        "recuperacao de dados", "desconto para estudante",
        "desconto promocional", "fora de sao paulo",
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
        "diagnostico", "formatacao", "limpeza", "rede", "wifi",
        "roteador", "visita tecnica",
    }
    if q in generic and not contains_any(q, services):
        return result(LocalAnswer(AMBIGUOUS, "", "ambiguous"))

    price_words = {"quanto custa", "preco", "valor", "quanto pago"}
    deadline_words = {"prazo", "quanto tempo", "demora", "duracao"}

    if "diagnostico" in q:
        if contains_any(q, price_words):
            return result(LocalAnswer(
                "O diagnóstico de computador custa R$ 80,00.",
                "Diagnóstico de computador: preço de R$ 80,00.",
            ))
        if contains_any(q, deadline_words):
            return result(LocalAnswer(
                "O prazo do diagnóstico é de até 2 dias úteis.",
                "Prazo: até 2 dias úteis.",
            ))
        if contains_any(q, {"descontado", "aprovar", "reparo"}):
            return result(LocalAnswer(
                "O valor do diagnóstico é descontado do total quando o reparo é aprovado.",
                "O valor é descontado do total quando o reparo é aprovado.",
            ))

    if contains_any(q, {"formatacao", "formatar"}):
        if contains_any(q, price_words):
            return result(LocalAnswer(
                "A formatação e instalação do sistema custa R$ 180,00.",
                "Formatação e instalação do sistema: preço de R$ 180,00.",
            ))
        if contains_any(q, deadline_words):
            return result(LocalAnswer(
                "O prazo da formatação e instalação do sistema é de 2 dias úteis.",
                "Prazo de 2 dias úteis.",
            ))
        if "licenca" in q:
            return result(LocalAnswer(
                "A licença do sistema não está incluída.",
                "A licença do sistema não está incluída.",
            ))
        if contains_any(q, {"copia", "arquivos", "backup"}):
            return result(LocalAnswer(
                "A cópia dos arquivos deve ser solicitada antes do início do serviço.",
                "A cópia de arquivos deve ser solicitada antes do início.",
            ))

    if "limpeza" in q:
        if contains_any(q, price_words):
            return result(LocalAnswer(
                "A limpeza interna custa R$ 120,00.",
                "Limpeza interna: preço de R$ 120,00.",
            ))
        if contains_any(q, deadline_words):
            return result(LocalAnswer(
                "O prazo da limpeza interna é de 1 dia útil.",
                "Prazo de 1 dia útil.",
            ))
        if contains_any(q, {"troca", "componente", "peca"}):
            return result(LocalAnswer(
                "A troca de componentes não está incluída na limpeza interna.",
                "A troca de componentes não está incluída.",
            ))

    if contains_any(q, {"rede", "wifi", "roteador"}):
        if contains_any(q, price_words):
            return result(LocalAnswer(
                "A configuração da rede sem fio custa R$ 150,00.",
                "Configuração de rede sem fio: preço de R$ 150,00.",
            ))
        if contains_any(q, deadline_words):
            return result(LocalAnswer(
                "A configuração da rede sem fio dura até 2 horas.",
                "Duração de até 2 horas.",
            ))
        if contains_any(q, {"dispositivo", "dispositivos", "quantos"}):
            return result(LocalAnswer(
                "A configuração inclui a conexão de até cinco dispositivos.",
                "Conexão de até cinco dispositivos.",
            ))
        if contains_any(q, {"incluido", "equipamento"}):
            return result(LocalAnswer(
                "O roteador e outros equipamentos não estão incluídos.",
                "Equipamentos não estão incluídos.",
            ))

    if "visita" in q:
        if contains_any(q, price_words):
            return result(LocalAnswer(
                "A visita técnica custa R$ 100,00.",
                "Visita técnica: preço de R$ 100,00.",
            ))
        if contains_any(q, deadline_words):
            return result(LocalAnswer(
                "A visita técnica tem duração de até 1 hora.",
                "Duração de até 1 hora.",
            ))

    if contains_any(q, {"horario", "atendimento", "sabado", "domingo", "feriado"}):
        if "sabado" in q and contains_any(q, {"tarde", "apos 12", "depois do meio dia"}):
            return result(LocalAnswer(
                "Não. Aos sábados, o atendimento ocorre das 8h às 12h.",
                "Sábados, das 8h às 12h.",
            ))
        if contains_any(q, {"domingo", "feriado"}):
            return result(LocalAnswer(
                "Não há atendimento aos domingos e feriados.",
                "Não há atendimento aos domingos e feriados.",
            ))
        if "horario" in q or "atendimento" in q:
            return result(LocalAnswer(
                "O atendimento ocorre de segunda a sexta, das 8h às 18h, e aos sábados, das 8h às 12h.",
                "Segunda a sexta-feira, das 8h às 18h. Sábados, das 8h às 12h.",
            ))

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
        return result(LocalAnswer(
            "Os serviços possuem garantia de 30 dias.",
            "Os serviços possuem garantia de 30 dias.",
        ))

    if contains_any(q, {"campinas", "fora de sao paulo"}):
        return result(LocalAnswer(
            "A empresa atende somente no município de São Paulo.",
            "A empresa atende somente no município de São Paulo.",
        ))

    return None
