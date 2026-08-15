from .business_config import load_business
from .text import normalize


def reply(answer, evidence=''):
    return {
        'answer': answer,
        'evidence': evidence,
        'status': 'answered',
        'cached': False,
        'source': 'faq',
    }


def _service_answer(service):
    observations = ' '.join(service.get('observacoes', []))
    text = f"{service['nome']}: {service['preco']}; prazo {service['prazo']}. {observations}"
    return reply(text.strip(), str(service))


def _price_list(config):
    lines = [f"{service['nome']}: {service['preco']}" for service in config['servicos']]
    return reply('Preços dos serviços:\n' + '\n'.join(lines), str(config['servicos']))


def _service_list(config):
    names = ', '.join(service['nome'] for service in config['servicos'])
    return reply(f'Oferecemos {names}.', str(config['servicos']))


def lookup(question):
    config = load_business()
    normalized = normalize(question)
    company = config['empresa']
    policies = config['politicas']

    if any(normalize(item) in normalized for item in config['fora_do_escopo']):
        return {
            'answer': config['conversa']['informacao_ausente'],
            'evidence': '',
            'status': 'absent',
            'cached': False,
            'source': 'faq',
        }

    # "valor" sozinho é ambíguo: preço ou valores institucionais.
    if normalized == 'valor':
        return reply(
            'Você quer consultar o preço de um serviço ou os valores institucionais da empresa?'
        )

    institutional_value_markers = (
        'valores da empresa', 'valores institucionais', 'principios da empresa',
        'principios institucionais', 'valor a empresa defende', 'valor que a empresa defende',
    )
    if normalized == 'valores' or any(marker in normalized for marker in institutional_value_markers):
        values = ', '.join(company['valores'])
        return reply(f'Valores: {values}.', values)

    price_list_markers = (
        'preco', 'precos', 'tabela de precos', 'lista de precos',
        'quais os precos', 'quanto custam os servicos', 'valores dos servicos',
        'valor dos servicos', 'tabela de valores',
    )
    general_price_query = (
        normalized in price_list_markers
        or any(marker in normalized for marker in price_list_markers[2:])
    )

    service_list_markers = (
        'servico', 'servicos', 'lista de servicos', 'quais servicos',
        'o que a empresa faz', 'o que voces faz', 'o que oferecem',
        'o que voces oferecem', 'atividade da empresa',
    )
    if normalized in service_list_markers or any(
        marker in normalized for marker in service_list_markers[2:]
    ):
        return _service_list(config)

    if 'quem e a empresa' in normalized or 'quem sao voces' in normalized:
        return reply(
            f"A {company['nome']} é uma {company['natureza']} voltada a {company['descricao']}.",
            str(company),
        )

    if 'missao' in normalized:
        return reply(f"Missão: {company['missao']}", company['missao'])
    if 'visao' in normalized:
        return reply(f"Visão: {company['visao']}", company['visao'])

    # Serviço específico tem prioridade sobre lista geral de preços.
    matched_services = []
    for service in config['servicos']:
        if any(normalize(variation) in normalized for variation in service['variacoes']):
            matched_services.append(service)
    if len(matched_services) == 1:
        return _service_answer(matched_services[0])
    if len(matched_services) > 1:
        lines = [
            f"{service['nome']}: {service['preco']}; prazo {service['prazo']}."
            for service in matched_services
        ]
        return reply('\n'.join(lines), str(matched_services))

    if general_price_query:
        return _price_list(config)

    payment_markers = (
        'dinheiro', 'pix', 'pagamento', 'pagar', 'cartao', 'parcelar',
        'parcelamento', 'cheque', 'formas de pagamento',
    )
    if any(marker in normalized for marker in payment_markers):
        payment = config['pagamentos']
        return reply(
            f"Aceitamos {', '.join(payment['formas_aceitas'])}. "
            f"{payment['parcelamento']}. "
            f"Não aceitamos {', '.join(payment['formas_nao_aceitas'])}.",
            str(payment),
        )

    if any(marker in normalized for marker in ('horario', 'sabado', 'domingo', 'feriado', 'onde atendem')):
        hours = config['atendimento']
        return reply(
            f"Segunda a sexta: {hours['segunda_a_sexta']}; sábado: {hours['sabado']}; "
            f"domingo e feriados: {hours['domingo_e_feriados']}. Atendimento {hours['area']}.",
            str(hours),
        )

    budget_markers = ('orcamento', 'aprovar', 'aprovacao')
    if any(marker in normalized for marker in budget_markers):
        pieces = [policies['orcamento']]
        if 'validade' in normalized or 'quanto tempo' in normalized:
            pieces.append(policies['validade_orcamento'])
        return reply(' '.join(pieces), ' '.join(pieces))

    policy_map = {
        'agend': 'agendamento',
        'cancel': 'cancelamento',
        'reagend': 'cancelamento',
        'desloc': 'deslocamento',
        'garantia': 'garantia',
        'pecas': 'materiais',
        'cabos': 'materiais',
        'materiais': 'materiais',
    }
    selected = []
    for marker, key in policy_map.items():
        if marker in normalized and key not in selected:
            selected.append(key)
    if selected:
        evidence = ' '.join(policies[key] for key in selected)
        return reply(evidence, evidence)

    if any(marker in normalized for marker in ('gratis', 'tem que pagar', 'precisa pagar')):
        return reply(
            'Os serviços são pagos. Diga qual serviço procura e eu informo o preço.',
            'serviços pagos',
        )

    return None
