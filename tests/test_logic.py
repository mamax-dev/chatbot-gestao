from app.config import AMBIGUOUS, REFUSAL
from app.gemini_service import classify_before_model


def test_generic_price_question_is_ambiguous():
    result = classify_before_model("Quanto custa o serviço?")
    assert result is not None
    assert result["status"] == "ambiguous"
    assert result["answer"] == AMBIGUOUS


def test_specific_price_question_is_not_preclassified():
    assert classify_before_model("Quanto custa o diagnóstico?") is None


def test_cellphone_question_is_absent():
    result = classify_before_model("Vocês consertam celulares?")
    assert result is not None
    assert result["status"] == "absent"
    assert result["answer"] == REFUSAL


def test_data_recovery_is_absent():
    result = classify_before_model("Vocês fazem recuperação de dados?")
    assert result is not None
    assert result["status"] == "absent"
