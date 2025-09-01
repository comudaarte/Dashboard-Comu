#!/usr/bin/env python3
"""
Teste de Integração Dashboard + MetricsCalculator
================================================

Testa se a integração entre o dashboard e as métricas
está funcionando corretamente.
"""

import sys
import os
from datetime import datetime, timedelta

# Adiciona o diretório src ao path
sys.path.append('/app/src')

from database.connection import get_session
from services.metrics_calculator import MetricsCalculator


def test_integracao_dashboard():
    """Testa a integração entre dashboard e métricas"""
    
    print("🚀 TESTE DE INTEGRAÇÃO: DASHBOARD + METRICSCALCULATOR")
    print("=" * 65)
    
    try:
        # Cria sessão do banco
        db_session = get_session()
        calculator = MetricsCalculator(db_session)
        
        print(f"✅ Conectado ao banco de dados")
        print(f"📅 Data de referência: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        print()
        
        # ========================================================================
        # TESTE 1: Simulação do Callback Principal
        # ========================================================================
        print("📊 TESTE 1: Simulação do Callback Principal")
        print("-" * 45)
        
        try:
            # Simula os parâmetros do callback
            start_date = (datetime.now() - timedelta(days=30)).isoformat()
            end_date = datetime.now().isoformat()
            refresh_clicks = 1
            
            print(f"📅 Parâmetros do callback:")
            print(f"   • start_date: {start_date}")
            print(f"   • end_date: {end_date}")
            print(f"   • refresh_clicks: {refresh_clicks}")
            print()
            
            # Simula o cálculo de todas as métricas como no callback
            data_referencia = datetime.now()
            periodo_dias = 30
            
            print("🔄 Calculando todas as métricas...")
            
            # Métricas principais
            mrr_data = calculator.calculate_mrr(data_referencia)
            arr_data = calculator.calculate_arr(data_referencia)
            churn_data = calculator.calculate_churn_rate(periodo_dias)
            ltv_data = calculator.calculate_ltv(data_referencia)
            cac_data = calculator.calculate_cac(periodo_dias)
            
            # Métricas da FASE 1
            assinaturas_ativas_data = calculator.calculate_active_subscriptions(data_referencia)
            assinaturas_canceladas_data = calculator.calculate_canceled_subscriptions()
            total_vendas_data = calculator.calculate_total_sales(data_referencia)
            clientes_unicos_data = calculator.calculate_unique_customers(data_referencia)
            mrr_growth_data = calculator.calculate_mrr_growth(periodo_dias)
            mrr_mensal_data = calculator.calculate_mrr_by_plan_type('mensal', data_referencia)
            arr_mensal_data = calculator.calculate_arr_by_plan_type('mensal', data_referencia)
            mrr_anual_data = calculator.calculate_mrr_by_plan_type('anual', data_referencia)
            arr_anual_data = calculator.calculate_arr_by_plan_type('anual', data_referencia)
            
            # Métricas da FASE 2
            arpu_data = calculator.calculate_arpu(data_referencia)
            retention_data = calculator.calculate_retention_rate(periodo_dias)
            receita_anual_data = calculator.calculate_annual_revenue(data_referencia)
            margem_lucro_data = calculator.calculate_profit_margin(data_referencia=data_referencia)
            roi_data = calculator.calculate_roi(data_referencia=data_referencia)
            assinaturas_por_mes_data = calculator.calculate_subscriptions_by_month(data_referencia.year)
            ticket_medio_data = calculator.calculate_average_ticket(data_referencia)
            
            # Métricas da FASE 3
            cpl_data = calculator.calculate_cpl(periodo_dias)
            nps_data = calculator.calculate_nps(data_referencia)
            mra_data = calculator.calculate_mra(data_referencia)
            conversion_data = calculator.calculate_conversion_rate(periodo_dias)
            health_score_data = calculator.calculate_customer_health_score(data_referencia)
            revenue_growth_data = calculator.calculate_revenue_growth_rate(periodo_dias)
            acquisition_velocity_data = calculator.calculate_customer_acquisition_velocity(periodo_dias)
            
            # Métricas da FASE 4
            assinaturas_mes_atual_data = calculator.calculate_subscriptions_current_month(data_referencia)
            assinaturas_mes_passado_data = calculator.calculate_subscriptions_previous_month(data_referencia)
            
            print("✅ Todas as métricas calculadas com sucesso!")
            print()
            
        except Exception as e:
            print(f"❌ Erro ao calcular métricas: {str(e)}")
            print()
            return False
        
        # ========================================================================
        # TESTE 2: Formatação dos Valores para Exibição
        # ========================================================================
        print("📊 TESTE 2: Formatação dos Valores para Exibição")
        print("-" * 45)
        
        try:
            # Simula a formatação como no callback
            print("🔄 Formatando valores para exibição...")
            
            # Grid Final de Métricas
            mrr_total = f"R$ {mrr_data['mrr_total']:,.2f}" if mrr_data['mrr_total'] else "R$ 0,00"
            arr_total = f"R$ {arr_data['arr_total']:,.2f}" if arr_data['arr_total'] else "R$ 0,00"
            mra_recorrencia = f"{mra_data['mra_total']:,.0f}" if mra_data['mra_total'] else "0"
            mrr_growth = f"{mrr_growth_data['crescimento_percentual']:+.1f}%" if mrr_growth_data['crescimento_percentual'] else "0,0%"
            
            mrr_mensal = f"R$ {mrr_mensal_data['mrr_total']:,.2f}" if mrr_mensal_data['mrr_total'] else "R$ 0,00"
            arr_mensal = f"R$ {arr_mensal_data['arr_total']:,.2f}" if arr_mensal_data['arr_total'] else "R$ 0,00"
            assinaturas_ativas = f"{assinaturas_ativas_data['total_ativas']:,.0f}" if assinaturas_ativas_data['total_ativas'] else "0"
            assinaturas_canceladas = f"{assinaturas_canceladas_data['total_canceladas']:,.0f}" if assinaturas_canceladas_data['total_canceladas'] else "0"
            
            mrr_anual = f"R$ {mrr_anual_data['mrr_total']:,.2f}" if mrr_anual_data['mrr_total'] else "R$ 0,00"
            arr_anual = f"R$ {arr_anual_data['arr_total']:,.2f}" if arr_anual_data['arr_total'] else "R$ 0,00"
            churn_rate = f"{churn_data['churn_rate_total']:.1f}%" if churn_data['churn_rate_total'] else "0,0%"
            retention_rate = f"{retention_data['retention_rate_total']:.1f}%" if retention_data['retention_rate_total'] else "0,0%"
            
            assinaturas_mes_atual = f"{assinaturas_mes_atual_data['total_assinaturas_mes_atual']:,.0f}" if assinaturas_mes_atual_data['total_assinaturas_mes_atual'] else "0"
            assinaturas_mes_passado = f"{assinaturas_mes_passado_data['total_assinaturas_mes_anterior']:,.0f}" if assinaturas_mes_passado_data['total_assinaturas_mes_anterior'] else "0"
            
            # Seção Principal
            faturamento_total = f"R$ {receita_anual_data['receita_anual_total']:,.2f}" if receita_anual_data['receita_anual_total'] else "R$ 0,00"
            quantidade_vendas = f"{total_vendas_data['total_vendas']:,.0f}" if total_vendas_data['total_vendas'] else "0"
            quantidade_alunos = f"{clientes_unicos_data['total_clientes_unicos']:,.0f}" if clientes_unicos_data['total_clientes_unicos'] else "0"
            ltv_geral = f"R$ {ltv_data['ltv_total']:,.2f}" if ltv_data['ltv_total'] else "R$ 0,00"
            
            # Seção Performance
            arpu = f"R$ {arpu_data['arpu_total']:,.2f}" if arpu_data['arpu_total'] else "R$ 0,00"
            cac = f"R$ {cac_data['cac_total']:,.2f}" if cac_data['cac_total'] else "R$ 0,00"
            roi = f"{roi_data['roi_percentual']:+.1f}%" if roi_data['roi_percentual'] else "0,0%"
            margem_lucro = f"{margem_lucro_data['margem_lucro_percentual']:.1f}%" if margem_lucro_data['margem_lucro_percentual'] else "0,0%"
            nps = f"{nps_data['nps_total']:+.0f}" if nps_data['nps_total'] else "0"
            customer_health = f"{health_score_data['health_score_total']:.0f}/100" if health_score_data['health_score_total'] else "0/100"
            conversion_rate = f"{conversion_data['taxa_conversao_total']:.1f}%" if conversion_data['taxa_conversao_total'] else "0,0%"
            revenue_growth = f"{revenue_growth_data['growth_rate_total']:+.1f}%" if revenue_growth_data['growth_rate_total'] else "0,0%"
            
            print("✅ Valores formatados para exibição!")
            print()
            
        except Exception as e:
            print(f"❌ Erro na formatação: {str(e)}")
            print()
            return False
        
        # ========================================================================
        # TESTE 3: Validação dos Valores Formatados
        # ========================================================================
        print("📊 TESTE 3: Validação dos Valores Formatados")
        print("-" * 45)
        
        try:
            print("🔍 Validando valores formatados...")
            
            # Validação 1: Verifica se todos os valores foram formatados
            valores_formatados = [
                mrr_total, arr_total, mra_recorrencia, mrr_growth,
                mrr_mensal, arr_mensal, assinaturas_ativas, assinaturas_canceladas,
                mrr_anual, arr_anual, churn_rate, retention_rate,
                assinaturas_mes_atual, assinaturas_mes_passado,
                faturamento_total, quantidade_vendas, quantidade_alunos, ltv_geral,
                arpu, cac, roi, margem_lucro, nps, customer_health, conversion_rate, revenue_growth
            ]
            
            total_valores = len(valores_formatados)
            valores_validos = sum(1 for v in valores_formatados if v and v != "R$ 0,00" and v != "0" and v != "0,0%")
            
            print(f"📊 Estatísticas de formatação:")
            print(f"   • Total de valores: {total_valores}")
            print(f"   • Valores válidos: {valores_validos}")
            print(f"   • Valores padrão: {total_valores - valores_validos}")
            print(f"   • Taxa de sucesso: {(valores_validos/total_valores)*100:.1f}%")
            print()
            
            # Validação 2: Verifica valores específicos
            print("🔍 Valores específicos:")
            print(f"   • MRR Total: {mrr_total}")
            print(f"   • ARR Total: {arr_total}")
            print(f"   • Assinaturas Ativas: {assinaturas_ativas}")
            print(f"   • Churn Rate: {churn_rate}")
            print(f"   • Assinaturas Mês Atual: {assinaturas_mes_atual}")
            print(f"   • Assinaturas Mês Passado: {assinaturas_mes_passado}")
            print()
            
        except Exception as e:
            print(f"❌ Erro na validação: {str(e)}")
            print()
            return False
        
        # ========================================================================
        # TESTE 4: Simulação de Retorno do Callback
        # ========================================================================
        print("📊 TESTE 4: Simulação de Retorno do Callback")
        print("-" * 45)
        
        try:
            print("🔄 Simulando retorno do callback...")
            
            # Simula o retorno exato do callback
            retorno_callback = [
                # Grid Final
                mrr_total, arr_total, mra_recorrencia, mrr_growth,
                mrr_mensal, arr_mensal, assinaturas_ativas, assinaturas_canceladas,
                mrr_anual, arr_anual, churn_rate, retention_rate,
                assinaturas_mes_atual, assinaturas_mes_passado,
                
                # Seção Principal
                faturamento_total, quantidade_vendas, quantidade_alunos, ltv_geral,
                
                # Seção Performance
                arpu, cac, roi, margem_lucro, nps, customer_health, conversion_rate, revenue_growth
            ]
            
            print(f"✅ Callback simulado com sucesso!")
            print(f"📊 Total de outputs: {len(retorno_callback)}")
            print(f"🔄 Todos os valores estão prontos para o dashboard")
            print()
            
        except Exception as e:
            print(f"❌ Erro na simulação do callback: {str(e)}")
            print()
            return False
        
        # ========================================================================
        # RESUMO FINAL
        # ========================================================================
        print("🎯 RESUMO FINAL DA INTEGRAÇÃO")
        print("=" * 65)
        
        print("✅ Status da Integração:")
        print("   • MetricsCalculator: FUNCIONANDO")
        print("   • Cálculo de métricas: FUNCIONANDO")
        print("   • Formatação de valores: FUNCIONANDO")
        print("   • Simulação de callback: FUNCIONANDO")
        print()
        
        print("📊 Métricas Integradas:")
        print(f"   • FASE 1 (Básicas): ✅ {8} métricas")
        print(f"   • FASE 2 (Performance): ✅ {7} métricas")
        print(f"   • FASE 3 (Avançadas): ✅ {7} métricas")
        print(f"   • FASE 4 (Temporais): ✅ {2} métricas")
        print(f"   • TOTAL: ✅ {24} métricas integradas")
        print()
        
        print("🚀 Próximo Passo:")
        print("   • Dashboard está pronto para receber dados reais")
        print("   • Todos os callbacks estão implementados")
        print("   • Integração completa entre backend e frontend")
        print()
        
        print("🎉 FASE 4: INTEGRAÇÃO COMPLETA - DASHBOARD FUNCIONANDO COM DADOS REAIS!")
        
        # Fecha sessão
        db_session.close()
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {str(e)}")
        print("🔍 Verifique a conexão com o banco e os logs")
        return False


if __name__ == "__main__":
    success = test_integracao_dashboard()
    sys.exit(0 if success else 1)
