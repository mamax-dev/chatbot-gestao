import os
from google import genai
from google.genai import types
from pydantic import BaseModel,Field
from .business_config import load_business
from .config import GEMINI_MODEL
class Answer(BaseModel):answer:str=Field(min_length=1);evidence:list[str]=Field(default_factory=list)
def ask(question):
    api_key=os.getenv('GEMINI_API_KEY')
    if not api_key:return None
    client=genai.Client(api_key=api_key)
    try:
        cfg=load_business()
        response=client.models.generate_content(model=GEMINI_MODEL,contents=f'Use somente a configuração fornecida. Responda com cordialidade, objetividade e até 4 frases. CONFIGURAÇÃO:{cfg}\nPERGUNTA:{question}',config=types.GenerateContentConfig(response_mime_type='application/json',response_schema=Answer,max_output_tokens=900))
        value=response.parsed or Answer.model_validate_json(response.text)
        if not value.evidence:return None
        return {'answer':value.answer.strip(),'evidence':' '.join(value.evidence),'status':'answered','cached':False,'source':'gemini'}
    finally:client.close()
