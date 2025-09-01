#!/usr/bin/env python3
"""
Backfill completo da Ticto usando o novo HistoricalDataProcessor
Processa todas as orders e subscriptions disponíveis na API
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any, List

from src.scripts.ticto_api_client import TictoAPIClient
from src.services.data_processor import HistoricalDataProcessor
from src.scripts.backfill_utils import setup_logging, create_backup_log

class TictoBackfillCompleto:
    """
    Executa o backfill completo da Ticto usando o novo HistoricalDataProcessor
    """
    
    def __init__(self):
        self.logger = setup_logging("ticto_backfill_completo")
        self.api_client = TictoAPIClient()
        self.data_processor = HistoricalDataProcessor()
        self.stats = {
            "orders_processed": 0,
            "orders_created": 0,
            "orders_updated": 0,
            "subscriptions_processed": 0,
            "subscriptions_created": 0,
            "subscriptions_updated": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None
        }
    
    def executar_backfill_completo(self):
        """
        Executa o backfill completo da Ticto
        """
        self.stats["start_time"] = datetime.now()
        self.logger.info("🚀 Iniciando BACKFILL COMPLETO da Ticto")
        self.logger.info("=" * 60)
        
        try:
            # 1. Autenticação
            if not self.api_client.authenticate():
                self.logger.error("❌ Falha na autenticação com a API Ticto")
                return False
            
            self.logger.info("✅ Autenticação Ticto realizada com sucesso")
            
            # 2. Processa todas as orders
            self.processar_todas_orders()
            
            # 3. Processa todas as subscriptions
            self.processar_todas_subscriptions()
            
            # 4. Relatório final
            self.stats["end_time"] = datetime.now()
            self.gerar_relatorio_final()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro fatal no backfill completo: {e}")
            return False
        finally:
            self.data_processor.close_session()
    
    def processar_todas_orders(self):
        """
        Processa todas as orders disponíveis na API
        """
        self.logger.info("📦 Iniciando processamento de todas as orders...")
        
        page = 1
        total_orders = 0
        
        while True:
            try:
                self.logger.info(f"📦 Buscando orders página {page}...")
                orders = self.api_client.get_orders_history(page=page)
                
                if not orders:
                    self.logger.info(f"📦 Nenhuma order encontrada na página {page}. Finalizando...")
                    break
                
                # Extrai os dados da resposta da API
                orders_data = orders.get("data", [])
                if not orders_data:
                    self.logger.info(f"📦 Nenhuma order encontrada na página {page}. Finalizando...")
                    break
                
                self.logger.info(f"📦 Orders página {page}: {len(orders_data)} registros")
                
                # Processa cada order
                for order_data in orders_data:
                    try:
                        result = self.data_processor.process_ticto_order(order_data)
                        
                        if result.get("status") == "transacao_criada":
                            self.stats["orders_created"] += 1
                            self.logger.info(f"✅ Order {order_data.get('id')} criada com sucesso")
                        elif result.get("status") == "transacao_atualizada":
                            self.stats["orders_updated"] += 1
                            self.logger.info(f"🔄 Order {order_data.get('id')} atualizada")
                        else:
                            self.stats["errors"] += 1
                            self.logger.error(f"❌ Erro ao processar order {order_data.get('id')}: {result.get('motivo')}")
                        
                        self.stats["orders_processed"] += 1
                        total_orders += 1
                        
                        # Log a cada 100 orders processadas
                        if total_orders % 100 == 0:
                            self.logger.info(f"📊 Progresso: {total_orders} orders processadas...")
                        
                    except Exception as e:
                        self.stats["errors"] += 1
                        self.logger.error(f"❌ Erro ao processar order {order_data.get('id')}: {e}")
                
                page += 1
                
                # Pequena pausa para não sobrecarregar a API
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"❌ Erro ao buscar orders página {page}: {e}")
                break
        
        self.logger.info(f"📦 Processamento de orders concluído. Total: {total_orders}")
    
    def processar_todas_subscriptions(self):
        """
        Processa todas as subscriptions disponíveis na API
        """
        self.logger.info("📋 Iniciando processamento de todas as subscriptions...")
        
        page = 1
        total_subscriptions = 0
        
        while True:
            try:
                self.logger.info(f"📋 Buscando subscriptions página {page}...")
                subscriptions = self.api_client.get_subscriptions_history(page=page)
                
                if not subscriptions:
                    self.logger.info(f"📋 Nenhuma subscription encontrada na página {page}. Finalizando...")
                    break
                
                # Extrai os dados da resposta da API
                subscriptions_data = subscriptions.get("data", [])
                if not subscriptions_data:
                    self.logger.info(f"📋 Nenhuma subscription encontrada na página {page}. Finalizando...")
                    break
                
                self.logger.info(f"📋 Subscriptions página {page}: {len(subscriptions_data)} registros")
                
                # Processa cada subscription
                for subscription_data in subscriptions_data:
                    try:
                        result = self.data_processor.process_ticto_subscription(subscription_data)
                        
                        if result.get("status") == "assinatura_criada":
                            self.stats["subscriptions_created"] += 1
                            self.logger.info(f"✅ Subscription {subscription_data.get('id')} criada com sucesso")
                        elif result.get("status") == "assinatura_atualizada":
                            self.stats["subscriptions_updated"] += 1
                            self.logger.info(f"🔄 Subscription {subscription_data.get('id')} atualizada")
                        else:
                            self.stats["errors"] += 1
                            self.logger.error(f"❌ Erro ao processar subscription {subscription_data.get('id')}: {result.get('motivo')}")
                        
                        self.stats["subscriptions_processed"] += 1
                        total_subscriptions += 1
                        
                        # Log a cada 50 subscriptions processadas
                        if total_subscriptions % 50 == 0:
                            self.logger.info(f"📊 Progresso: {total_subscriptions} subscriptions processadas...")
                        
                    except Exception as e:
                        self.stats["errors"] += 1
                        self.logger.error(f"❌ Erro ao processar subscription {subscription_data.get('id')}: {e}")
                
                page += 1
                
                # Pequena pausa para não sobrecarregar a API
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"❌ Erro ao buscar subscriptions página {page}: {e}")
                break
        
        self.logger.info(f"📋 Processamento de subscriptions concluído. Total: {total_subscriptions}")
    
    def gerar_relatorio_final(self):
        """
        Gera relatório final do backfill
        """
        duration = self.stats["end_time"] - self.stats["start_time"]
        
        self.logger.info("=" * 60)
        self.logger.info("📊 RELATÓRIO FINAL DO BACKFILL COMPLETO DA TICTO")
        self.logger.info("=" * 60)
        self.logger.info(f"📦 Orders processadas: {self.stats['orders_processed']}")
        self.logger.info(f"   ├─ Criadas: {self.stats['orders_created']}")
        self.logger.info(f"   └─ Atualizadas: {self.stats['orders_updated']}")
        self.logger.info(f"📋 Subscriptions processadas: {self.stats['subscriptions_processed']}")
        self.logger.info(f"   ├─ Criadas: {self.stats['subscriptions_created']}")
        self.logger.info(f"   └─ Atualizadas: {self.stats['subscriptions_updated']}")
        self.logger.info(f"❌ Erros: {self.stats['errors']}")
        self.logger.info(f"⏱️  Duração total: {duration}")
        self.logger.info("=" * 60)
        
        if self.stats["errors"] == 0:
            self.logger.info("🎉 BACKFILL COMPLETO CONCLUÍDO COM SUCESSO!")
        else:
            self.logger.warning(f"⚠️  Backfill concluído com {self.stats['errors']} erros")

def main():
    """
    Função principal
    """
    backfill = TictoBackfillCompleto()
    success = backfill.executar_backfill_completo()
    
    if success:
        print("✅ Backfill completo da Ticto concluído com sucesso!")
    else:
        print("❌ Backfill completo da Ticto falhou!")
        exit(1)

if __name__ == "__main__":
    main()
