#!/usr/bin/env python3
"""
Script para verificar dados no banco de dados
"""

import sys
import os
sys.path.append('src')

from database.connection import get_session
from services.metrics_calculator import MetricsCalculator
from datetime import datetime

def check_database():
    """Verifica dados no banco de dados"""
    try:
        print("🔍 Verificando banco de dados...")
        
        # Conecta ao banco
        session = get_session()
        calculator = MetricsCalculator(session)
        
        # Verifica contagem de registros
        print("\n📊 CONTAGEM DE REGISTROS:")
        
        # Clientes
        clientes_count = session.execute("SELECT COUNT(*) FROM clientes").scalar()
        print(f"   Clientes: {clientes_count}")
        
        # Assinaturas
        assinaturas_count = session.execute("SELECT COUNT(*) FROM assinaturas").scalar()
        print(f"   Assinaturas: {assinaturas_count}")
        
        # Transações
        transacoes_count = session.execute("SELECT COUNT(*) FROM transacoes").scalar()
        print(f"   Transações: {transacoes_count}")
        
        # Verifica dados de exemplo
        print("\n📋 DADOS DE EXEMPLO:")
        
        # Cliente
        cliente = session.execute("SELECT * FROM clientes LIMIT 1").fetchone()
        if cliente:
            print(f"   Cliente: {cliente.nome} ({cliente.email}) - Criado: {cliente.data_criacao}")
        else:
            print("   ❌ Nenhum cliente encontrado")
        
        # Assinatura
        assinatura = session.execute("SELECT * FROM assinaturas LIMIT 1").fetchone()
        if assinatura:
            print(f"   Assinatura: {assinatura.produto_nome} - Status: {assinatura.status} - Início: {assinatura.data_inicio}")
        else:
            print("   ❌ Nenhuma assinatura encontrada")
        
        # Transação
        transacao = session.execute("SELECT * FROM transacoes LIMIT 1").fetchone()
        if transacao:
            print(f"   Transação: R$ {transacao.valor} - Status: {transacao.status} - Data: {transacao.data_transacao}")
        else:
            print("   ❌ Nenhuma transação encontrada")
        
        # Testa cálculo de métricas
        print("\n🧮 TESTANDO CÁLCULO DE MÉTRICAS:")
        
        data_ref = datetime.now()
        
        try:
            mrr = calculator.calculate_mrr(data_ref)
            print(f"   ✅ MRR: R$ {mrr['mrr_total']:.2f}")
        except Exception as e:
            print(f"   ❌ Erro ao calcular MRR: {str(e)}")
        
        try:
            arr = calculator.calculate_arr(data_ref)
            print(f"   ✅ ARR: R$ {arr['arr_total']:.2f}")
        except Exception as e:
            print(f"   ❌ Erro ao calcular ARR: {str(e)}")
        
        try:
            churn = calculator.calculate_churn_rate(30)
            print(f"   ✅ Churn Rate: {churn['taxa_churn']:.2f}%")
        except Exception as e:
            print(f"   ❌ Erro ao calcular Churn: {str(e)}")
        
        try:
            ltv = calculator.calculate_ltv(data_ref)
            print(f"   ✅ LTV: R$ {ltv['ltv_medio']:.2f}")
        except Exception as e:
            print(f"   ❌ Erro ao calcular LTV: {str(e)}")
        
        try:
            assinaturas_ativas = calculator.calculate_active_subscriptions(data_ref)
            print(f"   ✅ Assinaturas Ativas: {assinaturas_ativas['total_assinaturas_ativas']}")
        except Exception as e:
            print(f"   ❌ Erro ao calcular Assinaturas Ativas: {str(e)}")
        
        session.close()
        
        print("\n✅ Verificação concluída!")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
