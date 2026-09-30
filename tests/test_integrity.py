import json
from pathlib import Path
def test_original_visual_assets_preserved():
    assert Path('static/ai-bot.json').stat().st_size==133712
    assert Path('static/style.css').stat().st_size==12211
    assert Path('static/app.js').stat().st_size==4932
    assert Path('templates/index.html').stat().st_size==7113
def test_business_config():
    data=json.loads(Path('data/empresa.json').read_text(encoding='utf-8'))
    assert len(data['servicos'])==5 and data['transferencia_simulada']['ativa'] is True
def test_original_video_present_and_referenced():
    assert Path('static/hero-support.mp4').stat().st_size > 0
    assert '/static/hero-support.mp4' in Path('templates/index.html').read_text(encoding='utf-8')
