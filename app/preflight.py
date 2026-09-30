import json,sys
from pathlib import Path
from .business_config import load_business
from .document import load_document
REQUIRED={'empresa','servicos','atendimento','pagamentos','politicas','conversa','fora_do_escopo'}
def run():
    cfg=load_business();missing=REQUIRED-set(cfg)
    if missing:raise RuntimeError('Campos ausentes: '+', '.join(sorted(missing)))
    ids=[s.get('id') for s in cfg['servicos']]
    if None in ids or len(ids)!=len(set(ids)):raise RuntimeError('IDs de serviços ausentes ou duplicados')
    if not load_document().strip():raise RuntimeError('Documento vazio')
    print('PREFLIGHT_OK')
if __name__=='__main__':run()
