# Dicionário de mapeamento de campos Guru x Ticto

MAPEAMENTO_TRANSACOES = {
    "id_transacao_origem": {
        "guru": "payment.marketplace_id",  # Corrigido: usa marketplace_id do payment
        "ticto": "order.transaction_hash",
        "tipo": "str",
        "nota": "Para abandoned_cart usa order.hash, para card_exchanged usa transaction.hash"
    },
    "id_assinatura_origem": {
        "guru": "subscription.id",
        "ticto": "subscriptions[0].id",
        "tipo": "str",
        "nota": "Pode ser null para eventos especiais. Para Guru, subscription pode ser dict ou None"
    },
    "plataforma": {
        "guru": "guru",
        "ticto": "ticto",
        "tipo": "str"
    },
    "email_cliente": {
        "guru": "contact.email",
        "ticto": "customer.email",
        "tipo": "str",
        "nota": "Para abandoned_cart usa email direto"
    },
    "valor_total": {
        "guru": "payment.total",
        "ticto": "item.amount",
        "tipo": "float",
        "transformacao": "ticto: dividir por 100"
    },
    "status": {
        "guru": "status",
        "ticto": "status",
        "tipo": "str"
    },
    "metodo_pagamento": {
        "guru": "payment.method",
        "ticto": "payment_method",
        "tipo": "str"
    },
    "data_evento": {
        "guru": "dates.created_at",
        "ticto": "status_date",
        "tipo": "datetime",
        "nota": "Para abandoned_cart usa created_at, para outros usa status_date"
    },
    "json_completo": {
        "guru": "json",
        "ticto": "json",
        "tipo": "json"
    },
    "produto_nome": {
        "guru": "product.name",
        "ticto": "item.name",
        "tipo": "str",
        "nota": "Nome do produto principal da transação"
    },
    "nome_oferta": {
        "guru": "items[0].offer.name",
        "ticto": "item.offer_name",
        "tipo": "str",
        "nota": "Nome da oferta específica (diferente do produto)"
    }
}

MAPEAMENTO_CLIENTES = {
    "nome": {
        "guru": "contact.name",
        "ticto": "customer.name",
        "tipo": "str",
        "nota": "Para abandoned_cart usa name direto"
    },
    "email": {
        "guru": "contact.email",
        "ticto": "customer.email",
        "tipo": "str",
        "nota": "Para abandoned_cart usa email direto"
    },
    "documento": {
        "guru": "contact.doc",
        "ticto": "customer.cpf",
        "tipo": "str",
        "nota": "Para abandoned_cart usa document direto"
    },
    "data_criacao": {
        "guru": "dates.created_at",
        "ticto": "order.order_date",
        "tipo": "datetime",
        "nota": "Para abandoned_cart usa created_at"
    }
}

MAPEAMENTO_ASSINATURAS = {
    "id_assinatura_origem": {
        "guru": "subscription.subscription_code",
        "ticto": "subscriptions[0].id",
        "tipo": "str",
        "nota": "Para Guru usa subscription_code, para Ticto usa id"
    },
    "plataforma": {
        "guru": "guru",
        "ticto": "ticto",
        "tipo": "str"
    },
    "cliente_email": {
        "guru": "contact.email",
        "ticto": "customer.email",
        "tipo": "str",
        "nota": "Para abandoned_cart usa email direto"
    },
    "produto_nome": {
        "guru": "product.name",
        "ticto": "item.product_name",
        "tipo": "str",
        "nota": "Para abandoned_cart usa product_name direto"
    },
    "nome_oferta": {
        "guru": "product.offer.name",
        "ticto": "item.offer_name",
        "tipo": "str",
        "nota": "Nome da oferta específica (diferente do produto)"
    },
    "status": {
        "guru": "subscription.last_status",
        "ticto": "status",
        "tipo": "str"
    },
    "data_inicio": {
        "guru": "subscription.started_at",
        "ticto": "status_date",
        "tipo": "datetime",
        "nota": "Para abandoned_cart usa created_at"
    },
    "data_proxima_cobranca": {
        "guru": "subscription.next_charge",
        "ticto": "subscriptions[0].next_charge",
        "tipo": "datetime"
    },
    "data_cancelamento": {
        "guru": "subscription.canceled_at",
        "ticto": "subscriptions[0].canceled_at",
        "tipo": "datetime"
    },
    "valor_mensal": {
        "guru": "CALCULADO_DINAMICAMENTE",
        "ticto": "CALCULADO_DINAMICAMENTE",
        "tipo": "float",
        "nota": "Será calculado baseado no tipo de plano (anual/mensal) identificado pelo product_id"
    },
    "valor_anual": {
        "guru": "CALCULADO_DINAMICAMENTE",
        "ticto": "CALCULADO_DINAMICAMENTE",
        "tipo": "float",
        "nota": "Será calculado baseado no tipo de plano (anual/mensal) identificado pelo product_id"
    },
    "ultima_atualizacao": {
        "guru": "dates.updated_at",
        "ticto": "status_date",
        "tipo": "datetime"
    }
} 