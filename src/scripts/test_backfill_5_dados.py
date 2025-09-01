"""
Script de teste para validar o backfill com apenas 5 dados da API Ticto
Usa o novo HistoricalDataProcessor e processa apenas 5 orders e 5 subscriptions
"""
import sys
import os
from typing import Dict, List, Any

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.ticto_api_client import TictoAPIClient
from scripts.backfill_utils import setup_logging, create_backup_log, format_progress
from services.data_processor import HistoricalDataProcessor

class TictoBackfillTest5Dados:
    def __init__(self):
        self.logger = setup_logging("ticto_backfill_test_5_dados")
        self.api_client = TictoAPIClient()
        self.data_processor = HistoricalDataProcessor()
        
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
        Processa uma order individual usando o novo processador
        """
        try:
            # Processa usando o novo HistoricalDataProcessor
            result = self.data_processor.process_ticto_order(order_data)
            
            if result.get("status") == "erro":
                self.logger.error(f"Erro ao processar order {order_data.get('id')}: {result.get('motivo')}")
                self.stats["errors"] += 1
                return False
            
            self.stats["orders_processed"] += 1
            
            # Log de sucesso
            if "transacao_criada" in result.get("status", ""):
                self.stats["orders_created"] += 1
                self.logger.info(f"✅ Order {order_data.get('id')} criada com sucesso")
            elif "transacao_atualizada" in result.get("status", ""):
                self.stats["orders_updated"] += 1
                self.logger.info(f"🔄 Order {order_data.get('id')} atualizada")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao processar order {order_data.get('id')}: {e}")
            self.stats["errors"] += 1
            return False
    
    def process_subscription(self, subscription_data: Dict[str, Any]) -> bool:
        """
        Processa uma subscription individual usando o novo processador
        """
        try:
            # Processa usando o novo HistoricalDataProcessor
            result = self.data_processor.process_ticto_subscription(subscription_data)
            
            if result.get("status") == "erro":
                self.logger.error(f"Erro ao processar subscription {subscription_data.get('id')}: {result.get('motivo')}")
                self.stats["errors"] += 1
                return False
            
            self.stats["subscriptions_processed"] += 1
            
            # Log de sucesso
            if "assinatura_criada" in result.get("status", ""):
                self.stats["subscriptions_created"] += 1
                self.logger.info(f"✅ Subscription {subscription_data.get('id')} criada com sucesso")
            elif "assinatura_atualizada" in result.get("status", ""):
                self.stats["subscriptions_updated"] += 1
                self.logger.info(f"🔄 Subscription {subscription_data.get('id')} atualizada")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao processar subscription {subscription_data.get('id')}: {e}")
            self.stats["errors"] += 1
            return False
    
    def run_test_backfill_5_dados(self):
        """
        Executa o backfill de teste com apenas 5 orders e 5 subscriptions
        """
        self.logger.info("🧪 Iniciando backfill de teste da Ticto (5 dados)")
        
        try:
            # 1. Autentica com a API
            if not self.api_client.authenticate():
                self.logger.error("❌ Falha na autenticação com a API Ticto")
                return False
            
            # 2. Busca primeira página de orders e processa apenas 5
            self.logger.info("📦 Buscando primeira página de orders...")
            orders_response = self.api_client.get_orders_history(1)
            
            if orders_response and orders_response.get("data"):
                orders = orders_response.get("data", [])
                # Limita a apenas 5 orders
                orders_to_process = orders[:5]
                self.logger.info(f"📊 Processando apenas {len(orders_to_process)} orders (limitado a 5)...")
                
                for i, order in enumerate(orders_to_process, 1):
                    self.process_order(order)
                    self.logger.info(f"📦 Order {i}/{len(orders_to_process)} processada")
                
                # Backup dos dados processados
                create_backup_log({"orders": orders_to_process}, "ticto_orders_test_5_dados_backup")
            
            # 3. Busca primeira página de subscriptions e processa apenas 5
            self.logger.info("📋 Buscando primeira página de subscriptions...")
            subscriptions_response = self.api_client.get_subscriptions_history(1)
            
            if subscriptions_response and subscriptions_response.get("data"):
                subscriptions = subscriptions_response.get("data", [])
                # Limita a apenas 5 subscriptions
                subscriptions_to_process = subscriptions[:5]
                self.logger.info(f"📊 Processando apenas {len(subscriptions_to_process)} subscriptions (limitado a 5)...")
                
                for i, subscription in enumerate(subscriptions_to_process, 1):
                    self.process_subscription(subscription)
                    self.logger.info(f"📋 Subscription {i}/{len(subscriptions_to_process)} processada")
                
                # Backup dos dados processados
                create_backup_log({"subscriptions": subscriptions_to_process}, "ticto_subscriptions_test_5_dados_backup")
            
            # 4. Relatório final
            self.print_final_report()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro durante backfill de teste: {e}")
            return False
        finally:
            # Fecha a sessão do processador
            self.data_processor.close_session()
    
    def print_final_report(self):
        """
        Imprime relatório final do backfill
        """
        self.logger.info("=" * 50)
        self.logger.info("📊 RELATÓRIO FINAL DO BACKFILL DE TESTE (5 DADOS)")
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
    Função principal para executar o backfill de teste com 5 dados
    """
    print("🧪 Iniciando Backfill de Teste da Ticto (5 dados)")
    print("=" * 50)
    
    # Executa backfill de teste
    backfill_test = TictoBackfillTest5Dados()
    success = backfill_test.run_test_backfill_5_dados()
    
    if success:
        print("✅ Backfill de teste (5 dados) concluído com sucesso!")
        print("🎯 Agora você pode executar o backfill completo com segurança")
    else:
        print("❌ Backfill de teste (5 dados) falhou!")
        sys.exit(1)

if __name__ == "__main__":
    main() 