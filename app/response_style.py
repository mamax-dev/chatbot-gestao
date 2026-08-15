from .config import REFUSAL
FRIENDLY_NOT_FOUND='Não encontrei essa informação nas orientações disponíveis. Posso ajudar com serviços, preços, prazos ou pagamentos. 🙂'
def style_result(result,channel='web'):
    value={**result}
    if value.get('status')=='absent' or value.get('answer')==REFUSAL:value['answer']=FRIENDLY_NOT_FOUND;value['evidence']=''
    return value
