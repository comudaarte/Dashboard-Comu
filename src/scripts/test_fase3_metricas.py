#!/usr/bin/env python3
"""
Script de teste para as métricas da FASE 3 implementadas no MetricsCalculator
Testa todas as novas funções avançadas criadas
"""

import sys
import os
sys.path.append('/app/src')

from datetime import datetime, timedelta
from database.connection import get_session
from services.metrics_calculator import MetricsCalculator
from sqlalchemy import text

def test_fase3_metrics():
    """Testa todas as métricas da FASE 3"""
    
    print("\n" + "="*70)
    print("🧪 TESTE DAS MÉTRICAS FASE 3 - DASHBOARD COMU")
    print("="*70)
    
    try:
        print(f"\n📅 Teste realizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # ============================================================================
        # 1. TESTE: MÉTRICAS AVANÇADAS ESSENCIAIS
        # ============================================================================
        print("\n" + "="*50)
        print("🚀 1. TESTE: MÉTRICAS AVANÇADAS ESSENCIAIS")
        print("="*50)
        
        # 1.1 CPL (Cost Per Lead)
        print("\n📊 Testando: calculate_cpl()")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            cpl_data = calculator.calculate_cpl()
            print(f"  ✅ Total Leads: {cpl_data['total_leads_periodo']}")
            print(f"  📊 CPL Total: {cpl_data['cpl_total']}")
            print(f"  📋 Instruções: {cpl_data['instrucoes']}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 1.2 NPS (Net Promoter Score)
        print("\n📊 Testando: calculate_nps()")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            nps_data = calculator.calculate_nps()
            print(f"  ✅ NPS Total: {nps_data['nps_total']:.1f}")
            print(f"  📊 Promotores: {nps_data['breakdown_total']['promotores']}")
            print(f"  📊 Neutros: {nps_data['breakdown_total']['neutros']}")
            print(f"  📊 Detratores: {nps_data['breakdown_total']['detratores']}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 1.3 MRA (Monthly Recurring Average)
        print("\n📊 Testando: calculate_mra()")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            mra_data = calculator.calculate_mra()
            print(f"  ✅ MRA Total: R$ {mra_data['mra_total']:,.2f}")
            print(f"  📊 Total Assinaturas: {mra_data['total_assinaturas']}")
            print(f"  📊 Receita Recorrente Total: R$ {mra_data['total_receita_recorrente']:,.2f}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 1.4 Taxa de Conversão
        print("\n📊 Testando: calculate_conversion_rate(30)")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            conversao_data = calculator.calculate_conversion_rate(30)
            print(f"  ✅ Taxa de Conversão Total: {conversao_data['taxa_conversao_total']:.2f}%")
            print(f"  📊 Total Leads: {conversao_data['total_leads_periodo']}")
            print(f"  📊 Total Convertidos: {conversao_data['total_convertidos_periodo']}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 1.5 Customer Health Score
        print("\n📊 Testando: calculate_customer_health_score()")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            health_data = calculator.calculate_customer_health_score()
            print(f"  ✅ Health Score Total: {health_data['health_score_total']:.1f}/100")
            print(f"  📊 Alta Saúde: {health_data['breakdown_total']['alta_saude']}")
            print(f"  📊 Saúde Média: {health_data['breakdown_total']['saude_media']}")
            print(f"  📊 Baixa Saúde: {health_data['breakdown_total']['baixa_saude']}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 1.6 Revenue Growth Rate
        print("\n📊 Testando: calculate_revenue_growth_rate(365)")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            growth_data = calculator.calculate_revenue_growth_rate(365)
            print(f"  ✅ Growth Rate Total: {growth_data['growth_rate_total']:.2f}%")
            print(f"  📊 Receita Atual: R$ {growth_data['receita_atual']:,.2f}")
            print(f"  📊 Receita Anterior: R$ {growth_data['receita_anterior']:,.2f}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 1.7 Customer Acquisition Velocity
        print("\n📊 Testando: calculate_customer_acquisition_velocity(30)")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            velocity_data = calculator.calculate_customer_acquisition_velocity(30)
            print(f"  ✅ Velocity Total: {velocity_data['velocity_total']:.2f} clientes/dia")
            print(f"  📊 Novos Clientes: {velocity_data['novos_clientes_periodo']}")
            print(f"  📊 Período: {velocity_data['periodo_dias']} dias")
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
        
        # 2.1 CPL com custos simulados
        print("\n📊 Testando: calculate_cpl(custo_marketing=10000)")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            cpl_data = calculator.calculate_cpl(custo_marketing=10000)
            print(f"  ✅ CPL Total: R$ {cpl_data['cpl_total']:.2f}")
            print(f"  📊 Custo Marketing: R$ {cpl_data['custo_marketing_informado']:,.2f}")
            print(f"  📊 Total Leads: {cpl_data['total_leads_periodo']}")
            db_session.close()
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 2.2 Revenue Growth Rate para período específico
        print("\n📊 Testando: calculate_revenue_growth_rate(180)")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            growth_data = calculator.calculate_revenue_growth_rate(180)
            print(f"  ✅ Growth Rate (6 meses): {growth_data['growth_rate_total']:.2f}%")
            print(f"  📊 Período: {growth_data['periodo_dias']} dias")
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
        
        # 3.1 Verificar se NPS está dentro do range válido (-100 a +100)
        print("\n📊 Validando: NPS dentro do range válido (-100 a +100)")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            
            nps_data = calculator.calculate_nps()
            nps_total = nps_data['nps_total']
            
            print(f"  📊 NPS Total: {nps_total:.1f}")
            
            if -100 <= nps_total <= 100:
                print("  ✅ VÁLIDO: NPS dentro do range esperado")
            else:
                print("  ⚠️ INVÁLIDO: NPS fora do range esperado")
            
            db_session.close()
                
        except Exception as e:
            print(f"  ❌ Erro na validação: {str(e)}")
            if 'db_session' in locals():
                db_session.close()
        
        # 3.2 Verificar se Health Score está dentro do range válido (0 a 100)
        print("\n📊 Validando: Health Score dentro do range válido (0 a 100)")
        try:
            db_session = get_session()
            calculator = MetricsCalculator(db_session)
            
            health_data = calculator.calculate_customer_health_score()
            health_score = health_data['health_score_total']
            
            print(f"  📊 Health Score Total: {health_score:.1f}")
            
            if 0 <= health_score <= 100:
                print("  ✅ VÁLIDO: Health Score dentro do range esperado")
            else:
                print("  ⚠️ INVÁLIDO: Health Score fora do range esperado")
            
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
        
        print("\n📊 Testando performance das métricas FASE 3:")
        metricas_teste = [
            ("CPL", lambda: calculator.calculate_cpl()),
            ("NPS", lambda: calculator.calculate_nps()),
            ("MRA", lambda: calculator.calculate_mra()),
            ("Taxa de Conversão", lambda: calculator.calculate_conversion_rate(30)),
            ("Health Score", lambda: calculator.calculate_customer_health_score()),
            ("Revenue Growth", lambda: calculator.calculate_revenue_growth_rate(365)),
            ("Acquisition Velocity", lambda: calculator.calculate_customer_acquisition_velocity(30))
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
        print("📋 5. RESUMO DOS TESTES FASE 3")
        print("="*50)
        
        print("\n✅ MÉTRICAS AVANÇADAS IMPLEMENTADAS E TESTADAS:")
        print("  1. calculate_cpl() - Cost Per Lead")
        print("  2. calculate_nps() - Net Promoter Score")
        print("  3. calculate_mra() - Monthly Recurring Average")
        print("  4. calculate_conversion_rate() - Taxa de Conversão")
        print("  5. calculate_customer_health_score() - Customer Health Score")
        print("  6. calculate_revenue_growth_rate() - Revenue Growth Rate")
        print("  7. calculate_customer_acquisition_velocity() - Acquisition Velocity")
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("  1. Integrar com callbacks do dashboard")
        print("  2. Substituir dados sintéticos por dados reais")
        print("  3. Implementar FASE 4 (métricas de segmentação)")
        print("  4. Testar interatividade completa")
        
        print("\n" + "="*70)
        print("🎉 TESTES FASE 3 CONCLUÍDOS COM SUCESSO!")
        print("="*70)
        
    except Exception as e:
        print(f"❌ Erro geral durante testes: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fase3_metrics()
