from dataclasses import dataclass
from .document import normalize
TOPICS={
'diagnostico':{'diagnostico','travando','lento','lentidao'},'formatacao':{'formatacao','formatar','arquivos','backup','licenca'},
'limpeza':{'limpeza','poeira','ventilacao'},'rede':{'wifi','wi fi','rede sem fio','roteador','dispositivos'},
'visita':{'visita','tecnico no local'},'horario':{'horario','sabado','domingo','feriado'},
'agendamento':{'agendamento','agendar','marcar'},'cancelamento':{'cancelamento','cancelar','reagendar','reagendamento','deslocamento'},
'pagamento':{'pagamento','pagar','pix','debito','credito','dinheiro','cheque','parcelar','dividir','cobranca'},
'orcamento':{'orcamento','aprovar','aprovacao','validade'},'garantia':{'garantia'},'materiais':{'materiais','pecas','cabos','incluido','incluida'},
'missao':{'missao'},'visao':{'visao'},'valores':{'valores','principios'}}
COMPLEX={'explique','porque','por que','importancia','medidas','cuidados','evitar','relacione','compare','sintese','resumo','recomendacao','orientacao','redija','elabore','considerando','seguro','transparente','primeira vez','prepare'}
EXTERNAL={'capital da franca','melhor marca','seguro contra roubo','celular','smartphone','recuperacao de dados','desconto para estudante'}
@dataclass(frozen=True)
class Analysis:normalized:str;topics:tuple[str,...];complex:bool;external:bool
def analyze(question):
    q=normalize(question);topics=tuple(k for k,v in TOPICS.items() if any(term in q for term in v))
    return Analysis(q,topics,any(x in q for x in COMPLEX) or len(topics)>=3,any(x in q for x in EXTERNAL))
