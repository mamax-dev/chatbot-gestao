from app.input_policy import inspect_input
from app.response_style import style_result, FRIENDLY_NOT_FOUND
from app.knowledge_engine import answer_from_text

DOC='''SERVIÇOS
Diagnóstico: R$ 80,00.
PAGAMENTO E ORÇAMENTO
São aceitos Pix, cartão de débito, cartão de crédito e dinheiro.
'''
def test_greetings_and_noise_do_not_reach_ai():
    for text in ['oi','olá','a','aaaaaa','!!!']:
        assert not inspect_input(text).valid

def test_long_input_is_rejected_early():
    assert not inspect_input('x'*501).valid

def test_friendly_absence():
    styled=style_result({'answer':'x','status':'absent','evidence':'','source':'fallback'})
    assert styled['answer']==FRIENDLY_NOT_FOUND

def test_payment_answers_are_short_and_cordial():
    assert answer_from_text('é grátis?',DOC)['answer'].startswith('Os serviços são pagos')
    assert answer_from_text('dinheiro',DOC)['answer'].startswith('Sim.')

def test_telegram_style_caps_block_dump():
    r={'answer':'Informações relacionadas:\n• Um.\n• Dois.\n• Três.\n• Quatro.','status':'answered','evidence':'x','source':'fallback'}
    assert 'Quatro' not in style_result(r,'telegram')['answer']
