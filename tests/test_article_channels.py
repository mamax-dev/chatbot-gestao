import pytest

from app.business_config import load_business
from tests.test_routing import COMPARISON, COMPARISON_REPLY


ARTICLE_CASES = [
    ('O que vc fz?', 'faq', ['Diagnóstico', 'Formatação', 'Limpeza', 'rede sem fio', 'Visita técnica']),
    ('Quanto custa o diagnostco?', 'faq', ['R$ 80,00', '2 dias úteis']),
    ('Qual a gartia?', 'faq', ['30 dias']),
    ('Valor', 'faq', ['preço de um serviço', 'valores institucionais']),
    ('A empresa oferece seguro contra roubo?', 'faq', ['Não encontrei']),
    ('abcd', 'local', ['Não consegui identificar']),
]


@pytest.fixture
def telegram_sender(monkeypatch):
    sent = []

    async def send(method, payload):
        sent.append((method, payload))
        return {'ok': True}

    monkeypatch.setenv('TELEGRAM_WEBHOOK_SECRET', 'local-test-secret')
    monkeypatch.setattr('app.telegram_service.telegram_request', send)
    monkeypatch.setattr('app.routes.telegram.telegram_request', send)
    return sent


def telegram_question(client, sent, question, chat=123):
    before = len(sent)
    response = client.post(
        '/telegram/webhook',
        headers={'X-Telegram-Bot-Api-Secret-Token': 'local-test-secret'},
        json={'message': {'text': question, 'chat': {'id': chat}}},
    )
    assert response.status_code == 200 and response.json() == {'ok': True}
    assert len(sent) == before + 1
    method, payload = sent[-1]
    assert method == 'sendMessage' and payload['chat_id'] == chat
    return payload['text']


@pytest.mark.parametrize('channel', ['web', 'telegram'])
@pytest.mark.parametrize('question,source,terms', ARTICLE_CASES)
def test_article_local_cases_in_both_channels(
    channel, question, source, terms, web_client, telegram_sender, fake_gemini,
):
    if channel == 'web':
        response = web_client.post('/api/perguntar', json={'question': question})
        assert response.status_code == 200
        result = response.json()
        assert result['source'] == source
        assert not result['cached']
        text = result['answer']
    else:
        text = telegram_question(web_client, telegram_sender, question)
    assert all(term in text for term in terms)
    assert not fake_gemini.calls


@pytest.mark.parametrize('channel', ['web', 'telegram'])
def test_article_open_question_and_cache(
    channel, web_client, telegram_sender, fake_gemini,
):
    fake_gemini.text = COMPARISON_REPLY
    if channel == 'web':
        first = web_client.post('/api/perguntar', json={'question': COMPARISON}).json()
        second = web_client.post('/api/perguntar', json={'question': COMPARISON}).json()
        assert first['source'] == 'gemini' and not first['cached']
        assert second['source'] == 'cache' and second['cached']
        assert first['request_id'] != second['request_id']
        assert first['answer'] == second['answer'] == COMPARISON_REPLY
    else:
        first = telegram_question(web_client, telegram_sender, COMPARISON)
        second = telegram_question(web_client, telegram_sender, COMPARISON)
        assert first == second == COMPARISON_REPLY
    assert len(fake_gemini.calls) == 1


@pytest.mark.parametrize('channel', ['web', 'telegram'])
def test_value_clarifications(channel, web_client, telegram_sender, fake_gemini):
    for question, term in [
        ('valor', 'valores institucionais'),
        ('preço de um serviço', 'R$ 80,00'),
        ('valores institucionais da empresa', 'clareza'),
    ]:
        if channel == 'web':
            result = web_client.post('/api/perguntar', json={'question': question})
            assert result.status_code == 200
            text = result.json()['answer']
        else:
            text = telegram_question(web_client, telegram_sender, question)
        assert term in text
    assert not fake_gemini.calls


@pytest.mark.parametrize('question,term', [
    ('Quais são os valores?', 'clareza'),
    ('Quais os valores?', 'clareza'),
    ('Posso cancelar?', '4 horas'),
    ('Posso agendar?', 'disponibilidade'),
])
def test_corrected_short_faqs(question, term, web_client, fake_gemini):
    response = web_client.post('/api/perguntar', json={'question': question})
    assert response.status_code == 200
    assert response.json()['source'] == 'faq'
    assert term in response.json()['answer']
    assert not fake_gemini.calls


def test_home_assets_and_health(web_client):
    assert web_client.get('/health').json() == {'status': 'ok'}
    page = web_client.get('/')
    assert page.status_code == 200
    assert 'id="form"' in page.text and '/static/app.js' in page.text
    for path in ['app.js', 'style.css', 'ai-bot.json', 'hero-support.png', 'hero-support.mp4']:
        response = web_client.get('/static/' + path)
        assert response.status_code == 200 and response.content


@pytest.mark.parametrize('question', ['', 'a', 'x' * 501])
def test_web_rejects_invalid_lengths(question, web_client):
    assert web_client.post('/api/perguntar', json={'question': question}).status_code == 422


@pytest.mark.parametrize('secret,header', [(None, None), ('local-test-secret', None), ('local-test-secret', 'wrong')])
def test_telegram_rejects_missing_or_wrong_secret(secret, header, web_client, monkeypatch):
    if secret is None:
        monkeypatch.delenv('TELEGRAM_WEBHOOK_SECRET', raising=False)
    else:
        monkeypatch.setenv('TELEGRAM_WEBHOOK_SECRET', secret)
    headers = {'X-Telegram-Bot-Api-Secret-Token': header} if header else {}
    response = web_client.post('/telegram/webhook', headers=headers, json={})
    assert response.status_code == 403


def test_telegram_rate_limit(web_client, telegram_sender):
    from app.telegram_service import START_MESSAGE
    for _ in range(8):
        assert telegram_question(web_client, telegram_sender, '/start') == START_MESSAGE
    assert 'Aguarde' in telegram_question(web_client, telegram_sender, '/start')


@pytest.mark.parametrize('failure', ['api_error', 'unsupported_money'])
def test_failed_generation_is_not_cached(failure, web_client, fake_gemini):
    if failure == 'api_error':
        fake_gemini.error = RuntimeError('API indisponível')
    elif failure == 'unsupported_money':
        fake_gemini.text = 'O diagnóstico custa R$ 999,00 e a visita técnica custa R$ 100,00.'
    for _ in range(2):
        result = web_client.post('/api/perguntar', json={'question': COMPARISON}).json()
        assert result['source'] == 'fallback' and result['status'] == 'failed'
        assert 'temporariamente indisponível' in result['answer']
        assert not result['cached']
    assert len(fake_gemini.calls) == 2


@pytest.mark.parametrize('channel', ['web', 'telegram'])
def test_insufficient_context_is_absent_not_api_failure(
    channel, web_client, telegram_sender, fake_gemini, caplog,
):
    question = 'Por favor, resuma como a transparência aparece nas regras de atendimento.'
    fake_gemini.text = 'INFORMAÇÃO INSUFICIENTE.'
    for _ in range(2):
        if channel == 'web':
            response = web_client.post('/api/perguntar', json={'question': question})
            assert response.status_code == 200
            result = response.json()
            assert result['source'] == 'fallback' and result['status'] == 'absent'
            assert not result['cached']
            text = result['answer']
        else:
            text = telegram_question(web_client, telegram_sender, question)
        assert text == load_business()['conversa']['informacao_ausente']
        assert 'temporariamente indisponível' not in text
    assert len(fake_gemini.calls) == 2
    assert 'GeminiError' not in caplog.text
