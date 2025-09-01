"""
Script de teste para validar o backfill com apenas 5 dados da API Guru
Processa apenas 5 transactions e 5 subscriptions para teste rápido
"""
import sys
import os
from typing import Dict, List, Any
from datetime import datetime, timedelta

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.guru_api_client import GuruAPIClient
from scripts.backfill_utils import setup_logging, create_backup_log, format_progress
from services.webhook_handler import processar_guru_transacao, processar_guru_assinatura
from utils.mapeamento_backfill import MapeamentoBackfillGuru

class GuruBackfillTest5Dados:
    def __init__(self):
        self.logger = setup_logging("guru_backfill_test_5_dados")
        self.api_client = GuruAPIClient()
        self.mapeador = MapeamentoBackfillGuru()
        
        # Estatísticas
        self.stats = {
            "transactions_processed": 0,
            "transactions_created": 0,
            "transactions_updated": 0,
            "subscriptions_processed": 0,
            "subscriptions_created": 0,
            "subscriptions_updated": 0,
            "errors": 0
        }
    
    def process_transaction(self, transaction_data: Dict[str, Any]) -> bool:
        """
        Processa uma transação individual usando o novo mapeamento
        """
        try:
            print(f"[DEBUG] Processando transação ID: {transaction_data.get('id')}")
            
            # Usa o novo mapeamento para converter dados da API
            mapeado = self.mapeador.mapear_transaction_guru(transaction_data)
            print(f"[DEBUG] Mapeamento concluído: {mapeado}")
            
            # Converte para formato de webhook
            webhook_payload = self.convert_transaction_to_webhook(mapeado)
            print(f"[DEBUG] Webhook convertido: {webhook_payload}")
            
            # Processa usando a lógica existente
            result = processar_guru_transacao(webhook_payload)
            
            if result.get("status") == "erro":
                self.logger.error(f"Erro ao processar transação {transaction_data.get('id')}: {result.get('motivo')}")
                self.stats["errors"] += 1
                return False
            
            self.stats["transactions_processed"] += 1
            
            # Log de sucesso
            if result.get("status") == "criada":
                self.stats["transactions_created"] += 1
                self.logger.info(f"✅ Transação {transaction_data.get('id')} criada com sucesso")
            elif result.get("status") == "atualizada":
                self.stats["transactions_updated"] += 1
                self.logger.info(f"🔄 Transação {transaction_data.get('id')} atualizada")
            elif result.get("status") == "ja_existente":
                self.logger.info(f"ℹ️ Transação {transaction_data.get('id')} já existente")
            
            return True
            
        except Exception as e:
            import traceback
            self.logger.error(f"❌ Erro ao processar transação {transaction_data.get('id')}: {e}")
            self.logger.error(f"❌ Traceback: {traceback.format_exc()}")
            self.stats["errors"] += 1
            return False
    
    def process_subscription(self, subscription_data: Dict[str, Any]) -> bool:
        """
        Processa uma assinatura individual usando o novo mapeamento
        """
        try:
            # Usa o novo mapeamento para converter dados da API
            mapeado = self.mapeador.mapear_subscription_guru(subscription_data)
            
            # Converte para formato de webhook
            webhook_payload = self.convert_subscription_to_webhook(mapeado)
            
            # Processa usando a lógica existente
            result = processar_guru_assinatura(webhook_payload)
            
            if result.get("status") == "erro":
                self.logger.error(f"Erro ao processar assinatura {subscription_data.get('id')}: {result.get('motivo')}")
                self.stats["errors"] += 1
                return False
            
            self.stats["subscriptions_processed"] += 1
            
            # Log de sucesso
            if "assinatura_id" in result:
                self.stats["subscriptions_created"] += 1
                self.logger.info(f"✅ Assinatura {subscription_data.get('id')} criada com sucesso")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao processar assinatura {subscription_data.get('id')}: {e}")
            self.stats["errors"] += 1
            return False
    
    def convert_transaction_to_webhook(self, mapeado: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converte dados mapeados para formato de webhook
        """
        webhook_data = {
            "webhook_type": "transaction",
            "id": mapeado["id_transacao_origem"],  # Agora usa payment.marketplace_id
            "status": mapeado["status"],
            "contact": {
                "name": mapeado["cliente"]["nome"],
                "email": mapeado["cliente"]["email"],
                "doc": mapeado["cliente"]["documento"]
            },
            "payment": {
                "total": mapeado["valor"],
                "gross": mapeado["valor_bruto"],
                "net": mapeado["valor_liquido"],
                "method": mapeado["metodo_pagamento"],
                "refuse_reason": mapeado.get("motivo_recusa"),
                "marketplace_id": mapeado["id_transacao_origem"]  # Adicionado marketplace_id
            },
            "product": {
                "name": mapeado["produto_nome"],
                "id": mapeado["produto"]["id"]
            },
            "items": [{
                "name": mapeado["produto_nome"],
                "id": mapeado["produto"]["id"],
                "internal_id": mapeado["produto"]["internal_id"],
                "marketplace_id": mapeado["produto"]["marketplace_id"],  # Adicionado marketplace_id do produto
                "offer": {
                    "name": mapeado["nome_oferta"],
                    "id": mapeado["oferta"]["id"]
                }
            }],
            "dates": {
                "created_at": mapeado["data_transacao"],
                "confirmed_at": mapeado["data_transacao"]
            },
            "subscription": mapeado["assinatura"] if mapeado["assinatura"]["id"] else None
        }
        
        return webhook_data
    
    def convert_subscription_to_webhook(self, mapeado: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converte dados mapeados para formato de webhook
        """
        webhook_data = {
            "webhook_type": "subscription",
            "id": mapeado["id_assinatura_origem"],
            "subscription_code": mapeado["subscription_code"],
            "last_status": mapeado["status"],
            "charged_every_days": mapeado["intervalo"],
            "charged_times": mapeado["assinatura"]["charged_times"],
            "contact": {
                "name": mapeado["cliente"]["nome"],
                "email": mapeado["cliente"]["email"],
                "doc": mapeado["cliente"]["documento"]
            },
            "product": {
                "name": mapeado["produto"]["nome"],
                "id": mapeado["produto"]["id"]
            },
            "dates": {
                "started_at": mapeado["data_inicio"],
                "last_status_at": mapeado["ultima_atualizacao"],
                "next_cycle_at": mapeado["data_proxima_cobranca"],
                "canceled_at": mapeado["data_cancelamento"],
                "cycle_end_date": mapeado["data_expiracao_acesso"]
            },
            "subscriber": {
                "name": mapeado["cliente"]["nome"],
                "email": mapeado["cliente"]["email"],
                "doc": mapeado["cliente"]["documento"]
            },
            "current_invoice": {
                "value": mapeado["valor_mensal"] if mapeado["valor_mensal"] is not None else 0  # Guru já vem em reais
            }
        }
        
        return webhook_data
    
    def run_test_backfill_5_dados(self):
        """
        Executa o backfill de teste com apenas 5 transactions e 5 subscriptions
        """
        self.logger.info("🧪 Iniciando backfill de teste da Guru (5 dados)")
        
        try:
            # 1. Busca 5 transações (últimos 7 dias)
            print("💰 Buscando 5 transações...")
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            transactions_data = self.api_client.get_transactions(start_date, end_date)
            
            if transactions_data:
                transactions = transactions_data.get("data", [])
                # Limita a 5 transações
                test_transactions = transactions[:5]
                
                print(f"📦 Processando {len(test_transactions)} transações...")
                for i, transaction in enumerate(test_transactions, 1):
                    self.process_transaction(transaction)
                    print(f"   {i}/{len(test_transactions)} - {transaction.get('id')}")
            else:
                print("⚠️ Nenhuma transação encontrada no período")
            
            # 2. Busca 5 assinaturas
            print("\n📋 Buscando 5 assinaturas...")
            # Usa o novo método que implementa cursor-based pagination
            all_subscriptions = self.api_client.get_all_subscriptions()
            
            if all_subscriptions:
                # Limita a 5 assinaturas para teste
                test_subscriptions = all_subscriptions[:5]
                
                print(f"📋 Processando {len(test_subscriptions)} assinaturas...")
                for i, subscription in enumerate(test_subscriptions, 1):
                    self.process_subscription(subscription)
                    print(f"   {i}/{len(test_subscriptions)} - {subscription.get('id')}")
            else:
                print("⚠️ Nenhuma assinatura encontrada")
            
            # 3. Cria backup dos dados processados
            backup_data = {
                "test_type": "guru_backfill_5_dados",
                "period": {"start": start_date, "end": end_date},
                "transactions_count": len(test_transactions) if 'test_transactions' in locals() else 0,
                "subscriptions_count": len(test_subscriptions) if 'test_subscriptions' in locals() else 0,
                "stats": self.stats,
                "timestamp": datetime.now().isoformat()
            }
            
            create_backup_log(backup_data, "guru_backfill_test_5_dados")
            
            print("\n✅ Teste de backfill concluído!")
            self.print_final_report()
            
        except Exception as e:
            self.logger.error(f"❌ Erro durante teste de backfill: {e}")
            print(f"❌ Erro durante teste de backfill: {e}")
    
    def print_final_report(self):
        """
        Imprime relatório final do teste
        """
        print("\n" + "="*50)
        print("📊 RELATÓRIO FINAL - TESTE BACKFILL GURU (5 DADOS)")
        print("="*50)
        print(f"💰 Transações processadas: {self.stats['transactions_processed']}")
        print(f"   ├─ Criadas: {self.stats['transactions_created']}")
        print(f"   └─ Atualizadas: {self.stats['transactions_updated']}")
        print(f"📋 Assinaturas processadas: {self.stats['subscriptions_processed']}")
        print(f"   ├─ Criadas: {self.stats['subscriptions_created']}")
        print(f"   └─ Atualizadas: {self.stats['subscriptions_updated']}")
        print(f"❌ Erros: {self.stats['errors']}")
        print("="*50)

def main():
    """
    Função principal para executar o teste
    """
    print("🧪 Iniciando teste de backfill da Guru (5 dados)")
    
    test = GuruBackfillTest5Dados()
    test.run_test_backfill_5_dados()

if __name__ == "__main__":
    main() 