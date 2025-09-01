"""
Callbacks para Integração das Métricas com o Dashboard
====================================================

Integra todas as métricas calculadas pelo MetricsCalculator
com os componentes visuais do dashboard, substituindo
dados sintéticos por dados reais do banco.
"""

import dash
from dash import Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
import logging
from datetime import datetime, timedelta
import traceback

# Configuração de logging
logger = logging.getLogger(__name__)


def register_metrics_callbacks(app):
    """
    Registra todos os callbacks relacionados às métricas.
    
    Args:
        app: Aplicação Dash
    """
    
    # ========================================================================
    # CALLBACK PRINCIPAL: Atualiza todas as métricas do dashboard
    # ========================================================================
    @app.callback(
        [
            # Grid Final de Métricas
            Output('mrr-total', 'children'),
            Output('arr-total', 'children'),
            Output('mra-recorrencia', 'children'),
            Output('mrr-growth', 'children'),
            Output('mrr-mensal', 'children'),
            Output('arr-mensal', 'children'),
            Output('assinaturas-ativas', 'children'),
            Output('assinaturas-canceladas', 'children'),
            Output('mrr-anual', 'children'),
            Output('arr-anual', 'children'),
            Output('churn-rate', 'children'),
            Output('retention-rate', 'children'),
            Output('assinaturas-mes-atual', 'children'),
            Output('assinaturas-mes-passado', 'children'),
            
            # Seção Principal
            Output('faturamento-total', 'children'),
            Output('quantidade-vendas', 'children'),
            Output('quantidade-alunos', 'children'),
            Output('ltv-geral', 'children'),
            
            # Seção Performance
            Output('arpu', 'children'),
            Output('cac', 'children'),
            Output('roi', 'children'),
            Output('margem-lucro', 'children'),
            Output('nps', 'children'),
            Output('customer-health', 'children'),
            Output('conversion-rate', 'children'),
            Output('revenue-growth', 'children')
        ],
        [
            Input('date-picker', 'start_date'),
            Input('date-picker', 'end_date'),
            Input('refresh-button', 'n_clicks')
        ],
        prevent_initial_call=False
    )
    def update_all_metrics(start_date, end_date, refresh_clicks):
        """
        Callback principal que atualiza todas as métricas do dashboard.
        
        Args:
            start_date: Data de início do filtro
            end_date: Data de fim do filtro
            refresh_clicks: Contador de cliques no botão de refresh
            
        Returns:
            Lista com todos os valores das métricas atualizadas
        """
        try:
            logger.info("🔄 Atualizando todas as métricas do dashboard")
            
            # Determina período de análise
            if start_date and end_date:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                periodo_dias = (end_dt - start_dt).days
                data_referencia = end_dt
                logger.info(f"📅 Período selecionado: {start_dt.date()} até {end_dt.date()} ({periodo_dias} dias)")
            else:
                # Período padrão: últimos 30 dias
                data_referencia = datetime.now()
                periodo_dias = 30
                logger.info(f"📅 Período padrão: últimos {periodo_dias} dias")
            
            # Importa MetricsCalculator (importação local para evitar problemas de indentação)
            try:
                from services.metrics_calculator import MetricsCalculator
                from database.connection import get_session
                
                # Cria sessão e calculadora
                db_session = get_session()
                calculator = MetricsCalculator(db_session)
                
                logger.info("✅ Conectado ao banco e criado MetricsCalculator")
                
                # ========================================================================
                # CÁLCULO DE TODAS AS MÉTRICAS
                # ========================================================================
                
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
                
                logger.info("✅ Todas as métricas calculadas com sucesso")
                
                # Fecha sessão
                db_session.close()
                
                # ========================================================================
                # FORMATAÇÃO DOS VALORES PARA EXIBIÇÃO
                # ========================================================================
                
                # Grid Final de Métricas
                mrr_total = f"R$ {mrr_data['mrr_total']:,.2f}" if mrr_data['mrr_total'] else "R$ 0,00"
                arr_total = f"R$ {arr_data['arr_total']:,.2f}" if arr_data['arr_total'] else "R$ 0,00"
                mra_recorrencia = f"{mra_data['mra_total']:,.0f}" if mra_data['mra_total'] else "0"
                mrr_growth = f"{mrr_growth_data['crescimento_percentual']:+.1f}%" if mrr_growth_data['crescimento_percentual'] else "0,0%"
                
                mrr_mensal = f"R$ {mrr_mensal_data['mrr_mensal']:,.2f}" if mrr_mensal_data['mrr_mensal'] else "R$ 0,00"
                arr_mensal = f"R$ {arr_mensal_data['arr_mensal']:,.2f}" if arr_mensal_data['arr_mensal'] else "R$ 0,00"
                assinaturas_ativas = f"{assinaturas_ativas_data['total_assinaturas_ativas']:,.0f}" if assinaturas_ativas_data['total_assinaturas_ativas'] else "0"
                assinaturas_canceladas = f"{assinaturas_canceladas_data['total_assinaturas_canceladas']:,.0f}" if assinaturas_canceladas_data['total_assinaturas_canceladas'] else "0"
                
                mrr_anual = f"R$ {mrr_anual_data['mrr_anual']:,.2f}" if mrr_anual_data['mrr_anual'] else "R$ 0,00"
                arr_anual = f"R$ {arr_anual_data['arr_anual']:,.2f}" if arr_anual_data['arr_anual'] else "R$ 0,00"
                churn_rate = f"{churn_data['taxa_churn']:.1f}%" if churn_data['taxa_churn'] else "0,0%"
                retention_rate = f"{retention_data['taxa_retencao']:.1f}%" if retention_data['taxa_retencao'] else "0,0%"
                
                assinaturas_mes_atual = f"{assinaturas_mes_atual_data['total_assinaturas_mes_atual']:,.0f}" if assinaturas_mes_atual_data['total_assinaturas_mes_atual'] else "0"
                assinaturas_mes_passado = f"{assinaturas_mes_passado_data['total_assinaturas_mes_anterior']:,.0f}" if assinaturas_mes_passado_data['total_assinaturas_mes_anterior'] else "0"
                
                # Seção Principal
                faturamento_total = f"R$ {receita_anual_data['receita_anual_total']:,.2f}" if receita_anual_data['receita_anual_total'] else "R$ 0,00"
                quantidade_vendas = f"{total_vendas_data['total_vendas']:,.0f}" if total_vendas_data['total_vendas'] else "0"
                quantidade_alunos = f"{clientes_unicos_data['total_clientes_unicos']:,.0f}" if clientes_unicos_data['total_clientes_unicos'] else "0"
                ltv_geral = f"R$ {ltv_data['ltv_medio']:,.2f}" if ltv_data['ltv_medio'] else "R$ 0,00"
                
                # Seção Performance
                arpu = f"R$ {arpu_data['arpu']:,.2f}" if arpu_data['arpu'] else "R$ 0,00"
                cac = f"R$ {cac_data['cac']:,.2f}" if cac_data['cac'] else "R$ 0,00"
                roi = f"{roi_data['roi_percentual']:+.1f}%" if roi_data['roi_percentual'] else "0,0%"
                margem_lucro = f"{margem_lucro_data['margem_lucro']:.1f}%" if margem_lucro_data['margem_lucro'] else "0,0%"
                nps = f"{nps_data['nps_total']:+.0f}" if nps_data['nps_total'] else "0"
                customer_health = f"{health_score_data['health_score_medio']:.0f}/100" if health_score_data['health_score_medio'] else "0/100"
                conversion_rate = f"{conversion_data['taxa_conversao']:.1f}%" if conversion_data['taxa_conversao'] else "0,0%"
                revenue_growth = f"{revenue_growth_data['growth_rate']:+.1f}%" if revenue_growth_data['growth_rate'] else "0,0%"
                
                logger.info("✅ Valores formatados para exibição")
                
                # Retorna todos os valores atualizados
                return [
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
                
            except ImportError as e:
                logger.error(f"❌ Erro de importação: {str(e)}")
                # Retorna valores padrão em caso de erro
                return ["R$ 0,00"] * 30  # 30 métricas com valores padrão
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar métricas: {str(e)}")
            logger.error(f"🔍 Traceback: {traceback.format_exc()}")
            
            # Retorna valores padrão em caso de erro
            return ["R$ 0,00"] * 30  # 30 métricas com valores padrão
    
    # ========================================================================
    # CALLBACKS ESPECÍFICOS PARA COMPONENTES INDIVIDUAIS
    # ========================================================================
    
    @app.callback(
        Output('metrics-loading', 'children'),
        Input('refresh-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_loading_state(refresh_clicks):
        """Mostra estado de carregamento durante atualização"""
        if refresh_clicks:
            return "🔄 Atualizando métricas..."
        return ""
    
    @app.callback(
        Output('last-update', 'children'),
        Input('refresh-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def update_last_update_timestamp(refresh_clicks):
        """Atualiza timestamp da última atualização"""
        if refresh_clicks:
            return f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        return ""
    
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
