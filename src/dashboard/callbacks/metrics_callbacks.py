"""
Callbacks de Métricas
====================

Callbacks para atualização de métricas do dashboard com dados reais.
"""

import dash
from dash import Input, Output, State
import logging
from datetime import datetime, timedelta

# Configuração de logging
logger = logging.getLogger(__name__)

def register_metrics_callbacks(app):
    """
    Registra callbacks relacionados às métricas principais.
    
    Args:
        app: Aplicação Dash
    """
    
    @app.callback(
        [Output("faturamento-total", "children"),
         Output("quantidade-vendas", "children"),
         Output("quantidade-alunos", "children"),
         Output("ltv-geral", "children"),
         Output("badge-crescimento-mes", "children"),
         Output("badge-crescimento-ano", "children"),
         Output("receita-bruta", "children")],
        [Input("date-range-store", "data"),  # CORRIGIDO: usar dados reais das datas
         Input("refresh-button", "n_clicks")]
    )
    def update_all_metrics(date_range_data, refresh_clicks):
        """
        Atualiza TODAS as métricas principais com dados reais do banco.
        """
        try:
            logger.info("🔄 Iniciando atualização completa de métricas...")
            logger.info(f"   Date range data: {date_range_data}")
            logger.info(f"   Refresh cliques: {refresh_clicks}")
            
            # Inicializa variáveis
            start_dt = None
            end_dt = None
            data_referencia = datetime.now()
            periodo_dias = 30
            
            # Determina período de análise baseado nas datas selecionadas
            if date_range_data and date_range_data.get('start_date') and date_range_data.get('end_date'):
                start_date = date_range_data['start_date']
                end_date = date_range_data['end_date']
                
                # Converte strings para datetime
                if isinstance(start_date, str):
                    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                else:
                    start_dt = start_date
                    
                if isinstance(end_date, str):
                    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                else:
                    end_dt = end_date
                
                # CORREÇÃO: Define end_dt como final do dia (23:59:59) para incluir todas as transações do dia
                end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
                
                data_referencia = end_dt
                periodo_dias = (end_dt.date() - start_dt.date()).days + 1  # +1 para incluir o dia final
                logger.info(f"   Período selecionado: {start_dt.date()} a {end_dt.date()} ({periodo_dias} dias)")
                logger.info(f"   Start datetime: {start_dt}")
                logger.info(f"   End datetime: {end_dt}")
            else:
                # Período padrão se não houver datas selecionadas
                data_referencia = datetime.now()
                periodo_dias = 30
                logger.info(f"   Usando período padrão: {periodo_dias} dias")
                logger.info(f"   Data referência: {data_referencia}")
            
            # Importa MetricsCalculator
            try:
                logger.info("   Importando MetricsCalculator...")
                from services.metrics_calculator import MetricsCalculator
                from database.connection import get_session
                
                # Cria sessão e calculadora
                logger.info("   Criando sessão do banco...")
                db_session = get_session()
                calculator = MetricsCalculator(db_session)
                
                logger.info("   Calculando métricas principais...")
                
                # NOVA IMPLEMENTAÇÃO: Usa função específica do dashboard
                if start_dt and end_dt:
                    # Calcula todas as métricas usando a nova função
                    dashboard_metrics = calculator.calculate_dashboard_metrics_for_period(
                        start_date=start_dt,
                        end_date=end_dt
                    )
                    
                    # Extrai valores das métricas
                    faturamento_total = dashboard_metrics.get('faturamento_total', 0)
                    total_vendas = dashboard_metrics.get('total_vendas', 0)
                    total_alunos = dashboard_metrics.get('total_alunos', 0)
                    ltv_geral = dashboard_metrics.get('ltv_geral', 0)
                    
                    logger.info(f"   ✅ Faturamento Total: R$ {faturamento_total:.2f}")
                    logger.info(f"   ✅ Total de Vendas: {total_vendas}")
                    logger.info(f"   ✅ Total de Alunos: {total_alunos}")
                    logger.info(f"   ✅ LTV Geral: R$ {ltv_geral:.2f}")
                    
                else:
                    # Comportamento padrão se não houver datas selecionadas
                    faturamento_total = 0
                    total_vendas = 0
                    total_alunos = 0
                    ltv_geral = 0
                    logger.info("   ⚠️ Sem datas selecionadas, usando valores padrão")
                
                # 5. Crescimento mensal (mantém lógica atual)
                crescimento_mes = 0.0
                if periodo_dias >= 30:
                    try:
                        mrr_mes_atual = calculator.calculate_mrr(data_referencia)
                        mrr_mes_anterior = calculator.calculate_mrr(data_referencia - timedelta(days=30))
                        
                        if mrr_mes_anterior.get('mrr_total', 0) > 0:
                            crescimento_mes = ((mrr_mes_atual.get('mrr_total', 0) - mrr_mes_anterior.get('mrr_total', 0)) / mrr_mes_anterior.get('mrr_total', 0)) * 100
                        logger.info(f"   ✅ Crescimento mensal: {crescimento_mes:.2f}%")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Erro ao calcular crescimento mensal: {str(e)}")
                
                # 6. Crescimento anual (mantém lógica atual)
                crescimento_ano = 0.0
                if periodo_dias >= 365:
                    try:
                        mrr_ano_atual = calculator.calculate_mrr(data_referencia)
                        mrr_ano_anterior = calculator.calculate_mrr(data_referencia - timedelta(days=365))
                        
                        if mrr_ano_anterior.get('mrr_total', 0) > 0:
                            crescimento_ano = ((mrr_ano_atual.get('mrr_total', 0) - mrr_ano_anterior.get('mrr_total', 0)) / mrr_ano_anterior.get('mrr_total', 0)) * 100
                        logger.info(f"   ✅ Crescimento anual: {crescimento_ano:.2f}%")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Erro ao calcular crescimento anual: {str(e)}")
                
                # 7. ARR para receita bruta (mantém lógica atual)
                arr_data = calculator.calculate_arr(data_referencia)
                arr_total = arr_data.get('arr_total', 0)
                logger.info(f"   ✅ ARR calculado: R$ {arr_total:.2f}")
                
                # Fecha sessão
                db_session.close()
                logger.info("   ✅ Sessão do banco fechada")
                
                # Formata valores para exibição
                faturamento_total_formatted = f"R$ {faturamento_total:,.2f}"
                quantidade_vendas = f"{total_vendas:,}"
                quantidade_alunos = f"{total_alunos:,}"
                ltv_geral_formatted = f"R$ {ltv_geral:,.2f}"
                
                # CORRIGIDO: Badges com setas corretas baseadas no crescimento
                if crescimento_mes >= 0:
                    badge_crescimento_mes = f"↑{crescimento_mes:.1f}%"
                else:
                    badge_crescimento_mes = f"↓{abs(crescimento_mes):.1f}%"
                
                if crescimento_ano >= 0:
                    badge_crescimento_ano = f"↑{crescimento_ano:.1f}%"
                else:
                    badge_crescimento_ano = f"↓{abs(crescimento_ano):.1f}%"
                
                receita_bruta = f"Receita bruta de R$ {dashboard_metrics.get('receita_bruta', 0):,.2f}"
                
                logger.info("🎉 TODAS as métricas calculadas com sucesso!")
                logger.info(f"   💰 Faturamento: {faturamento_total_formatted}")
                logger.info(f"   📊 Vendas: {quantidade_vendas}")
                logger.info(f"   👥 Alunos: {quantidade_alunos}")
                logger.info(f"   💎 LTV: {ltv_geral_formatted}")
                logger.info(f"   📈 Crescimento Mês: {badge_crescimento_mes}")
                logger.info(f"   📈 Crescimento Ano: {badge_crescimento_ano}")
                logger.info(f"   💵 Receita Bruta: {receita_bruta}")
                
                return (faturamento_total_formatted, quantidade_vendas, quantidade_alunos, 
                       ltv_geral_formatted, badge_crescimento_mes, badge_crescimento_ano, receita_bruta)
                
            except Exception as e:
                logger.error(f"❌ Erro ao calcular métricas: {str(e)}")
                import traceback
                logger.error(f"   Traceback: {traceback.format_exc()}")
                
                # Retorna valores padrão em caso de erro
                return ("R$ 0,00", "0", "0", "R$ 0,00", "↑0,0%", "↑0,0%", "Receita bruta de R$ 0,00")
                
        except Exception as e:
            logger.error(f"❌ Erro geral no callback: {str(e)}")
            import traceback
            logger.error(f"   Traceback: {traceback.format_exc()}")
            
            # Retorna valores padrão em caso de erro
            return ("R$ 0,00", "0", "0", "R$ 0,00", "↑0,0%", "↑0,0%", "Receita bruta de R$ 0,00")
    
    logger.info("✅ Callbacks de métricas registrados com sucesso")


def create_metrics_summary(metrics_data):
    """
    Cria um resumo das métricas para exibição.
    
    Args:
        metrics_data: Dados das métricas calculadas
        
    Returns:
        Dict com resumo formatado
    """
    try:
        return {
            "timestamp": datetime.now().isoformat(),
            "total_metricas": len(metrics_data),
            "status": "success",
            "metricas_principais": {
                "mrr": metrics_data.get('mrr_total', 0),
                "arr": metrics_data.get('arr_total', 0),
                "churn_rate": metrics_data.get('taxa_churn', 0),
                "assinaturas_ativas": metrics_data.get('total_assinaturas_ativas', 0)
            }
        }
    except Exception as e:
        logger.error(f"Erro ao criar resumo das métricas: {str(e)}")
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e)
        }
