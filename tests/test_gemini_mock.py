import importlib,sys
from types import ModuleType,SimpleNamespace
import pytest

def import_gemini(monkeypatch,text='Resposta completa.',reason='STOP'):
    class Models:
        def generate_content(self,**kwargs):return SimpleNamespace(text=text,candidates=[SimpleNamespace(finish_reason=reason)])
    class Client:
        def __init__(self,**kwargs):self.models=Models()
        def close(self):pass
    google=ModuleType('google');genai=ModuleType('google.genai');types=ModuleType('google.genai.types')
    genai.Client=Client
    class GenerateContentConfig:
        def __init__(self,**kwargs):self.kwargs=kwargs
    types.GenerateContentConfig=GenerateContentConfig;genai.types=types;google.genai=genai
    config=ModuleType('app.config');config.GEMINI_MODEL='test-model';monkeypatch.setitem(sys.modules,'app.config',config);
    monkeypatch.setitem(sys.modules,'google',google);monkeypatch.setitem(sys.modules,'google.genai',genai);monkeypatch.setitem(sys.modules,'google.genai.types',types)
    sys.modules.pop('app.gemini',None)
    return importlib.import_module('app.gemini')

def test_normal_text(monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY','x');g=import_gemini(monkeypatch)
    assert g.ask('q','c')=='Resposta completa.'
def test_empty_rejected(monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY','x');g=import_gemini(monkeypatch,text='')
    with pytest.raises(RuntimeError):g.ask('q','c')
def test_truncated_rejected(monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY','x');g=import_gemini(monkeypatch,reason='MAX_TOKENS')
    with pytest.raises(RuntimeError):g.ask('q','c')
def test_insufficient_returns_none(monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY','x');g=import_gemini(monkeypatch,text='INFORMAÇÃO INSUFICIENTE.')
    assert g.ask('q','c') is None
