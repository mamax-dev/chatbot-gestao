from app.service import sync_answer
from app.policy import local_reply

def test_noise():
    for x in ['aaa','abcd','afgi','nmgk','!!!']:assert local_reply(x)
def test_social():
    for x in ['oi','obrigado','tchau','ok']:assert local_reply(x)
def test_company_variants_same():
    values=[sync_answer(x)['answer'] for x in ['O que vocês fazem?','O que vcs fazem?','O que a empresa faz?']]
    assert len(set(values))==1
def test_simple_faq():
    assert 'R$ 80,00' in sync_answer('Quanto custa o diagnostco?')['answer']
    assert 'Pix' in sync_answer('dinheiro')['answer']
def test_same_core_for_channels():
    assert sync_answer('Qual é a missão?')['answer']==sync_answer('Qual é a missão?')['answer']
