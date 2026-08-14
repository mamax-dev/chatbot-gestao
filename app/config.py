import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENT_PATH = BASE_DIR / "instrucoes.rtf"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")
REFUSAL = "Essa informação não consta no arquivo de instruções."
AMBIGUOUS = "Por favor, especifique qual serviço ou informação deseja consultar."
QUOTA_MESSAGE = "O limite diário de consultas foi atingido. Tente novamente após a renovação da cota."
TECHNICAL_MESSAGE = "O atendimento está temporariamente indisponível. Tente novamente mais tarde."
TELEGRAM_USERNAME = os.getenv("TELEGRAM_USERNAME", "").lstrip("@")
MAX_QUESTION_LENGTH = int(os.getenv("MAX_QUESTION_LENGTH", "500"))
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "8"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "86400"))
