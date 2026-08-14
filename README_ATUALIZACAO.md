# Atualização estável v3

Substitua:
- `app/config.py`
- `app/document.py`
- `app/cache.py`
- `app/rate_limit.py`
- `app/gemini_service.py`
- `app/prompt.py`
- `app/routes/web.py`
- `app/routes/telegram.py`

Adicione:
- `app/knowledge_engine.py`
- `tests/test_engine.py`
- `tests/test_retry_cache_rate.py`

Principais mudanças:
- respostas locais extraídas dinamicamente do `instrucoes.rtf`;
- composição de múltiplos tópicos sem parar na primeira correspondência;
- retry automático curto para 429/503/504;
- falhas da API não contam no limite local;
- cache versionado e sem erros;
- testes de reformulações inéditas e perguntas compostas.

Commit: `Aplicar arquitetura estável v3`
Depois: `Clear build cache & deploy` no Render.
