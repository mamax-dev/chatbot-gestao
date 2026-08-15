from dataclasses import dataclass
from .text import normalize
@dataclass(frozen=True)
class FAQ:answer:str;evidence:str=''
FAQS={
'diagnostico':FAQ('O diagnóstico custa R$ 80,00 e leva até 2 dias úteis. O valor é descontado se o reparo for aprovado.','Diagnóstico de computador: preço R$ 80,00; prazo até 2 dias úteis.'),
'formatacao':FAQ('A formatação custa R$ 180,00 e leva 2 dias úteis. Peça a cópia dos arquivos antes do início.','Formatação: R$ 180,00; prazo 2 dias úteis; cópia prévia dos arquivos.'),
'limpeza':FAQ('A limpeza interna custa R$ 120,00 e leva 1 dia útil. Troca de componentes não está incluída.','Limpeza interna: R$ 120,00; prazo 1 dia útil.'),
'rede':FAQ('A configuração da rede sem fio custa R$ 150,00, leva até 2 horas e conecta até cinco dispositivos.','Rede sem fio: R$ 150,00; até 2 horas; até cinco dispositivos.'),
'visita':FAQ('A visita técnica custa R$ 100,00 e dura até 1 hora. Serviços adicionais são informados antes.','Visita técnica: R$ 100,00; até 1 hora.'),
'pagamento':FAQ('Aceitamos Pix, dinheiro, débito e crédito. Valores a partir de R$ 300,00 podem ser parcelados em até 3 vezes.','Pix, dinheiro, débito e crédito; parcelamento a partir de R$ 300,00.'),
'horario':FAQ('Atendemos de segunda a sexta, das 8h às 18h, e sábado, das 8h às 12h. Não atendemos domingo e feriados.','Horários de atendimento.'),
'empresa':FAQ('Oferecemos diagnóstico, formatação, limpeza interna, configuração de rede sem fio e visita técnica. 🙂','Serviços oferecidos pela Solução Prática.'),
'missao':FAQ('Nossa missão é simplificar o suporte técnico com atendimento claro, acessível e confiável.','Missão institucional.'),
'visao':FAQ('Nossa visão é ser reconhecida pela praticidade, transparência e qualidade no atendimento tecnológico.','Visão institucional.'),
'valores':FAQ('Nossos valores são clareza, respeito, confiança, responsabilidade e compromisso com o cliente.','Valores institucionais.'),
'gratis':FAQ('Os serviços são pagos. Diga qual serviço procura e eu informo o preço. 🙂','Tabela de serviços.'),
}
PATTERNS=[
('empresa',['o que voces faz','o que a empresa faz','quais servicos','atividade da empresa','quem e a empresa']),('diagnostico',['diagnostico']),('formatacao',['formatacao','formatar']),('limpeza',['limpeza']),('rede',['wifi','rede sem fio','roteador']),('visita',['visita tecnica']),('pagamento',['dinheiro','pix','pagamento','pagar','cartao','parcelar']),('horario',['horario','sabado','domingo','feriado']),('missao',['missao']),('visao',['visao']),('valores',['valores']),('gratis',['gratis','tem que pagar','precisa pagar'])]
def lookup(question):
    q=normalize(question)
    for key,terms in PATTERNS:
        if any(term in q for term in terms):return FAQS[key]
    return None
