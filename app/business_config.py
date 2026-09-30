import json
from functools import lru_cache
from .config import BUSINESS_PATH
@lru_cache(maxsize=1)
def load_business():
    data=json.loads(BUSINESS_PATH.read_text(encoding='utf-8'))
    required={'empresa','servicos','atendimento','pagamentos','politicas','conversa','fora_do_escopo'}
    missing=required-set(data)
    if missing:raise RuntimeError('Configuração inválida: '+', '.join(sorted(missing)))
    return data
