import json
from pathlib import Path

import pytest

from app.business_config import load_business
from app.faq import lookup
from app.text import normalize


def answer(question):
    result = lookup(question)
    assert result is not None
    return result['answer']


def test_price_list_variations():
    for question in ['preço', 'preços', 'quais os preços', 'tabela de preços', 'quanto custam os serviços', 'preço de um serviço']:
        text = answer(question)
        for expected in ['R$ 80,00', 'R$ 180,00', 'R$ 120,00', 'R$ 150,00', 'R$ 100,00']:
            assert expected in text


def test_service_list_variations():
    for question in ['serviços', 'quais serviços', 'o que vocês oferecem', 'o que vc fz']:
        text = answer(question)
        assert 'Diagnóstico' in text and 'Visita técnica' in text


def test_value_disambiguation():
    assert 'preço de um serviço' in answer('valor')
    assert 'clareza' in answer('valores')
    assert 'clareza' in answer('princípios da empresa')
    assert 'clareza' in answer('valores institucionais da empresa')
    assert 'R$ 80,00' in answer('valor do diagnóstico')


def test_budget_is_not_institutional_values():
    text = answer('Qual a validade do orçamento?')
    assert '7 dias' in text
    assert 'clareza' not in text


def test_common_aliases():
    assert normalize('o que vc fz') == 'o que voces faz'
    assert normalize('qto custa o diagnostco') == 'quanto custa o diagnostico'
    assert normalize('qual a gartia') == 'qual a garantia'


