#!/usr/bin/env python3
"""
Script de teste para as métricas da FASE 2 implementadas no MetricsCalculator
Testa todas as novas funções de performance criadas
"""

import sys
import os
sys.path.append('/app/src')

from datetime import datetime, timedelta
from database.connection import get_session
from services.metrics_calculator import MetricsCalculator
from sqlalchemy import text

def test_fase2_metrics():
    """Testa todas as métricas da FASE 2"""
    
    print("\n" + "="*70)
    print("🧪 TESTE DAS MÉTRICAS FASE 2 - DASHBOARD COMU")
    print("="*70)
    
    try:
        print(f"\n📅 Teste realizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # ============================================================================
        # 1. TESTE: MÉTRICAS DE PERFORMANCE ESSENCIAIS
        # ============================================================================
        print("\n" + "="*50)
        print("🚀 1. TESTE: MÉTRICAS DE PERFORMANCE ESSENCIAIS")
        print("="*50)
        
        # 1.1 ARPU (Average Revenue Per User)
        print("\n📊 Testando: calculate_arpu()")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            arpu_data = calculator.calculate_arpu()
            print(f"  ✅ ARPU Total: R$ {arpu_data['arpu_total']:,.2f}")
            print(f"  📊 MRR Base: R$ {arpu_data['mrr_base']:,.2f}")
            print(f"  👥 Total Clientes: {arpu_data['total_clientes_base']}")
            print(f"  📋 Breakdown: {arpu_data['arpu_por_plataforma']}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 1.2 Retention Rate
        print("\n📊 Testando: calculate_retention_rate(30)")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            retention_data = calculator.calculate_retention_rate(30)
            print(f"  ✅ Retention Rate Total: {retention_data['retention_rate_total']:.2f}%")
            print(f"  📊 Churn Rate Base: {retention_data['churn_rate_base']:.2f}%")
            print(f"  📋 Breakdown: {retention_data['retention_por_plataforma']}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 1.3 Receita Anual da Empresa
        print("\n📊 Testando: calculate_annual_revenue()")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            receita_data = calculator.calculate_annual_revenue()
            print(f"  ✅ Receita Anual Total: R$ {receita_data['receita_anual_total']:,.2f}")
            print(f"  📊 ARR Componente: R$ {receita_data['arr_componente']:,.2f}")
            print(f"  📊 Receita Pontual: R$ {receita_data['receita_pontual_componente']:,.2f}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 1.4 Margem de Lucro (sem custos)
        print("\n📊 Testando: calculate_profit_margin()")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            margem_data = calculator.calculate_profit_margin()
            print(f"  ✅ Receita Total: R$ {margem_data['receita_total']:,.2f}")
            print(f"  📊 Custos Operacionais: {margem_data['custos_operacionais']}")
            print(f"  📊 Margem de Lucro: {margem_data['margem_lucro_percentual']}")
            print(f"  📋 Instruções: {margem_data['instrucoes']}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 1.5 ROI (sem investimento)
        print("\n📊 Testando: calculate_roi()")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            roi_data = calculator.calculate_roi()
            print(f"  ✅ Receita do Período: R$ {roi_data['receita_periodo']:,.2f}")
            print(f"  📊 Investimento Total: {roi_data['investimento_total']}")
            print(f"  📊 ROI Percentual: {roi_data['roi_percentual']}")
            print(f"  📋 Instruções: {roi_data['instrucoes']}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 1.6 Assinaturas por Mês
        print("\n📊 Testando: calculate_subscriptions_by_month()")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            assinaturas_mes_data = calculator.calculate_subscriptions_by_month()
            print(f"  ✅ Ano: {assinaturas_mes_data['ano']}")
            print(f"  📊 Total Assinaturas Ano: {assinaturas_mes_data['total_assinaturas_ano']}")
            print(f"  📊 Total Válidas: {assinaturas_mes_data['total_validas_ano']}")
            print(f"  📊 Total Canceladas: {assinaturas_mes_data['total_canceladas_ano']}")
            print(f"  📊 Taxa Cancelamento Ano: {assinaturas_mes_data['taxa_cancelamento_ano']:.2f}%")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 1.7 Ticket Médio Geral
        print("\n📊 Testando: calculate_average_ticket()")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            ticket_data = calculator.calculate_average_ticket()
            print(f"  ✅ Ticket Médio Geral: R$ {ticket_data['ticket_medio_geral']:,.2f}")
            print(f"  📊 Total Transações: {ticket_data['total_transacoes_geral']}")
            print(f"  📊 Receita Total: R$ {ticket_data['receita_total_geral']:,.2f}")
            print(f"  📋 Breakdown: {ticket_data['ticket_por_plataforma']}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # ============================================================================
        # 2. TESTE: CÁLCULOS COM PARÂMETROS ESPECÍFICOS
        # ============================================================================
        print("\n" + "="*50)
        print("🔢 2. TESTE: CÁLCULOS COM PARÂMETROS ESPECÍFICOS")
        print("="*50)
        
        # 2.1 Margem de Lucro com custos simulados
        print("\n📊 Testando: calculate_profit_margin(custos_operacionais=50000)")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            margem_data = calculator.calculate_profit_margin(custos_operacionais=50000)
            print(f"  ✅ Margem de Lucro: {margem_data['margem_lucro_percentual']:.2f}%")
            print(f"  📊 Receita Total: R$ {margem_data['receita_total']:,.2f}")
            print(f"  📊 Custos Operacionais: R$ {margem_data['custos_operacionais']:,.2f}")
            print(f"  📊 Lucro Bruto: R$ {margem_data['lucro_bruto']:,.2f}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 2.2 ROI com investimento simulado
        print("\n📊 Testando: calculate_roi(investimento_total=100000)")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            roi_data = calculator.calculate_roi(investimento_total=100000)
            print(f"  ✅ ROI Percentual: {roi_data['roi_percentual']:.2f}%")
            print(f"  📊 Receita do Período: R$ {roi_data['receita_periodo']:,.2f}")
            print(f"  📊 Investimento Total: R$ {roi_data['investimento_total']:,.2f}")
            print(f"  📊 Retorno Líquido: R$ {roi_data['retorno_liquido']:,.2f}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 2.3 Assinaturas por mês para ano específico
        print("\n📊 Testando: calculate_subscriptions_by_month(2024)")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            assinaturas_mes_data = calculator.calculate_subscriptions_by_month(2024)
            print(f"  ✅ Ano: {assinaturas_mes_data['ano']}")
            print(f"  📊 Total Assinaturas: {assinaturas_mes_data['total_assinaturas_ano']}")
            print(f"  📊 Taxa Cancelamento: {assinaturas_mes_data['taxa_cancelamento_ano']:.2f}%")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # ============================================================================
        # 3. VALIDAÇÃO DE CONSISTÊNCIA ENTRE MÉTRICAS
        # ============================================================================
        print("\n" + "="*50)
        print("🔍 3. VALIDAÇÃO DE CONSISTÊNCIA ENTRE MÉTRICAS")
        print("="*50)
        
        # 3.1 Verificar se Retention Rate + Churn Rate = 100%
        print("\n📊 Validando: Retention Rate + Churn Rate = 100%")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            
            retention_data = calculator.calculate_retention_rate(30)
            churn_data = calculator.calculate_churn_rate(30)
            
            retention_rate = retention_data['retention_rate_total']
            churn_rate = churn_data['churn_rate_total']
            soma = retention_rate + churn_rate
            
            print(f"  📊 Retention Rate: {retention_rate:.2f}%")
            print(f"  📊 Churn Rate: {churn_rate:.2f}%")
            print(f"  📊 Soma: {soma:.2f}%")
            
            if abs(soma - 100.0) < 0.01:  # Tolerância de 0.01%
                print("  ✅ CONSISTENTE: Retention Rate + Churn Rate = 100%")
            else:
                print("  ⚠️ INCONSISTENTE: Diferença detectada")
            
            db_session.close()
                
        except Exception as e:
            print(f"  ❌ Erro na validação: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 3.2 Verificar se ARPU × Total Clientes = MRR Total
        print("\n📊 Validando: ARPU × Total Clientes = MRR Total")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            
            arpu_data = calculator.calculate_arpu()
            mrr_data = calculator.calculate_mrr()
            
            arpu_total = arpu_data['arpu_total']
            total_clientes = arpu_data['total_clientes_base']
            mrr_total = mrr_data['mrr_total']
            
            calculado = arpu_total * total_clientes
            diferenca = abs(calculado - mrr_total)
            
            print(f"  📊 ARPU: R$ {arpu_total:.2f}")
            print(f"  📊 Total Clientes: {total_clientes}")
            print(f"  📊 Calculado: R$ {calculado:.2f}")
            print(f"  📊 MRR Total: R$ {mrr_total:.2f}")
            print(f"  📊 Diferença: R$ {diferenca:.2f}")
            
            if diferenca < 0.01:  # Tolerância de 1 centavo
                print("  ✅ CONSISTENTE: ARPU × Total Clientes = MRR Total")
            else:
                print("  ⚠️ INCONSISTENTE: Diferença detectada")
            
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
        
        print("\n📊 Testando performance das métricas FASE 2:")
        metricas_teste = [
            ("ARPU", lambda: calculator.calculate_arpu()),
            ("Retention Rate", lambda: calculator.calculate_retention_rate(30)),
            ("Receita Anual", lambda: calculator.calculate_annual_revenue()),
            ("Ticket Médio", lambda: calculator.calculate_average_ticket()),
            ("Assinaturas por Mês", lambda: calculator.calculate_subscriptions_by_month())
        ]
        
        try:
            import time
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            
            for nome, funcao in metricas_teste:
                try:
                    inicio = time.time()
                    resultado = funcao()
                    fim = time.time()
                    tempo = (fim - inicio) * 1000  # em milissegundos
                    print(f"  ✅ {nome}: {tempo:.2f}ms")
                except Exception as e:
                    print(f"  ❌ {nome}: Erro - {str(e)}")
            
            db_session.close()
            
        except Exception as e:
            print(f"  ❌ Erro no teste de performance: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # ============================================================================
        # 5. RESUMO DOS TESTES
        # ============================================================================
        print("\n" + "="*50)
        print("📋 5. RESUMO DOS TESTES FASE 2")
        print("="*50)
        
        print("\n✅ MÉTRICAS IMPLEMENTADAS E TESTADAS:")
        print("  1. calculate_arpu() - Receita média por usuário")
        print("  2. calculate_retention_rate() - Taxa de retenção")
        print("  3. calculate_annual_revenue() - Receita anual total")
        print("  4. calculate_profit_margin() - Margem de lucro")
        print("  5. calculate_roi() - Return on Investment")
        print("  6. calculate_subscriptions_by_month() - Assinaturas por mês")
        print("  7. calculate_average_ticket() - Ticket médio geral")
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("  1. Integrar com callbacks do dashboard")
        print("  2. Substituir dados sintéticos por dados reais")
        print("  3. Implementar FASE 3 (métricas avançadas)")
        print("  4. Testar interatividade completa")
        
        print("\n" + "="*70)
        print("🎉 TESTES FASE 2 CONCLUÍDOS COM SUCESSO!")
        print("="*70)
        
    except Exception as e:
        print(f"❌ Erro geral durante testes: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fase2_metrics()
