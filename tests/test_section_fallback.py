from app.document import sections_from_text
from app.knowledge_engine import answer_from_text, select
from app.query_analysis import TOPICS
from app.fallback import build_document_fallback

DOC = """IDENTIDADE INSTITUCIONAL
A empresa fictícia é a Solução Prática.
SERVIÇOS
Diagnóstico de computador: R$ 80,00.
Formatação e instalação do sistema: R$ 180,00.
Limpeza interna: R$ 120,00.
Configuração de rede sem fio: R$ 150,00.
Visita técnica: R$ 100,00.
AGENDAMENTO
O cliente deve informar nome, serviço, dia e período desejado. A confirmação depende da disponibilidade.
CANCELAMENTO E REAGENDAMENTO
Cancelamentos devem ser solicitados com pelo menos 4 horas de antecedência. Se o técnico já estiver em deslocamento, a visita poderá ser cobrada.
PAGAMENTO E ORÇAMENTO
Nenhum reparo adicional é iniciado sem aprovação. O orçamento vale por 7 dias corridos.
GARANTIA E MATERIAIS
Os serviços possuem garantia de 30 dias. Peças e materiais não estão incluídos.
"""

def test_sections_keep_heading_content_together():
    sections = dict(sections_from_text(DOC))
    assert sections['AGENDAMENTO'][0].startswith('O cliente deve informar')

def test_fallback_contains_all_requested_section_content():
    result = build_document_fallback('Prepare uma orientação relacionando agendamento, cancelamento, orçamento e garantia.', DOC)
    text = result['answer']
    for expected in ['nome, serviço, dia', '4 horas', '7 dias corridos', 'garantia de 30 dias']:
        assert expected in text

def test_company_activity_excludes_policy_sections():
    result = answer_from_text('O que vc fazem?', DOC)
    text = result['answer']
    assert 'Diagnóstico' in text and 'Visita técnica' in text
    assert 'Cancelamentos' not in text and 'garantia de 30 dias' not in text

def test_heading_is_never_returned_alone():
    blocks = select(DOC, TOPICS['agendamento'])
    assert blocks == ['O cliente deve informar nome, serviço, dia e período desejado. A confirmação depende da disponibilidade.']
