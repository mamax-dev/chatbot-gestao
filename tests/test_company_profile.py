from app.knowledge_engine import answer_from_text

DOC = """
Empresa fictícia: Solução Prática Serviços. Conteúdo criado exclusivamente para testes acadêmicos.
MISSÃO
A missão da Solução Prática é simplificar o suporte técnico, oferecendo atendimento claro, acessível e confiável.
VISÃO
A visão da Solução Prática é ser reconhecida pela praticidade, transparência e qualidade no atendimento tecnológico.
VALORES
Os valores da Solução Prática são clareza, respeito, confiança, responsabilidade e compromisso com o cliente.
SERVIÇOS
Diagnóstico de computador: preço de R$ 80,00.
Formatação e instalação do sistema: preço de R$ 180,00.
Limpeza interna: preço de R$ 120,00.
Configuração de rede sem fio: preço de R$ 150,00.
Visita técnica: preço de R$ 100,00.
"""

def answer(question):
    result = answer_from_text(question, DOC)
    assert result is not None
    return result["answer"].lower()

def test_who_is_company_is_complete():
    text = answer("Quem é a empresa?")
    assert "solução prática serviços" in text
    assert "simplificar o suporte técnico" in text
    assert "diagnóstico" in text

def test_what_company_does_formal():
    text = answer("O que a empresa faz?")
    for term in ["diagnóstico", "formatação", "limpeza", "rede sem fio", "visita técnica"]:
        assert term in text

def test_what_company_does_informal():
    text = answer("O que vc fazem")
    assert "diagnóstico" in text
    assert "visita técnica" in text

def test_other_variations():
    for question in ["Quem são vocês?", "O que vcs fazem?", "Qual é a atividade da empresa?"]:
        assert answer_from_text(question, DOC) is not None
