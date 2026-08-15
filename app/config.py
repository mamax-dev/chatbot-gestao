import os
from pathlib import Path
BASE_DIR=Path(__file__).resolve().parent.parent
DOCUMENT_PATH=BASE_DIR/'instrucoes.rtf'
GEMINI_MODEL=os.getenv('GEMINI_MODEL','gemini-3.6-flash')
PUBLIC_BASE_URL=os.getenv('PUBLIC_BASE_URL','').rstrip('/')
TELEGRAM_USERNAME=os.getenv('TELEGRAM_USERNAME','').lstrip('@')
MAX_QUESTION_LENGTH=500
CACHE_TTL_SECONDS=int(os.getenv('CACHE_TTL_SECONDS','86400'))
CACHE_VERSION=os.getenv('CACHE_VERSION','stable-faq-v1')
