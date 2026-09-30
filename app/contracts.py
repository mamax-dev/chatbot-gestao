from enum import Enum
from pydantic import BaseModel, Field

class Source(str, Enum):
    LOCAL='local'; FAQ='faq'; CACHE='cache'; GEMINI='gemini'; FALLBACK='fallback'; HANDOFF='handoff'
class Status(str, Enum):
    ANSWERED='answered'; ABSENT='absent'; FAILED='failed'; REJECTED='rejected'
class BotReply(BaseModel):
    answer: str = Field(min_length=1, max_length=2400)
    evidence: str = Field(default='', max_length=5000)
    status: Status = Status.ANSWERED
    source: Source = Source.LOCAL
    cached: bool = False
    request_id: str = ''
    def as_dict(self): return self.model_dump(mode='json')
