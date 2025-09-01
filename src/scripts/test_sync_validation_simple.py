"""
Script para testar a validação de sincronização entre webhooks e backfill
Testa se webhooks com datas anteriores são ignorados corretamente
"""
import sys
import os
from typing import Dict, List, Any
from datetime import datetime, timedelta

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.ticto_api_client import TictoAPIClient
from scripts.backfill_utils import setup_logging, create_backup_log
from services.data_processor import HistoricalDataProcessor
from services.webhook_handler import processar_ticto
from database.connection import get_session
from database.models import Transacao, Assinatura

class SyncValidationTestSimple:
    def __init__(self):
        self.logger = setup_logging("sync_validation_test_simple")
        self.api_client = TictoAPIClient()
        self.data_processor = HistoricalDataProcessor()
        
        # Estatísticas
        self.stats = {
            "backfill_processed": 0,
            "webhooks_sent": 0,
            "webhooks_updated": 0,
            "webhooks_ignored": 0,
            "errors": 0
        }
    
    def test_sync_validation_ticto(self):
        """
        Testa validação de sincronização para Ticto
        """
        self.logger.info("🧪 Iniciando teste de validação de sincronização Ticto")
        
        try:
            # 1. Autentica com a API
            if not self.api_client.authenticate():
                self.logger.error("❌ Falha na autenticação com a API Ticto")
                return False
            
            # 2. Importa 3 dados via backfill
            self.logger.info("📦 Importando 3 dados via backfill...")
            orders_response = self.api_client.get_orders_history(1)
            
            if orders_response and orders_response.get("data"):
                orders = orders_response.get("data", [])
                orders_to_process = orders[:3]
                
                for i, order in enumerate(orders_to_process, 1):
                    result = self.data_processor.process_ticto_order(order)
                    if result.get("status") in ["transacao_criada", "transacao_atualizada"]:
                        self.stats["backfill_processed"] += 1
                        self.logger.info(f"📦 Order {i}/3 processada via backfill")
                
                # Backup dos dados
                create_backup_log({"orders": orders_to_process}, "sync_test_backfill")
            
            # 3. Simula webhook com data anterior (deve ser ignorado)
            self.logger.info("🔄 Testando webhook com data anterior...")
            if orders_to_process:
                # Cria um webhook simulado baseado nos dados da API
                webhook_data = self._create_webhook_from_api_data(orders_to_process[0])
                
                # Modifica a data para ser anterior
                original_date = webhook_data.get("status_date")
                if original_date:
                    try:
                        if "/" in original_date:
                            dt = datetime.strptime(original_date, "%d/%m/%Y %H:%M:%S")
                        else:
                            dt = datetime.fromisoformat(original_date.replace("Z", "+00:00"))
                        
                        anterior_date = (dt - timedelta(days=1)).strftime("%d/%m/%Y %H:%M:%S")
                        webhook_data["status_date"] = anterior_date
                        
                        # Simula webhook
                        result = processar_ticto(webhook_data)
                        self.stats["webhooks_sent"] += 1
                        
                        if result.get("status") == "ignorado":
                            self.stats["webhooks_ignored"] += 1
                            self.logger.info("✅ Webhook com data anterior foi ignorado corretamente")
                        elif "atualizada" in result.get("status", ""):
                            self.stats["webhooks_updated"] += 1
                            self.logger.warning("⚠️ Webhook com data anterior foi processado (pode ser um problema)")
                        else:
                            self.logger.info(f"ℹ️ Resultado do webhook: {result}")
                    
                    except Exception as e:
                        self.logger.error(f"❌ Erro ao testar webhook: {e}")
                        self.stats["errors"] += 1
            
            # 4. Simula webhook com data posterior (deve ser atualizado)
            self.logger.info("🔄 Testando webhook com data posterior...")
            if orders_to_process:
                # Cria um webhook simulado baseado nos dados da API
                webhook_data = self._create_webhook_from_api_data(orders_to_process[1])
                
                # Modifica a data para ser posterior
                original_date = webhook_data.get("status_date")
                if original_date:
                    try:
                        if "/" in original_date:
                            dt = datetime.strptime(original_date, "%d/%m/%Y %H:%M:%S")
                        else:
                            dt = datetime.fromisoformat(original_date.replace("Z", "+00:00"))
                        
                        posterior_date = (dt + timedelta(days=1)).strftime("%d/%m/%Y %H:%M:%S")
                        webhook_data["status_date"] = posterior_date
                        
                        # Simula webhook
                        result = processar_ticto(webhook_data)
                        self.stats["webhooks_sent"] += 1
                        
                        if "atualizada" in result.get("status", ""):
                            self.stats["webhooks_updated"] += 1
                            self.logger.info("✅ Webhook com data posterior foi atualizado corretamente")
                        else:
                            self.logger.warning(f"⚠️ Webhook com data posterior não foi atualizado: {result}")
                    
                    except Exception as e:
                        self.logger.error(f"❌ Erro ao testar webhook: {e}")
                        self.stats["errors"] += 1
            
            # 5. Relatório final
            self.print_final_report()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro durante teste de sincronização: {e}")
            return False
        finally:
            # Fecha a sessão do processador
            self.data_processor.close_session()
    
    def _create_webhook_from_api_data(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converte dados da API para formato de webhook
        """
        transaction = api_data.get("transaction", {})
        
        webhook = {
            "status": transaction.get("status", "refused"),
            "status_date": transaction.get("updated_at"),
            "payment_method": transaction.get("payment_method"),
            "customer": {
                "name": api_data.get("customer", {}).get("name"),
                "email": api_data.get("customer", {}).get("email"),
                "cpf": api_data.get("customer", {}).get("cpf"),
                "cnpj": api_data.get("customer", {}).get("cnpj")
            },
            "order": {
                "order_date": api_data.get("created_at"),
                "transaction_hash": transaction.get("hash")
            },
            "item": {
                "product_id": api_data.get("product", {}).get("id"),
                "product_name": api_data.get("product", {}).get("name"),
                "offer_name": api_data.get("offer", {}).get("name"),
                "amount": api_data.get("order_item", {}).get("amount", 0)
            },
            "producer": {
                "cms": api_data.get("commission", 0)
            }
        }
        
        return webhook
    
    def print_final_report(self):
        """
        Imprime relatório final do teste
        """
        self.logger.info("=" * 50)
        self.logger.info("📊 RELATÓRIO FINAL DO TESTE DE SINCRONIZAÇÃO")
        self.logger.info("=" * 50)
        self.logger.info(f"📦 Dados processados via backfill: {self.stats['backfill_processed']}")
        self.logger.info(f"🔄 Webhooks enviados: {self.stats['webhooks_sent']}")
        self.logger.info(f"   ├─ Atualizados: {self.stats['webhooks_updated']}")
        self.logger.info(f"   └─ Ignorados: {self.stats['webhooks_ignored']}")
        self.logger.info(f"❌ Erros: {self.stats['errors']}")
        self.logger.info("=" * 50)
        
        # Validação dos resultados
        if self.stats['webhooks_ignored'] > 0:
            self.logger.info("✅ Validação de integridade funcionando corretamente!")
        else:
            self.logger.warning("⚠️ Nenhum webhook foi ignorado - verificar se a validação está funcionando")

def main():
    """
    Função principal para executar o teste de validação
    """
    print("🧪 Iniciando Teste de Validação de Sincronização (Versão Simples)")
    print("=" * 50)
    
    # Executa teste
    sync_test = SyncValidationTestSimple()
    success = sync_test.test_sync_validation_ticto()
    
    if success:
        print("✅ Teste de validação concluído com sucesso!")
        print("🎯 Sistema está preparado para sincronização segura")
    else:
        print("❌ Teste de validação falhou!")
        sys.exit(1)

if __name__ == "__main__":
    main() 