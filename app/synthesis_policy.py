from .document import normalize

SYNTHESIS_TERMS = {
    "considere todo o documento",
    "considerando todo o documento",
    "usando apenas o documento",
    "com base em todo o documento",
    "redija",
    "elabore",
    "sintese",
    "resumo geral",
    "recomendacao",
    "orientacao preventiva",
    "cuidados",
    "evitar atrasos",
    "evitar custos",
    "custos adicionais",
    "cobrancas inesperadas",
    "mais seguro",
    "mais segura",
    "transparente para o cliente",
    "primeira vez",
}


def is_synthesis_question(question: str) -> bool:
    normalized = normalize(question)
    return any(term in normalized for term in SYNTHESIS_TERMS)


def synthesis_retry_prompt(question: str, document: str) -> str:
    return f"""
DOCUMENTO COMPLETO:
---
{document}
---

PERGUNTA:
{question}

REVISÃO OBRIGATÓRIA:
A pergunta solicita uma síntese ou recomendação baseada em várias regras do documento.
Não procure uma frase idêntica à pergunta.
Relacione fatos explícitos do documento, sem criar fatos novos.
Use status "answered" quando houver regras relacionadas que permitam a síntese.
Use status "absent" somente se o documento não contiver nenhum fato relacionado.
A evidência deve copiar trechos literais que sustentem todos os pontos centrais.
""".strip()
