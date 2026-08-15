from app.service import sync_answer

def answer(q):return sync_answer(q)['answer']
def test_social():
    for q,term in [('Oi','Que bom'),('Obrigado','Por nada'),('Tchau','Até mais'),('Ok','Certo')]:assert term in answer(q)
def test_company_variants():
    values=[answer(q) for q in ['O que a empresa faz?','O que vocês fazem?','O que você faz?','O que vcs fazem?']]
    assert len(set(values))==1 and 'Diagnóstico' in values[0]
def test_services():
    cases=[('Quanto custa o diagnostco?','R$ 80,00'),('Quanto custa a formatação?','R$ 180,00'),('Quanto custa a limpeza?','R$ 120,00'),('Quanto custa configurar o Wi-Fi?','R$ 150,00'),('Quanto custa a visita técnica?','R$ 100,00')]
    for q,term in cases:assert term in answer(q)
def test_payment_and_hours():
    assert 'até 3 vezes' in answer('Aceita dinheiro e parcelamento?')
    result=answer('Qual é o horário de sábado? Atendem domingo?');assert '8h às 12h' in result and 'não há atendimento' in result
def test_identity():
    assert 'Simplificar' in answer('Qual é a missão?');assert 'praticidade' in answer('Qual é a visão?');assert 'clareza' in answer('Quais são os valores?')
def test_policies():
    assert '4 horas' in answer('Posso cancelar?');assert '7 dias' in answer('Qual a validade do orçamento?');assert '30 dias' in answer('Qual é a garantia?')
def test_noise():
    for q in ['aaa','abcd','afgi','nmgk','!!!']:assert 'identificar' in answer(q)
def test_absent():
    for q in ['Vocês vendem celulares?','Fazem recuperação de dados?','A empresa oferece seguro contra roubo?']:assert 'Não encontrei' in answer(q)
def test_handoff():assert 'simulada' in answer('Quero falar com atendente')
def test_open_question_without_key_is_graceful(monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY',raising=False)
    assert 'temporariamente indisponível' in answer('Resuma como a transparência aparece nas regras de atendimento.')
