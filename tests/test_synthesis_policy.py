import sys
import types

# Minimal document stub allows testing the pure routing policy in isolation.
document = types.ModuleType("app.document")
document.normalize = lambda text: text.lower().replace("ç", "c").replace("ã", "a").replace("á", "a").replace("é", "e")
sys.modules["app.document"] = document

from app.synthesis_policy import is_synthesis_question, synthesis_retry_prompt


def test_detects_critical_synthesis_questions():
    questions = [
        "Considerando todo o documento, quais cuidados tornam o atendimento mais seguro e transparente para o cliente?",
        "Usando apenas o documento, redija uma recomendação preventiva para uma pessoa que contratará a empresa pela primeira vez.",
        "Elabore uma orientação para evitar atrasos e custos adicionais.",
    ]
    assert all(is_synthesis_question(question) for question in questions)


def test_does_not_capture_simple_questions():
    assert not is_synthesis_question("Quanto custa o diagnóstico?")
    assert not is_synthesis_question("Qual é o horário de atendimento?")


def test_retry_prompt_requires_relational_synthesis():
    prompt = synthesis_retry_prompt("Crie uma recomendação.", "DOCUMENTO TESTE")
    assert "DOCUMENTO COMPLETO" in prompt
    assert "Não procure uma frase idêntica" in prompt
    assert 'status "answered"' in prompt
