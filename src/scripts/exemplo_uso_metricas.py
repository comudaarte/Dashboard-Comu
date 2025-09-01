"""
Exemplo de Uso do Calculador de Métricas
========================================

Este script demonstra como usar o MetricsCalculator em diferentes cenários
práticos do dia a dia do negócio.

Autor: Dashboard Comu
Data: 2024
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Adiciona o diretório raiz do projeto ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import get_session
from src.services.metrics_calculator import MetricsCalculator

def exemplo_relatorio_mensal():
    """
    Exemplo: Gerar relatório mensal de métricas.
    """
    print("📊 RELATÓRIO MENSAL DE MÉTRICAS")
    print("=" * 50)
    
    db_session = get_session()
    calculator = MetricsCalculator(db_session)
    
    try:
        # Obtém métricas consolidadas
        metrics = calculator.get_dashboard_metrics()
        
        print(f"\n📅 Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        print(f"📊 Período de análise: {metrics['periodo_analise_dias']} dias")
        
        print(f"\n💰 RECEITAS:")
        print(f"   MRR: R$ {metrics['metricas_principais']['mrr']['valor']:,.2f}")
        print(f"   ARR: R$ {metrics['metricas_principais']['arr']['valor']:,.2f}")
        
        print(f"\n📈 RETENÇÃO:")
        print(f"   Taxa de Churn: {metrics['metricas_principais']['churn_rate']['valor']:.2f}%")
        print(f"   Taxa de Renovação: {metrics['metricas_principais']['renewal_rate']['valor']:.2f}%")
        
        print(f"\n👥 CLIENTES:")
        print(f"   Assinaturas Ativas: {metrics['metricas_principais']['total_assinaturas_ativas']['valor']:,}")
        print(f"   LTV Médio: R$ {metrics['metricas_principais']['ltv']['valor']:,.2f}")
        
        print(f"\n🏢 POR PLATAFORMA:")
        for plataforma, dados in metrics['metricas_por_plataforma'].items():
            print(f"   {plataforma.upper()}:")
            print(f"     MRR: R$ {dados['mrr']:,.2f}")
            print(f"     Churn: {dados['churn_rate']:.2f}%")
            print(f"     LTV: R$ {dados['ltv']:,.2f}")
        
    finally:
        db_session.close()

def exemplo_analise_crescimento():
    """
    Exemplo: Analisar crescimento ao longo do tempo.
    """
    print("\n📈 ANÁLISE DE CRESCIMENTO")
    print("=" * 50)
    
    db_session = get_session()
    calculator = MetricsCalculator(db_session)
    
    try:
        # Compara MRR atual vs mês passado
        mrr_atual = calculator.calculate_mrr()
        mrr_mes_passado = calculator.calculate_mrr(datetime.now() - timedelta(days=30))
        
        crescimento = ((mrr_atual['mrr_total'] - mrr_mes_passado['mrr_total']) / mrr_mes_passado['mrr_total'] * 100) if mrr_mes_passado['mrr_total'] > 0 else 0
        
        print(f"\n💰 EVOLUÇÃO DO MRR:")
        print(f"   Atual: R$ {mrr_atual['mrr_total']:,.2f}")
        print(f"   Mês Passado: R$ {mrr_mes_passado['mrr_total']:,.2f}")
        print(f"   Crescimento: {crescimento:+.2f}%")
        
        # Análise de churn por diferentes períodos
        print(f"\n📉 EVOLUÇÃO DO CHURN:")
        for periodo in [7, 15, 30, 60]:
            churn = calculator.calculate_churn_rate(periodo)
            print(f"   {periodo} dias: {churn['churn_rate_total']:.2f}%")
        
    finally:
        db_session.close()

def exemplo_analise_cac_ltv():
    """
    Exemplo: Análise da relação CAC vs LTV.
    """
    print("\n💎 ANÁLISE CAC vs LTV")
    print("=" * 50)
    
    db_session = get_session()
    calculator = MetricsCalculator(db_session)
    
    try:
        # Calcula LTV
        ltv = calculator.calculate_ltv()
        
        # Simula CAC com diferentes custos de marketing
        custos_marketing = [5000, 10000, 15000, 20000]
        novos_clientes = calculator.calculate_cac(30)['novos_clientes_periodo']
        
        print(f"\n👥 Novos clientes (30 dias): {novos_clientes}")
        print(f"💎 LTV Médio: R$ {ltv['ltv_total']:,.2f}")
        
        print(f"\n📊 ANÁLISE CAC vs LTV:")
        print(f"{'Custo Marketing':<15} {'CAC':<12} {'Ratio LTV/CAC':<15} {'Status'}")
        print("-" * 60)
        
        for custo in custos_marketing:
            if novos_clientes > 0:
                cac = custo / novos_clientes
                ratio = ltv['ltv_total'] / cac if cac > 0 else 0
                
                if ratio >= 3:
                    status = "✅ EXCELENTE"
                elif ratio >= 2:
                    status = "✅ BOM"
                elif ratio >= 1:
                    status = "⚠️  VIÁVEL"
                else:
                    status = "❌ RUIM"
                
                print(f"R$ {custo:>10,}   R$ {cac:>8,.0f}   {ratio:>8.1f}x        {status}")
        
    finally:
        db_session.close()

def exemplo_alertas_negocio():
    """
    Exemplo: Sistema de alertas baseado nas métricas.
    """
    print("\n🚨 ALERTAS DE NEGÓCIO")
    print("=" * 50)
    
    db_session = get_session()
    calculator = MetricsCalculator(db_session)
    
    try:
        # Validação de integridade
        validation = calculator.validate_data_integrity()
        
        # Métricas principais
        metrics = calculator.get_dashboard_metrics()
        churn = metrics['metricas_principais']['churn_rate']['valor']
        
        alertas = []
        
        # Alerta 1: Integridade dos dados
        if validation['alertas']:
            alertas.append("🔴 CRÍTICO: Problemas na integridade dos dados")
            for alerta in validation['alertas']:
                alertas.append(f"   - {alerta}")
        
        # Alerta 2: Churn alto
        if churn > 10:
            alertas.append(f"🔴 CRÍTICO: Taxa de churn muito alta ({churn:.1f}%)")
        elif churn > 5:
            alertas.append(f"🟡 ATENÇÃO: Taxa de churn elevada ({churn:.1f}%)")
        
        # Alerta 3: Poucos dados para análise
        total_assinaturas = metrics['metricas_principais']['total_assinaturas_ativas']['valor']
        if total_assinaturas < 100:
            alertas.append(f"🟡 ATENÇÃO: Poucos dados para análise confiável ({total_assinaturas} assinaturas)")
        
        # Alerta 4: LTV vs CAC (simulado)
        ltv = metrics['metricas_principais']['ltv']['valor']
        if ltv < 1000:  # Exemplo de threshold
            alertas.append(f"🟡 ATENÇÃO: LTV baixo (R$ {ltv:.0f})")
        
        # Exibe alertas
        if alertas:
            print("\n⚠️  ALERTAS ENCONTRADOS:")
            for alerta in alertas:
                print(f"   {alerta}")
        else:
            print("\n✅ NENHUM ALERTA - Métricas estão saudáveis!")
        
    finally:
        db_session.close()

def exemplo_export_json():
    """
    Exemplo: Exportar métricas em formato JSON para integração.
    """
    print("\n💾 EXPORTAÇÃO EM JSON")
    print("=" * 50)
    
    import json
    
    db_session = get_session()
    calculator = MetricsCalculator(db_session)
    
    try:
        # Obtém todas as métricas
        metrics = calculator.get_dashboard_metrics()
        
        # Converte para JSON
        json_output = json.dumps(metrics, indent=2, ensure_ascii=False, default=str)
        
        # Salva em arquivo (opcional)
        output_file = f"metrics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        print(f"📄 Estrutura JSON gerada (primeiras 500 chars):")
        print(json_output[:500] + "...")
        
        print(f"\n💾 Para salvar em arquivo, descomente as linhas abaixo:")
        print(f"# with open('{output_file}', 'w', encoding='utf-8') as f:")
        print(f"#     f.write(json_output)")
        
    finally:
        db_session.close()

if __name__ == "__main__":
    print("🧮 EXEMPLOS DE USO DO CALCULADOR DE MÉTRICAS")
    print("=" * 60)
    
    try:
        # Executa todos os exemplos
        exemplo_relatorio_mensal()
        exemplo_analise_crescimento()
        exemplo_analise_cac_ltv()
        exemplo_alertas_negocio()
        exemplo_export_json()
        
        print("\n🎉 TODOS OS EXEMPLOS EXECUTADOS COM SUCESSO!")
        print("\n💡 PRÓXIMOS PASSOS:")
        print("   1. Integrar com dashboard visual (Dash/Plotly)")
        print("   2. Configurar alertas automáticos")
        print("   3. Criar relatórios automatizados")
        print("   4. Implementar APIs de métricas")
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        print("   Verifique se o banco de dados está configurado e contém dados")
