from app.input_policy import inspect_input
from app.fallback import build_document_fallback
from app.response_style import style_result
DOC='''AGENDAMENTO
Informe nome, serviço, dia e período. A confirmação depende da disponibilidade.
CANCELAMENTO E REAGENDAMENTO
Cancele com 4 horas de antecedência. Em deslocamento, a visita pode ser cobrada.
PAGAMENTO E ORÇAMENTO
O orçamento vale 7 dias. Reparos extras exigem aprovação.
GARANTIA E MATERIAIS
A garantia é de 30 dias. Cobre somente o serviço realizado.
'''
Q='Prepare uma orientação relacionando agendamento, cancelamento, orçamento e garantia.'
def test_input_protection():
    for x in ['oi','a','aaaa','!!!','x'*501]:assert not inspect_input(x).valid
def test_same_answer_both_channels():
    r=build_document_fallback(Q,DOC);assert style_result(r,'web')['answer']==style_result(r,'telegram')['answer']
def test_complete_and_short():
    a=style_result(build_document_fallback(Q,DOC))['answer']
    for x in ['Agendamento:','Cancelamento:','Orçamento:','Garantia:']:assert x in a
    assert len(a)<800
