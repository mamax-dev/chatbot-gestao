from app.input_policy import inspect_input


def test_random_short_strings_are_blocked():
    for text in ['abcd', 'afgi', 'nmgk', 'qwerty', 'zxcp']:
        decision = inspect_input(text)
        assert decision.valid is False
        assert 'pergunta' in decision.reply.lower()


def test_legitimate_short_terms_are_allowed():
    for text in ['pix', 'wifi', 'garantia', 'dinheiro', 'diagnóstico']:
        assert inspect_input(text).valid is True


def test_small_talk_is_local_and_cordial():
    examples = {
        'obrigado': 'Por nada',
        'tchau': 'Até mais',
        'ok': 'Certo',
        'oi': 'Olá',
    }
    for text, expected in examples.items():
        decision = inspect_input(text)
        assert decision.valid is False
        assert expected in decision.reply


def test_common_typo_is_corrected_without_ai():
    decision = inspect_input('quanto custa o diagnostco')
    assert decision.valid is True
    assert 'diagnostico' in decision.corrected


def test_contextual_sentence_is_not_blocked():
    assert inspect_input('me explique os cuidados antes de contratar o serviço').valid is True
