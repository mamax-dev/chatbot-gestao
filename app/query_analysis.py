from dataclasses import dataclass
from .document import normalize

TOPICS={
'diagnostico':{'diagnostico','analisar','avaliar','travando','trava','lento','lentidao'},
'formatacao':{'formatacao','formatar','sistema','arquivos','licenca','backup','documentos'},
'limpeza':{'limpeza','poeira','ventilacao','componentes'},
'rede':{'wifi','wi fi','rede sem fio','roteador','dispositivos'},
'visita':{'visita','tecnico no local','deslocamento'},
'horario':{'horario','sabado','domingo','feriado'},
'agendamento':{'agendamento','agendar','marcar'},
'cancelamento':{'cancelamento','cancelar','reagendar','reagendamento','deslocamento'},
'pagamento':{'pagamento','pagar','pix','debito','credito','dinheiro','cheque','parcelar','dividir','cobranca'},
'orcamento':{'orcamento','aprovar','aprovacao','validade'},
'garantia':{'garantia'},'materiais':{'materiais','pecas','cabos','licencas','incluido','incluida'},
'missao':{'missao'},'visao':{'visao'},'valores':{'valores','principios'},
}
COMPLEX={'explique','porque','por que','importancia','medidas','cuidados','evitar','relacione','compare','sintese','resumo','recomendacao','orientacao','redija','elabore','considerando','seguro','transparente','primeira vez'}
EXTERNAL={'capital da franca','melhor marca de computador','seguro contra roubo','celular','smartphone','recuperacao de dados','desconto para estudante'}
@dataclass(frozen=True)
class Analysis:
    normalized:str;topics:tuple[str,...];complex:bool;external:bool

def analyze(question:str)->Analysis:
    q=normalize(question)
    topics=tuple(k for k,v in TOPICS.items() if any(term in q for term in v))
    return Analysis(q,topics,any(t in q for t in COMPLEX) or len(topics)>=3,any(t in q for t in EXTERNAL))
