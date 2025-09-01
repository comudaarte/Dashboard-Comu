"""
Script de teste para API da Guru
Verifica conectividade e funcionamento básico
"""
import sys
import os
from datetime import datetime, timedelta

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.guru_api_client import GuruAPIClient

def test_guru_connectivity():
    """
    Testa conectividade básica com a API da Guru
    """
    print("🔍 Testando conectividade com API da Guru...")
    
    try:
        client = GuruAPIClient()
        
        # Testa headers
        headers = client.get_headers()
        print(f"✅ Headers gerados: {headers}")
        
        # Testa busca de transações (últimos 7 dias)
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        print(f"\n💰 Testando busca de transações de {start_date} até {end_date}...")
        
        transactions_data = client.get_transactions_with_cursor(start_date, end_date)
        
        if transactions_data:
            transactions = transactions_data.get("data", [])
            print(f"✅ Transações encontradas: {len(transactions)}")
            
            if transactions:
                # Mostra exemplo da primeira transação
                first_transaction = transactions[0]
                print(f"\n📋 Exemplo de transação:")
                print(f"   ID: {first_transaction.get('id')}")
                print(f"   Status: {first_transaction.get('status')}")
                print(f"   Cliente: {first_transaction.get('contact', {}).get('name')}")
                print(f"   Email: {first_transaction.get('contact', {}).get('email')}")
                print(f"   Valor: R$ {first_transaction.get('payment', {}).get('total', 0)}")
        else:
            print("⚠️ Nenhuma transação encontrada no período")
        
        # Testa busca de assinaturas
        print(f"\n📋 Testando busca de assinaturas...")
        
        subscriptions_data = client.get_subscriptions_with_dates(start_date, end_date)
        
        if subscriptions_data:
            subscriptions = subscriptions_data.get("data", [])
            print(f"✅ Assinaturas encontradas: {len(subscriptions)}")
            
            if subscriptions:
                # Mostra exemplo da primeira assinatura
                first_subscription = subscriptions[0]
                print(f"\n📋 Exemplo de assinatura:")
                print(f"   ID: {first_subscription.get('id')}")
                print(f"   Status: {first_subscription.get('last_status')}")
                print(f"   Cliente: {first_subscription.get('contact', {}).get('name')}")
                print(f"   Email: {first_subscription.get('contact', {}).get('email')}")
                print(f"   Produto: {first_subscription.get('product', {}).get('name')}")
        else:
            print("⚠️ Nenhuma assinatura encontrada")
        
        print("\n✅ Teste de conectividade concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no teste de conectividade: {e}")
        return False
    
    return True

def test_guru_backfill_sample():
    """
    Testa o backfill com uma amostra pequena de dados
    """
    print("\n🧪 Testando backfill com amostra...")
    
    try:
        from scripts.backfill_guru import GuruBackfill
        
        # Testa com apenas 1 dia
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        backfill = GuruBackfill()
        backfill.run_backfill(start_date, end_date)
        
        print("✅ Teste de backfill concluído!")
        
    except Exception as e:
        print(f"❌ Erro no teste de backfill: {e}")

def main():
    """
    Função principal
    """
    print("🚀 Iniciando testes da API Guru...")
    
    # Teste 1: Conectividade
    if test_guru_connectivity():
        print("\n" + "="*50)
        print("✅ Todos os testes de conectividade passaram!")
        print("="*50)
        
        # Teste 2: Backfill (opcional)
        response = input("\n🧪 Deseja testar o backfill com amostra? (s/n): ")
        if response.lower() in ['s', 'sim', 'y', 'yes']:
            test_guru_backfill_sample()
    else:
        print("\n❌ Testes de conectividade falharam!")
        print("Verifique:")
        print("1. Se as variáveis de ambiente estão configuradas")
        print("2. Se os tokens da Guru são válidos")
        print("3. Se há conexão com a internet")

if __name__ == "__main__":
    main() 