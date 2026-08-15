import os
from google import genai
from google.genai import types
from pydantic import BaseModel,Field
from .config import GEMINI_MODEL
from .document import load_document
class Answer(BaseModel):answer:str=Field(min_length=1);evidence:list[str]=Field(default_factory=list)
def ask(question):
    key=os.getenv('GEMINI_API_KEY')
    if not key:return None
    prompt=f'''Use somente o documento. Responda em até 4 frases curtas, com cordialidade, sem omitir partes da pergunta.\nDOCUMENTO:\n{load_document()}\nPERGUNTA:{question}'''
    r=genai.Client(api_key=key).models.generate_content(model=GEMINI_MODEL,contents=prompt,config=types.GenerateContentConfig(response_mime_type='application/json',response_schema=Answer,max_output_tokens=900))
    value=r.parsed or Answer.model_validate_json(r.text)
    if not value.evidence:return None
    return {'answer':value.answer.strip(),'evidence':' '.join(value.evidence),'status':'answered','cached':False,'source':'gemini'}
