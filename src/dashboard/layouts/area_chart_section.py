"""
Seção de Gráfico de Áreas
========================

Gráfico de áreas para "Receita de Recorrência x Vendas" baseado na screenshot.
Detecta automaticamente produtos no banco de dados e analisa a evolução temporal.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


def create_area_chart_section():
    """
    Cria a seção do gráfico de áreas "Receita de Recorrência x Vendas".
    
    Returns:
        dbc.Container: Container com gráfico de áreas
    """
    return dbc.Container([
        # Card principal do gráfico
        dbc.Card([
            # Cabeçalho do gráfico
            dbc.CardHeader([
                html.Div([
                    # Título principal
                    html.H5(
                        "Receita de recorrência x vendas",
                        className="text-dark fw-bold mb-0",
                        style={"fontSize": "1.25rem"}
                    )
                ], className="d-flex justify-content-between align-items-center")
            ], className="bg-white border-0 py-3 px-4"),
            
            # Corpo do gráfico
            dbc.CardBody([
                # Área do gráfico
                dcc.Graph(
                    id="area-chart-revenue-sales",
                    style={"height": "400px"},
                    config={
                        "displayModeBar": True,
                        "displaylogo": False,
                        "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d", "zoom2d", "autoScale2d"],
                        "toImageButtonOptions": {
                            "format": "png",
                            "filename": "receita_recorrencia_vendas",
                            "height": 400,
                            "width": 1200,
                            "scale": 2
                        }
                    }
                )
            ], className="px-4 pb-4 pt-2")
        ], 
        className="border-0 shadow-sm mb-4",
        style={
            "backgroundColor": "white",
            "borderRadius": "0.75rem"
        })
        
    ], fluid=True, className="px-0")


def create_area_chart_section_with_data(chart_data):
    """
    Cria seção do gráfico de áreas com dados reais.
    
    Args:
        chart_data (dict): Dados do gráfico contendo séries temporais
    
    Returns:
        dbc.Container: Container com gráfico populado
    """
    return dbc.Container([
        # Card principal do gráfico
        dbc.Card([
            # Cabeçalho do gráfico com metadados
            dbc.CardHeader([
                html.Div([
                    # Título principal
                    html.H5(
                        "Receita de recorrência x vendas",
                        className="text-dark fw-bold mb-0",
                        style={"fontSize": "1.25rem"}
                    ),
                    
                    # Metadados do gráfico
                    html.Div([
                        html.Span([
                            html.I(className="fas fa-chart-area me-1", style={"color": "#6b7280"}),
                            f"{chart_data.get('total_products', 0)} produtos analisados"
                        ], 
                        className="text-muted small",
                        style={"fontSize": "0.875rem"})
                    ])
                ], className="d-flex justify-content-between align-items-center")
            ], className="bg-white border-0 py-3 px-4"),
            
            # Corpo do gráfico
            dbc.CardBody([
                # Área do gráfico
                dcc.Graph(
                    id="area-chart-revenue-sales",
                    style={"height": "400px"},
                    config={
                        "displayModeBar": True,
                        "displaylogo": False,
                        "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d", "zoom2d", "autoScale2d"],
                        "toImageButtonOptions": {
                            "format": "png",
                            "filename": "receita_recorrencia_vendas",
                            "height": 400,
                            "width": 1200,
                            "scale": 2
                        }
                    }
                )
            ], className="px-4 pb-4 pt-2")
        ], 
        className="border-0 shadow-sm mb-4",
        style={
            "backgroundColor": "white",
            "borderRadius": "0.75rem"
        })
        
    ], fluid=True, className="px-0")


def create_area_chart_section_loading():
    """
    Cria seção do gráfico de áreas com estado de carregamento.
    
    Returns:
        dbc.Container: Container com gráfico em loading
    """
    return dbc.Container([
        # Card principal do gráfico
        dbc.Card([
            # Cabeçalho do gráfico
            dbc.CardHeader([
                html.Div([
                    # Título principal
                    html.H5(
                        "Receita de recorrência x vendas",
                        className="text-dark fw-bold mb-0",
                        style={"fontSize": "1.25rem"}
                    ),
                    
                    # Indicador de carregamento
                    html.Div([
                        dbc.Spinner(size="sm", color="primary"),
                        html.Span("Carregando dados...", className="text-muted small ms-2")
                    ], className="d-flex align-items-center")
                ], className="d-flex justify-content-between align-items-center")
            ], className="bg-white border-0 py-3 px-4"),
            
            # Corpo do gráfico com skeleton
            dbc.CardBody([
                # Skeleton do gráfico
                html.Div([
                    html.Div([
                        html.Div(className="placeholder-glow"),
                        html.Div(className="placeholder bg-secondary", style={"height": "300px", "borderRadius": "8px"})
                    ], className="text-center")
                ], style={"height": "400px", "display": "flex", "alignItems": "center", "justifyContent": "center"})
            ], className="px-4 pb-4 pt-2")
        ], 
        className="border-0 shadow-sm mb-4",
        style={
            "backgroundColor": "white",
            "borderRadius": "0.75rem"
        })
        
    ], fluid=True, className="px-0")
