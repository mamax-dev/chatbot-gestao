from app.config import AMBIGUOUS, REFUSAL
from app.knowledge_engine import answer_from_text

DOC = """
Atendimento: de segunda a sexta-feira, das 8h às 18h, e aos sábados, das 8h às 12h.
A empresa não realiza atendimento aos domingos e feriados.
A empresa atende somente no município de São Paulo.
Diagnóstico de computador: verifica falhas, lentidão e travamentos. Preço: R$ 80,00. Prazo: até 2 dias úteis. O valor é descontado quando o reparo é aprovado.
Formatação e instalação do sistema: preço de R$ 180,00 e prazo de 2 dias úteis. A licença não está incluída. A cópia de arquivos deve ser solicitada antes do início.
Limpeza interna: preço de R$ 120,00 e prazo de 1 dia útil. A troca de componentes não está incluída.
Configuração de rede sem fio: preço de R$ 150,00, duração de até 2 horas e conexão de até cinco dispositivos. Equipamentos não estão incluídos.
Visita técnica: preço de R$ 100,00 e duração de até 1 hora. Se o técnico já estiver em deslocamento, a visita poderá ser cobrada.
Agendamento: o cliente deve informar nome, serviço, dia e período desejado. A confirmação depende da disponibilidade.
Cancelamentos ou reagendamentos devem ser solicitados com pelo menos 4 horas de antecedência.
São aceitos Pix, débito, crédito e dinheiro. Não são aceitos cheques. Valores a partir de R$ 300,00 podem ser parcelados em até 3 vezes no cartão de crédito.
Nenhum reparo adicional é iniciado sem aprovação. O orçamento vale por 7 dias corridos.
Os serviços possuem garantia de 30 dias. A garantia cobre somente o serviço realizado.
Peças, cabos, roteadores, licenças e materiais não estão incluídos, salvo indicação expressa.
"""


def answer(question):
    return answer_from_text(question, DOC)


def assert_contains(question, *parts):
    item = answer(question)
    assert item is not None, question
    text = item["answer"].lower()
    for part in parts:
        assert part.lower() in text, (question, part, item["answer"])


def test_unseen_reformulations_and_compound_intents():
    assert_contains("Em que período vocês trabalham no sábado? Também abrem domingo?", "8h às 12h", "domingos")
    assert_contains("Quanto fica para analisar um computador e quando recebo o resultado?", "R$ 80,00", "2 dias úteis")
    assert_contains("Quero formatar e preservar meus documentos. O que preciso solicitar?", "R$ 180,00", "cópia de arquivos")
    assert_contains("Posso dividir uma cobrança de 350 reais?", "3 vezes")
    assert_contains("O técnico já saiu e eu quero cancelar. Pode haver cobrança?", "deslocamento", "cobrada")
    assert_contains("Informe preço, prazo e itens não incluídos na instalação do sistema.", "R$ 180,00", "2 dias úteis", "licença")
    assert_contains("Quais serviços existem, quanto custam e quanto tempo levam?", "R$ 80,00", "R$ 180,00", "R$ 120,00", "R$ 150,00", "R$ 100,00")
    assert_contains("Explique agendamento, cancelamento, pagamento e garantia.", "nome", "4 horas", "Pix", "30 dias")


def test_contradictions_and_absence():
    assert_contains("A empresa atende aos domingos, certo?", "domingos")
    assert_contains("A licença já está incluída nos R$ 180,00?", "não está incluída")
    assert_contains("Posso pagar com cheque?", "não são aceitos cheques")
    assert_contains("A visita técnica dura o dia inteiro?", "1 hora")
    assert answer("Qual é a capital da França?")["answer"] == REFUSAL


def test_ambiguity():
    assert answer("Quanto custa o serviço?")["answer"] == AMBIGUOUS
