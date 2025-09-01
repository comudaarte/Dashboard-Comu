"""
Mapeamento de dados para backfill histórico das APIs
Separa a lógica de mapeamento de webhooks do mapeamento de dados históricos
"""

from typing import Dict, Any, Optional
from datetime import datetime

class MapeamentoBackfillTicto:
    """
    Mapeamento de dados históricos da API Ticto para o formato interno do banco
    """
    
    @staticmethod
    def mapear_order_ticto(order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapeia dados de order da API Ticto para formato interno
        """
        transaction = order_data.get("transaction", {})
        customer = order_data.get("customer", {})
        product = order_data.get("product", {})
        order = order_data.get("order", {})
        order_item = order_data.get("order_item", {})
        
        # Converte valores de centavos para reais
        paid_amount = transaction.get("paid_amount", 0) / 100 if transaction.get("paid_amount") else 0
        order_item_amount = order_item.get("amount", 0) / 100 if order_item.get("amount") else 0
        commission = order_data.get("commission", 0) / 100 if order_data.get("commission") else 0
        
        # Valor líquido é igual à comissão (já descontada a taxa da plataforma)
        valor_liquido = commission
        
        # Determina status baseado na transação
        status = transaction.get("status", "authorized")
        
        # Extrai informações de recusa
        tipo_recusa = None
        motivo_recusa = None
        if status == "refused":
            tipo_recusa = "recusada_primeira_venda" if transaction.get("occurrence", 0) == 1 else "recusada_cobranca_assinatura"
            motivo_recusa = transaction.get("refused_reason")
        
        return {
            # Dados da transação
            "id_transacao_origem": transaction.get("hash"),
            "status": status,
            "valor": paid_amount,  # transaction.paid_amount
            "valor_bruto": order_item_amount,  # order_item.amount
            "valor_liquido": valor_liquido,  # commission (valor líquido já descontada a taxa da plataforma)
            "metodo_pagamento": transaction.get("payment_method"),
            "motivo_recusa": motivo_recusa,
            "tipo_recusa": tipo_recusa,
            "data_transacao": transaction.get("updated_at") or order_data.get("updated_at"),
            
            # Dados do cliente
            "cliente": {
                "nome": customer.get("name"),
                "email": customer.get("email"),
                "documento": customer.get("cpf") or customer.get("cnpj"),
                "data_criacao": order_data.get("created_at")
            },
            
            # Dados do produto
            "produto": {
                "nome": product.get("name"),
                "id": product.get("id"),
                "tipo": product.get("type"),
                "is_subscription": product.get("is_subscription")
            },
            
            # Dados da oferta
            "oferta": {
                "nome": order_data.get("offer", {}).get("name"),
                "id": order_data.get("offer", {}).get("id"),
                "codigo": order_data.get("offer", {}).get("code")
            },
            
            # Dados da ordem
            "ordem": {
                "id": order.get("id"),
                "hash": order.get("hash"),
                "tipo": order.get("type")
            },
            
            # Dados da assinatura (se aplicável)
            "assinatura": {
                "id": order_data.get("subscription_id"),
                "intervalo": None,  # Orders não têm intervalo
                "situacao": None
            },
            
            # Dados originais para referência
            "dados_originais": order_data
        }
    
    @staticmethod
    def mapear_subscription_ticto(subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapeia dados de subscription da API Ticto para formato interno
        """
        customer = subscription_data.get("customer", {})
        product = subscription_data.get("product", {})
        order = subscription_data.get("order", {})
        
        # Converte valores de centavos para reais
        price = subscription_data.get("price", 0) / 100 if subscription_data.get("price") else 0
        first_charge_price = subscription_data.get("first_charge_price", 0) / 100 if subscription_data.get("first_charge_price") else 0
        
        # Calcula valores mensais e anuais baseado no ID do produto
        product_id = product.get("id")
        from utils.helpers import calcular_valores_assinatura_por_tipo
        
        # Usa a função consolidada para calcular valores corretos
        valor_mensal, valor_anual = calcular_valores_assinatura_por_tipo(price, product_id, "ticto")
        
        # Determina status baseado na situação
        situation = subscription_data.get("situation", "Ativa")
        status_mapping = {
            "Ativa": "active",
            "Cancelada": "canceled",
            "Atrasada": "delayed",
            "Pendente": "waiting_payment"
        }
        status = status_mapping.get(situation, "active")
        
        # Extrai informações de recusa das transações
        tipo_recusa = None
        motivo_recusa = None
        transactions = subscription_data.get("transactions", [])
        if transactions:
            latest_transaction = transactions[0]
            if latest_transaction.get("status") == "refused":
                tipo_recusa = "recusada_primeira_venda" if latest_transaction.get("occurrence", 0) == 1 else "recusada_cobranca_assinatura"
                motivo_recusa = latest_transaction.get("refused_reason")
        
        return {
            # Dados da assinatura
            "id_assinatura_origem": str(subscription_data.get("id")),
            "status": status,
            "data_inicio": order.get("created_at"),
            "data_proxima_cobranca": subscription_data.get("next_charge"),
            "data_cancelamento": subscription_data.get("canceled_at"),
            "valor_mensal": valor_mensal,
            "valor_anual": valor_anual,
            
            # Dados da transação associada (não usado no backfill, apenas para referência)
            "transacao": {
                "id_transacao_origem": order.get("hash"),
                "status": status,
                "valor": price,
                "valor_bruto": price,
                "valor_liquido": price,  # Para subscriptions, valor líquido = valor total (sem comissão)
                "metodo_pagamento": subscription_data.get("payment_method"),
                "motivo_recusa": motivo_recusa,
                "tipo_recusa": tipo_recusa,
                "data_transacao": subscription_data.get("updated_at")
            },
            
            # Dados do cliente
            "cliente": {
                "nome": customer.get("name"),
                "email": customer.get("email"),
                "documento": customer.get("cpf") or customer.get("cnpj"),
                "data_criacao": order.get("created_at")
            },
            
            # Dados do produto
            "produto": {
                "nome": product.get("name"),
                "id": product.get("id")
            },
            
            # Dados da ordem
            "ordem": {
                "id": order.get("id"),
                "hash": order.get("hash")
            },
            
            # Dados específicos da assinatura
            "assinatura": {
                "intervalo": subscription_data.get("interval", 12),
                "situacao": situation,
                "melhor_dia_cobranca": subscription_data.get("best_day_to_charge"),
                "cobrancas_sucesso": subscription_data.get("successful_charges"),
                "cobrancas_falha": subscription_data.get("failed_charges")
            },
            
            # Dados originais para referência
            "dados_originais": subscription_data
        }

class MapeamentoBackfillGuru:
    """
    Mapeamento de dados históricos da API Guru para o formato interno do banco
    """
    
    @staticmethod
    def mapear_transaction_guru(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapeia dados de transaction da API Guru para formato interno
        """
        contact = transaction_data.get("contact", {})
        payment = transaction_data.get("payment", {})
        invoice = transaction_data.get("invoice", {})
        items = transaction_data.get("items", [])
        subscription = transaction_data.get("subscription", {})
        dates = transaction_data.get("dates", {})
        
        # Pega o primeiro item (produto principal)
        item = items[0] if items else {}
        
        # Converte valores
        valor_total = payment.get("total", 0)
        valor_bruto = payment.get("gross", 0)
        valor_liquido = payment.get("net", 0)
        
        # Determina status
        status = transaction_data.get("status", "approved")
        
        # Extrai informações de recusa
        motivo_recusa = None
        if status == "refused":
            motivo_recusa = payment.get("refuse_reason")
        
        # Converte timestamps para ISO se necessário
        def converter_timestamp(timestamp):
            if isinstance(timestamp, int):
                from datetime import datetime, timezone
                return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
            elif isinstance(timestamp, str):
                # Se já é string ISO, apenas garante que tem timezone
                if timestamp.endswith('Z'):
                    return timestamp.replace('Z', '+00:00')
                elif '+' not in timestamp and '-' in timestamp:
                    # Assume UTC se não tem timezone
                    return timestamp + '+00:00'
                return timestamp
            return timestamp
        
        # Dados da assinatura (se aplicável)
        # Tratamento especial para subscription que pode ser lista ou dict
        subscription_data = {}
        if isinstance(subscription, list) and len(subscription) > 0:
            subscription_data = subscription[0]
        elif isinstance(subscription, dict):
            subscription_data = subscription
        
        return {
            # Dados da transação
            "id_transacao_origem": payment.get("marketplace_id"),  # Corrigido: usa marketplace_id do payment
            "status": status,
            "valor": valor_total,
            "valor_bruto": valor_bruto,
            "valor_liquido": valor_liquido,
            "metodo_pagamento": payment.get("method"),
            "motivo_recusa": motivo_recusa,
            "data_transacao": converter_timestamp(dates.get("created_at")),
            "produto_nome": item.get("name") if item else None,
            "nome_oferta": item.get("offer", {}).get("name") if item and item.get("offer") else None,
            
            # Dados do cliente
            "cliente": {
                "nome": contact.get("name"),
                "email": contact.get("email"),
                "documento": contact.get("doc"),
                "data_criacao": converter_timestamp(dates.get("created_at"))
            },
            
            # Dados do produto
            "produto": {
                "nome": item.get("name") if item else None,
                "id": item.get("id") if item else None,
                "internal_id": item.get("internal_id") if item else None,
                "marketplace_id": item.get("marketplace_id") if item else None,  # Adicionado marketplace_id do produto
                "tipo": item.get("type") if item else None
            },
            
            # Dados da oferta
            "oferta": {
                "nome": item.get("offer", {}).get("name") if item and item.get("offer") else None,
                "id": item.get("offer", {}).get("id") if item and item.get("offer") else None
            },
            
            # Dados da assinatura (se aplicável)
            "assinatura": {
                "id": subscription_data.get("id"),
                "subscription_code": subscription_data.get("subscription_code"),
                "intervalo": subscription_data.get("charged_every_days"),
                "situacao": subscription_data.get("last_status")
            },
            
            # Dados originais para referência
            "dados_originais": transaction_data
        }
    
    @staticmethod
    def mapear_subscription_guru(subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapeia dados de subscription da API Guru para formato interno
        """
        contact = subscription_data.get("contact", {})
        product = subscription_data.get("product", {})
        
        # Converte timestamps para ISO se necessário
        def converter_timestamp(timestamp):
            if isinstance(timestamp, int):
                from datetime import datetime, timezone
                return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
            elif isinstance(timestamp, str):
                # Se já é string ISO, apenas garante que tem timezone
                if timestamp.endswith('Z'):
                    return timestamp.replace('Z', '+00:00')
                elif '+' not in timestamp and '-' in timestamp:
                    # Assume UTC se não tem timezone
                    return timestamp + '+00:00'
                return timestamp
            return timestamp
        
        # Determina status
        status = subscription_data.get("last_status", "active")
        
        # Calcula valores baseados no ID do produto
        product_id = str(product.get("id", ""))
        from utils.helpers import calcular_valores_assinatura_por_tipo
        
        # Usa dados enriquecidos se disponível
        enriched_values = subscription_data.get("enriched_values", {})
        unit_value = enriched_values.get("unit_value", 0)
        
        # Debug: verifica os valores
        print(f"[MAPEAMENTO] product_id: {product_id}")
        print(f"[MAPEAMENTO] unit_value: {unit_value}, tipo: {type(unit_value)}")
        
        # Garante que unit_value é um número válido
        if unit_value and isinstance(unit_value, (int, float)) and unit_value > 0:
            # Usa a função consolidada para calcular valores corretos
            valor_mensal, valor_anual = calcular_valores_assinatura_por_tipo(float(unit_value), product_id, "guru")
        else:
            print(f"[MAPEAMENTO] unit_value inválido ou zero: {unit_value}")
            # Usa valores padrão baseados no tipo de plano
            charged_every_days = subscription_data.get("charged_every_days", 30)
            if charged_every_days == 365:
                valor_mensal, valor_anual = calcular_valores_assinatura_por_tipo(1164.00, product_id, "guru")
                print(f"[MAPEAMENTO] Usando valor padrão anual: R$ 1164.00")
            else:
                valor_mensal, valor_anual = calcular_valores_assinatura_por_tipo(97.00, product_id, "guru")
                print(f"[MAPEAMENTO] Usando valor padrão mensal: R$ 97.00")
        
        return {
            # Dados da assinatura
            "id_assinatura_origem": subscription_data.get("subscription_code"),
            "subscription_code": subscription_data.get("subscription_code"),
            "status": status,
            "intervalo": charged_every_days,
            "situacao": status,
            "data_inicio": converter_timestamp(subscription_data.get("started_at")),
            "data_proxima_cobranca": subscription_data.get("next_cycle_at"),
            "data_cancelamento": converter_timestamp(subscription_data.get("cancelled_at")),
            "data_expiracao_acesso": subscription_data.get("cycle_end_date"),
            "valor_mensal": valor_mensal,
            "valor_anual": valor_anual,
            "ultima_atualizacao": converter_timestamp(subscription_data.get("updated_at")),
            
            # Dados do cliente
            "cliente": {
                "nome": contact.get("name"),
                "email": contact.get("email"),
                "documento": contact.get("doc"),
                "data_criacao": converter_timestamp(subscription_data.get("created_at"))
            },
            
            # Dados do produto
            "produto": {
                "nome": product.get("name"),
                "id": product.get("id"),
                "marketplace_id": product.get("marketplace_id")
            },
            
            # Dados específicos da assinatura
            "assinatura": {
                "intervalo": subscription_data.get("charged_every_days", 30),
                "situacao": status,
                "charged_times": subscription_data.get("charged_times", 1),
                "payment_method": subscription_data.get("payment_method"),
                "is_cycling": subscription_data.get("is_cycling", False)
            },
            
            # Dados originais para referência
            "dados_originais": subscription_data
        }

def converter_data_backfill(data_string: str) -> Optional[datetime]:
    """
    Converte strings de data da API para datetime
    Suporta múltiplos formatos encontrados nas APIs
    """
    if not data_string:
        return None
    
    try:
        # Formato ISO: "2026-07-25T03:00:00.000000Z"
        if "T" in data_string and "Z" in data_string:
            return datetime.fromisoformat(data_string.replace("Z", "+00:00"))
        
        # Formato brasileiro: "25/07/2025 17:30:13"
        if "/" in data_string and ":" in data_string:
            return datetime.strptime(data_string, "%d/%m/%Y %H:%M:%S")
        
        # Formato simples: "2025-07-25"
        if len(data_string) == 10 and "-" in data_string:
            return datetime.strptime(data_string, "%Y-%m-%d")
        
        # Fallback: tenta parse automático
        return datetime.fromisoformat(data_string)
        
    except Exception as e:
        print(f"Erro ao converter data '{data_string}': {e}")
        return None 