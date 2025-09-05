"""
Script de teste para o sistema de autenticação
"""
import requests
import json
import time

def test_auth_endpoints():
    """Testa todos os endpoints de autenticação"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testando Sistema de Autenticação")
    print("=" * 50)
    
    # Teste 1: Health check
    print("\n1. Testando health check...")
    try:
        response = requests.get(f"{base_url}/auth/health")
        if response.status_code == 200:
            print("✅ Health check OK")
        else:
            print(f"❌ Health check falhou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
    
    # Teste 2: Login com credenciais válidas
    print("\n2. Testando login com credenciais válidas...")
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("✅ Login bem-sucedido!")
            print(f"   Token: {token[:50]}...")
            
            # Teste 3: Acessar endpoint protegido
            print("\n3. Testando acesso a endpoint protegido...")
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{base_url}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                print("✅ Acesso a endpoint protegido OK!")
                print(f"   Usuário: {user_data.get('username')}")
                print(f"   Role: {user_data.get('role')}")
            else:
                print(f"❌ Falha no acesso protegido: {response.status_code}")
                
        else:
            print(f"❌ Login falhou: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro no teste de login: {e}")
    
    # Teste 4: Login com credenciais inválidas
    print("\n4. Testando login com credenciais inválidas...")
    try:
        login_data = {
            "username": "admin",
            "password": "senha_errada"
        }
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        
        if response.status_code == 401:
            print("✅ Login com credenciais inválidas rejeitado corretamente!")
        else:
            print(f"❌ Login com credenciais inválidas deveria falhar: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro no teste de login inválido: {e}")
    
    # Teste 5: Acesso sem token
    print("\n5. Testando acesso sem token...")
    try:
        response = requests.get(f"{base_url}/auth/me")
        
        if response.status_code == 401:
            print("✅ Acesso sem token rejeitado corretamente!")
        else:
            print(f"❌ Acesso sem token deveria falhar: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro no teste sem token: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Testes de autenticação concluídos!")

def test_dashboard_access():
    """Testa acesso ao dashboard"""
    print("\n📊 Testando acesso ao Dashboard...")
    
    try:
        response = requests.get("http://localhost:8052")
        if response.status_code == 200:
            print("✅ Dashboard acessível!")
        else:
            print(f"❌ Dashboard não acessível: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar dashboard: {e}")

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes do sistema de autenticação...")
    
    # Aguardar serviços iniciarem
    print("⏳ Aguardando serviços iniciarem...")
    time.sleep(5)
    
    # Testar endpoints de autenticação
    test_auth_endpoints()
    
    # Testar acesso ao dashboard
    test_dashboard_access()
    
    print("\n📋 Resumo dos testes:")
    print("- Health check da API")
    print("- Login com credenciais válidas")
    print("- Acesso a endpoint protegido")
    print("- Login com credenciais inválidas")
    print("- Acesso sem token")
    print("- Acesso ao dashboard")
    
    print("\n✅ Testes concluídos! Verifique os resultados acima.")

if __name__ == "__main__":
    main()
