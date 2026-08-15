import ast
from pathlib import Path


def test_client_is_kept_alive_until_request_finishes():
    source = Path('app/gemini.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    assert 'client = genai.Client' in source
    assert 'client.models.generate_content' in source
    assert 'finally:' in source
    assert 'client.close()' in source
    assert 'genai.Client(api_key=api_key).models' not in source
