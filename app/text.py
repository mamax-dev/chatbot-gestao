import re
import unicodedata

ALIASES = {
    'vc': 'voces',
    'vcs': 'voces',
    'voce': 'voces',
    'fazem': 'faz',
    'fz': 'faz',
    'qto': 'quanto',
    'qnto': 'quanto',
    'diagnostco': 'diagnostico',
    'diagnotico': 'diagnostico',
    'gartia': 'garantia',
    'garntia': 'garantia',
    'precos': 'precos',
    'principios': 'principios',
}


def normalize(text):
    value = unicodedata.normalize('NFKD', (text or '').lower())
    value = ''.join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r'[^a-z0-9]+', ' ', value).strip()
    return ' '.join(ALIASES.get(word, word) for word in value.split())
