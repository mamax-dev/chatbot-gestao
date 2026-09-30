import asyncio

from app.service import sync_answer
from app.telegram_service import START_MESSAGE, answer_message


COMPARISON = (
    'Compare o diagnóstico de computador com a visita técnica e explique qual '
    'serviço é mais adequado para um computador com lentidão, considerando '
    'finalidade, preço e prazo.'
)
COMPARISON_REPLY = (
    'O diagnóstico de computador verifica falhas e lentidão, custa R$ 80,00 '
    'e leva até 2 dias úteis. A visita técnica oferece atendimento no local, '
    'custa R$ 100,00 e dura até 1 hora. Para investigar um computador com '
    'lentidão, o diagnóstico é o serviço mais adequado.'
)


def test_start_is_handled_as_command(monkeypatch):
    sent = []

    async def send(method, payload):
        sent.append((method, payload))

    async def unexpected_answer(question):
        raise AssertionError('/start não deve ser uma pergunta comercial')

    monkeypatch.setattr('app.telegram_service.telegram_request', send)
    monkeypatch.setattr('app.telegram_service.answer', unexpected_answer)
    asyncio.run(answer_message(123, '/start@bot_teste'))
    assert sent == [('sendMessage', {'chat_id': 123, 'text': START_MESSAGE})]


def test_open_questions_bypass_literal_faq(fake_gemini):
    fake_gemini.text = COMPARISON_REPLY
    result = sync_answer(COMPARISON)
    assert result['source'] == 'gemini'
    assert result['status'] == 'answered'
    assert len(fake_gemini.calls) == 1
    contents = fake_gemini.calls[0]['contents']
    assert '[servico:diagnostico]' in contents
    assert '[servico:visita]' in contents
    assert 'R$ 80,00' in contents and 'R$ 100,00' in contents


def test_summary_routes_to_gemini(fake_gemini):
    fake_gemini.text = (
        'A transparência aparece na aprovação prévia do orçamento, na garantia '
        'de 30 dias e no aviso sobre cancelamentos com 4 horas de antecedência.'
    )
    result = sync_answer('Resuma como a transparência aparece nas regras de atendimento.')
    assert result['source'] == 'gemini'
    assert len(fake_gemini.calls) == 1


def test_ordinary_faq_never_calls_gemini(fake_gemini):
    result = sync_answer('Quanto custa o diagnóstico?')
    assert result['source'] == 'faq' and 'R$ 80,00' in result['answer']
    assert not fake_gemini.calls
