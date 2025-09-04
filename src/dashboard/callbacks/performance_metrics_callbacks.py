"""
Callbacks de Métricas de Performance
====================================

Callbacks para atualização das métricas de performance do dashboard com dados reais.
Aplica a mesma lógica de correção das outras métricas: conta apenas assinaturas com transações aprovadas.
"""

from dash import callback, Input, Output, State
from datetime import datetime, timedelta
import logging

# Configuração de logging
logger = logging.getLogger(__name__)


def register_performance_metrics_callbacks(app):
    """
    Registra callbacks relacionados às métricas de performance.
    
    Args:
        app: Aplicação Dash
    """
    
    @app.callback(
        [Output("arpu-value", "children"),
         Output("cac-geral-value", "children"),
         Output("cpl-geral-value", "children"),
         Output("nps-geral-value", "children"),
         Output("receita-media-mensal-value", "children"),
         Output("receita-anual-value", "children"),
         Output("roi-geral-value", "children"),
         Output("margem-lucro-value", "children"),
         Output("receita-anual-badge", "children"),
         Output("roi-geral-badge", "children"),
         Output("margem-lucro-badge", "children")],
        [Input("date-range-store", "data"),
         Input("refresh-button", "n_clicks")]
    )
    def update_performance_metrics(date_range_data, refresh_clicks):
        """
        Atualiza métricas de performance com dados reais baseados no período selecionado.
        Aplica a mesma lógica de correção: conta apenas assinaturas com transações aprovadas.
        """
        try:
            logger.info("🔄 Atualizando métricas de performance")
            
            # Inicializa variáveis
            start_dt = None
            end_dt = None
            data_referencia = datetime.now()
            
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
                logger.info(f"   Período selecionado: {start_dt.date()} a {end_dt.date()}")
            else:
                # Período padrão se não houver datas selecionadas
                data_referencia = datetime.now()
                logger.info(f"   Usando período padrão")
            
            # Importa MetricsCalculator
            try:
                from services.metrics_calculator import MetricsCalculator
                from database.connection import get_session
                
                # Cria sessão e calculadora
                db_session = get_session()
                calculator = MetricsCalculator(db_session)
                
                # Calcula métricas de performance baseadas no período
                if start_dt and end_dt:
                    # Usa dados do período selecionado
                    dashboard_metrics = calculator.calculate_dashboard_metrics_for_period(start_dt, end_dt)
                    
                    # Calcula métricas específicas de performance
                    from sqlalchemy import text
                    
                    # 1. ARPU (Average Revenue Per User) - Receita média por usuário
                    query_arpu = text("""
                        SELECT 
                            COALESCE(AVG(t.valor_bruto), 0) as arpu
                        FROM assinaturas a
                        INNER JOIN transacoes t ON a.id = t.assinatura_id
                        WHERE a.data_inicio BETWEEN :start_date AND :end_date
                        AND a.status NOT IN ('refunded', 'chargeback')
                        AND t.status IN ('approved', 'paid', 'authorized')
                        AND t.valor_bruto > 0
                    """)
                    
                    result_arpu = calculator.db.execute(query_arpu, {
                        "start_date": start_dt,
                        "end_date": end_dt
                    }).fetchone()
                    
                    arpu = float(result_arpu.arpu) if result_arpu.arpu else 0
                    
                    # 2. CAC Geral (Customer Acquisition Cost) - Custo de aquisição por cliente
                    # ZERADO: Aguardando integração com dados de marketing do Facebook
                    cac_geral = 0.0
                    
                    # 3. CPL Geral (Cost Per Lead) - Custo por lead
                    # ZERADO: Aguardando integração com dados de marketing do Facebook
                    cpl_geral = 0.0
                    
                    # 4. NPS Geral (Net Promoter Score) - Score de satisfação
                    # ZERADO: Aguardando integração com dados de marketing do Facebook
                    nps_geral = 0
                    
                    # 5. Receita média mensal
                    periodo_dias = (end_dt.date() - start_dt.date()).days + 1
                    receita_total = dashboard_metrics.get('faturamento_total', 0)
                    receita_media_mensal = (receita_total / periodo_dias) * 30 if periodo_dias > 0 else 0
                    
                    # 6. Receita Anual da Empresa (projetada)
                    receita_anual = receita_media_mensal * 12
                    
                    # 7. ROI Geral (Return on Investment)
                    # ZERADO: Aguardando integração com dados de marketing do Facebook
                    roi_geral = 0.0
                    
                    # 8. Margem de Lucro
                    # ZERADO: Aguardando integração com dados de marketing do Facebook
                    margem_lucro = 0.0
                    
                else:
                    # Fallback para valores padrão
                    arpu = 0
                    cac_geral = 0
                    cpl_geral = 0
                    nps_geral = 0
                    receita_media_mensal = 0
                    receita_anual = 0
                    roi_geral = 0
                    margem_lucro = 0
                
                # Fecha sessão
                db_session.close()
                
                logger.info(f"✅ Métricas de performance calculadas:")
                logger.info(f"   ARPU: {arpu:.2f}")
                logger.info(f"   CAC Geral: {cac_geral:.2f} (ZERADO - aguardando dados de marketing)")
                logger.info(f"   CPL Geral: {cpl_geral:.2f} (ZERADO - aguardando dados de marketing)")
                logger.info(f"   NPS Geral: {nps_geral} (ZERADO - aguardando dados de marketing)")
                logger.info(f"   Receita média mensal: {receita_media_mensal:.2f}")
                logger.info(f"   Receita anual: {receita_anual:.2f}")
                logger.info(f"   ROI Geral: {roi_geral:.2f}% (ZERADO - aguardando dados de marketing)")
                logger.info(f"   Margem de Lucro: {margem_lucro:.2f}% (ZERADO - aguardando dados de marketing)")
                
            except Exception as e:
                logger.error(f"❌ Erro ao carregar dados reais: {str(e)}")
                # Fallback para valores padrão
                arpu = 0
                cac_geral = 0
                cpl_geral = 0
                nps_geral = 0
                receita_media_mensal = 0
                receita_anual = 0
                roi_geral = 0
                margem_lucro = 0
            
            # Formata os valores para exibição
            arpu_formatted = f"{arpu:,.0f}" if arpu > 0 else "0"
            cac_geral_formatted = f"{cac_geral:,.0f}" if cac_geral > 0 else "0"
            cpl_geral_formatted = f"{cpl_geral:,.0f}" if cpl_geral > 0 else "0"
            nps_geral_formatted = f"{nps_geral}" if nps_geral > 0 else "0"
            receita_media_mensal_formatted = f"R$ {receita_media_mensal:,.0f}" if receita_media_mensal > 0 else "R$ 0"
            receita_anual_formatted = f"R$ {receita_anual:,.0f}" if receita_anual > 0 else "R$ 0"
            roi_geral_formatted = f"{roi_geral:,.0f}%" if roi_geral > 0 else "0%"
            margem_lucro_formatted = f"{margem_lucro:,.0f}%" if margem_lucro > 0 else "0%"
            
            # Calcula badges de crescimento baseados em dados reais
            from dash import html
            
            # Badge Receita Anual - calcula crescimento real comparando com período anterior
            periodo_dias = (end_dt.date() - start_dt.date()).days + 1
            
            # Calcula receita do período anterior (mesmo número de dias)
            start_anterior = start_dt - timedelta(days=periodo_dias)
            end_anterior = start_dt - timedelta(days=1)
            
            # Busca receita do período anterior
            query_receita_anterior = text("""
                SELECT COALESCE(SUM(valor_liquido), 0) as receita_anterior
                FROM transacoes
                WHERE data_transacao BETWEEN :start_date AND :end_date
                AND status IN ('approved', 'paid', 'authorized')
                AND valor_liquido > 0
            """)
            
            result_anterior = calculator.db.execute(query_receita_anterior, {
                "start_date": start_anterior,
                "end_date": end_anterior
            }).fetchone()
            
            receita_anterior = float(result_anterior.receita_anterior) if result_anterior.receita_anterior else 0
            receita_atual = receita_total
            
            # Calcula percentual de crescimento
            if receita_anterior > 0:
                crescimento_percentual = ((receita_atual - receita_anterior) / receita_anterior) * 100
            else:
                crescimento_percentual = 100 if receita_atual > 0 else 0
            
            # Define ícone e cor baseado no crescimento
            if crescimento_percentual > 0:
                icon_class = "fas fa-arrow-up"
                color = "#10B981"  # Verde para crescimento
            elif crescimento_percentual < 0:
                icon_class = "fas fa-arrow-down"
                color = "#EF4444"  # Vermelho para queda
            else:
                icon_class = "fas fa-minus"
                color = "#8B5CF6"  # Roxo para neutro
            
            receita_anual_badge = html.Span([
                html.I(className=f"{icon_class} me-1", style={"fontSize": "0.75rem", "color": "white"}), 
                f"{abs(crescimento_percentual):.1f}%"
            ], style={"backgroundColor": color})
            
            # Badge ROI Geral (zerado pois ROI está zerado)
            roi_geral_badge = html.Span([
                html.I(className="fas fa-minus me-1", style={"fontSize": "0.75rem", "color": "white"}), 
                "0%"
            ])
            
            # Badge Margem de Lucro (zerado pois margem está zerada)
            margem_lucro_badge = html.Span([
                html.I(className="fas fa-minus me-1", style={"fontSize": "0.75rem", "color": "white"}), 
                "0%"
            ])
            
            return (
                arpu_formatted,
                cac_geral_formatted,
                cpl_geral_formatted,
                nps_geral_formatted,
                receita_media_mensal_formatted,
                receita_anual_formatted,
                roi_geral_formatted,
                margem_lucro_formatted,
                receita_anual_badge,
                roi_geral_badge,
                margem_lucro_badge
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar métricas de performance: {str(e)}")
            # Retorna valores padrão em caso de erro
            from dash import html
            
            default_badge = html.Span([
                html.I(className="fas fa-minus me-1", style={"fontSize": "0.75rem", "color": "white"}), 
                "0%"
            ])
            
            return ("0", "0", "0", "0", "R$ 0", "R$ 0", "0%", "0%", default_badge, default_badge, default_badge)
    
    logger.info("✅ Callbacks de métricas de performance registrados com sucesso")
