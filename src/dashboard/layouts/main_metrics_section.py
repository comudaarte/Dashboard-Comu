"""
Seção Principal de Métricas
===========================

Seção que mostra o card principal de Faturamento Total e os cards secundários
conforme o design da screenshot de referência.
"""

import dash_bootstrap_components as dbc
from dash import html
from ..components.metric_card import create_metric_card
from ..components.growth_badge import create_growth_badge


def create_main_metrics_section():
    """
    Cria a seção principal de métricas conforme o design da screenshot.
    
    Returns:
        dbc.Container: Container com o layout principal
    """
    return dbc.Container([
        # Container centralizado
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    # Card principal - Faturamento Total (lado esquerdo)
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                # Cabeçalho com título e badges alinhados
                                html.Div([
                                    # Título
                                    html.H6(
                                        "Faturamento Total",
                                        className="text-muted mb-0",
                                        style={"fontSize": "0.875rem", "fontWeight": "400"}
                                    ),
                                    
                                    # Badges alinhados horizontalmente (lado direito)
                                    html.Div([
                                        # Badge "Esse Mês"
                                        html.Div([
                                            html.Span("Esse Mês", className="me-2", style={
                                                "fontSize": "0.75rem",
                                                "color": "#6b7280"
                                            }),
                                            html.Span([
                                                html.I(className="fas fa-arrow-up me-1", style={
                                                    "fontSize": "0.75rem",
                                                    "color": "white"
                                                }),
                                                "7,9%"
                                            ], className="badge", style={
                                                "backgroundColor": "#8B5CF6",
                                                "color": "white",
                                                "fontSize": "0.75rem",
                                                "fontWeight": "500",
                                                "padding": "4px 8px",
                                                "borderRadius": "12px"
                                            })
                                        ], className="d-flex align-items-center me-3"),
                                        
                                        # Badge "Esse Ano"
                                        html.Div([
                                            html.Span("Esse Ano", className="me-2", style={
                                                "fontSize": "0.75rem",
                                                "color": "#6b7280"
                                            }),
                                            html.Span([
                                                html.I(className="fas fa-arrow-up me-1", style={
                                                    "fontSize": "0.75rem",
                                                    "color": "white"
                                                }),
                                                "7,9%"
                                            ], className="badge", style={
                                                "backgroundColor": "#8B5CF6",
                                                "color": "white",
                                                "fontSize": "0.75rem",
                                                "fontWeight": "500",
                                                "padding": "4px 8px",
                                                "borderRadius": "12px"
                                            })
                                        ], className="d-flex align-items-center")
                                    ], className="d-flex align-items-center")
                                ], className="d-flex justify-content-between align-items-center mb-2"),
                                
                                # Valor principal
                                html.H1(
                                    "R$ 514.396,77",
                                    className="fw-bold text-dark mb-1",
                                    style={"fontSize": "2.5rem", "lineHeight": "1.2"}
                                ),
                                
                                # Subtítulo
                                html.P(
                                    "Receita bruta de R$1.000.000,00",
                                    className="text-muted mb-0",
                                    style={"fontSize": "0.875rem"}
                                )
                            ], className="p-4", style={"minHeight": "140px"})
                        ], className="h-100 border-0 shadow-sm", style={
                            "borderRadius": "12px",
                            "background": "white"
                        })
                    ], width=12, lg=6, className="mb-4"),
                    
                    # Cards secundários (lado direito) - NA MESMA LINHA HORIZONTAL
                    dbc.Col([
                        # Card Quantidade Vendas (maior no topo)
                        dbc.Card([
                            dbc.CardBody([
                                html.H6(
                                    "Quantidade Vendas",
                                    className="text-muted mb-2",
                                    style={"fontSize": "0.875rem", "fontWeight": "400"}
                                ),
                                html.H3(
                                    "4.161",
                                    className="fw-bold text-dark mb-0",
                                    style={"fontSize": "2rem"}
                                )
                            ], className="p-3")
                        ], className="border-0 shadow-sm mb-3", style={
                            "borderRadius": "12px",
                            "background": "white"
                        }),
                        
                        # Linha com dois cards menores alinhados
                        dbc.Row([
                            # Card Qnt. de Alunos
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6(
                                            "Qnt. de Alunos",
                                            className="text-muted mb-2",
                                            style={"fontSize": "0.75rem", "fontWeight": "400"}
                                        ),
                                        html.H4(
                                            "4.161",
                                            className="fw-bold text-dark mb-0",
                                            style={"fontSize": "1.25rem"}
                                        )
                                    ], className="p-2")
                                ], className="h-100 border-0 shadow-sm", style={
                                    "borderRadius": "8px",
                                    "background": "white",
                                    "minHeight": "80px"
                                })
                            ], width=6, className="pe-1"),
                            
                            # Card LTV Geral
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6(
                                            "LTV Geral",
                                            className="text-muted mb-2",
                                            style={"fontSize": "0.75rem", "fontWeight": "400"}
                                        ),
                                        html.H4(
                                            "4.161",
                                            className="fw-bold text-dark mb-0",
                                            style={"fontSize": "1.25rem"}
                                        )
                                    ], className="p-2")
                                ], className="h-100 border-0 shadow-sm", style={
                                    "borderRadius": "8px",
                                    "background": "white",
                                    "minHeight": "80px"
                                })
                            ], width=6, className="ps-1")
                        ])
                    ], width=12, lg=6)
                ], className="justify-content-center align-items-start")
            ], width=12)
        ], className="mb-5")
    ], fluid=True, className="px-4")


def create_main_metrics_section_with_data(revenue_data, sales_data, students_data, ltv_data):
    """
    Cria a seção principal de métricas com dados reais.
    
    Args:
        revenue_data (dict): Dados de faturamento
        sales_data (dict): Dados de vendas
        students_data (dict): Dados de alunos
        ltv_data (dict): Dados de LTV
    
    Returns:
        dbc.Container: Container com métricas populadas
    """
    return dbc.Container([
        dbc.Row([
            # Card principal - Faturamento Total
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        # Cabeçalho com título e badges alinhados
                        html.Div([
                            # Título
                            html.H6(
                                "Faturamento Total",
                                className="text-muted mb-0",
                                style={"fontSize": "0.875rem", "fontWeight": "400"}
                            ),
                            
                            # Badges alinhados horizontalmente (lado direito)
                            html.Div([
                                # Badge "Esse Mês"
                                html.Div([
                                    html.Span("Esse Mês", className="me-2", style={
                                        "fontSize": "0.75rem",
                                        "color": "#6b7280"
                                    }),
                                    html.Span([
                                        html.I(className="fas fa-arrow-up me-1", style={
                                            "fontSize": "0.75rem",
                                            "color": "white"
                                        }),
                                        f"{revenue_data.get('growth_month', 7.9):.1f}%"
                                    ], className="badge", style={
                                        "backgroundColor": "#8B5CF6",
                                        "color": "white",
                                        "fontSize": "0.75rem",
                                        "fontWeight": "500",
                                        "padding": "4px 8px",
                                        "borderRadius": "12px"
                                    })
                                ], className="d-flex align-items-center me-3"),
                                
                                # Badge "Esse Ano"
                                html.Div([
                                    html.Span("Esse Ano", className="me-2", style={
                                        "fontSize": "0.75rem",
                                        "color": "#6b7280"
                                    }),
                                    html.Span([
                                        html.I(className="fas fa-arrow-up me-1", style={
                                            "fontSize": "0.75rem",
                                            "color": "white"
                                        }),
                                        f"{revenue_data.get('growth_year', 7.9):.1f}%"
                                    ], className="badge", style={
                                        "backgroundColor": "#8B5CF6",
                                        "color": "white",
                                        "fontSize": "0.75rem",
                                        "fontWeight": "500",
                                        "padding": "4px 8px",
                                        "borderRadius": "12px"
                                    })
                                ], className="d-flex align-items-center")
                            ], className="d-flex align-items-center")
                        ], className="d-flex justify-content-between align-items-center mb-2"),
                        
                        # Valor principal
                        html.H1(
                            f"R$ {revenue_data.get('total', 0):,.2f}",
                            className="fw-bold text-dark mb-1",
                            style={"fontSize": "2.5rem", "lineHeight": "1.2"}
                        ),
                        
                        # Subtítulo
                        html.P(
                            f"Receita bruta de R$ {revenue_data.get('gross_revenue', 0):,.2f}",
                            className="text-muted mb-0",
                            style={"fontSize": "0.875rem"}
                        )
                    ], className="p-4", style={"minHeight": "140px"})
                ], className="h-100 border-0 shadow-sm", style={
                    "borderRadius": "12px",
                    "background": "white"
                })
            ], width=12, lg=6, className="mb-4"),
            
            # Cards secundários - NA MESMA LINHA HORIZONTAL
            dbc.Col([
                # Card Quantidade Vendas (maior no topo)
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6(
                                    "Quantidade Vendas",
                                    className="text-muted mb-2",
                                    style={"fontSize": "0.875rem", "fontWeight": "400"}
                                ),
                                html.H3(
                                    f"{sales_data.get('total', 0):,}",
                                    className="fw-bold text-dark mb-0",
                                    style={"fontSize": "2rem"}
                                )
                            ], className="p-3")
                        ], className="h-100 border-0 shadow-sm", style={
                            "borderRadius": "12px"
                        })
                    ], width=12, className="mb-3")
                ]),
                
                # Linha com dois cards menores alinhados
                dbc.Row([
                    # Card Qnt. de Alunos
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6(
                                    "Qnt. de Alunos",
                                    className="text-muted mb-2",
                                    style={"fontSize": "0.75rem", "fontWeight": "400"}
                                ),
                                html.H4(
                                    f"{students_data.get('total', 0):,}",
                                    className="fw-bold text-dark mb-0",
                                    style={"fontSize": "1.25rem"}
                                )
                            ], className="p-2")
                        ], className="h-100 border-0 shadow-sm", style={
                            "borderRadius": "8px",
                            "minHeight": "80px"
                        })
                    ], width=6, className="pe-1"),
                    
                    # Card LTV Geral
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6(
                                    "LTV Geral",
                                    className="text-muted mb-2",
                                    style={"fontSize": "0.75rem", "fontWeight": "400"}
                                ),
                                html.H4(
                                    f"R$ {ltv_data.get('total', 0):,.0f}",
                                    className="fw-bold text-dark mb-0",
                                    style={"fontSize": "1.25rem"}
                                )
                            ], className="p-2")
                        ], className="h-100 border-0 shadow-sm", style={
                            "borderRadius": "8px",
                            "minHeight": "80px"
                        })
                    ], width=6, className="ps-1")
                ])
            ], width=12, lg=6)
        ], className="mb-5 justify-content-center align-items-start")
    ], fluid=True)


def create_main_metrics_section_loading():
    """
    Cria a seção principal de métricas com estado de carregamento.
    
    Returns:
        dbc.Container: Container com loading
    """
    loading_spinner = html.Div([
        html.Div(className="spinner-border spinner-border-sm me-2", style={"color": "#8B5CF6"}),
        "Carregando..."
    ], className="text-center text-muted")
    
    return dbc.Container([
        dbc.Row([
            # Card principal em loading
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        loading_spinner
                    ], style={"minHeight": "140px", "display": "flex", "alignItems": "center", "justifyContent": "center"})
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px"})
            ], width=12, lg=6, className="mb-4"),
            
            # Cards secundários em loading
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([loading_spinner], className="p-3")
                        ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px"})
                    ], width=12, className="mb-3"),
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([loading_spinner], className="p-3")
                                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px"})
                            ], width=6, className="mb-3"),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([loading_spinner], className="p-3")
                                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px"})
                            ], width=6, className="mb-3")
                        ])
                    ], width=12)
                ])
            ], width=12, lg=6)
        ], className="mb-5 justify-content-center align-items-start")
    ], fluid=True)
