# Helper functions 
# src/utils/helpers.py

from utils.mapeamento import MAPEAMENTO_TRANSACOES

# IDs dos produtos para identificar planos mensais e anuais
PRODUTOS_GURU = {
    "1741887379": "anual",    # Plano Anual - Comu Academy
    "1741871695": "mensal",   # Plano Mensal (confirmar ID)
    "1742214167": "orderbump_ebook",  # Ebook - Como Criar Personagens (order bump)
    "1742215996": "ebook_vitalicio", # Comissions na Gringa (ebook vitalício)
    "1752494625": "orderbump_ebook"   # Pack de Ebooks (order bump)
}

PRODUTOS_TICTO = {
    41146: "anual",    # Plano Anual
    41145: "mensal",    # Plano Mensal
   
}

OFFERS_TICTO = {
    # Exemplos, ajuste conforme os offer_code reais
    "O8578C9AB": "anual", # Plano Anual
    "O84ABA07F": "mensal" # Plano Mensal
    # Adicione outros offer_codes conforme necessário
}

# Códigos especiais de offer_code para produtos orderbump/ebook vitalício
OFFER_CODES_ESPECIAIS = {
    "O0AB56C79": "orderbump_ebook",
    "O06463C35": "ebook_vitalicio"
}

def identificar_tipo_plano_guru(product_id: str) -> str:
    """
    Identifica se o produto Guru é plano mensal ou anual baseado no ID.
    Retorna: 'anual', 'mensal' ou 'desconhecido'
    """
    return PRODUTOS_GURU.get(product_id, "desconhecido")

def identificar_tipo_plano_ticto(product_id: int, offer_code: str = None) -> str:
    """
    Identifica se o produto Ticto é plano mensal ou anual baseado no ID ou offer_code.
    Retorna: 'anual', 'mensal' ou 'desconhecido'
    """
    # Primeiro tenta pelo product_id
    tipo = PRODUTOS_TICTO.get(product_id)
    if tipo and tipo in ("anual", "mensal"):
        return tipo
    # Se não encontrou, tenta pelo offer_code
    if offer_code:
        return OFFERS_TICTO.get(offer_code, "desconhecido")
    return "desconhecido"

def mapear_transacao_ticto(payload: dict) -> dict:
    """
    Mapeia os campos do payload Ticto para o formato da tabela transacoes.
    Trata diferentes tipos de webhook (vendas normais, carrinho abandonado, eventos especiais).
    """
    transacao = {}
    status = payload.get("status", "")
    offer_code = payload.get("item", {}).get("offer_code")
    tipo_produto = identificar_tipo_produto_ticto(offer_code)

    # Mapeamento específico por tipo de evento
    if status == "abandoned_cart":
        # Carrinho abandonado tem estrutura diferente
        transacao["id_transacao_origem"] = f"abandoned_{payload.get('email', 'unknown')}_{payload.get('created_at', 'unknown')}"
        transacao["id_assinatura_origem"] = None
        transacao["plataforma"] = "ticto"
        transacao["email_cliente"] = payload.get("email")
        transacao["valor_total"] = 0  # Carrinho abandonado não tem valor
        transacao["status"] = status
        transacao["metodo_pagamento"] = None
        transacao["data_evento"] = payload.get("created_at")
        transacao["json_completo"] = payload
        return transacao
    
    elif status in ["card_exchanged", "claimed"]:
        # Eventos especiais
        transacao["id_transacao_origem"] = payload.get("transaction", {}).get("hash") or payload.get("order", {}).get("transaction_hash")
        transacao["id_assinatura_origem"] = None
        transacao["plataforma"] = "ticto"
        transacao["email_cliente"] = payload.get("customer", {}).get("email")
        transacao["valor_total"] = 0  # Eventos especiais não têm valor
        transacao["status"] = status
        transacao["metodo_pagamento"] = payload.get("payment_method")
        transacao["data_evento"] = payload.get("status_date") or payload.get("order", {}).get("order_date")
        transacao["json_completo"] = payload
        return transacao
    
    elif tipo_produto == "orderbump_ebook":
        # Order bump: valor vem de item.amount (centavos)
        valor_bump = payload.get("item", {}).get("amount", 0) / 100
        transacao["id_transacao_origem"] = payload.get("transaction", {}).get("hash") or payload.get("order", {}).get("transaction_hash")
        transacao["id_assinatura_origem"] = payload.get("subscriptions", [{}])[0].get("id") if payload.get("subscriptions") else None
        transacao["plataforma"] = "ticto"
        transacao["email_cliente"] = payload.get("customer", {}).get("email")
        transacao["valor_total"] = valor_bump
        transacao["valor_bruto"] = valor_bump
        transacao["valor"] = valor_bump  # Para uso direto no banco
        transacao["status"] = status
        transacao["metodo_pagamento"] = payload.get("payment_method")
        transacao["data_evento"] = payload.get("order", {}).get("order_date")
        transacao["json_completo"] = payload
        return transacao
    
    else:
        # Webhooks normais (vendas, assinaturas, etc.)
        for campo_db, info in MAPEAMENTO_TRANSACOES.items():
            caminho = info["ticto"].split(".")
            valor = payload
            try:
                for parte in caminho:
                    if parte.endswith("]"):
                        # Suporte para listas, ex: subscriptions[0].id
                        nome_lista, idx = parte[:-1].split("[")
                        valor = valor[nome_lista][int(idx)]
                    else:
                        valor = valor[parte]
            except (KeyError, IndexError, TypeError):
                valor = None
            # Transformação especial (ex: dividir por 100 para Ticto)
            if campo_db == "valor_total" and valor is not None and info.get("transformacao") == "ticto: dividir por 100":
                valor = valor / 100
            transacao[campo_db] = valor
        return transacao

def mapear_transacao_guru(payload: dict) -> dict:
    """
    Mapeia os campos do payload Guru para o formato da tabela transacoes.
    """
    # Se o payload estiver aninhado, extrai o payload real
    if "payload" in payload:
        payload = payload["payload"]
        
    transacao = {}
    for campo_db, info in MAPEAMENTO_TRANSACOES.items():
        caminho = info["guru"].split(".")
        valor = payload
        try:
            for parte in caminho:
                if parte.endswith("]"):
                    nome_lista, idx = parte[:-1].split("[")
                    valor = valor[nome_lista][int(idx)]
                else:
                    # Tratamento especial para subscription.id
                    if parte == "subscription" and valor is not None:
                        subscription = valor.get("subscription")
                        if subscription is None or not isinstance(subscription, dict):
                            valor = None
                            break
                        valor = subscription
                    else:
                        valor = valor[parte]
        except (KeyError, IndexError, TypeError):
            valor = None
        transacao[campo_db] = valor
    return transacao

def identificar_tipo_produto_ticto(offer_code: str) -> str:
    """
    Retorna o tipo especial do produto baseado no offer_code.
    """
    return OFFER_CODES_ESPECIAIS.get(offer_code, "assinatura")

def identificar_tipo_produto_guru(product_id: str, is_order_bump: int = 0) -> str:
    """
    Identifica o tipo especial do produto Guru baseado no product_id.
    Retorna: 'assinatura', 'orderbump_ebook', 'ebook_vitalicio'
    """
    # Verifica se é um produto especial
    tipo_especial = PRODUTOS_GURU.get(product_id)
    if tipo_especial in ("orderbump_ebook", "ebook_vitalicio"):
        return tipo_especial
    
    # Se não for especial, verifica se é order bump
    if is_order_bump == 1:
        return "orderbump_ebook"
    
    return "assinatura"

def tipo_venda_recusada_ticto(payload):
    subs = payload.get("subscriptions", [{}])
    if not subs or not isinstance(subs, list):
        return "desconhecido"
    sub = subs[0]
    failed = sub.get("failed_charges", 0)
    success = sub.get("successful_charges", 0)
    if failed == 0 and success == 0:
        return "recusada_primeira_venda"
    else:
        return "recusada_cobranca_assinatura"

def calcular_valores_assinatura_por_tipo(valor_webhook, product_id, plataforma):
    """
    Calcula os valores de assinatura baseado no tipo de plano.
    Retorna: (valor_mensal, valor_anual)
    
    Args:
        valor_webhook: Valor recebido no webhook
        product_id: ID do produto para identificar o tipo de plano
        plataforma: 'guru' ou 'ticto'
    
    Returns:
        tuple: (valor_mensal, valor_anual) - apenas um será preenchido
    """
    # Identifica tipo de plano
    if plataforma == "guru":
        tipo_plano = identificar_tipo_plano_guru(str(product_id))
    else:  # ticto
        tipo_plano = identificar_tipo_plano_ticto(int(product_id))
    
    # Retorna apenas o campo correto baseado no tipo de plano
    if tipo_plano == "anual":
        # Plano anual: preenche apenas valor_anual
        print(f"[HELPERS] ✅ Plano anual detectado para {plataforma} - product_id: {product_id}, valor: R$ {valor_webhook}")
        return None, valor_webhook
    elif tipo_plano == "mensal":
        # Plano mensal: preenche apenas valor_mensal
        print(f"[HELPERS] ✅ Plano mensal detectado para {plataforma} - product_id: {product_id}, valor: R$ {valor_webhook}")
        return valor_webhook, None
    else:
        # Produto desconhecido: assume mensal como fallback
        print(f"[HELPERS] ⚠️ Tipo de plano não identificado para {plataforma} - product_id: {product_id}, assumindo mensal")
        return valor_webhook, None