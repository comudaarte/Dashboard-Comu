"""
Script de Backfill Histórico da Ticto
Busca dados históricos da API e insere no banco de dados
"""
import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Any

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.ticto_api_client import TictoAPIClient
from scripts.backfill_utils import setup_logging, create_backup_log, format_progress
from services.webhook_handler import processar_ticto
from database.connection import get_session
from database.models import Cliente, Assinatura, Transacao

class TictoBackfill:
    def __init__(self):
        self.logger = setup_logging("ticto_backfill")
        self.api_client = TictoAPIClient()
        self.session = get_session()
        
        # Estatísticas
        self.stats = {
            "orders_processed": 0,
            "orders_created": 0,
            "orders_updated": 0,
            "subscriptions_processed": 0,
            "subscriptions_created": 0,
            "subscriptions_updated": 0,
            "errors": 0
        }
    
    def process_order(self, order_data: Dict[str, Any]) -> bool:
        """
        Processa uma order individual e insere/atualiza no banco
        """
        try:
            # Simula um webhook para usar a lógica existente
            webhook_payload = self.convert_order_to_webhook(order_data)
            
            # Processa usando a lógica existente
            result = processar_ticto(webhook_payload)
            
            if result.get("status") == "erro":
                self.logger.error(f"Erro ao processar order {order_data.get('id')}: {result.get('motivo')}")
                self.stats["errors"] += 1
                return False
            
            self.stats["orders_processed"] += 1
            
            # Log de sucesso
            if "transacao" in result:
                self.stats["orders_created"] += 1
                self.logger.info(f"✅ Order {order_data.get('id')} criada com sucesso")
            elif "transacao_atualizada" in result:
                self.stats["orders_updated"] += 1
                self.logger.info(f"🔄 Order {order_data.get('id')} atualizada")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao processar order {order_data.get('id')}: {e}")
            self.stats["errors"] += 1
            return False
    
    def process_subscription(self, subscription_data: Dict[str, Any]) -> bool:
        """
        Processa uma subscription individual e insere/atualiza no banco
        """
        try:
            # Simula um webhook para usar a lógica existente
            webhook_payload = self.convert_subscription_to_webhook(subscription_data)
            
            # Processa usando a lógica existente
            result = processar_ticto(webhook_payload)
            
            if result.get("status") == "erro":
                self.logger.error(f"Erro ao processar subscription {subscription_data.get('id')}: {result.get('motivo')}")
                self.stats["errors"] += 1
                return False
            
            self.stats["subscriptions_processed"] += 1
            
            # Log de sucesso
            if "assinatura" in result:
                self.stats["subscriptions_created"] += 1
                self.logger.info(f"✅ Subscription {subscription_data.get('id')} criada com sucesso")
            elif "assinatura_atualizada" in result:
                self.stats["subscriptions_updated"] += 1
                self.logger.info(f"🔄 Subscription {subscription_data.get('id')} atualizada")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao processar subscription {subscription_data.get('id')}: {e}")
            self.stats["errors"] += 1
            return False
    
    def convert_order_to_webhook(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converte dados da API de order para formato de webhook
        """
        # Extrai dados da transação
        transaction = order_data.get("transaction", {})
        
        # Determina o status baseado na transação
        status = transaction.get("status", "authorized")
        
        # Converte valores de centavos para reais
        paid_amount = transaction.get("paid_amount", 0) / 100 if transaction.get("paid_amount") else 0
        order_item_amount = order_data.get("order_item", {}).get("amount", 0) / 100 if order_data.get("order_item", {}).get("amount") else 0
        
        # Calcula valor líquido (comissão do produtor)
        commission = order_data.get("commission", 0) / 100 if order_data.get("commission") else 0
        valor_liquido = paid_amount - commission if paid_amount > 0 else None
        
        # Extrai método de pagamento e informações de recusa
        metodo_pagamento = transaction.get("payment_method")
        tipo_recusa = None
        motivo_recusa = None
        
        if transaction.get("status") == "refused":
            tipo_recusa = "recusada_primeira_venda" if transaction.get("occurrence", 0) == 1 else "recusada_cobranca_assinatura"
            motivo_recusa = transaction.get("refused_label") or transaction.get("refused_reason")
        
        webhook = {
            "status": status,
            "order": {
                "id": order_data.get("order", {}).get("id"),
                "hash": order_data.get("order", {}).get("hash"),
                "transaction_hash": transaction.get("hash"),
                "order_date": order_data.get("created_at"),
                "paid_amount": paid_amount
            },
            "customer": {
                "name": order_data.get("customer", {}).get("name"),
                "email": order_data.get("customer", {}).get("email"),
                "cpf": order_data.get("customer", {}).get("cpf")
            },
            "item": {
                "product_name": order_data.get("product", {}).get("name"),
                "product_id": order_data.get("product", {}).get("id"),
                "amount": order_item_amount
            },
            "subscriptions": [],  # Orders normais não têm assinaturas
            "payment_method": metodo_pagamento,
            "status_date": transaction.get("updated_at") or order_data.get("updated_at"),
            "transaction": {
                "hash": transaction.get("hash"),
                "status": status,
                "return_code": transaction.get("return_code"),
                "refused_reason": transaction.get("refused_reason"),
                "refused_label": transaction.get("refused_label"),
                "paid_amount": paid_amount,
                "created_at": transaction.get("created_at"),
                "updated_at": transaction.get("updated_at")
            },
            "producer": {
                "cms": commission
            },
            "tipo_recusa": tipo_recusa,
            "motivo_recusa": motivo_recusa
        }
        
        return webhook
    
    def convert_subscription_to_webhook(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converte dados da API de subscription para formato de webhook
        """
        # Converte valores de centavos para reais
        price = subscription_data.get("price", 0) / 100 if subscription_data.get("price") else 0
        first_charge_price = subscription_data.get("first_charge_price", 0) / 100 if subscription_data.get("first_charge_price") else 0
        
        # Extrai método de pagamento e informações de recusa
        metodo_pagamento = subscription_data.get("payment_method")
        tipo_recusa = None
        motivo_recusa = None
        
        # Verifica se há transações recusadas
        transactions = subscription_data.get("transactions", [])
        if transactions:
            latest_transaction = transactions[0]  # Assume que a primeira é a mais recente
            if latest_transaction.get("status") == "refused":
                tipo_recusa = "recusada_primeira_venda" if latest_transaction.get("occurrence", 0) == 1 else "recusada_cobranca_assinatura"
                motivo_recusa = latest_transaction.get("refused_label") or latest_transaction.get("refused_reason")
        
        # Determina status baseado na situação
        situation = subscription_data.get("situation", "Ativa")
        status_mapping = {
            "Ativa": "active",
            "Cancelada": "canceled",
            "Atrasada": "delayed",
            "Pendente": "pending"
        }
        status = status_mapping.get(situation, "active")
        
        # Calcula valores mensais e anuais baseado no intervalo
        interval = subscription_data.get("interval", 12)
        valor_mensal = price / interval if interval > 0 else price
        valor_anual = price if interval == 12 else price
        
        webhook = {
            "status": status,
            "subscriptions": [{
                "id": subscription_data.get("id"),
                "next_charge": subscription_data.get("next_charge"),
                "canceled_at": subscription_data.get("canceled_at"),
                "cancellation_requested_at": subscription_data.get("cancellation_requested_at")
            }],
            "customer": {
                "name": subscription_data.get("customer", {}).get("name"),
                "email": subscription_data.get("customer", {}).get("email"),
                "cpf": subscription_data.get("customer", {}).get("cpf")
            },
            "item": {
                "product_name": subscription_data.get("product", {}).get("name"),
                "product_id": subscription_data.get("product", {}).get("id"),
                "amount": price
            },
            "order": {
                "id": subscription_data.get("order", {}).get("id"),
                "hash": subscription_data.get("order", {}).get("hash"),
                "order_date": subscription_data.get("order", {}).get("created_at"),
                "transaction_hash": subscription_data.get("order", {}).get("hash")  # Usa order.hash como transaction_hash
            },
            "status_date": subscription_data.get("updated_at"),
            "payment_method": metodo_pagamento,
            "subscription_data": {
                "price": price,
                "first_charge_price": first_charge_price,
                "interval": interval,
                "valor_mensal": valor_mensal,
                "valor_anual": valor_anual,
                "best_day_to_charge": subscription_data.get("best_day_to_charge"),
                "successful_charges": subscription_data.get("successful_charges", 0),
                "failed_charges": subscription_data.get("failed_charges", 0),
                "payment_method": subscription_data.get("payment_method")
            },
            "producer": {
                "cms": price  # Para subscriptions, o valor líquido é o mesmo do valor total
            },
            "tipo_recusa": tipo_recusa,
            "motivo_recusa": motivo_recusa
        }
        
        return webhook
    
    def run_backfill(self):
        """
        Executa o backfill completo
        """
        self.logger.info("🚀 Iniciando backfill histórico da Ticto")
        
        try:
            # 1. Autentica com a API
            if not self.api_client.authenticate():
                self.logger.error("❌ Falha na autenticação com a API Ticto")
                return False
            
            # 2. Busca todas as orders
            self.logger.info("📦 Buscando orders históricas...")
            orders = self.api_client.get_all_orders()
            
            if orders:
                self.logger.info(f"📊 Processando {len(orders)} orders...")
                for i, order in enumerate(orders, 1):
                    self.process_order(order)
                    
                    # Log de progresso a cada 10 orders
                    if i % 10 == 0:
                        self.logger.info(format_progress(i, len(orders), "Orders processadas"))
                
                # Backup dos dados
                create_backup_log({"orders": orders}, "ticto_orders_backup")
            
            # 3. Busca todas as subscriptions
            self.logger.info("📋 Buscando subscriptions históricas...")
            subscriptions = self.api_client.get_all_subscriptions()
            
            if subscriptions:
                self.logger.info(f"📊 Processando {len(subscriptions)} subscriptions...")
                for i, subscription in enumerate(subscriptions, 1):
                    self.process_subscription(subscription)
                    
                    # Log de progresso a cada 10 subscriptions
                    if i % 10 == 0:
                        self.logger.info(format_progress(i, len(subscriptions), "Subscriptions processadas"))
                
                # Backup dos dados
                create_backup_log({"subscriptions": subscriptions}, "ticto_subscriptions_backup")
            
            # 4. Relatório final
            self.print_final_report()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro durante backfill: {e}")
            return False
        finally:
            self.session.close()
    
    def print_final_report(self):
        """
        Imprime relatório final do backfill
        """
        self.logger.info("=" * 50)
        self.logger.info("📊 RELATÓRIO FINAL DO BACKFILL TICTO")
        self.logger.info("=" * 50)
        self.logger.info(f"📦 Orders processadas: {self.stats['orders_processed']}")
        self.logger.info(f"   ├─ Criadas: {self.stats['orders_created']}")
        self.logger.info(f"   └─ Atualizadas: {self.stats['orders_updated']}")
        self.logger.info(f"📋 Subscriptions processadas: {self.stats['subscriptions_processed']}")
        self.logger.info(f"   ├─ Criadas: {self.stats['subscriptions_created']}")
        self.logger.info(f"   └─ Atualizadas: {self.stats['subscriptions_updated']}")
        self.logger.info(f"❌ Erros: {self.stats['errors']}")
        self.logger.info("=" * 50)

def main():
    """
    Função principal para executar o backfill
    """
    print("🚀 Iniciando Backfill Histórico da Ticto")
    print("=" * 50)
    
    # Executa backfill
    backfill = TictoBackfill()
    success = backfill.run_backfill()
    
    if success:
        print("✅ Backfill concluído com sucesso!")
    else:
        print("❌ Backfill falhou!")
        sys.exit(1)

if __name__ == "__main__":
    main()
