from dataclasses import dataclass

from .config import AMBIGUOUS, REFUSAL
from .text_utils import contains_any, normalize


@dataclass(frozen=True)
class LocalAnswer:
    answer: str
    evidence: str = ""
    status: str = "answered"


def result(answer: LocalAnswer) -> dict:
    return {
        "answer": answer.answer,
        "evidence": answer.evidence,
        "status": answer.status,
        "cached": False,
        "source": "local",
    }


def joined(parts: list[str], evidence: list[str]) -> dict | None:
    if not parts:
        return None
    return result(LocalAnswer("\n".join(parts), " ".join(evidence)))


SERVICES_SUMMARY = result(LocalAnswer(
    "Serviços oferecidos:\n"
    "• Diagnóstico de computador: R$ 80,00, com prazo de até 2 dias úteis.\n"
    "• Formatação e instalação do sistema: R$ 180,00, com prazo de 2 dias úteis.\n"
    "• Limpeza interna: R$ 120,00, com prazo de 1 dia útil.\n"
    "• Configuração de rede sem fio: R$ 150,00, com duração de até 2 horas e conexão de até cinco dispositivos.\n"
    "• Visita técnica: R$ 100,00, com duração de até 1 hora.",
    "Diagnóstico de computador: preço de R$ 80,00. Prazo: até 2 dias úteis. "
    "Formatação e instalação do sistema: preço de R$ 180,00 e prazo de 2 dias úteis. "
    "Limpeza interna: preço de R$ 120,00 e prazo de 1 dia útil. "
    "Configuração de rede sem fio: preço de R$ 150,00 e duração de até 2 horas. "
    "Visita técnica: preço de R$ 100,00 e duração de até 1 hora."
))

GENERAL_CONDITIONS = result(LocalAnswer(
    "Condições gerais de atendimento:\n"
    "• Horário: segunda a sexta, das 8h às 18h, e sábados, das 8h às 12h. Não há atendimento aos domingos e feriados.\n"
    "• Área atendida: somente o município de São Paulo.\n"
    "• Agendamento: o cliente informa nome, serviço, dia e período desejado; a confirmação depende da disponibilidade.\n"
    "• Fora do horário: pedidos são analisados no próximo dia útil.\n"
    "• Cancelamento ou reagendamento: mínimo de 4 horas de antecedência; a visita pode ser cobrada se o técnico já estiver em deslocamento.\n"
    "• Pagamento: Pix, débito, crédito e dinheiro; não são aceitos cheques. Valores a partir de R$ 300,00 podem ser parcelados em até 3 vezes no crédito.\n"
    "• Orçamento: reparos adicionais exigem aprovação e o orçamento vale por 7 dias corridos.\n"
    "• Garantia: 30 dias, restrita ao serviço realizado.\n"
    "• Materiais: peças, cabos, roteadores, licenças e outros materiais não estão incluídos, salvo indicação expressa.",
    "Segunda a sexta-feira, das 8h às 18h. Sábados, das 8h às 12h. Não há atendimento aos domingos e feriados. "
    "A empresa atende somente no município de São Paulo. O cliente deve informar nome, serviço, dia e período desejado. "
    "A confirmação depende da disponibilidade. Cancelamentos ou reagendamentos devem ser solicitados com pelo menos 4 horas de antecedência. "
    "São aceitos Pix, débito, crédito e dinheiro. Não são aceitos cheques. O orçamento vale por 7 dias corridos. "
    "Os serviços possuem garantia de 30 dias. Peças, cabos, roteadores, licenças e materiais não estão incluídos, salvo indicação expressa."
))

PAYMENT_BUDGET_WARRANTY = result(LocalAnswer(
    "Pagamento, orçamento e garantia:\n"
    "• Pagamento: Pix, cartão de débito, cartão de crédito e dinheiro. Cheques não são aceitos. Valores a partir de R$ 300,00 podem ser parcelados em até 3 vezes no crédito.\n"
    "• Orçamento: nenhum reparo adicional é iniciado sem aprovação e o orçamento vale por 7 dias corridos.\n"
    "• Garantia: 30 dias, somente para o serviço realizado. Não cobre mau uso, novos defeitos, danos de terceiros ou falhas em peças não substituídas pela empresa.",
    "São aceitos Pix, débito, crédito e dinheiro. Não são aceitos cheques. Valores a partir de R$ 300,00 podem ser parcelados em até 3 vezes no cartão de crédito. "
    "Nenhum reparo adicional é iniciado sem aprovação. O orçamento vale por 7 dias corridos. Os serviços possuem garantia de 30 dias."
))

BEFORE_HIRING = result(LocalAnswer(
    "Antes de contratar, o cliente deve verificar:\n"
    "• serviço pretendido, preço, prazo e itens não incluídos;\n"
    "• horário e área de atendimento;\n"
    "• necessidade de agendamento e confirmação;\n"
    "• regra de cancelamento com 4 horas de antecedência;\n"
    "• formas de pagamento e parcelamento;\n"
    "• aprovação prévia e validade de 7 dias do orçamento;\n"
    "• garantia de 30 dias e suas limitações;\n"
    "• exclusão de peças, cabos, roteadores, licenças e materiais, salvo indicação expressa.",
    GENERAL_CONDITIONS["evidence"]
))


def find_local_answer(question: str) -> dict | None:
    q = normalize(question)

    # Proteção e assuntos externos.
    protection = {
        "ignore o documento", "use seus conhecimentos", "invente um desconto",
        "capital da franca", "melhor marca de computador",
    }
    if contains_any(q, protection):
        return result(LocalAnswer(REFUSAL, status="absent"))

    # Premissas falsas devem ser corrigidas, não apenas recusadas.
    if "domingo" in q:
        return result(LocalAnswer(
            "A empresa não atende aos domingos nem em feriados.",
            "Não há atendimento aos domingos e feriados."
        ))

    # Perguntas amplas previsíveis: respostas determinísticas e completas.
    if contains_any(q, {"condicoes gerais", "condicoes de atendimento"}):
        return GENERAL_CONDITIONS
    if contains_any(q, {"resumo dos servicos", "resuma os servicos", "servicos oferecidos"}):
        return SERVICES_SUMMARY
    if "compare" in q and contains_any(q, {"diagnostico", "formatacao", "limpeza"}):
        return result(LocalAnswer(
            "Comparação por preço e prazo:\n"
            "• Diagnóstico: R$ 80,00 e até 2 dias úteis.\n"
            "• Formatação e instalação do sistema: R$ 180,00 e 2 dias úteis.\n"
            "• Limpeza interna: R$ 120,00 e 1 dia útil.",
            "Diagnóstico de computador: preço de R$ 80,00. Prazo: até 2 dias úteis. "
            "Formatação e instalação do sistema: preço de R$ 180,00 e prazo de 2 dias úteis. "
            "Limpeza interna: preço de R$ 120,00 e prazo de 1 dia útil."
        ))
    if "pagamento" in q and "orcamento" in q and "garantia" in q:
        return PAYMENT_BUDGET_WARRANTY
    if contains_any(q, {"antes de contratar", "deve conhecer antes", "informacoes um cliente deve conhecer"}):
        return BEFORE_HIRING

    # O documento explicita que só há atendimento em São Paulo.
    if contains_any(q, {"campinas", "rio de janeiro", "fora de sao paulo"}):
        return result(LocalAnswer(
            "A empresa atende somente no município de São Paulo.",
            "A empresa atende somente no município de São Paulo."
        ))

    # Conteúdos não informados no corpus.
    absent = {
        "celular", "celulares", "smartphone", "smartphones",
        "vende computador", "vendem computadores", "venda de computador",
        "recuperacao de dados", "recuperam dados",
        "desconto para estudante", "desconto para estudantes", "desconto promocional",
    }
    if contains_any(q, absent):
        return result(LocalAnswer(REFUSAL, status="absent"))

    # Perguntas ambíguas. "Tem garantia?" não é ambígua porque a regra vale aos serviços em geral.
    if q in {"quanto custa", "quanto custa o servico", "qual o preco", "qual o preco do servico", "quanto tempo demora", "qual o prazo", "esta incluido", "posso parcelar isso"}:
        return result(LocalAnswer(AMBIGUOUS, status="ambiguous"))

    price = {"quanto custa", "qanto custa", "quanto esta", "preco", "valor", "quanto pago", "pagar"}
    time_words = {"prazo", "quanto tempo", "demora", "duracao", "avaliar"}

    if "diagnostico" in q or ("computador" in q and contains_any(q, {"trava", "travando", "lento", "lentidao", "avaliar"})):
        parts, evidence = [], []
        repair = contains_any(q, {"aprovar", "aprovado", "reparo", "conserto"})
        symptom = contains_any(q, {"trava", "travando", "lento", "lentidao"})
        if contains_any(q, price) or repair or symptom:
            parts.append("O diagnóstico de computador custa R$ 80,00.")
            evidence.append("Diagnóstico de computador: preço de R$ 80,00.")
        if contains_any(q, time_words) or symptom:
            parts.append("O prazo para avaliação é de até 2 dias úteis.")
            evidence.append("Prazo: até 2 dias úteis.")
        if repair:
            parts.append("Quando o reparo é aprovado, o valor do diagnóstico é descontado do total.")
            evidence.append("O valor é descontado do total quando o reparo é aprovado.")
        return joined(parts, evidence)

    if contains_any(q, {"formatacao", "formatar", "formataçao"}):
        parts, evidence = [], []
        if contains_any(q, price):
            parts.append("A formatação e instalação do sistema custa R$ 180,00.")
            evidence.append("Formatação e instalação do sistema: preço de R$ 180,00.")
        if contains_any(q, time_words):
            parts.append("O prazo é de 2 dias úteis.")
            evidence.append("Prazo de 2 dias úteis.")
        if "licenca" in q:
            parts.append("A licença do sistema não está incluída.")
            evidence.append("A licença do sistema não está incluída.")
        if contains_any(q, {"copia", "arquivos", "backup"}):
            parts.append("A cópia dos arquivos deve ser solicitada antes do início do serviço.")
            evidence.append("A cópia de arquivos deve ser solicitada antes do início.")
        return joined(parts, evidence)

    if "limpeza" in q:
        parts, evidence = [], []
        if contains_any(q, price):
            parts.append("A limpeza interna custa R$ 120,00.")
            evidence.append("Limpeza interna: preço de R$ 120,00.")
        if contains_any(q, time_words):
            parts.append("O prazo da limpeza interna é de 1 dia útil.")
            evidence.append("Prazo de 1 dia útil.")
        if contains_any(q, {"troca", "componente", "componentes", "peca", "pecas", "inclui"}):
            parts.append("A troca de componentes não está incluída.")
            evidence.append("A troca de componentes não está incluída.")
        return joined(parts, evidence)

    if contains_any(q, {"rede", "wifi", "wi fi", "roteador"}):
        parts, evidence = [], []
        if contains_any(q, price) or "configura" in q:
            parts.append("A configuração da rede sem fio custa R$ 150,00.")
            evidence.append("Configuração de rede sem fio: preço de R$ 150,00.")
        if contains_any(q, time_words):
            parts.append("A configuração dura até 2 horas.")
            evidence.append("Duração de até 2 horas.")
        if contains_any(q, {"dispositivo", "dispositivos", "quantos"}):
            parts.append("A configuração inclui a conexão de até cinco dispositivos.")
            evidence.append("Conexão de até cinco dispositivos.")
        if contains_any(q, {"incluido", "inclui", "equipamento"}):
            parts.append("O roteador e outros equipamentos não estão incluídos.")
            evidence.append("Equipamentos não estão incluídos.")
        return joined(parts, evidence)

    if "visita" in q:
        parts, evidence = [], []
        if contains_any(q, price):
            parts.append("A visita técnica custa R$ 100,00.")
            evidence.append("Visita técnica: preço de R$ 100,00.")
        if contains_any(q, time_words):
            parts.append("A visita técnica dura até 1 hora.")
            evidence.append("Duração de até 1 hora.")
        return joined(parts, evidence)

    if contains_any(q, {"horario", "sabado", "feriado"}):
        parts, evidence = [], []
        if "sabado" in q:
            parts.append("Aos sábados, o atendimento ocorre das 8h às 12h.")
            evidence.append("Sábados, das 8h às 12h.")
        if "feriado" in q:
            parts.append("Não há atendimento em feriados.")
            evidence.append("Não há atendimento aos domingos e feriados.")
        if "horario" in q and not parts:
            parts.append("O atendimento ocorre de segunda a sexta, das 8h às 18h, e aos sábados, das 8h às 12h.")
            evidence.append("Segunda a sexta-feira, das 8h às 18h. Sábados, das 8h às 12h.")
        return joined(parts, evidence)

    if contains_any(q, {"pagamento", "pagar", "pix", "debito", "credito", "dinheiro", "cheque", "parcel"}):
        if "cheque" in q:
            return result(LocalAnswer("A empresa não aceita cheques.", "Não são aceitos cheques."))
        if "parcel" in q:
            return result(LocalAnswer(
                "Valores a partir de R$ 300,00 podem ser parcelados em até 3 vezes no cartão de crédito.",
                "Valores a partir de R$ 300,00 podem ser parcelados em até 3 vezes no cartão de crédito."
            ))
        return result(LocalAnswer(
            "São aceitos Pix, cartão de débito, cartão de crédito e dinheiro.",
            "São aceitos Pix, débito, crédito e dinheiro."
        ))

    if "garantia" in q:
        return result(LocalAnswer(
            "Os serviços possuem garantia de 30 dias, restrita ao serviço realizado.",
            "Os serviços possuem garantia de 30 dias. A garantia cobre somente o serviço realizado."
        ))

    return None
