"""
Grid Final de Métricas
======================

Grid final com 14 métricas organizadas conforme layout da screenshot.
Layout: 4+4+4+2 métricas com card destacado para "Assinaturas Ativas".
"""

import dash_bootstrap_components as dbc
from dash import html


def create_final_metrics_grid():
    """
    Cria o grid final com 14 métricas seguindo layout da screenshot.
    
    Returns:
        dbc.Container: Container com grid de métricas finais
    """
    return dbc.Container([
        # Primeira linha: 4 métricas
        dbc.Row([
            # MRR - (TOTAL)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("MRR - (TOTAL)", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4("R$ 556 330,48", id="mrr-total", className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3"),
            
            # ARR - (TOTAL)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("ARR - (TOTAL)", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4("R$ 556 330,48", id="arr-total", className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3"),
            
            # Recorrência - MRA (Monthly Recurrence Average)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Recorrência - MRA (Monthly Recurrence Average)", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4("50 499", id="mra", className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3"),
            
            # MRR - Growth (%)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("MRR - Growth (%)", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4("50 499", id="mrr-growth", className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3")
        ], className="mb-3"),
        
        # Segunda linha: 4 métricas
        dbc.Row([
            # MRR - (Plano Mensal)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("MRR - (Plano Mensal)", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4("R$ 556 330,48", id="mrr-mensal", className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3"),
            
            # ARR - (Plano Mensal)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("ARR - (Plano Mensal)", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4("R$ 556 330,48", id="arr-mensal", className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3"),
            
            # Assinaturas Ativas (DESTAQUE - ROXO)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Assinaturas Ativas", className="text-white mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4("73", id="assinaturas-ativas", className="fw-bold text-white mb-0", style={"fontSize": "2rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#8B5CF6"})
            ], width=12, md=6, lg=3, className="mb-3"),
            
            # Assinaturas Canceladas
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Assinaturas Canceladas", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4("73", id="assinaturas-canceladas", className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3")
        ], className="mb-3"),
        
        # Terceira linha: 4 métricas
        dbc.Row([
            # MRR - (Plano Anual)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("MRR - (Plano Anual)", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4("R$ 556 330,48", id="mrr-anual", className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3"),
            
            # ARR - (Plano Anual)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("ARR - (Plano Anual)", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4("R$ 556 330,48", id="arr-anual", className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3"),
            
            # Churn Rate (%)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Churn Rate (%)", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4("556 330,48", id="churn-rate", className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3"),
            
            # Retention Rate (%)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Retention Rate (%)", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4("73", id="retention-rate", className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3")
        ], className="mb-3"),
        
        # Quarta linha: 2 métricas grandes
        dbc.Row([
            # Assinaturas esse mês
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Assinaturas esse mês", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4("73", id="assinaturas-mes-atual", className="fw-bold text-dark mb-0", style={"fontSize": "2rem", "textAlign": "center"})
                    ], className="p-4")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa", "minHeight": "120px"})
            ], width=12, md=6, className="mb-3"),
            
            # Assinaturas do Mês Passado
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Assinaturas do Mês Passado", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4("73", id="assinaturas-mes-passado", className="fw-bold text-dark mb-0", style={"fontSize": "2rem", "textAlign": "center"})
                    ], className="p-4")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa", "minHeight": "120px"})
            ], width=12, md=6, className="mb-3")
        ])
        
    ], fluid=True, className="py-4")


def create_final_metrics_grid_with_data(metrics_data):
    """
    Cria grid final de métricas com dados reais.
    
    Args:
        metrics_data (dict): Dados das métricas
    
    Returns:
        dbc.Container: Container com métricas populadas
    """
    return dbc.Container([
        # Primeira linha: 4 métricas com dados
        dbc.Row([
            # MRR - (TOTAL)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("MRR - (TOTAL)", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4(metrics_data.get('mrr_total', 'R$ 556 330,48'), className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3"),
            
            # ARR - (TOTAL)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("ARR - (TOTAL)", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4(metrics_data.get('arr_total', 'R$ 556 330,48'), className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3"),
            
            # Recorrência - MRA
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Recorrência - MRA (Monthly Recurrence Average)", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4(metrics_data.get('mra', '50 499'), className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3"),
            
            # MRR - Growth (%)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("MRR - Growth (%)", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4(metrics_data.get('mrr_growth', '50 499'), className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3")
        ], className="mb-3"),
        
        # Segunda linha: 4 métricas com dados
        dbc.Row([
            # MRR - (Plano Mensal)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("MRR - (Plano Mensal)", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4(metrics_data.get('mrr_mensal', 'R$ 556 330,48'), className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3"),
            
            # ARR - (Plano Mensal)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("ARR - (Plano Mensal)", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4(metrics_data.get('arr_mensal', 'R$ 556 330,48'), className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3"),
            
            # Assinaturas Ativas (DESTAQUE - ROXO)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Assinaturas Ativas", className="text-white mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4(metrics_data.get('assinaturas_ativas', '73'), className="fw-bold text-white mb-0", style={"fontSize": "2rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#8B5CF6"})
            ], width=12, md=6, lg=3, className="mb-3"),
            
            # Assinaturas Canceladas
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Assinaturas Canceladas", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4(metrics_data.get('assinaturas_canceladas', '73'), className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3")
        ], className="mb-3"),
        
        # Terceira linha: 4 métricas com dados
        dbc.Row([
            # MRR - (Plano Anual)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("MRR - (Plano Anual)", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4(metrics_data.get('mrr_anual', 'R$ 556 330,48'), className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3"),
            
            # ARR - (Plano Anual)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("ARR - (Plano Anual)", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4(metrics_data.get('arr_anual', 'R$ 556 330,48'), className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3"),
            
            # Churn Rate (%)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Churn Rate (%)", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4(metrics_data.get('churn_rate', '556 330,48'), className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3"),
            
            # Retention Rate (%)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Retention Rate (%)", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4(metrics_data.get('retention_rate', '73'), className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                    ], className="p-3")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"})
            ], width=12, md=6, lg=3, className="mb-3")
        ], className="mb-3"),
        
        # Quarta linha: 2 métricas grandes com dados
        dbc.Row([
            # Assinaturas esse mês
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Assinaturas esse mês", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4(metrics_data.get('assinaturas_mes_atual', '73'), className="fw-bold text-dark mb-0", style={"fontSize": "2rem", "textAlign": "center"})
                    ], className="p-4")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa", "minHeight": "120px"})
            ], width=12, md=6, className="mb-3"),
            
            # Assinaturas do Mês Passado
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Assinaturas do Mês Passado", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H4(metrics_data.get('assinaturas_mes_passado', '73'), className="fw-bold text-dark mb-0", style={"fontSize": "2rem", "textAlign": "center"})
                    ], className="p-4")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "backgroundColor": "#f8f9fa", "minHeight": "120px"})
            ], width=12, md=6, className="mb-3")
        ])
        
    ], fluid=True, className="py-4")