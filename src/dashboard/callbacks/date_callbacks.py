"""
Callbacks de Data
=================

Callbacks para seleção e manipulação de datas.
"""

from dash import callback, Input, Output, State, html
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import json


def register_date_callbacks(app):
    """
    Registra callbacks relacionados à seleção de datas.
    
    Args:
        app: Aplicação Dash
    """
    
    @app.callback(
        Output("date-picker-modal", "is_open"),
        [Input("date-picker-button", "n_clicks"),
         Input("close-date-modal", "n_clicks"),
         Input("apply-date-selection", "n_clicks"),
         Input("cancel-date-selection", "n_clicks")],
        [State("date-picker-modal", "is_open")]
    )
    def toggle_date_modal(open_clicks, close_clicks, apply_clicks, cancel_clicks, is_open):
        """
        Controla abertura/fechamento do modal de seleção de datas.
        """
        if open_clicks or close_clicks or apply_clicks or cancel_clicks:
            return not is_open
        return is_open
    
    @app.callback(
        Output("date-range-picker", "start_date"),
        [Input("quick-7-days", "n_clicks"),
         Input("quick-30-days", "n_clicks"),
         Input("quick-90-days", "n_clicks"),
         Input("quick-this-year", "n_clicks")],
        [State("date-range-picker", "start_date")]
    )
    def update_start_date(btn_7d, btn_30d, btn_90d, btn_year, current_start):
        """
        Atualiza data inicial baseado nos botões de período rápido.
        """
        from dash import callback_context
        ctx = callback_context
        
        if not ctx.triggered:
            return current_start
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        today = datetime.now()
        
        if button_id == "quick-7-days":
            return (today - timedelta(days=7)).strftime("%Y-%m-%d")
        elif button_id == "quick-30-days":
            return (today - timedelta(days=30)).strftime("%Y-%m-%d")
        elif button_id == "quick-90-days":
            return (today - timedelta(days=90)).strftime("%Y-%m-%d")
        elif button_id == "quick-this-year":
            return datetime(today.year, 1, 1).strftime("%Y-%m-%d")
        
        return current_start
    
    @app.callback(
        Output("date-range-picker", "end_date"),
        [Input("quick-7-days", "n_clicks"),
         Input("quick-30-days", "n_clicks"),
         Input("quick-90-days", "n_clicks"),
         Input("quick-this-year", "n_clicks")],
        [State("date-range-picker", "end_date")]
    )
    def update_end_date(btn_7d, btn_30d, btn_90d, btn_year, current_end):
        """
        Atualiza data final baseado nos botões de período rápido.
        """
        from dash import callback_context
        ctx = callback_context
        
        if not ctx.triggered:
            return current_end
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        today = datetime.now()
        
        if button_id in ["quick-7-days", "quick-30-days", "quick-90-days"]:
            return today.strftime("%Y-%m-%d")
        elif button_id == "quick-this-year":
            return today.strftime("%Y-%m-%d")
        
        return current_end
    
    @app.callback(
        Output("date-range-store", "data"),
        [Input("apply-date-selection", "n_clicks")],
        [State("date-range-picker", "start_date"),
         State("date-range-picker", "end_date")]
    )
    def store_date_range(apply_clicks, start_date, end_date):
        """
        Armazena o intervalo de datas selecionado.
        """
        if apply_clicks and start_date and end_date:
            return {
                "start_date": start_date,
                "end_date": end_date,
                "timestamp": datetime.now().isoformat()
            }
        return None
    
    @app.callback(
        Output("date-picker-button", "children"),
        [Input("date-range-store", "data")]
    )
    def update_date_button_text(date_range_data):
        """
        Atualiza o texto do botão de seleção de datas.
        """
        if not date_range_data:
            return [
                html.I(className="fas fa-calendar me-2", style={"fontSize": "1rem"}),
                html.Span("Selecionar intervalo de datas", style={"fontSize": "0.875rem"})
            ]
        
        start_date = date_range_data.get("start_date", "")
        end_date = date_range_data.get("end_date", "")
        
        if start_date and end_date:
            # Formata as datas
            start_formatted = datetime.strptime(start_date, "%Y-%m-%d").strftime("%d/%m/%Y")
            end_formatted = datetime.strptime(end_date, "%Y-%m-%d").strftime("%d/%m/%Y")
            
            return [
                html.I(className="fas fa-calendar me-2", style={"fontSize": "1rem"}),
                html.Span(f"{start_formatted} - {end_formatted}", style={"fontSize": "0.875rem"})
            ]
        
        return [
            html.I(className="fas fa-calendar me-2", style={"fontSize": "1rem"}),
            html.Span("Selecionar intervalo de datas", style={"fontSize": "0.875rem"})
        ]
    
    @app.callback(
        Output("dashboard-data-store", "data"),
        [Input("date-range-store", "data")],
        prevent_initial_call=False
    )
    def load_dashboard_data(date_range_data):
        """
        Carrega dados do dashboard baseado no intervalo de datas.
        """
        try:
            # Importa o serviço de dados
            from ..services.dashboard_data_service import DashboardDataService
            from ...database.connection import get_db_session
            
            # Determina as datas
            if not date_range_data:
                # Dados padrão (últimos 30 dias)
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
            else:
                start_date = datetime.strptime(date_range_data["start_date"], "%Y-%m-%d")
                end_date = datetime.strptime(date_range_data["end_date"], "%Y-%m-%d")
            
            # Cria sessão do banco e serviço
            db_session = get_db_session()
            dashboard_service = DashboardDataService(db_session)
            
            # Carrega dados reais
            dashboard_data = dashboard_service.get_dashboard_data(start_date, end_date)
            
            # Fecha sessão
            db_session.close()
            
            return dashboard_data
            
        except Exception as e:
            print(f"Erro ao carregar dados do dashboard: {e}")
            # Retorna dados de fallback em caso de erro
            return {
                "mrr_total": 0,
                "arr_total": 0,
                "churn_rate_total": 0,
                "ltv_total": 0,
                "arpu": 0,
                "cac": 0,
                "cpl": 0,
                "nps": 0,
                "roi": 0,
                "profit_margin": 0,
                "conversion_rate": 0,
                "retention_30d": 0,
                "avg_order_value": 0,
                "purchase_frequency": 0,
                "annual_revenue": 0,
                "revenue_growth": 0,
                "purchases_by_product": {},
                "revenue_by_product": {},
                "sales_by_date": {},
                "recurring_revenue": {},
                "churn_rate": {},
                "total_purchases": 0,
                "total_revenue": 0,
                "current_mrr": 0,
                "current_churn": 0,
                "date_range": "Erro ao carregar dados",
                "last_updated": datetime.now().isoformat(),
                "data_source": "error_fallback"
            }
