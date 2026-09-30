# Procedimento antes da publicação

1. Preserve a versão atualmente publicada para permitir reversão.
2. Use os arquivos desta pasta no repositório conectado ao Render.
3. Instale `requirements-dev.txt` no ambiente local e execute `python -m app.preflight`, `python -m compileall -q app main.py`, `python -m pytest -q` e `python -m pip check`.
4. Confirme que `from main import app` funciona.
5. No Render, use o build `pip install -r requirements.txt`, o início `uvicorn main:app --host 0.0.0.0 --port $PORT` e a verificação `/health`, conforme `render.yaml`.
6. Configure `GEMINI_API_KEY` e confirme `GEMINI_MODEL`. Para o Telegram, configure `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, `PUBLIC_BASE_URL` e `TELEGRAM_USERNAME`. O endereço público deve ser HTTPS e corresponder ao serviço publicado.
7. Reinicie ou publique o serviço. Na inicialização, o código tenta registrar o webhook quando token, segredo e URL estão preenchidos.
8. Execute a matriz em `MATRIZ_TESTES_CHATBOT.md` no site e no Telegram real. Registre a URL, as respostas, o modelo e as repetições.
9. Se o site funcionar e o Telegram não responder, confira o registro do webhook e as variáveis no serviço. Uma inicialização bem-sucedida do site, sozinha, não comprova o funcionamento do Telegram.
10. Se houver regressão, restaure a versão preservada.

A validação local desta cópia está em `VALIDACAO_LOCAL.md`. Nenhuma publicação foi realizada nesta etapa. A disponibilidade contínua depende da hospedagem escolhida e precisa de verificação após implantação.
