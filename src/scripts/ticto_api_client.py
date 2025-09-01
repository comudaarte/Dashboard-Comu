"""
Cliente da API Ticto para backfill histórico
"""
import requests
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
from .backfill_utils import retry_on_error, get_env_var, validate_response

class TictoAPIClient:
    def __init__(self):
        self.base_url = "https://glados.ticto.cloud/api"
        self.token_url = f"{self.base_url}/security/oauth/token"
        self.access_token = None
        self.token_expires_at = None
        
        # Credenciais do .env
        self.client_id = get_env_var("TICTO_CLIENT_ID")
        self.client_secret = get_env_var("TICTO_CLIENT_SECRET")
        
    def authenticate(self) -> bool:
        """
        Autentica com a API Ticto usando client credentials
        """
        try:
            payload = {
                "grant_type": "client_credentials",
                "scope": "*",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            
            headers = {
                "accept": "application/json",
                "content-type": "application/json"
            }
            
            response = requests.post(self.token_url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if validate_response(data, ["access_token", "expires_in"]):
                self.access_token = data["access_token"]
                self.token_expires_at = datetime.now().timestamp() + data["expires_in"]
                print(f"✅ Autenticação Ticto realizada com sucesso. Token expira em {data['expires_in']}s")
                return True
            else:
                print("❌ Resposta de autenticação inválida")
                return False
                
        except Exception as e:
            print(f"❌ Erro na autenticação Ticto: {e}")
            return False
    
    def is_token_valid(self) -> bool:
        """
        Verifica se o token ainda é válido
        """
        if not self.access_token or not self.token_expires_at:
            return False
        
        # Renova se faltar menos de 5 minutos
        return datetime.now().timestamp() < (self.token_expires_at - 300)
    
    def get_headers(self) -> Dict[str, str]:
        """
        Retorna headers com token de autenticação
        """
        if not self.is_token_valid():
            if not self.authenticate():
                raise Exception("Falha na autenticação Ticto")
        
        return {
            "accept": "application/json",
            "authorization": f"Bearer {self.access_token}"
        }
    
    @retry_on_error(max_retries=3, delay=2.0)
    def get_orders_history(self, page: int = 1) -> Optional[Dict[str, Any]]:
        """
        Busca histórico de orders com paginação
        """
        try:
            url = f"{self.base_url}/v1/orders/history?page={page}"
            headers = self.get_headers()
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Valida estrutura básica da resposta
            if not validate_response(data, ["data", "meta"]):
                print(f"❌ Resposta de orders inválida na página {page}")
                return None
            
            print(f"📦 Orders página {page}: {len(data.get('data', []))} registros")
            return data
            
        except Exception as e:
            print(f"❌ Erro ao buscar orders página {page}: {e}")
            return None
    
    @retry_on_error(max_retries=3, delay=2.0)
    def get_subscriptions_history(self, page: int = 1) -> Optional[Dict[str, Any]]:
        """
        Busca histórico de subscriptions com paginação
        """
        try:
            url = f"{self.base_url}/v1/subscriptions/history?page={page}"
            headers = self.get_headers()
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Valida estrutura básica da resposta
            if not validate_response(data, ["data", "meta"]):
                print(f"❌ Resposta de subscriptions inválida na página {page}")
                return None
            
            print(f"📋 Subscriptions página {page}: {len(data.get('data', []))} registros")
            return data
            
        except Exception as e:
            print(f"❌ Erro ao buscar subscriptions página {page}: {e}")
            return None
    
    def get_all_orders(self) -> List[Dict[str, Any]]:
        """
        Busca todas as orders usando paginação
        """
        all_orders = []
        page = 1
        
        print("🔄 Iniciando busca de todas as orders...")
        
        while True:
            response = self.get_orders_history(page)
            
            if not response:
                print(f"❌ Falha ao buscar orders página {page}")
                break
            
            orders = response.get("data", [])
            if not orders:
                print(f"✅ Fim das orders na página {page}")
                break
            
            all_orders.extend(orders)
            print(f"📊 Total de orders coletadas: {len(all_orders)}")
            
            # Verifica se há mais páginas
            meta = response.get("meta", {})
            if page >= meta.get("last_page", page):
                print("✅ Todas as páginas de orders foram processadas")
                break
            
            page += 1
            time.sleep(0.5)  # Rate limiting
        
        print(f"🎉 Busca de orders concluída: {len(all_orders)} registros")
        return all_orders
    
    def get_all_subscriptions(self) -> List[Dict[str, Any]]:
        """
        Busca todas as subscriptions usando paginação
        """
        all_subscriptions = []
        page = 1
        
        print("🔄 Iniciando busca de todas as subscriptions...")
        
        while True:
            response = self.get_subscriptions_history(page)
            
            if not response:
                print(f"❌ Falha ao buscar subscriptions página {page}")
                break
            
            subscriptions = response.get("data", [])
            if not subscriptions:
                print(f"✅ Fim das subscriptions na página {page}")
                break
            
            all_subscriptions.extend(subscriptions)
            print(f"📊 Total de subscriptions coletadas: {len(all_subscriptions)}")
            
            # Verifica se há mais páginas
            meta = response.get("meta", {})
            if page >= meta.get("last_page", page):
                print("✅ Todas as páginas de subscriptions foram processadas")
                break
            
            page += 1
            time.sleep(0.5)  # Rate limiting
        
        print(f"🎉 Busca de subscriptions concluída: {len(all_subscriptions)} registros")
        return all_subscriptions
