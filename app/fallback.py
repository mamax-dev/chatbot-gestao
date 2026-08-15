from .config import REFUSAL
from .query_analysis import TOPICS, analyze


def build_document_fallback(question: str, document: str) -> dict:
    """Build a complete grounded fallback from full document sections."""
    from .knowledge_engine import select

    analysis = analyze(question)
    blocks = []
    for topic in analysis.topics:
        blocks.extend(select(document, TOPICS[topic]))
    unique = list(dict.fromkeys(blocks))
    if not unique:
        return {
            'answer': REFUSAL, 'evidence': '', 'status': 'absent',
            'cached': False, 'source': 'fallback', 'complete': True,
        }
    return {
        'answer': 'Informações relacionadas:\n' + '\n'.join('• ' + block for block in unique),
        'evidence': ' '.join(unique),
        'status': 'answered', 'cached': False, 'source': 'fallback', 'complete': True,
    }
