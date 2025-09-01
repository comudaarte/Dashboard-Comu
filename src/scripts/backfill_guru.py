"""
Script de backfill histórico da API Guru
Busca dados históricos e insere no banco usando a lógica de webhook existente
"""
import sys
import os
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import argparse

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.guru_api_client import GuruAPIClient
from scripts.backfill_logging import setup_backfill_logging, log_transaction_details, log_subscription_details, log_api_call, log_statistics, create_backup_log, finalize_backfill_logging
from scripts.backfill_utils import format_progress
from services.webhook_handler import processar_guru_transacao, processar_assinatura_guru
from utils.mapeamento_backfill import MapeamentoBackfillGuru

class GuruBackfill:
    def __init__(self, start_date: str = None, end_date: str = None):
        # Configura logging robusto para backfill
        self.logger, self.base_name = setup_backfill_logging("guru_backfill", start_date, end_date)
        
        self.api_client = GuruAPIClient(self.logger)
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
        
        # Timestamp de início para cálculo de duração
        self.start_time = time.time()
    
    def process_transaction(self, transaction_data: Dict[str, Any]) -> bool:
        """
        Processa uma transação individual usando o novo mapeamento
        """
        try:
            # Log detalhado da transação sendo processada
            log_transaction_details(self.logger, transaction_data, "PROCESSAMENTO")
            
            # Usa o novo mapeamento para converter dados da API
            mapeado = self.mapeador.mapear_transaction_guru(transaction_data)
            
            # Converte para formato de webhook
            webhook_payload = self.convert_transaction_to_webhook(mapeado)
            
            # Processa usando a lógica existente
            result = processar_guru_transacao(webhook_payload)
            
            if result.get("status") == "erro":
                self.logger.error(f"❌ Erro ao processar transação {transaction_data.get('id')}: {result.get('motivo')}")
                self.stats["errors"] += 1
                return False
            
            self.stats["transactions_processed"] += 1
            
            # Log de sucesso com resultado
            if result.get("status") == "criada":
                self.stats["transactions_created"] += 1
                log_transaction_details(self.logger, transaction_data, "CRIADA", result)
            elif result.get("status") == "atualizada":
                self.stats["transactions_updated"] += 1
                log_transaction_details(self.logger, transaction_data, "ATUALIZADA", result)
            elif result.get("status") == "ja_existente":
                log_transaction_details(self.logger, transaction_data, "JÁ EXISTENTE", result)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao processar transação {transaction_data.get('id')}: {e}")
            self.stats["errors"] += 1
            return False
    
    def process_subscription(self, subscription_data: Dict[str, Any], start_date: str = None, end_date: str = None):
        """
        Processa uma assinatura individual com enriquecimento de dados
        CORREÇÃO: Agora enriquece DURANTE o processamento usando as datas corretas
        """
        try:
            subscription_id = subscription_data.get("id", "unknown")
            
            # Log detalhado da assinatura sendo processada
            log_subscription_details(self.logger, subscription_data, "PROCESSAMENTO")
            
            # Enriquece dados da assinatura com transações DURANTE o processamento
            contact_id = subscription_data.get("contact", {}).get("id")
            if not contact_id:
                self.logger.warning(f"⚠️ Assinatura {subscription_id} sem contact.id, ignorando")
                return
            
            # CORREÇÃO: Passa as datas para o enriquecimento
            enriched_data = self.enrich_subscription_with_transactions(
                subscription_data, 
                start_date, 
                end_date
            )
            
            if enriched_data:
                # Log dos dados enriquecidos
                log_subscription_details(self.logger, subscription_data, "DADOS ENRIQUECIDOS", enriched_data)
                
                # Processa usando a função do webhook handler
                result = processar_assinatura_guru(enriched_data)
                
                if result.get("status") == "processado_guru_assinatura_hibrido":
                    self.stats["subscriptions_created"] += 1
                    print(f"✅ Assinatura {subscription_id} processada com sucesso")
                else:
                    self.stats["subscriptions_updated"] += 1
                    print(f"🔄 Assinatura {subscription_id} atualizada")
                
                self.stats["subscriptions_processed"] += 1
            else:
                print(f"⚠️ Assinatura {subscription_id} sem dados enriquecidos")
                
        except Exception as e:
            self.stats["errors"] += 1
            print(f"❌ Erro ao processar assinatura {subscription_id}: {e}")
            # Log detalhado do erro mas não para o backfill
            import traceback
            traceback.print_exc()
            # Continua processando outras assinaturas
    
    def enrich_subscription_with_transactions(self, subscription_data: Dict[str, Any], start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """
        Enriquece dados da assinatura com transações relacionadas
        CORREÇÕES IMPLEMENTADAS:
        1. Aceita todos os status de assinatura (active, canceled, expired, inactive)
        2. Usa subscription_id para consultas específicas (não apenas contact_id)
        3. Extrai data_cancelamento de transações canceladas
        4. Extrai nome_oferta do campo product.offer.name
        """
        try:
            contact_id = subscription_data.get("contact", {}).get("id")
            subscription_id = subscription_data.get("id")
            
            if not contact_id or not subscription_id:
                print(f"❌ Dados insuficientes para assinatura {subscription_data.get('id', 'unknown')}")
                print(f"   - Contact ID: {contact_id}")
                print(f"   - Subscription ID: {subscription_id}")
                return None
            
            print(f"🔍 Enriquecendo assinatura {subscription_id} (status: {subscription_data.get('status', 'unknown')})")
            print(f"   - Contato: {contact_id}")
            
            # CORREÇÃO 2: Busca transações específicas da assinatura usando subscription_id
            # Isso garante que pegamos apenas transações relacionadas à assinatura específica
            print(f"🔄 Buscando transações específicas da assinatura {subscription_id}")
            transactions = self.api_client.get_all_transactions_by_subscription(subscription_id)
            
            if not transactions:
                print(f"⚠️ Nenhuma transação encontrada para assinatura {subscription_id}")
                # CORREÇÃO 1: Mesmo sem transações, continua o enriquecimento
                # para assinaturas com status diferentes de "active"
                return self._enrich_without_transactions(subscription_data)
            
            print(f"💰 Total de transações da assinatura {subscription_id}: {len(transactions)} registros")
            
            # CORREÇÃO 1: Aceita todos os status de assinatura para enriquecimento
            subscription_status = subscription_data.get("status", "unknown")
            print(f"📊 Status da assinatura: {subscription_status}")
            
            # Filtra transações válidas e analisa valores
            valid_transactions = []
            total_value = 0
            transaction_count = 0
            # CORREÇÃO 3: Extrai data_cancelamento de múltiplas fontes
            data_cancelamento = None
            nome_oferta = None
            
            print(f"🔍 Analisando transações da assinatura:")
            
            for transaction in transactions:
                transaction_id = transaction.get('id', 'unknown')
                transaction_status = transaction.get('status', 'unknown')
                
                # CORREÇÃO 4: Extrai nome_oferta do campo product.offer.name
                if not nome_oferta:
                    items = transaction.get('items', [])
                    if items and len(items) > 0:
                        offer = items[0].get('offer', {})
                        nome_oferta = offer.get('name')
                        if nome_oferta:
                            print(f"   🏷️ Nome da oferta encontrado: {nome_oferta}")
                
                # Busca data_cancelamento em transações com diferentes status
                if not data_cancelamento:
                    dates = transaction.get('dates', {})
                    # Tenta diferentes campos de data de cancelamento
                    canceled_at = dates.get('canceled_at') or dates.get('cancelled_at') or dates.get('refunded_at')
                    if canceled_at:
                        data_cancelamento = canceled_at
                        print(f"   📅 Data de cancelamento encontrada na transação {transaction_id}: {canceled_at}")
                
                # CORREÇÃO 1: Aceita transações com diferentes status para enriquecimento
                # Diferentes status podem ter informações valiosas
                if transaction_status in ["approved", "paid", "confirmed", "completed", "refunded", "canceled", "expired"]:
                    valid_transactions.append(transaction)
                    
                    # Para cálculo de valores, prioriza transações aprovadas
                    if transaction_status in ["approved", "paid", "confirmed", "completed"]:
                        items = transaction.get('items', [])
                        if items:
                            item = items[0]  # Primeiro item
                            unit_value = item.get('unit_value', 0)
                            total_value += unit_value
                            transaction_count += 1
                            
                            print(f"   ✅ Transação {transaction_id}: Status = '{transaction_status}', Valor = R$ {unit_value}")
                        else:
                            print(f"   ⚠️ Transação {transaction_id} sem items")
                    else:
                        print(f"   ℹ️ Transação {transaction_id}: Status = '{transaction_status}' (usada para dados, não para cálculo)")
                else:
                    print(f"   ❌ Transação {transaction_id} ignorada (status não reconhecido: {transaction_status})")
            
            # 3. Se ainda não encontrou data_cancelamento e o status indica cancelamento, usa fallback
            if not data_cancelamento and subscription_status in ["canceled", "expired", "inactive"]:
                # Usa a data de última atualização como fallback para data de cancelamento
                last_updated = subscription_data.get("updated_at") or subscription_data.get("last_status_at")
                if last_updated:
                    data_cancelamento = last_updated
                    print(f"   📅 Data de cancelamento definida como fallback (última atualização): {data_cancelamento}")
                else:
                    # Último recurso: usa data atual
                    data_cancelamento = datetime.now().isoformat()
                    print(f"   📅 Data de cancelamento definida como data atual (fallback): {data_cancelamento}")
            
            print(f"🔍 Analisando transações da assinatura:")
            
            # Calcula valor médio por transação para determinar valores da assinatura
            unit_value = total_value / transaction_count if transaction_count > 0 else 0
            
            print(f"📊 Resumo das transações válidas:")
            print(f"   - Total de transações para cálculo: {transaction_count}")
            print(f"   - Valor médio por transação: R$ {unit_value}")
            
            # Determina tipo de plano baseado no intervalo
            charged_every_days = subscription_data.get("charged_every_days", 30)
            print(f"   - Intervalo de cobrança: {charged_every_days} dias")
            
            # NOVA LÓGICA: Salva apenas o valor correspondente ao tipo de assinatura
            valor_mensal = None
            valor_anual = None
            
            if unit_value > 0:
                # Usa valores reais das transações da API
                if charged_every_days == 365:
                    # Plano anual: salva APENAS valor_anual
                    valor_anual = unit_value
                    valor_mensal = None  # Não salva valor mensal para planos anuais
                    print(f"✅ Assinatura ANUAL detectada - salvando apenas valor_anual:")
                    print(f"   - Valor anual: R$ {valor_anual:.2f}")
                elif charged_every_days == 30:
                    # Plano mensal: salva APENAS valor_mensal
                    valor_mensal = unit_value
                    valor_anual = None  # Não salva valor anual para planos mensais
                    print(f"✅ Assinatura MENSAL detectada - salvando apenas valor_mensal:")
                    print(f"   - Valor mensal: R$ {valor_mensal:.2f}")
                else:
                    # Outros intervalos: usa valor unitário como base mensal
                    valor_mensal = unit_value
                    valor_anual = None
                    print(f"✅ Assinatura com intervalo personalizado ({charged_every_days} dias) - salvando como valor_mensal:")
                    print(f"   - Valor mensal: R$ {valor_mensal:.2f}")
            else:
                # Se não há transações válidas, tenta extrair valores do payment.installments
                print(f"⚠️ Nenhuma transação válida para cálculo, tentando extrair valores de installments...")
                
                # Busca valores em payment.installments se disponível
                for transaction in transactions:
                    payment = transaction.get('payment', {})
                    installments = payment.get('installments', {})
                    
                    if installments.get('value') and installments.get('qty'):
                        installment_value = installments['value']
                        installment_qty = installments['qty']
                        total_installment_value = installment_value * installment_qty
                        
                        if charged_every_days == 365:
                            # Plano anual: salva APENAS valor_anual
                            valor_anual = total_installment_value
                            valor_mensal = None
                            print(f"✅ Valores extraídos de installments (ANUAL):")
                            print(f"   - Valor da parcela: R$ {installment_value}")
                            print(f"   - Quantidade de parcelas: {installment_qty}")
                            print(f"   - Valor anual: R$ {valor_anual:.2f}")
                        elif charged_every_days == 30:
                            # Plano mensal: salva APENAS valor_mensal
                            valor_mensal = installment_value  # Valor da parcela mensal
                            valor_anual = None
                            print(f"✅ Valores extraídos de installments (MENSAL):")
                            print(f"   - Valor da parcela: R$ {installment_value}")
                            print(f"   - Valor mensal: R$ {valor_mensal:.2f}")
                        else:
                            # Outros intervalos: usa como valor mensal
                            valor_mensal = installment_value
                            valor_anual = None
                            print(f"✅ Valores extraídos de installments (PERSONALIZADO):")
                            print(f"   - Valor da parcela: R$ {installment_value}")
                            print(f"   - Valor mensal: R$ {valor_mensal:.2f}")
                        break
                
                if not valor_mensal and not valor_anual:
                    print(f"⚠️ Não foi possível determinar valores para a assinatura")
                    # CORREÇÃO 1: Continua mesmo sem valores para assinaturas com status diferentes
                    if subscription_status in ["canceled", "expired", "inactive"]:
                        print(f"   ℹ️ Assinatura com status '{subscription_status}' - continuando sem valores")
                    else:
                        print(f"   ❌ Assinatura ativa sem valores - retornando None")
                        return None
            
            # CORREÇÃO 4: Garante que nome_oferta seja extraído
            if not nome_oferta:
                # Tenta extrair do próprio subscription_data
                product = subscription_data.get("product", {})
                nome_oferta = product.get("name")
                if nome_oferta:
                    print(f"   🏷️ Nome da oferta extraído do subscription: {nome_oferta}")
            
            # Retorna payload no formato esperado pela função processar_assinatura_guru
            return {
                "subscription": subscription_data,
                "contact": subscription_data.get("contact", {}),
                "product": subscription_data.get("product", {}),
                "enriched_values": {
                    "unit_value": unit_value,
                    "valor_mensal": valor_mensal,
                    "valor_anual": valor_anual,
                    "total_transactions": transaction_count,
                    "data_cancelamento": data_cancelamento,  # CORREÇÃO 3
                    "nome_oferta": nome_oferta  # CORREÇÃO 4
                }
            }
            
        except Exception as e:
            print(f"❌ Erro ao enriquecer assinatura {subscription_data.get('id', 'unknown')}: {e}")
            return None
    
    def _enrich_without_transactions(self, subscription_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Enriquece assinatura sem transações (para status canceled, expired, inactive)
        CORREÇÃO 1: Permite enriquecimento mesmo sem transações válidas
        CORREÇÃO 3: Extrai data_cancelamento do subscription_data
        """
        try:
            subscription_status = subscription_data.get("status", "unknown")
            print(f"🔄 Enriquecendo assinatura {subscription_data.get('id', 'unknown')} sem transações")
            print(f"   - Status: {subscription_status}")
            
            # CORREÇÃO 4: Extrai nome_oferta do subscription_data
            product = subscription_data.get("product", {})
            nome_oferta = product.get("name")
            if nome_oferta:
                print(f"   🏷️ Nome da oferta: {nome_oferta}")
            
            # CORREÇÃO 3: Extrai data_cancelamento do subscription_data
            data_cancelamento = None
            if subscription_status in ["canceled", "expired", "inactive"]:
                # Tenta extrair de diferentes campos
                data_cancelamento = (
                    subscription_data.get("cancelled_at") or 
                    subscription_data.get("canceled_at") or 
                    subscription_data.get("updated_at") or 
                    subscription_data.get("last_status_at")
                )
                
                if data_cancelamento:
                    print(f"   📅 Data de cancelamento extraída: {data_cancelamento}")
                else:
                    # Fallback: usa data atual
                    data_cancelamento = datetime.now().isoformat()
                    print(f"   📅 Data de cancelamento definida como data atual (fallback): {data_cancelamento}")
            
            # Para assinaturas sem transações, retorna dados básicos
            return {
                "subscription": subscription_data,
                "contact": subscription_data.get("contact", {}),
                "product": subscription_data.get("product", {}),
                "enriched_values": {
                    "unit_value": 0,
                    "valor_mensal": None,
                    "valor_anual": None,
                    "total_transactions": 0,
                    "data_cancelamento": data_cancelamento,  # CORREÇÃO 3: Agora incluída
                    "nome_oferta": nome_oferta
                }
            }
            
        except Exception as e:
            print(f"❌ Erro ao enriquecer assinatura sem transações: {e}")
            return None
    
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
    
    def run_backfill(self, start_date: str = None, end_date: str = None):
        """
        Executa o backfill completo respeitando limites da API
        CORREÇÃO: Implementa fluxo correto: assinaturas enriquecidas primeiro, depois transações
        """
        self.logger.info("�� Iniciando backfill histórico da Guru")
        
        # Define período padrão se não fornecido
        if not start_date:
            start_date = "2025-06-07"  # Data específica solicitada
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        self.logger.info(f"📅 Período total: {start_date} até {end_date}")
        
        try:
            # CORREÇÃO: Fluxo correto implementado
            # 1. Processa assinaturas PRIMEIRO (enriquecendo cada uma com suas transações)
            print("\n📋 Processando assinaturas com enriquecimento...")
            all_subscriptions = self.process_subscriptions_with_rate_limit(start_date, end_date)
            
            if all_subscriptions:
                print(f"📋 Total de assinaturas encontradas: {len(all_subscriptions)}")
                for i, subscription in enumerate(all_subscriptions, 1):
                    # CORREÇÃO: Enriquece DURANTE o processamento de cada assinatura
                    self.process_subscription(subscription, start_date, end_date)
                    if i % 10 == 0:
                        print(f"   {i}/{len(all_subscriptions)} assinaturas processadas")
            else:
                print("⚠️ Nenhuma assinatura encontrada")
            
            # 2. Processa transações SEPARADAMENTE (para completar o banco)
            if start_date and end_date:
                print("\n💰 Processando transações em lotes de 180 dias...")
                all_transactions = self.process_transactions_in_batches(start_date, end_date)
                
                if all_transactions:
                    print(f"📦 Total de transações encontradas: {len(all_transactions)}")
                    for i, transaction in enumerate(all_transactions, 1):
                        self.process_transaction(transaction)
                        if i % 10 == 0:
                            print(f"   {i}/{len(all_transactions)} transações processadas")
                else:
                    print("⚠️ Nenhuma transação encontrada no período")
            else:
                print("⚠️ Sem filtro de data - transações não serão processadas (evita contagem incorreta)")
                all_transactions = []
            
            # 3. Cria backup dos dados processados
            backup_data = {
                "backfill_type": "guru_complete",
                "period": {"start": start_date, "end": end_date},
                "transactions_count": len(all_transactions) if all_transactions else 0,
                "subscriptions_count": len(all_subscriptions) if all_subscriptions else 0,
                "stats": self.stats,
                "timestamp": datetime.now().isoformat()
            }
            
            create_backup_log(backup_data, "guru_backfill_complete")
            
            print("\n✅ Backfill concluído!")
            self.print_final_report()
            
        except Exception as e:
            self.logger.error(f"❌ Erro durante backfill: {e}")
            print(f"❌ Erro durante backfill: {e}")
    
    def process_transactions_in_batches(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Processa transações em lotes de 180 dias respeitando limites da API
        CORREÇÃO: Usa filtros de data corretos (ordered_at_ini/end) e paginação cursor
        """
        all_transactions = []
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        current_start = start_datetime
        
        batch_number = 1
        
        while current_start <= end_datetime:
            # Calcula data final do lote (máximo 180 dias)
            batch_end = min(current_start + timedelta(days=179), end_datetime)
            
            batch_start_str = current_start.strftime("%Y-%m-%d")
            batch_end_str = batch_end.strftime("%Y-%m-%d")
            
            print(f"📦 Lote {batch_number}: {batch_start_str} até {batch_end_str}")
            
            try:
                # CORREÇÃO: Usa filtros de data corretos para transactions
                # Para transactions: ordered_at_ini e ordered_at_end
                batch_transactions = self.api_client.get_all_transactions_with_cursor(
                    start_date=batch_start_str, 
                    end_date=batch_end_str
                )
                
                if batch_transactions:
                    all_transactions.extend(batch_transactions)
                    print(f"   ✅ Lote {batch_number}: {len(batch_transactions)} transações encontradas")
                else:
                    print(f"   ⚠️ Lote {batch_number}: Nenhuma transação encontrada")
                
                # Rate limiting: espera 1 segundo entre lotes (360 req/min = 6 req/seg)
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"❌ Erro no lote {batch_number}: {e}")
                print(f"   ❌ Erro no lote {batch_number}: {e}")
            
            # Avança para o próximo lote
            current_start = batch_end + timedelta(days=1)
            batch_number += 1
        
        print(f"📊 Total de transações coletadas: {len(all_transactions)}")
        return all_transactions
    
    def process_subscriptions_with_rate_limit(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """
        Processa assinaturas com rate limiting usando cursor-based pagination
        CORREÇÃO: Usa filtros de data corretos (last_status_at_ini/end) e paginação cursor
        """
        all_subscriptions = []
        
        print("🔄 Buscando assinaturas com cursor-based pagination...")
        
        try:
            # CORREÇÃO: Usa filtros de data corretos para subscriptions
            # Para subscriptions: last_status_at_ini e last_status_at_end
            if start_date and end_date:
                print(f"📅 Filtrando assinaturas por período: {start_date} até {end_date}")
                all_subscriptions = self.api_client.get_all_subscriptions_with_dates(
                    start_date=start_date,
                    end_date=end_date
                )
            else:
                print("⚠️ Sem filtro de data - buscando todas as assinaturas")
                all_subscriptions = self.api_client.get_all_subscriptions()
            
            if all_subscriptions:
                print(f"📊 Total de assinaturas coletadas: {len(all_subscriptions)}")
                
                # Valida dados mínimos necessários
                valid_subscriptions = []
                for subscription in all_subscriptions:
                    if subscription.get("id") and subscription.get("contact"):
                        valid_subscriptions.append(subscription)
                    else:
                        print(f"⚠️ Assinatura sem dados mínimos, ignorando: {subscription.get('id')}")
                
                all_subscriptions = valid_subscriptions
                print(f"📋 Assinaturas válidas para processamento: {len(all_subscriptions)}")
            else:
                print("⚠️ Nenhuma assinatura encontrada")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar assinaturas: {e}")
            print(f"❌ Erro ao buscar assinaturas: {e}")
        
        print(f"📊 Total de assinaturas para processamento: {len(all_subscriptions)}")
        return all_subscriptions
    
    def print_final_report(self):
        """
        Imprime relatório final do backfill
        """
        print("\n" + "="*50)
        print("📊 RELATÓRIO FINAL - BACKFILL GURU")
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
    Função principal para executar o backfill
    """
    parser = argparse.ArgumentParser(description="Backfill histórico da Guru")
    parser.add_argument("--start-date", help="Data inicial (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="Data final (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    print("🚀 Iniciando backfill histórico da Guru")
    
    backfill = GuruBackfill(args.start_date, args.end_date)
    backfill.run_backfill(args.start_date, args.end_date)

if __name__ == "__main__":
    main() 