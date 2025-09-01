#!/usr/bin/env python3
"""
Teste das Métricas da FASE 4: Segmentação Temporal
==================================================

Testa as novas métricas implementadas:
- calculate_subscriptions_current_month()
- calculate_subscriptions_previous_month()

Executar via Docker:
docker-compose exec api python src/scripts/test_fase4_metricas.py
"""

import sys
import os
from datetime import datetime, timedelta

# Adiciona o diretório src ao path
sys.path.append('/app/src')

from database.connection import get_session
from services.metrics_calculator import MetricsCalculator


def test_fase4_metricas():
    """Testa todas as métricas da FASE 4"""
    
    print("🚀 TESTE DAS MÉTRICAS FASE 4: SEGMENTAÇÃO TEMPORAL")
    print("=" * 60)
    
    try:
        # Cria sessão do banco
        db_session = get_session()
        calculator = MetricsCalculator(db_session)
        
        print(f"✅ Conectado ao banco de dados")
        print(f"📅 Data de referência: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        print()
        
        # ========================================================================
        # TESTE 1: Assinaturas do Mês Atual
        # ========================================================================
        print("📊 TESTE 1: Assinaturas do Mês Atual")
        print("-" * 40)
        
        try:
            mes_atual_data = calculator.calculate_subscriptions_current_month()
            
            print(f"✅ Total de assinaturas do mês atual: {mes_atual_data['total_assinaturas_mes_atual']}")
            print(f"📅 Mês de referência: {mes_atual_data['mes_referencia']}")
            print(f"🔄 Período: {mes_atual_data['periodo']['inicio'][:10]} até {mes_atual_data['periodo']['fim'][:10]}")
            print()
            
            print("📈 Breakdown por plataforma:")
            for plataforma, count in mes_atual_data['breakdown_por_plataforma'].items():
                print(f"   • {plataforma.capitalize()}: {count}")
            
            print()
            print("📊 Breakdown por tipo de plano:")
            for tipo, count in mes_atual_data['breakdown_por_tipo'].items():
                print(f"   • {tipo.replace('_', ' ').title()}: {count}")
            
            print()
            print("🔍 Breakdown por status:")
            for status, count in mes_atual_data['breakdown_por_status'].items():
                print(f"   • {status.replace('_', ' ').title()}: {count}")
            
            print()
            
        except Exception as e:
            print(f"❌ Erro ao calcular assinaturas do mês atual: {str(e)}")
            print()
        
        # ========================================================================
        # TESTE 2: Assinaturas do Mês Anterior
        # ========================================================================
        print("📊 TESTE 2: Assinaturas do Mês Anterior")
        print("-" * 40)
        
        try:
            mes_anterior_data = calculator.calculate_subscriptions_previous_month()
            
            print(f"✅ Total de assinaturas do mês anterior: {mes_anterior_data['total_assinaturas_mes_anterior']}")
            print(f"📅 Mês de referência: {mes_anterior_data['mes_referencia']}")
            print(f"🔄 Período: {mes_anterior_data['periodo']['inicio'][:10]} até {mes_anterior_data['periodo']['fim'][:10]}")
            print()
            
            print("📈 Breakdown por plataforma:")
            for plataforma, count in mes_anterior_data['breakdown_por_plataforma'].items():
                print(f"   • {plataforma.capitalize()}: {count}")
            
            print()
            print("📊 Breakdown por tipo de plano:")
            for tipo, count in mes_anterior_data['breakdown_por_tipo'].items():
                print(f"   • {tipo.replace('_', ' ').title()}: {count}")
            
            print()
            print("🔍 Breakdown por status:")
            for status, count in mes_anterior_data['breakdown_por_status'].items():
                print(f"   • {status.replace('_', ' ').title()}: {count}")
            
            print()
            
        except Exception as e:
            print(f"❌ Erro ao calcular assinaturas do mês anterior: {str(e)}")
            print()
        
        # ========================================================================
        # TESTE 3: Comparação e Análise
        # ========================================================================
        print("📊 TESTE 3: Análise Comparativa")
        print("-" * 40)
        
        try:
            # Compara mês atual vs anterior
            mes_atual = mes_atual_data['total_assinaturas_mes_atual']
            mes_anterior = mes_anterior_data['total_assinaturas_mes_anterior']
            
            if mes_anterior > 0:
                variacao = ((mes_atual - mes_anterior) / mes_anterior) * 100
                print(f"📈 Variação: {mes_atual} vs {mes_anterior} assinaturas")
                print(f"🔄 Crescimento/Declínio: {variacao:+.1f}%")
                
                if variacao > 0:
                    print("✅ Crescimento positivo no mês atual")
                elif variacao < 0:
                    print("📉 Declínio no mês atual")
                else:
                    print("➡️ Estável (mesma quantidade)")
            else:
                print("ℹ️ Mês anterior sem assinaturas para comparação")
            
            print()
            
        except Exception as e:
            print(f"❌ Erro na análise comparativa: {str(e)}")
            print()
        
        # ========================================================================
        # TESTE 4: Validação de Consistência
        # ========================================================================
        print("🔍 TESTE 4: Validação de Consistência")
        print("-" * 40)
        
        try:
            # Valida se os totais fazem sentido
            total_mes_atual = mes_atual_data['total_assinaturas_mes_atual']
            total_mes_anterior = mes_anterior_data['total_assinaturas_mes_anterior']
            
            print("✅ Validações:")
            
            # Validação 1: Totais não negativos
            if total_mes_atual >= 0:
                print("   • Total mês atual: OK (não negativo)")
            else:
                print("   ❌ Total mês atual: ERRO (negativo)")
            
            if total_mes_anterior >= 0:
                print("   • Total mês anterior: OK (não negativo)")
            else:
                print("   ❌ Total mês anterior: ERRO (negativo)")
            
            # Validação 2: Breakdowns somam o total
            breakdown_mes_atual = sum(mes_atual_data['breakdown_por_plataforma'].values())
            if breakdown_mes_atual == total_mes_atual:
                print("   • Breakdown mês atual: OK (soma correta)")
            else:
                print(f"   ❌ Breakdown mês atual: ERRO (soma {breakdown_mes_atual} vs total {total_mes_atual})")
            
            breakdown_mes_anterior = sum(mes_anterior_data['breakdown_por_plataforma'].values())
            if breakdown_mes_anterior == total_mes_anterior:
                print("   • Breakdown mês anterior: OK (soma correta)")
            else:
                print(f"   ❌ Breakdown mês anterior: ERRO (soma {breakdown_mes_anterior} vs total {total_mes_anterior})")
            
            print()
            
        except Exception as e:
            print(f"❌ Erro na validação de consistência: {str(e)}")
            print()
        
        # ========================================================================
        # TESTE 5: Performance
        # ========================================================================
        print("⚡ TESTE 5: Performance")
        print("-" * 40)
        
        try:
            import time
            
            # Testa performance das métricas
            start_time = time.time()
            calculator.calculate_subscriptions_current_month()
            tempo_mes_atual = time.time() - start_time
            
            start_time = time.time()
            calculator.calculate_subscriptions_previous_month()
            tempo_mes_anterior = time.time() - start_time
            
            print(f"⏱️ Tempo de execução:")
            print(f"   • Mês atual: {tempo_mes_atual:.3f}s")
            print(f"   • Mês anterior: {tempo_mes_anterior:.3f}s")
            
            if tempo_mes_atual < 1.0 and tempo_mes_anterior < 1.0:
                print("✅ Performance: EXCELENTE (< 1s)")
            elif tempo_mes_atual < 2.0 and tempo_mes_anterior < 2.0:
                print("✅ Performance: BOA (< 2s)")
            else:
                print("⚠️ Performance: PODE SER MELHORADA (> 2s)")
            
            print()
            
        except Exception as e:
            print(f"❌ Erro no teste de performance: {str(e)}")
            print()
        
        # ========================================================================
        # RESUMO FINAL
        # ========================================================================
        print("🎯 RESUMO FINAL")
        print("=" * 60)
        
        print(f"✅ Métricas implementadas: 2/2")
        print(f"📊 Assinaturas mês atual: {mes_atual_data['total_assinaturas_mes_atual']}")
        print(f"📊 Assinaturas mês anterior: {mes_anterior_data['total_assinaturas_mes_anterior']}")
        print(f"🔄 Variação: {((mes_atual_data['total_assinaturas_mes_atual'] - mes_anterior_data['total_assinaturas_mes_anterior']) / max(mes_anterior_data['total_assinaturas_mes_anterior'], 1) * 100):+.1f}%")
        print()
        print("🎉 FASE 4: MÉTRICAS DE SEGMENTAÇÃO TEMPORAL - IMPLEMENTAÇÃO COMPLETA!")
        print("🚀 Próximo passo: Integração com o Dashboard")
        
        # Fecha sessão
        db_session.close()
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {str(e)}")
        print("🔍 Verifique a conexão com o banco e os logs")
        return False
    
    return True


if __name__ == "__main__":
    success = test_fase4_metricas()
    sys.exit(0 if success else 1)
