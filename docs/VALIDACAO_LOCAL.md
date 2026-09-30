# Registro de validação local do chatbot

Data da validação: 30 de setembro de 2026.

## Conclusão e alcance

O projeto passou nos 65 testes automatizados executados após as correções. A validação abrangeu as regras locais, o roteamento generativo, a seleção de contexto, a validação de respostas, o cache, as rotas HTTP da página web e do webhook do Telegram. As integrações externas foram simuladas de forma controlada.

Este resultado não comprova a disponibilidade pública 24 horas, a resposta real do Gemini nem o envio real pelo Telegram. Esses pontos dependem da implantação, das credenciais e dos serviços externos. O navegador de uma pessoa externa e a aparência em celular também precisam de conferência após a publicação.

Os documentos acadêmicos enviados foram usados para definir os casos de teste e não foram alterados nesta etapa.

## Linha de base e correções

A suíte do ZIP original foi executada neste ambiente: 28 testes, 23 aprovados e 5 falhas.

| Falha observada | Correção realizada |
| --- | --- |
| “Quais são os valores?” chegava ao Gemini | A FAQ passou a reconhecer essa expressão e “Quais os valores?” como valores institucionais, preservando as expressões específicas de preços e o esclarecimento para “valor”. |
| “Posso cancelar?” era recusada como entrada inválida | Os verbos “cancelar” e “agendar” passaram a integrar o vocabulário reconhecido pela triagem local. As políticas existentes fornecem a resposta. |
| Um teste cobrava esquema JSON e retentativas de uma versão anterior | Substituído por testes do contexto delimitado, modelo configurado, limite de tokens e encerramento do cliente, inclusive após erro. Não foram adicionadas retentativas. |
| Um teste cobrava um arquivo de instrução inexistente no ZIP | Substituído pela verificação da existência do vídeo e da referência no HTML. |
| Um teste cobrava literalmente um nome antigo de função | Substituído por testes que observam se perguntas abertas chegam à integração generativa e se a FAQ evita chamadas externas. |

A revisão também identificou uma falha na autorização do webhook: sem segredo configurado e sem cabeçalho, a comparação de dois valores ausentes aceitava a requisição. Agora o webhook exige um segredo configurado e o cabeçalho correspondente. Os testes cobrem segredo ausente, cabeçalho ausente, valor incorreto e requisição válida.

Os mocks antigos trocavam módulos inteiros e podiam deixar importações simuladas disponíveis a outros testes. Os testes atuais simulam somente o cliente externo e isolam o cache entre os casos.

Arquivos originais de aplicação alterados: `app/faq.py`, `app/conversation.py` e `app/routes/telegram.py`. Os arquivos de `static/`, `templates/` e `data/` foram comparados com o ZIP original e permanecem idênticos em bytes.

## Execução e critérios

Cada caso automatizado da suíte final foi executado uma vez na execução aprovada. Os testes de cache fazem duas solicitações iguais dentro do mesmo caso; o teste de limite do Telegram faz nove solicitações. Há casos parametrizados separados para web e Telegram. Os resultados automatizados não representam o histórico de repetição dos testes apresentados no artigo.

Os resultados esperados foram definidos a partir do Quadro 1 do artigo, das funcionalidades descritas no relatório e dos dados de `data/empresa.json`. A aprovação nesta etapa é determinada por asserções automatizadas sobre resposta, origem, estado, número de chamadas, reutilização e códigos HTTP.

Nos testes de integração generativa, o cliente da API é substituído por um simulador. Uma resposta de comparação previamente definida contém o diagnóstico a R$ 80,00, prazo de até dois dias úteis, visita a R$ 100,00 e duração de até uma hora. Isso permite verificar o processamento da resposta e a reutilização sem consumir a API. A capacidade real do modelo de produzir essa comparação não foi avaliada nesta execução.

O cliente HTTP de testes executa a aplicação FastAPI real. No Telegram, a requisição entra pela rota real do webhook e a função externa de envio é substituída por um simulador que registra a mensagem. Nenhuma mensagem foi enviada a pessoas.

## Cobertura dos oito casos do artigo

| Caso | Verificação local |
| --- | --- |
| “O que vc fz?” | Cinco serviços informados nos dois canais; nenhuma chamada generativa. |
| “Quanto custa o diagnostco?” | R$ 80,00 e dois dias úteis nos dois canais. |
| “Qual a gartia?” | Garantia de 30 dias nos dois canais. |
| “Valor” | Solicitação de escolha entre preço e valores institucionais nos dois canais; respostas às duas expressões de esclarecimento também testadas. |
| “A empresa oferece seguro contra roubo?” | Informação ausente nos dois canais. |
| “abcd” | Pedido de reformulação nos dois canais. |
| Comparação entre diagnóstico e visita técnica | Roteamento, contexto dos dois serviços e processamento da resposta simulada nos dois canais. |
| Repetição da comparação | Mesma resposta, apenas uma chamada externa simulada; indicador `cached` verificado na API web. |

Também foram testados saudação, encerramento, cinco serviços, pagamentos, horários, missão, visão, cancelamento, orçamento, garantia, transferência simulada, comando `/start`, limite de mensagens, falhas da API, respostas vazias ou truncadas, preço não sustentado pelo contexto, expiração e invalidação do cache, limites de entrada web, página inicial, arquivos estáticos e `/health`.

## Configuração observada

| Item | Valor |
| --- | --- |
| Python usado nesta validação | 3.12.14 |
| FastAPI instalado | 0.142.2 |
| Uvicorn instalado | 0.54.0 |
| google-genai instalado | 2.25.0 |
| Pydantic instalado | 2.13.5 |
| httpx instalado | 0.28.1 |
| pytest instalado | 8.4.2 |
| Modelo padrão configurado | `gemini-3.6-flash`, substituível por `GEMINI_MODEL` |
| Limite de saída enviado ao Gemini | 2048 tokens |
| Instrução de resposta | Somente o contexto; português; até quatro frases; informação insuficiente quando faltar conteúdo |
| Parâmetros de amostragem | Não definidos explicitamente pela aplicação |
| Cache | Em memória, até 256 entradas; duração padrão de 86400 segundos, ajustável por `CACHE_TTL_SECONDS` |
| Identificação do cache | Pergunta normalizada, resumo dos dados da empresa, modelo e versão interna do prompt |
| Persistência | O cache é perdido após reinício; não há banco permanente |
| Limite de Telegram | Oito mensagens por chat em janela de 60 segundos |
| Limite da pergunta web | De dois a 500 caracteres |

A versão de Python usada originalmente pelo autor para desenvolver o projeto não é identificável no ZIP. Python 3.12.14 é a versão desta validação; não deve ser apresentada como a versão histórica de desenvolvimento sem confirmação do autor.

As dependências originais usam intervalos de versões. Os números acima registram o ambiente desta execução; futuras instalações podem selecionar versões diferentes.

Normalização em `app/text.py`: converte para minúsculas, remove acentos, substitui pontuação por espaços e aplica os mapeamentos `vc/vcs/voce → voces`, `fazem/fz → faz`, `qto/qnto → quanto`, `diagnostco/diagnotico → diagnostico` e `gartia/garntia → garantia`. Isso reconhece variações cadastradas e não constitui correção ortográfica geral.

`RATE_LIMIT_REQUESTS`, `RATE_LIMIT_WINDOW_SECONDS` e `CACHE_VERSION` não alteram o comportamento atual, embora apareçam no exemplo ou na configuração. O limite Telegram está fixado no código; a versão usada pelo cache é a constante interna `PROMPT_VERSION`.

## Comandos aprovados

```bash
python -m app.preflight
python -m compileall -q app main.py
python -c 'from main import app; print("IMPORT_OK")'
python -m pip check
python -m pytest -q
```

Resultado final: `65 passed, 1 warning`. O aviso de depreciação é emitido pelo cliente de testes do Starlette sobre o uso de httpx; não houve falha funcional nos testes.

## Pendências para a demonstração e para o professor

1. Publicar o projeto e registrar a URL pública e o nome do bot.
2. Executar a matriz no navegador, no celular e no Telegram real.
3. Registrar o modelo efetivamente configurado e as respostas reais, especialmente a comparação e sua repetição.
4. Informar no artigo o número de casos, as repetições efetivamente realizadas, os canais usados e os critérios de aprovação. Não substituir os oito casos do artigo pelo número de testes automatizados deste registro.
5. Confirmar a versão histórica de Python antes de corrigir a referência específica solicitada pelo professor.
6. Definir a hospedagem conforme a disponibilidade pretendida e verificar a disponibilidade após implantação.
