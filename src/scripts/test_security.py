#!/usr/bin/env python3
"""
Script de teste para validar o sistema de segurança implementado
Testa autenticação, validação de payload e rate limiting
"""

import sys
import os
import json
import time
import requests
from typing import Dict, Any

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.security_config import security_config

class SecurityTester:
    """
    Classe para testar o sistema de segurança
    """
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """
        Registra resultado de um teste
        """
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_configuration(self):
        """
        Testa se as configurações de segurança estão corretas
        """
        print("🔧 Testando configurações de segurança...")
        
        # Testa se todas as configurações estão presentes
        is_configured = security_config.is_configured()
        self.log_test(
            "Configuração completa",
            is_configured,
            f"Guru: {bool(security_config.GURU_ACCOUNT_TOKEN)}, "
            f"Ticto: {len(security_config.get_ticto_tokens()) > 0}, "
            f"Secret: {bool(security_config.SECRET_KEY)}"
        )
        
        # Testa token Guru
        if security_config.GURU_ACCOUNT_TOKEN:
            self.log_test(
                "Token Guru configurado",
                True,
                f"Token: {security_config.GURU_ACCOUNT_TOKEN[:10]}..."
            )
        else:
            self.log_test("Token Guru configurado", False, "Token não encontrado")
        
        # Testa tokens Ticto
        ticto_tokens = security_config.get_ticto_tokens()
        if ticto_tokens:
            self.log_test(
                "Tokens Ticto configurados",
                True,
                f"Quantidade: {len(ticto_tokens)}"
            )
        else:
            self.log_test("Tokens Ticto configurados", False, "Nenhum token encontrado")
    
    def test_guru_webhook_authentication(self):
        """
        Testa autenticação do webhook da Guru
        """
        print("\n🔐 Testando autenticação Guru...")
        
        # Payload válido da Guru
        valid_payload = {
            "webhook_type": "transaction",
            "payload": {
                "api_token": security_config.GURU_ACCOUNT_TOKEN,
                "id": "test-123",
                "status": "approved"
            }
        }
        
        # Payload inválido (token errado)
        invalid_payload = {
            "webhook_type": "transaction",
            "payload": {
                "api_token": "token_invalido",
                "id": "test-123",
                "status": "approved"
            }
        }
        
        # Payload sem token
        no_token_payload = {
            "webhook_type": "transaction",
            "payload": {
                "id": "test-123",
                "status": "approved"
            }
        }
        
        # Testa payload válido
        try:
            response = requests.post(
                f"{self.base_url}/webhook/guru",
                json=valid_payload,
                timeout=10
            )
            self.log_test(
                "Webhook Guru - Token válido",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.log_test("Webhook Guru - Token válido", False, f"Erro: {str(e)}")
        
        # Testa payload inválido
        try:
            response = requests.post(
                f"{self.base_url}/webhook/guru",
                json=invalid_payload,
                timeout=10
            )
            self.log_test(
                "Webhook Guru - Token inválido",
                response.status_code == 401,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.log_test("Webhook Guru - Token inválido", False, f"Erro: {str(e)}")
        
        # Testa payload sem token
        try:
            response = requests.post(
                f"{self.base_url}/webhook/guru",
                json=no_token_payload,
                timeout=10
            )
            self.log_test(
                "Webhook Guru - Sem token",
                response.status_code == 401,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.log_test("Webhook Guru - Sem token", False, f"Erro: {str(e)}")
    
    def test_ticto_webhook_authentication(self):
        """
        Testa autenticação do webhook da Ticto
        """
        print("\n🔐 Testando autenticação Ticto...")
        
        ticto_tokens = security_config.get_ticto_tokens()
        if not ticto_tokens:
            self.log_test("Webhook Ticto - Testes", False, "Nenhum token Ticto configurado")
            return
        
        valid_token = ticto_tokens[0]
        
        # Payload válido da Ticto
        valid_payload = {
            "token": valid_token,
            "status": "authorized",
            "order": {
                "transaction_hash": "test-hash-123",
                "paid_amount": 1000
            },
            "customer": {
                "email": "test@example.com",
                "name": "Test User"
            }
        }
        
        # Payload inválido (token errado)
        invalid_payload = {
            "token": "token_invalido",
            "status": "authorized",
            "order": {
                "transaction_hash": "test-hash-123",
                "paid_amount": 1000
            },
            "customer": {
                "email": "test@example.com",
                "name": "Test User"
            }
        }
        
        # Payload sem token
        no_token_payload = {
            "status": "authorized",
            "order": {
                "transaction_hash": "test-hash-123",
                "paid_amount": 1000
            },
            "customer": {
                "email": "test@example.com",
                "name": "Test User"
            }
        }
        
        # Testa payload válido
        try:
            response = requests.post(
                f"{self.base_url}/webhook/ticto",
                json=valid_payload,
                timeout=10
            )
            self.log_test(
                "Webhook Ticto - Token válido",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.log_test("Webhook Ticto - Token válido", False, f"Erro: {str(e)}")
        
        # Testa payload inválido
        try:
            response = requests.post(
                f"{self.base_url}/webhook/ticto",
                json=invalid_payload,
                timeout=10
            )
            self.log_test(
                "Webhook Ticto - Token inválido",
                response.status_code == 401,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.log_test("Webhook Ticto - Token inválido", False, f"Erro: {str(e)}")
        
        # Testa payload sem token
        try:
            response = requests.post(
                f"{self.base_url}/webhook/ticto",
                json=no_token_payload,
                timeout=10
            )
            self.log_test(
                "Webhook Ticto - Sem token",
                response.status_code == 401,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.log_test("Webhook Ticto - Sem token", False, f"Erro: {str(e)}")
    
    def test_rate_limiting(self):
        """
        Testa rate limiting
        """
        print("\n⏱️ Testando rate limiting...")
        
        # Testa múltiplas requisições rápidas
        success_count = 0
        rate_limit_count = 0
        
        for i in range(10):
            try:
                response = requests.post(
                    f"{self.base_url}/webhook/guru",
                    json={
                        "webhook_type": "transaction",
                        "payload": {
                            "api_token": security_config.GURU_ACCOUNT_TOKEN,
                            "id": f"test-rate-{i}",
                            "status": "approved"
                        }
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 429:
                    rate_limit_count += 1
                
                time.sleep(0.1)  # Pequeno delay entre requisições
                
            except Exception as e:
                print(f"   Erro na requisição {i}: {str(e)}")
        
        self.log_test(
            "Rate limiting funcionando",
            rate_limit_count > 0 or success_count < 10,
            f"Sucessos: {success_count}, Rate limits: {rate_limit_count}"
        )
    
    def test_health_endpoint(self):
        """
        Testa endpoint de saúde
        """
        print("\n🏥 Testando endpoint de saúde...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                self.log_test(
                    "Endpoint de saúde",
                    True,
                    f"Status: {health_data.get('status')}, "
                    f"Security: {health_data.get('security_configured')}"
                )
            else:
                self.log_test("Endpoint de saúde", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Endpoint de saúde", False, f"Erro: {str(e)}")
    
    def run_all_tests(self):
        """
        Executa todos os testes
        """
        print("🚀 Iniciando testes de segurança...")
        print("=" * 60)
        
        # Verifica se a API está rodando
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code != 200:
                print("❌ API não está rodando. Execute 'uvicorn src.Api.webhooks:app --reload' primeiro.")
                return
        except:
            print("❌ API não está rodando. Execute 'uvicorn src.Api.webhooks:app --reload' primeiro.")
            return
        
        # Executa testes
        self.test_configuration()
        self.test_guru_webhook_authentication()
        self.test_ticto_webhook_authentication()
        self.test_rate_limiting()
        self.test_health_endpoint()
        
        # Resumo final
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total de testes: {total_tests}")
        print(f"✅ Aprovados: {passed_tests}")
        print(f"❌ Reprovados: {failed_tests}")
        
        if failed_tests == 0:
            print("\n🎉 Todos os testes passaram! Sistema de segurança funcionando perfeitamente.")
        else:
            print(f"\n⚠️ {failed_tests} teste(s) falharam. Verifique os logs acima.")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = SecurityTester()
    success = tester.run_all_tests()
    
    if not success:
        sys.exit(1)
