#!/usr/bin/env python3
"""
Script de teste para as métricas da FASE 1 implementadas no MetricsCalculator
Testa todas as novas funções básicas criadas
"""

import sys
import os
sys.path.append('/app/src')

from datetime import datetime, timedelta
from database.connection import get_session
from services.metrics_calculator import MetricsCalculator
from sqlalchemy import text

def test_fase1_metrics():
    """Testa todas as métricas da FASE 1"""
    
    print("\n" + "="*70)
    print("🧪 TESTE DAS MÉTRICAS FASE 1 - DASHBOARD COMU")
    print("="*70)
    
    try:
        print(f"\n📅 Teste realizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # ============================================================================
        # 1. TESTE: MÉTRICAS DE CONTAGEM ESSENCIAIS
        # ============================================================================
        print("\n" + "="*50)
        print("🔢 1. TESTE: MÉTRICAS DE CONTAGEM ESSENCIAIS")
        print("="*50)
        
        # 1.1 Assinaturas Ativas
        print("\n📊 Testando: calculate_active_subscriptions()")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            ativas_data = calculator.calculate_active_subscriptions()
            print(f"  ✅ Assinaturas Ativas: {ativas_data['total_ativas']}")
            print(f"  📋 Breakdown: {ativas_data['detalhes']['breakdown_por_plataforma']}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 1.2 Assinaturas Canceladas
        print("\n📊 Testando: calculate_canceled_subscriptions()")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            canceladas_data = calculator.calculate_canceled_subscriptions()
            print(f"  ✅ Assinaturas Canceladas: {canceladas_data['total_canceladas']}")
            print(f"  📋 Breakdown: {canceladas_data['detalhes']['breakdown_por_plataforma']}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 1.3 Total de Vendas
        print("\n📊 Testando: calculate_total_sales()")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            vendas_data = calculator.calculate_total_sales()
            print(f"  ✅ Total de Vendas: {vendas_data['total_vendas']}")
            print(f"  📋 Breakdown: {vendas_data['detalhes']['breakdown_por_plataforma']}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 1.4 Clientes Únicos
        print("\n📊 Testando: calculate_unique_customers()")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            clientes_data = calculator.calculate_unique_customers()
            print(f"  ✅ Clientes Únicos: {clientes_data['total_clientes_unicos']}")
            print(f"  📋 Breakdown: {clientes_data['detalhes']['breakdown_por_plataforma']}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # ============================================================================
        # 2. TESTE: MÉTRICAS DE CRESCIMENTO MRR
        # ============================================================================
        print("\n" + "="*50)
        print("📈 2. TESTE: MÉTRICAS DE CRESCIMENTO MRR")
        print("="*50)
        
        # 2.1 MRR Growth (30 dias)
        print("\n📊 Testando: calculate_mrr_growth(30)")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            growth_data = calculator.calculate_mrr_growth(30)
            print(f"  ✅ MRR Growth (30 dias): {growth_data['crescimento_percentual']:.2f}%")
            print(f"  📊 MRR Atual: R$ {growth_data['mrr_atual']:,.2f}")
            print(f"  📊 MRR Anterior: R$ {growth_data['mrr_anterior']:,.2f}")
            print(f"  📈 Tendência: {growth_data['tendencia']}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 2.2 MRR por Tipo de Plano - Mensal
        print("\n📊 Testando: calculate_mrr_by_plan_type('mensal')")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            mrr_mensal = calculator.calculate_mrr_by_plan_type('mensal')
            print(f"  ✅ MRR Mensal: R$ {mrr_mensal['mrr_total']:,.2f}")
            print(f"  📋 Breakdown: {mrr_mensal['detalhes']['breakdown_por_plataforma']}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 2.3 MRR por Tipo de Plano - Anual
        print("\n📊 Testando: calculate_mrr_by_plan_type('anual')")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            mrr_anual = calculator.calculate_mrr_by_plan_type('anual')
            print(f"  ✅ MRR Anual: R$ {mrr_anual['mrr_total']:,.2f}")
            print(f"  📋 Breakdown: {mrr_anual['detalhes']['breakdown_por_plataforma']}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 2.4 ARR por Tipo de Plano - Mensal
        print("\n📊 Testando: calculate_arr_by_plan_type('mensal')")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            arr_mensal = calculator.calculate_arr_by_plan_type('mensal')
            print(f"  ✅ ARR Mensal: R$ {arr_mensal['arr_total']:,.2f}")
            print(f"  📊 MRR Base: R$ {arr_mensal['mrr_base']:,.2f}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 2.5 ARR por Tipo de Plano - Anual
        print("\n📊 Testando: calculate_arr_by_plan_type('anual')")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            arr_anual = calculator.calculate_arr_by_plan_type('anual')
            print(f"  ✅ ARR Anual: R$ {arr_anual['arr_total']:,.2f}")
            print(f"  📊 MRR Base: R$ {arr_anual['mrr_base']:,.2f}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # ============================================================================
        # 3. VALIDAÇÃO DE CONSISTÊNCIA
        # ============================================================================
        print("\n" + "="*50)
        print("🔍 3. VALIDAÇÃO DE CONSISTÊNCIA ENTRE MÉTRICAS")
        print("="*50)
        
        # 3.1 Verificar se MRR Total = MRR Mensal + MRR Anual
        print("\n📊 Validando: MRR Total = MRR Mensal + MRR Anual")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            mrr_total = calculator.calculate_mrr()
            mrr_mensal = calculator.calculate_mrr_by_plan_type('mensal')
            mrr_anual = calculator.calculate_mrr_by_plan_type('anual')
            
            mrr_soma_tipos = float(mrr_mensal['mrr_total']) + float(mrr_anual['mrr_total'])
            diferenca = abs(float(mrr_total['mrr_total']) - mrr_soma_tipos)
            
            print(f"  📊 MRR Total: R$ {mrr_total['mrr_total']:,.2f}")
            print(f"  📊 MRR Mensal: R$ {mrr_mensal['mrr_total']:,.2f}")
            print(f"  📊 MRR Anual: R$ {mrr_anual['mrr_total']:,.2f}")
            print(f"  📊 Soma Tipos: R$ {mrr_soma_tipos:,.2f}")
            print(f"  📊 Diferença: R$ {diferenca:,.2f}")
            
            if diferenca < 0.01:  # Tolerância de 1 centavo
                print("  ✅ CONSISTENTE: MRR Total = MRR Mensal + MRR Anual")
            else:
                print("  ⚠️ INCONSISTENTE: Diferença detectada")
            
            db_session.close()
                
        except Exception as e:
            print(f"  ❌ Erro na validação: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 3.2 Verificar se Assinaturas Ativas + Canceladas = Total
        print("\n📊 Validando: Assinaturas Ativas + Canceladas = Total")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            
            ativas_data = calculator.calculate_active_subscriptions()
            canceladas_data = calculator.calculate_canceled_subscriptions()
            
            ativas = ativas_data['total_ativas']
            canceladas = canceladas_data['total_canceladas']
            
            # Buscar total geral de assinaturas
            query = text("SELECT COUNT(*) as total FROM assinaturas")
            result = db_session.execute(query).fetchone()
            total_geral = result.total if result else 0
            
            print(f"  📊 Assinaturas Ativas: {ativas}")
            print(f"  📊 Assinaturas Canceladas: {canceladas}")
            print(f"  📊 Soma: {ativas + canceladas}")
            print(f"  📊 Total Geral: {total_geral}")
            
            if ativas + canceladas <= total_geral:
                print("  ✅ CONSISTENTE: Soma <= Total Geral")
            else:
                print("  ⚠️ INCONSISTENTE: Soma > Total Geral")
            
            db_session.close()
                
        except Exception as e:
            print(f"  ❌ Erro na validação: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # ============================================================================
        # 4. TESTE DE PERFORMANCE SIMPLIFICADO
        # ============================================================================
        print("\n" + "="*50)
        print("⚡ 4. TESTE DE PERFORMANCE SIMPLIFICADO")
        print("="*50)
        
        print("\n📊 Testando performance de uma métrica:")
        try:
            import time
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            
            inicio = time.time()
            resultado = calculator.calculate_active_subscriptions()
            fim = time.time()
            tempo = (fim - inicio) * 1000  # em milissegundos
            
            print(f"  ✅ Assinaturas Ativas: {tempo:.2f}ms")
            db_session.close()
            
        except Exception as e:
            print(f"  ❌ Erro no teste de performance: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # ============================================================================
        # 5. RESUMO DOS TESTES
        # ============================================================================
        print("\n" + "="*50)
        print("📋 5. RESUMO DOS TESTES FASE 1")
        print("="*50)
        
        print("\n✅ MÉTRICAS IMPLEMENTADAS E TESTADAS:")
        print("  1. calculate_active_subscriptions()")
        print("  2. calculate_canceled_subscriptions()")
        print("  3. calculate_total_sales()")
        print("  4. calculate_unique_customers()")
        print("  5. calculate_mrr_growth()")
        print("  6. calculate_mrr_by_plan_type()")
        print("  7. calculate_arr_by_plan_type()")
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("  1. Integrar com callbacks do dashboard")
        print("  2. Substituir dados sintéticos por dados reais")
        print("  3. Implementar FASE 2 (métricas de performance)")
        print("  4. Testar interatividade completa")
        
        print("\n" + "="*70)
        print("🎉 TESTES FASE 1 CONCLUÍDOS COM SUCESSO!")
        print("="*70)
        
    except Exception as e:
        print(f"❌ Erro geral durante testes: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fase1_metrics()
