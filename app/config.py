import os
from pathlib import Path
BASE_DIR=Path(__file__).resolve().parent.parent
DOCUMENT_PATH=BASE_DIR/'instrucoes.rtf'
GEMINI_MODEL=os.getenv('GEMINI_MODEL','gemini-3.6-flash')
PUBLIC_BASE_URL=os.getenv('PUBLIC_BASE_URL','').rstrip('/')
TELEGRAM_USERNAME=os.getenv('TELEGRAM_USERNAME','').lstrip('@')
REFUSAL='Essa informação não consta no arquivo de instruções.'
AMBIGUOUS='Pode me dizer qual serviço ou informação deseja consultar? 🙂'
TECHNICAL_MESSAGE='O atendimento está temporariamente indisponível. Tente novamente mais tarde.'
MAX_QUESTION_LENGTH=500
CACHE_TTL_SECONDS=int(os.getenv('CACHE_TTL_SECONDS','86400'))
CACHE_VERSION=os.getenv('CACHE_VERSION','final-unified-v1')
AI_RETRY_ATTEMPTS=int(os.getenv('AI_RETRY_ATTEMPTS','2'))
AI_RETRY_BASE_SECONDS=float(os.getenv('AI_RETRY_BASE_SECONDS','1.5'))
