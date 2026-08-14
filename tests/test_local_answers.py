from app.config import AMBIGUOUS, REFUSAL
from app.local_answers import find_local_answer


def test_diagnostic_price_local():
    result = find_local_answer("Quanto custa o diagnóstico?")
    assert result["answer"] == "O diagnóstico de computador custa R$ 80,00."
    assert result["source"] == "local"


def test_formatting_with_typo_local():
    result = find_local_answer("Qanto custa a formataçao?")
    assert "R$ 180,00" in result["answer"]


def test_ambiguous_local():
    result = find_local_answer("Quanto custa o serviço?")
    assert result["answer"] == AMBIGUOUS


def test_absent_local():
    result = find_local_answer("Vocês consertam celulares?")
    assert result["answer"] == REFUSAL


def test_unknown_uses_model():
    assert find_local_answer("Explique as condições completas do atendimento") is None
