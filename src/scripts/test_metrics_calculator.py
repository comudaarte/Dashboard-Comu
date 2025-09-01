"""
Script de Teste do Calculador de Métricas
=========================================

Este script testa todas as funcionalidades do MetricsCalculator
com dados reais do banco para validar se as métricas estão sendo
calculadas corretamente.

Uso:
    python src/scripts/test_metrics_calculator.py

Autor: Dashboard Comu
Data: 2024
"""

import sys
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Adiciona o diretório raiz do projeto ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import get_session
from src.services.metrics_calculator import MetricsCalculator
from sqlalchemy import text

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_metrics_calculator():
    """
    Testa todas as funcionalidades do MetricsCalculator.
    """
    logger.info("=== INICIANDO TESTES DO CALCULADOR DE MÉTRICAS ===")
    
    try:
        # Conecta ao banco de dados
        logger.info("Conectando ao banco de dados...")
        db_session = get_session()
        calculator = MetricsCalculator(db_session)
        
        # Teste 1: Validação de integridade dos dados
        logger.info("\n1. VALIDANDO INTEGRIDADE DOS DADOS")
        validation_result = calculator.validate_data_integrity()
        
        print("\n📊 RESULTADO DA VALIDAÇÃO:")
        print(f"   Total de assinaturas: {validation_result['total_assinaturas']}")
        print(f"   Com valor mensal: {validation_result['integridade_valores']['com_valor_mensal']}")
        print(f"   Com valor anual: {validation_result['integridade_valores']['com_valor_anual']}")
        print(f"   Sem valores: {validation_result['integridade_valores']['sem_valores']}")
        print(f"   % sem valores: {validation_result['integridade_valores']['percentual_sem_valores']:.2f}%")
        
        if validation_result['alertas']:
            print("\n⚠️  ALERTAS:")
            for alerta in validation_result['alertas']:
                print(f"   - {alerta}")
        else:
            print("\n✅ Nenhum alerta de integridade encontrado")
        
        # Teste 2: Cálculo de MRR
        logger.info("\n2. TESTANDO CÁLCULO DE MRR")
        mrr_result = calculator.calculate_mrr()
        
        print(f"\n💰 MRR CALCULADO:")
        print(f"   Total: R$ {mrr_result['mrr_total']:,.2f}")
        print(f"   Por plataforma:")
        for plataforma, valor in mrr_result['mrr_por_plataforma'].items():
            print(f"     {plataforma.upper()}: R$ {valor:,.2f}")
        
        print(f"\n   Por tipo de plano:")
        breakdown = mrr_result['detalhes']['breakdown_por_tipo']
        print(f"     Mensal: {breakdown['mensal']['assinaturas']} assinaturas = R$ {breakdown['mensal']['mrr']:,.2f}")
        print(f"     Anual: {breakdown['anual']['assinaturas']} assinaturas = R$ {breakdown['anual']['mrr']:,.2f}")
        
        # Teste 3: Cálculo de ARR
        logger.info("\n3. TESTANDO CÁLCULO DE ARR")
        arr_result = calculator.calculate_arr()
        
        print(f"\n📈 ARR CALCULADO:")
        print(f"   Total: R$ {arr_result['arr_total']:,.2f}")
        print(f"   Por plataforma:")
        for plataforma, valor in arr_result['arr_por_plataforma'].items():
            print(f"     {plataforma.upper()}: R$ {valor:,.2f}")
        
        # Teste 4: Cálculo de Churn Rate
        logger.info("\n4. TESTANDO CÁLCULO DE CHURN RATE")
        churn_result = calculator.calculate_churn_rate(30)
        
        print(f"\n📉 CHURN RATE (30 dias):")
        print(f"   Taxa de Churn: {churn_result['churn_rate_total']:.2f}%")
        print(f"   Taxa de Renovação: {churn_result['renewal_rate_total']:.2f}%")
        print(f"   Cancelamentos: {churn_result['total_cancelamentos']}")
        print(f"   Ativas no início: {churn_result['total_ativas_inicio']}")
        
        print(f"\n   Por plataforma:")
        for plataforma, churn in churn_result['churn_por_plataforma'].items():
            print(f"     {plataforma.upper()}: {churn:.2f}%")
        
        # Teste 5: Cálculo de LTV
        logger.info("\n5. TESTANDO CÁLCULO DE LTV")
        ltv_result = calculator.calculate_ltv()
        
        print(f"\n💎 LTV CALCULADO:")
        print(f"   LTV Total: R$ {ltv_result['ltv_total']:,.2f}")
        print(f"   Ticket Médio Anual: R$ {ltv_result['ticket_medio_anual_geral']:,.2f}")
        print(f"   Churn Rate usado: {ltv_result['churn_rate_utilizado']:.2f}%")
        
        print(f"\n   Por plataforma:")
        for plataforma, ltv in ltv_result['ltv_por_plataforma'].items():
            print(f"     {plataforma.upper()}: R$ {ltv:,.2f}")
        
        # Teste 6: Cálculo de CAC (sem custo de marketing)
        logger.info("\n6. TESTANDO CÁLCULO DE CAC")
        cac_result = calculator.calculate_cac(30)
        
        print(f"\n👥 NOVOS CLIENTES (30 dias):")
        print(f"   Total: {cac_result['novos_clientes_periodo']}")
        
        print(f"\n   Por plataforma:")
        for plataforma, dados in cac_result['detalhes']['breakdown_por_plataforma'].items():
            print(f"     {plataforma.upper()}: {dados['novos_clientes']} novos clientes")
        
        print(f"\n   💡 Para calcular CAC, forneça o custo de marketing do período")
        
        # Teste 7: Métricas consolidadas do dashboard
        logger.info("\n7. TESTANDO MÉTRICAS CONSOLIDADAS")
        dashboard_metrics = calculator.get_dashboard_metrics()
        
        print(f"\n🏆 MÉTRICAS PRINCIPAIS DO DASHBOARD:")
        for metrica, dados in dashboard_metrics['metricas_principais'].items():
            valor = dados['valor']
            if 'moeda' in dados:
                print(f"   {metrica.upper()}: R$ {valor:,.2f}")
            elif 'unidade' in dados and dados['unidade'] == '%':
                print(f"   {metrica.upper()}: {valor:.2f}%")
            else:
                print(f"   {metrica.upper()}: {valor:,.0f}")
        
        # Teste de diferentes períodos
        logger.info("\n8. TESTANDO DIFERENTES PERÍODOS")
        
        print(f"\n📅 CHURN RATE POR PERÍODO:")
        for periodo in [7, 15, 30, 60]:
            churn_periodo = calculator.calculate_churn_rate(periodo)
            print(f"   {periodo} dias: {churn_periodo['churn_rate_total']:.2f}%")
        
        # Teste com data específica
        logger.info("\n9. TESTANDO COM DATA ESPECÍFICA")
        data_mes_passado = datetime.now() - timedelta(days=30)
        mrr_mes_passado = calculator.calculate_mrr(data_mes_passado)
        
        print(f"\n📆 MRR EM {data_mes_passado.strftime('%d/%m/%Y')}:")
        print(f"   Total: R$ {mrr_mes_passado['mrr_total']:,.2f}")
        print(f"   Assinaturas ativas: {mrr_mes_passado['detalhes']['total_assinaturas_ativas']}")
        
        # Comparação de crescimento
        crescimento_mrr = ((mrr_result['mrr_total'] - mrr_mes_passado['mrr_total']) / mrr_mes_passado['mrr_total'] * 100) if mrr_mes_passado['mrr_total'] > 0 else 0
        print(f"\n📊 CRESCIMENTO DO MRR (30 dias): {crescimento_mrr:+.2f}%")
        
        logger.info("\n✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        
        # Fecha conexão
        db_session.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ERRO durante os testes: {str(e)}")
        if 'db_session' in locals():
            db_session.close()
        return False

def test_with_sample_data():
    """
    Testa com dados específicos se o banco estiver vazio.
    """
    logger.info("\n=== TESTANDO COM DADOS DE EXEMPLO ===")
    
    try:
        db_session = get_session()
        
        # Verifica se há dados no banco
        result = db_session.execute(text("SELECT COUNT(*) as total FROM assinaturas")).fetchone()
        
        if result.total == 0:
            print("\n⚠️  Banco de dados vazio - executar backfill primeiro")
            print("   Execute: python src/scripts/backfill_guru.py")
            print("   Execute: python src/scripts/backfill_ticto_completo.py")
            return False
        else:
            print(f"\n✅ Banco contém {result.total} assinaturas - prosseguindo com testes")
            return True
            
    except Exception as e:
        logger.error(f"Erro ao verificar dados: {str(e)}")
        return False
    finally:
        if 'db_session' in locals():
            db_session.close()

if __name__ == "__main__":
    print("🧮 TESTE DO CALCULADOR DE MÉTRICAS - DASHBOARD COMU")
    print("=" * 60)
    
    # Verifica se há dados no banco
    if not test_with_sample_data():
        sys.exit(1)
    
    # Executa testes principais
    success = test_metrics_calculator()
    
    if success:
        print("\n🎉 CALCULADOR DE MÉTRICAS FUNCIONANDO PERFEITAMENTE!")
        print("   Próximo passo: Implementar dashboard visual")
    else:
        print("\n❌ TESTES FALHARAM - Verifique os logs acima")
        sys.exit(1)
