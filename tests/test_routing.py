from pathlib import Path


def test_start_is_handled_as_command():
    source = Path("app/telegram_service.py").read_text(encoding="utf-8")
    assert '== "/start"' in source
    assert "START_MESSAGE" in source


def test_open_questions_bypass_literal_faq():
    source = Path("app/service.py").read_text(encoding="utf-8")
    assert "if is_open_question(question):" in source
    assert source.index("if is_open_question(question):") < source.index("faq = lookup(question)")
    for marker in ["explique", "resuma", "compare", "por que"]:
        assert marker in source
