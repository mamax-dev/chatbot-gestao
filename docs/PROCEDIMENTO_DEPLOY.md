# Procedimento obrigatório antes do deploy
1. Preserve uma cópia do commit atual.
2. Execute `python -m app.preflight`.
3. Execute `python -m py_compile $(find app -name '*.py')`.
4. Execute `pytest -q`.
5. Confirme que `from main import app` funciona.
6. Faça o deploy somente se todas as etapas passarem.
7. Após o deploy, teste FAQ, pergunta complexa e repetição para cache.
8. Se houver regressão, reverta para o commit preservado.
