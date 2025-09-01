"""
Cliente da API Guru para backfill histórico
"""
import requests
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
from .backfill_utils import retry_on_error, get_env_var, validate_response

class GuruAPIClient:
    def __init__(self, logger=None):
        self.base_url = "https://digitalmanager.guru/api/v2"
        self.logger = logger
        
        # Credenciais do .env
        self.user_token = get_env_var("GURU_USER_TOKEN")
        self.account_token = get_env_var("GURU_ACCOUNT_TOKEN")
        
    def get_headers(self) -> Dict[str, str]:
        """
        Retorna headers com token de autenticação da Guru
        """
        return {
            "accept": "application/json",
            "authorization": f"Bearer {self.user_token}"
        }
    
    @retry_on_error(max_retries=3, delay=2.0)
    def get_transactions(self, confirmed_at_ini: str, confirmed_at_end: str, cursor: str = None) -> Optional[Dict[str, Any]]:
        """
        Busca transações da Guru com paginação por cursor
        Parâmetros obrigatórios:
        - confirmed_at_ini: Data de aprovação inicial (YYYY-MM-DD)
        - confirmed_at_end: Data de aprovação final (YYYY-MM-DD)
        - cursor: Cursor para paginação (opcional)
        """
        try:
            url = f"{self.base_url}/transactions"
            headers = self.get_headers()
            
            params = {
                "confirmed_at_ini": confirmed_at_ini,
                "confirmed_at_end": confirmed_at_end
            }
            
            # Adiciona cursor se fornecido
            if cursor:
                params["cursor"] = cursor
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Valida estrutura básica da resposta
            if not validate_response(data, ["data"]):
                print(f"❌ Resposta de transações inválida")
                return None
            
            # Log com informações de cursor
            cursor_info = f"cursor={cursor}" if cursor else "primeira página"
            next_cursor = data.get("next_cursor")
            if next_cursor:
                log_msg = f"💰 Transações {cursor_info}: {len(data.get('data', []))} registros | próximo: {next_cursor[:10]}..."
                if self.logger:
                    self.logger.info(log_msg)
                else:
                    print(log_msg)
            else:
                log_msg = f"💰 Transações {cursor_info}: {len(data.get('data', []))} registros | última página"
                if self.logger:
                    self.logger.info(log_msg)
                else:
                    print(log_msg)
            
            return data
            
        except Exception as e:
            print(f"❌ Erro ao buscar transações: {e}")
            return None
    
    def get_all_transactions(self, confirmed_at_ini: str, confirmed_at_end: str) -> List[Dict[str, Any]]:
        """
        Busca todas as transações em todas as páginas
        """
        all_transactions = []
        cursor = None
        page_count = 0
        
        print(f"🔄 Buscando transações de {confirmed_at_ini} até {confirmed_at_end}")
        
        while True:
            page_count += 1
            data = self.get_transactions(confirmed_at_ini, confirmed_at_end, cursor)
            
            if not data:
                print(f"❌ Erro ao buscar página {page_count}")
                break
            
            transactions = data.get("data", [])
            if not transactions:
                print(f"⚠️ Página {page_count} sem dados")
                break
            
            all_transactions.extend(transactions)
            print(f"📦 Total de transações coletadas: {len(all_transactions)}")
            
            # Verifica se há próxima página usando next_cursor
            next_cursor = data.get("next_cursor")
            if not next_cursor:
                print(f"✅ Última página alcançada (página {page_count})")
                break
            
            # Atualiza cursor para próxima página
            cursor = next_cursor
            
            # Rate limiting: espera 0.17 segundos entre requisições (360 req/min)
            time.sleep(0.17)
        
        print(f"✅ Total final de transações: {len(all_transactions)}")
        return all_transactions
    
    def get_all_subscriptions(self) -> List[Dict[str, Any]]:
        """
        Busca todas as assinaturas usando paginação por cursor
        """
        all_subscriptions = []
        cursor = None
        page_count = 0
        
        print("🔄 Buscando todas as assinaturas usando cursor-based pagination")
        
        while True:
            page_count += 1
            data = self.get_subscriptions(cursor)
            
            if not data:
                print(f"❌ Erro ao buscar página {page_count}")
                break
            
            subscriptions = data.get("data", [])
            if not subscriptions:
                print(f"⚠️ Página {page_count} sem dados")
                break
            
            all_subscriptions.extend(subscriptions)
            print(f"📋 Página {page_count}: {len(subscriptions)} assinaturas | Total: {len(all_subscriptions)}")
            
            # Verifica se há próxima página usando next_cursor
            next_cursor = data.get("next_cursor")
            if not next_cursor:
                print(f"✅ Última página alcançada (página {page_count})")
                break
            
            # Atualiza cursor para próxima página
            cursor = next_cursor
            
            # Rate limiting: espera 0.17 segundos entre requisições (360 req/min)
            time.sleep(0.17)
        
        print(f"✅ Total final de assinaturas: {len(all_subscriptions)} em {page_count} páginas")
        return all_subscriptions 

    @retry_on_error(max_retries=3, delay=2.0)
    def get_transactions_by_contact_no_dates(self, contact_id: str, cursor: str = None) -> Optional[Dict[str, Any]]:
        """
        Busca transações da Guru por ID do contato SEM filtros de data
        ESPECÍFICO para enriquecimento de assinaturas - busca histórico completo
        """
        try:
            url = f"{self.base_url}/transactions"
            headers = self.get_headers()
            
            params = {
                "contact_id": contact_id
            }
            
            # SEM filtros de data - busca histórico completo do contato
            # Adiciona cursor se fornecido
            if cursor:
                params["cursor"] = cursor
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Valida estrutura básica da resposta
            if not validate_response(data, ["data"]):
                print(f"❌ Resposta de transações por contato inválida")
                return None
            
            # Log com informações de cursor
            next_cursor = data.get("next_cursor")
            if next_cursor:
                print(f"💰 Transações do contato {contact_id}: {len(data.get('data', []))} registros | próximo: {next_cursor[:10]}...")
            else:
                print(f"💰 Transações do contato {contact_id}: {len(data.get('data', []))} registros | última página")
            
            return data
            
        except Exception as e:
            print(f"❌ Erro ao buscar transações do contato {contact_id}: {e}")
            return None

    @retry_on_error(max_retries=3, delay=2.0)
    def get_transactions_by_contact(self, contact_id: str, start_date: str = None, end_date: str = None, cursor: str = None) -> Optional[Dict[str, Any]]:
        """
        Busca transações da Guru por ID do contato com paginação por cursor
        """
        try:
            url = f"{self.base_url}/transactions"
            headers = self.get_headers()
            
            params = {
                "contact_id": contact_id
            }
            
            # Adiciona filtros de data se fornecidos
            if start_date:
                params["confirmed_at_ini"] = start_date
            if end_date:
                params["confirmed_at_end"] = end_date
            
            # Adiciona cursor se fornecido
            if cursor:
                params["cursor"] = cursor
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Valida estrutura básica da resposta
            if not validate_response(data, ["data"]):
                print(f"❌ Resposta de transações por contato inválida")
                return None
            
            # Log com informações de cursor
            next_cursor = data.get("next_cursor")
            if next_cursor:
                print(f"💰 Transações do contato {contact_id}: {len(data.get('data', []))} registros | próximo: {next_cursor[:10]}...")
            else:
                print(f"💰 Transações do contato {contact_id}: {len(data.get('data', []))} registros | última página")
            
            return data
            
        except Exception as e:
            print(f"❌ Erro ao buscar transações do contato {contact_id}: {e}")
            return None 

    def get_all_transactions_by_contact(self, contact_id: str, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """
        Busca todas as transações de um contato em todas as páginas usando cursor
        """
        all_transactions = []
        cursor = None
        page_count = 0
        
        print(f"🔄 Buscando todas as transações do contato {contact_id}")
        
        while True:
            page_count += 1
            data = self.get_transactions_by_contact(contact_id, start_date, end_date, cursor)
            
            if not data:
                print(f"❌ Erro ao buscar página {page_count}")
                break
            
            transactions = data.get("data", [])
            if not transactions:
                print(f"⚠️ Página {page_count} sem dados")
                break
            
            all_transactions.extend(transactions)
            print(f"📦 Total de transações do contato coletadas: {len(all_transactions)}")
            
            # Verifica se há próxima página usando next_cursor
            next_cursor = data.get("next_cursor")
            if not next_cursor:
                print(f"✅ Última página do contato alcançada (página {page_count})")
                break
            
            # Atualiza cursor para próxima página
            cursor = next_cursor
            
            # Rate limiting: espera 0.17 segundos entre requisições (360 req/min)
            time.sleep(0.17)
        
        print(f"✅ Total final de transações do contato {contact_id}: {len(all_transactions)}")
        return all_transactions

    @retry_on_error(max_retries=3, delay=2.0)
    def get_subscriptions(self, cursor: str = None) -> Optional[Dict[str, Any]]:
        """
        Busca assinaturas da Guru com paginação por cursor
        """
        try:
            url = f"{self.base_url}/subscriptions"
            headers = self.get_headers()
            
            params = {}
            if cursor:
                params["cursor"] = cursor
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Valida estrutura básica da resposta
            if not validate_response(data, ["data"]):
                print(f"❌ Resposta de assinaturas inválida")
                return None
            
            # Log com informações de cursor
            cursor_info = f"cursor={cursor}" if cursor else "primeira página"
            next_cursor = data.get("next_cursor")
            if next_cursor:
                print(f"📋 Assinaturas {cursor_info}: {len(data.get('data', []))} registros | próximo: {next_cursor[:10]}...")
            else:
                print(f"📋 Assinaturas {cursor_info}: {len(data.get('data', []))} registros | última página")
            
            return data
            
        except Exception as e:
            print(f"❌ Erro ao buscar assinaturas: {e}")
            return None 

    @retry_on_error(max_retries=3, delay=2.0)
    def get_transactions_with_cursor(self, ordered_at_ini: str, ordered_at_end: str, cursor: str = None) -> Optional[Dict[str, Any]]:
        """
        Busca transações da Guru com filtros de data corretos
        CORREÇÃO: Usa ordered_at_ini e ordered_at_end (não confirmed_at)
        """
        try:
            url = f"{self.base_url}/transactions"
            headers = self.get_headers()
            
            params = {
                "ordered_at_ini": ordered_at_ini,
                "ordered_at_end": ordered_at_end
            }
            
            # Adiciona cursor se fornecido
            if cursor:
                params["cursor"] = cursor
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Valida estrutura básica da resposta
            if not validate_response(data, ["data"]):
                print(f"❌ Resposta de transações inválida")
                return None
            
            # Log com informações de cursor
            cursor_info = f"cursor={cursor}" if cursor else "primeira página"
            next_cursor = data.get("next_cursor")
            if next_cursor:
                print(f"💰 Transações {cursor_info}: {len(data.get('data', []))} registros | próximo: {next_cursor[:10]}...")
            else:
                print(f"💰 Transações {cursor_info}: {len(data.get('data', []))} registros | última página")
            
            return data
            
        except Exception as e:
            print(f"❌ Erro ao buscar transações: {e}")
            return None
    
    def get_all_transactions_with_cursor(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Busca todas as transações usando filtros de data corretos
        CORREÇÃO: Usa ordered_at_ini e ordered_at_end
        """
        all_transactions = []
        cursor = None
        page_count = 0
        
        print(f"🔄 Buscando transações de {start_date} até {end_date} usando filtros corretos")
        
        while True:
            page_count += 1
            data = self.get_transactions_with_cursor(start_date, end_date, cursor)
            
            if not data:
                print(f"❌ Erro ao buscar página {page_count}")
                break
            
            transactions = data.get("data", [])
            if not transactions:
                print(f"⚠️ Página {page_count} sem dados")
                break
            
            all_transactions.extend(transactions)
            print(f"📦 Total de transações coletadas: {len(all_transactions)}")
            
            # Verifica se há próxima página usando next_cursor
            next_cursor = data.get("next_cursor")
            if not next_cursor:
                print(f"✅ Última página alcançada (página {page_count})")
                break
            
            # Atualiza cursor para próxima página
            cursor = next_cursor
            
            # Rate limiting: espera 0.17 segundos entre requisições (360 req/min)
            time.sleep(0.17)
        
        print(f"✅ Total final de transações: {len(all_transactions)}")
        return all_transactions

    @retry_on_error(max_retries=3, delay=2.0)
    def get_subscriptions_with_dates(self, last_status_at_ini: str, last_status_at_end: str, cursor: str = None) -> Optional[Dict[str, Any]]:
        """
        Busca assinaturas da Guru com filtros de data corretos
        CORREÇÃO: Usa last_status_at_ini e last_status_at_end
        """
        try:
            url = f"{self.base_url}/subscriptions"
            headers = self.get_headers()
            
            params = {
                "last_status_at_ini": last_status_at_ini,
                "last_status_at_end": last_status_at_end
            }
            
            # Adiciona cursor se fornecido
            if cursor:
                params["cursor"] = cursor
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Valida estrutura básica da resposta
            if not validate_response(data, ["data"]):
                print(f"❌ Resposta de assinaturas inválida")
                return None
            
            # Log com informações de cursor
            cursor_info = f"cursor={cursor}" if cursor else "primeira página"
            next_cursor = data.get("next_cursor")
            if next_cursor:
                print(f"📋 Assinaturas {cursor_info}: {len(data.get('data', []))} registros | próximo: {next_cursor[:10]}...")
            else:
                print(f"📋 Assinaturas {cursor_info}: {len(data.get('data', []))} registros | última página")
            
            return data
            
        except Exception as e:
            print(f"❌ Erro ao buscar assinaturas: {e}")
            return None
    
    def get_all_subscriptions_with_dates(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Busca todas as assinaturas usando filtros de data corretos
        CORREÇÃO: Usa last_status_at_ini e last_status_at_end
        """
        all_subscriptions = []
        cursor = None
        page_count = 0
        
        print(f"🔄 Buscando assinaturas de {start_date} até {end_date} usando filtros corretos")
        
        while True:
            page_count += 1
            data = self.get_subscriptions_with_dates(start_date, end_date, cursor)
            
            if not data:
                print(f"❌ Erro ao buscar página {page_count}")
                break
            
            subscriptions = data.get("data", [])
            if not subscriptions:
                print(f"⚠️ Página {page_count} sem dados")
                break
            
            all_subscriptions.extend(subscriptions)
            print(f"📋 Página {page_count}: {len(subscriptions)} assinaturas | Total: {len(all_subscriptions)}")
            
            # Verifica se há próxima página usando next_cursor
            next_cursor = data.get("next_cursor")
            if not next_cursor:
                print(f"✅ Última página alcançada (página {page_count})")
                break
            
            # Atualiza cursor para próxima página
            cursor = next_cursor
            
            # Rate limiting: espera 0.17 segundos entre requisições (360 req/min)
            time.sleep(0.17)
        
        print(f"✅ Total final de assinaturas: {len(all_subscriptions)} em {page_count} páginas")
        return all_subscriptions

    def get_all_transactions_by_contact_with_dates(self, contact_id: str, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """
        Busca todas as transações de um contato usando filtros de data corretos
        CORREÇÃO: Usa ordered_at_ini e ordered_at_end para filtros de data
        """
        all_transactions = []
        cursor = None
        page_count = 0
        
        print(f"🔄 Buscando transações do contato {contact_id} com filtros de data")
        
        while True:
            page_count += 1
            data = self.get_transactions_by_contact_with_dates(contact_id, start_date, end_date, cursor)
            
            if not data:
                print(f"❌ Erro ao buscar página {page_count}")
                break
            
            transactions = data.get("data", [])
            if not transactions:
                print(f"⚠️ Página {page_count} sem dados")
                break
            
            all_transactions.extend(transactions)
            print(f"📦 Total de transações do contato coletadas: {len(all_transactions)}")
            
            # Verifica se há próxima página usando next_cursor
            next_cursor = data.get("next_cursor")
            if not next_cursor:
                print(f"✅ Última página do contato alcançada (página {page_count})")
                break
            
            # Atualiza cursor para próxima página
            cursor = next_cursor
            
            # Rate limiting: espera 0.17 segundos entre requisições (360 req/min)
            time.sleep(0.17)
        
        print(f"✅ Total final de transações do contato {contact_id}: {len(all_transactions)}")
        return all_transactions

    @retry_on_error(max_retries=3, delay=2.0)
    def get_transactions_by_contact_with_dates(self, contact_id: str, start_date: str = None, end_date: str = None, cursor: str = None) -> Optional[Dict[str, Any]]:
        """
        Busca transações da Guru por ID do contato com filtros de data corretos
        CORREÇÃO: Usa ordered_at_ini e ordered_at_end para filtros de data
        """
        try:
            url = f"{self.base_url}/transactions"
            headers = self.get_headers()
            
            params = {
                "contact_id": contact_id
            }
            
            # CORREÇÃO: Usa filtros de data corretos para transactions
            if start_date:
                params["ordered_at_ini"] = start_date
            if end_date:
                params["ordered_at_end"] = end_date
            
            # Adiciona cursor se fornecido
            if cursor:
                params["cursor"] = cursor
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Valida estrutura básica da resposta
            if not validate_response(data, ["data"]):
                print(f"❌ Resposta de transações por contato inválida")
                return None
            
            # Log com informações de cursor
            next_cursor = data.get("next_cursor")
            if next_cursor:
                print(f"💰 Transações do contato {contact_id}: {len(data.get('data', []))} registros | próximo: {next_cursor[:10]}...")
            else:
                print(f"💰 Transações do contato {contact_id}: {len(data.get('data', []))} registros | última página")
            
            return data
            
        except Exception as e:
            print(f"❌ Erro ao buscar transações do contato {contact_id}: {e}")
            return None 

    def get_all_transactions_by_subscription(self, subscription_id: str) -> List[Dict[str, Any]]:
        """
        Busca TODAS as transações de uma assinatura específica usando subscription_id
        CORREÇÃO 2: Busca transações específicas da assinatura (não apenas do contato)
        """
        all_transactions = []
        cursor = None
        page_count = 0
        
        print(f"🔄 Buscando transações específicas da assinatura {subscription_id}")
        
        while True:
            page_count += 1
            data = self.get_transactions_by_subscription(subscription_id, cursor)
            
            if not data:
                print(f"❌ Erro ao buscar página {page_count}")
                break
            
            transactions = data.get("data", [])
            if not transactions:
                print(f"⚠️ Página {page_count} sem dados")
                break
            
            all_transactions.extend(transactions)
            print(f"📦 Total de transações da assinatura coletadas: {len(all_transactions)}")
            
            # Verifica se há próxima página usando next_cursor
            next_cursor = data.get("next_cursor")
            if not next_cursor:
                print(f"✅ Última página da assinatura alcançada (página {page_count})")
                break
            
            # Atualiza cursor para próxima página
            cursor = next_cursor
            
            # Rate limiting: espera 0.17 segundos entre requisições (360 req/min)
            time.sleep(0.17)
        
        print(f"✅ Total final de transações da assinatura {subscription_id}: {len(all_transactions)}")
        return all_transactions

    @retry_on_error(max_retries=3, delay=2.0)
    def get_transactions_by_subscription(self, subscription_id: str, cursor: str = None) -> Optional[Dict[str, Any]]:
        """
        Busca transações da Guru por ID da assinatura
        CORREÇÃO 2: Busca transações específicas de uma assinatura
        """
        try:
            url = f"{self.base_url}/transactions"
            headers = self.get_headers()
            
            params = {
                "subscription_id": subscription_id
            }
            
            # Adiciona cursor se fornecido
            if cursor:
                params["cursor"] = cursor
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Valida estrutura básica da resposta
            if not validate_response(data, ["data"]):
                print(f"❌ Resposta de transações por assinatura inválida")
                return None
            
            # Log com informações de cursor
            next_cursor = data.get("next_cursor")
            if next_cursor:
                print(f"💰 Transações da assinatura {subscription_id}: {len(data.get('data', []))} registros | próximo: {next_cursor[:10]}...")
            else:
                print(f"💰 Transações da assinatura {subscription_id}: {len(data.get('data', []))} registros | última página")
            
            return data
            
        except Exception as e:
            print(f"❌ Erro ao buscar transações da assinatura {subscription_id}: {e}")
            return None

    def get_all_transactions_by_contact_no_dates(self, contact_id: str) -> List[Dict[str, Any]]:
        """
        Busca TODAS as transações de um contato SEM filtros de data
        ESPECÍFICO para enriquecimento de assinaturas - busca histórico completo
        """
        all_transactions = []
        cursor = None
        page_count = 0
        
        print(f"🔄 Buscando TODAS as transações do contato {contact_id} (sem filtros de data)")
        
        while True:
            page_count += 1
            data = self.get_transactions_by_contact_no_dates(contact_id, cursor)
            
            if not data:
                print(f"❌ Erro ao buscar página {page_count}")
                break
            
            transactions = data.get("data", [])
            if not transactions:
                print(f"⚠️ Página {page_count} sem dados")
                break
            
            all_transactions.extend(transactions)
            print(f"📦 Total de transações do contato coletadas: {len(all_transactions)}")
            
            # Verifica se há próxima página usando next_cursor
            next_cursor = data.get("next_cursor")
            if not next_cursor:
                print(f"✅ Última página do contato alcançada (página {page_count})")
                break
            
            # Atualiza cursor para próxima página
            cursor = next_cursor
            
            # Rate limiting: espera 0.17 segundos entre requisições (360 req/min)
            time.sleep(0.17)
        
        print(f"✅ Total final de transações do contato {contact_id}: {len(all_transactions)}")
        return all_transactions 