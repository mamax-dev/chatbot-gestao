from app.knowledge_engine import answer_from_text

DOC="""
MISSÃO
A missão da Solução Prática é simplificar o suporte técnico, oferecendo atendimento claro, acessível e confiável.
VISÃO
A visão da Solução Prática é ser reconhecida pela praticidade, transparência e qualidade no atendimento tecnológico.
VALORES
Os valores da Solução Prática são clareza, respeito, confiança, responsabilidade e compromisso com o cliente.
SERVIÇOS
Diagnóstico de computador: preço de R$ 80,00 e prazo de até 2 dias úteis.
Formatação e instalação do sistema: preço de R$ 180,00 e prazo de 2 dias úteis.
Limpeza interna: preço de R$ 120,00 e prazo de 1 dia útil.
Configuração de rede sem fio: preço de R$ 150,00 e duração de até 2 horas.
Visita técnica: preço de R$ 100,00 e duração de até 1 hora.
"""

def answer(q):
    item=answer_from_text(q,DOC)
    assert item is not None
    return item["answer"]

def test_mission():
    assert "simplificar o suporte técnico" in answer("Qual é a missão da empresa?")

def test_vision_and_values():
    text=answer("Qual é a visão e quais são os valores?")
    assert "praticidade" in text and "clareza" in text

def test_what_company_does():
    text=answer("O que a empresa faz?")
    for expected in ["Diagnóstico","Formatação","Limpeza","rede sem fio","Visita técnica"]:
        assert expected.lower() in text.lower()
