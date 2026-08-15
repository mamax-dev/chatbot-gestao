import ast
from pathlib import Path

def test_contract_retry_and_lifecycle():
    source=Path('app/gemini.py').read_text(encoding='utf-8')
    ast.parse(source)
    assert 'response_schema=Answer' in source
    assert 'for attempt in range(3)' in source
    assert 'client.close()' in source
    assert 'Perguntas de síntese devem relacionar informações' in source
