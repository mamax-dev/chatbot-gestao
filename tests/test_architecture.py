from app.query_analysis import analyze
from app.knowledge_engine import answer_from_text
DOC='''Diagnóstico: R$ 80,00.\nAgendamento: informe nome e dia.\nCancelamento: 4 horas; deslocamento pode ser cobrado.\nOrçamento: aprovação obrigatória; validade 7 dias.\nGarantia: 30 dias.\nFormatação: cópia de arquivos antes do início.\nMateriais não incluídos.'''
def test_complex_never_partial_local():
    for q in ['Quais medidas evitam cobranças extras e problemas com arquivos?','Explique por que aprovação e validade são importantes','Prepare orientação relacionando agendamento, cancelamento, orçamento e garantia']:
        assert answer_from_text(q,DOC) is None
def test_simple_stays_local():
    assert answer_from_text('Quanto custa o diagnóstico?',DOC) is not None
def test_required_topics_are_detected():
    a=analyze('Explique agendamento, cancelamento, orçamento e garantia')
    assert {'agendamento','cancelamento','orcamento','garantia'}.issubset(a.topics)
