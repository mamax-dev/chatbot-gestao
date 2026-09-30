# Matriz para a demonstração do chatbot

Execute após publicar e configurar Gemini e Telegram. Esta é uma lista de verificações pendentes em ambiente real, não um registro de testes já aprovados publicamente. Anote data, canal, resposta obtida e aprovação em cada execução.

| Caso | Pergunta ou ação | Resultado esperado |
| --- | --- | --- |
| 1 | O que vc fz? | Listar os cinco serviços. |
| 2 | Quanto custa o diagnostco? | Diagnóstico a R$ 80,00; até dois dias úteis. |
| 3 | Qual a gartia? | Garantia de 30 dias. |
| 4 | Valor | Pedir esclarecimento: preço ou valores institucionais. |
| 4a | Após “valor”, enviar “preço de um serviço” | Listar os cinco preços. |
| 4b | Enviar “valores institucionais da empresa” | Informar clareza, respeito, confiança, responsabilidade e compromisso com o cliente. |
| 5 | A empresa oferece seguro contra roubo? | Informar ausência da informação. |
| 6 | abcd | Pedir reformulação. |
| 7 | Compare o diagnóstico de computador com a visita técnica e explique qual serviço é mais adequado para um computador com lentidão, considerando finalidade, preço e prazo. | Comparar os dois serviços com dados cadastrados e indicar diagnóstico para investigar lentidão. |
| 8 | Repetir exatamente a pergunta do caso 7 | Reutilizar a resposta; no site, mostrar o aviso de reutilização. |
| Complementar | Quais são os valores? | Informar os valores institucionais. |
| Complementar | Posso cancelar? | Informar antecedência mínima de quatro horas. |
| Complementar | Qual a validade do orçamento? | Aprovação prévia e validade de sete dias. |
| Telegram | /start | Mostrar saudação. |
| Telegram | Enviar nove mensagens em menos de um minuto | Na nona mensagem, pedir que aguarde. |

Faça os casos 1 a 8 nos dois canais. Os esclarecimentos 4a e 4b são verificações adicionais do caso de ambiguidade. Aguarde mais de um minuto entre blocos de até oito mensagens no mesmo chat do Telegram para não misturar o limite de frequência com os testes de conteúdo.

O cache é compartilhado entre os canais dentro do mesmo processo. Para avaliar geração real nos dois canais, use instâncias com cache vazio ou reinicie a aplicação entre as avaliações. Uma comparação já respondida no site pode ser reutilizada pelo Telegram.

Não marque como aprovada a geração real se aparecer a mensagem de indisponibilidade. Sem credenciais ou com falha da API, essa mensagem é a contingência esperada, mas a comparação do caso 7 continua pendente.

Critérios para a pergunta aberta: as duas finalidades devem estar corretas, os preços devem ser R$ 80,00 e R$ 100,00, os prazos devem respeitar os dados e a indicação deve relacionar diagnóstico à investigação da lentidão. A resposta pode variar na redação.


## Reteste da segunda correção

Após publicar a segunda revisão, envie `Por favor, resuma como a transparência aparece nas regras de atendimento.` no site e no Telegram. Uma resposta adequada relaciona regras documentadas, como aprovação prévia, validade do orçamento, garantia e antecedência de cancelamento, à transparência no atendimento. Repita a pergunta no site para verificar a reutilização.

Se o modelo declarar informação insuficiente, a versão atual deve mostrar a mensagem de informação ausente, sem dizer que a API está indisponível. Esse comportamento confirma a correção da classificação, mas a síntese continua sem aprovação. Se a API falhar, a mensagem de indisponibilidade permanece prevista; registre o motivo no log.
