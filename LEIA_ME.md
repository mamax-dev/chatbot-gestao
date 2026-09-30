# Chatbot de gestão validado localmente

Esta cópia mantém a aparência, os cinco serviços e os dados da empresa. Inclui a segunda correção, feita após os testes no site e no Telegram: diferencia informação insuficiente de indisponibilidade da API e orienta comparações e sínteses com os dados disponíveis. Esta atualização ainda precisa ser publicada.

## Resultado desta etapa

- Suíte original: 28 testes, 23 aprovados e 5 falhas.
- Suíte após as correções: 67 testes aprovados, sem falhas ou testes ignorados.
- Preflight, compilação, importação da aplicação e verificação das dependências aprovados.
- Gemini e Telegram externos simulados nos testes de integração. A geração real e a entrega real de mensagens ainda precisam ser verificadas após configurar as credenciais e publicar.

O registro completo está em `docs/VALIDACAO_LOCAL.md`. O roteiro para a demonstração está em `docs/MATRIZ_TESTES_CHATBOT.md`.

## Executar e conferir

Na pasta do projeto, com Python 3.12:

```bash
python -m venv .venv
```

Ative o ambiente virtual. No Windows:

```powershell
.venv\Scripts\Activate.ps1
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

Instale e valide:

```bash
python -m pip install -r requirements-dev.txt
python -m app.preflight
python -m pytest -q
```

Para abrir a aplicação localmente:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

Acesse `http://127.0.0.1:8000`. As perguntas locais funcionam sem chave do Gemini; perguntas abertas recebem a mensagem de indisponibilidade até a chave ser configurada.

Para usar suas configurações locais, copie `.env.example` para `.env`, preencha os valores necessários e inicie com:

```bash
uvicorn main:app --env-file .env --host 127.0.0.1 --port 8000
```

O `.env` é carregado pelo comando acima; a aplicação não o carrega automaticamente. No Render, configure as variáveis no painel do serviço. O procedimento está em `docs/PROCEDIMENTO_DEPLOY.md`.
