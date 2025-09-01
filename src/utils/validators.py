# Validation utilities 
# src/utils/validators.py

def validar_payload_ticto(payload: dict) -> bool:
    """
    Valida se o payload do webhook Ticto possui os campos essenciais.
    Retorna True se válido, False caso contrário.
    """
    # Campo obrigatório para todos os webhooks
    if "status" not in payload:
        print("[VALIDAÇÃO] Campo obrigatório ausente: status")
        return False
    
    status = payload.get("status")
    
    # Validação específica por tipo de evento
    if status == "abandoned_cart":
        # Carrinho abandonado tem estrutura diferente
        campos_obrigatorios = ["status", "email", "name", "product_name"]
        for campo in campos_obrigatorios:
            if campo not in payload:
                print(f"[VALIDAÇÃO] Campo obrigatório ausente para abandoned_cart: {campo}")
                return False
        return True
    
    elif status in ["card_exchanged", "claimed"]:
        # Eventos especiais podem ter estruturas únicas
        # Mínimo: status e algum identificador
        if "order" not in payload and "transaction" not in payload:
            print(f"[VALIDAÇÃO] Evento {status} deve ter order ou transaction")
            return False
        return True
    
    else:
        # Webhooks normais (vendas, assinaturas, etc.)
        campos_obrigatorios = ["status", "order", "customer"]
        for campo in campos_obrigatorios:
            if campo not in payload:
                print(f"[VALIDAÇÃO] Campo obrigatório ausente: {campo}")
                return False
        
        # Verifica se tem subscriptions (exceto para vendas pontuais)
        if status not in ["refused", "pix_expired", "bank_slip_delayed"]:
            if "subscriptions" not in payload:
                print("[VALIDAÇÃO] Campo obrigatório ausente: subscriptions")
                return False
        
        return True

def validar_payload_guru(payload: dict) -> bool:
    """
    Valida se o payload do webhook Guru possui os campos essenciais.
    Retorna True se válido, False caso contrário.
    """
    # Se o payload estiver aninhado, extrai o payload real
    if "payload" in payload:
        payload = payload["payload"]
    webhook_type = payload.get("webhook_type", "transaction")
    if webhook_type == "subscription":
        campos_obrigatorios = ["subscriber", "id", "last_status"]
        for campo in campos_obrigatorios:
            if campo not in payload or payload.get(campo) in (None, ""):
                print(f"[VALIDAÇÃO] Campo obrigatório ausente no webhook de assinatura: {campo}")
                return False
        return True
    else:
        campos_obrigatorios = [
            "status", "contact", "payment", "subscription"
        ]
        for campo in campos_obrigatorios:
            if campo not in payload:
                print(f"[VALIDAÇÃO] Campo obrigatório ausente: {campo}")
                return False
        return True