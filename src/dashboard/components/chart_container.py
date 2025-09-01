"""
Componente de Container de Gráfico
==================================

Container reutilizável para gráficos do dashboard.
Design baseado nas screenshots de referência.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


def create_chart_container(title, chart_id, subtitle=None, height=400, loading=False):
    """
    Cria um container para gráficos com título e controles.
    
    Args:
        title (str): Título do gráfico
        chart_id (str): ID do componente de gráfico
        subtitle (str, optional): Subtítulo explicativo
        height (int): Altura do gráfico em pixels
        loading (bool): Se deve mostrar estado de carregamento
    
    Returns:
        dbc.Card: Container do gráfico estilizado
    """
    # Constrói cabeçalho do gráfico
    header_content = [
        # Título principal
        html.H5(
            title,
            className="text-dark fw-bold mb-1",
            style={"fontSize": "1.125rem"}
        )
    ]
    
    # Adiciona subtítulo se fornecido
    if subtitle:
        header_content.append(
            html.P(
                subtitle,
                className="text-muted small mb-0",
                style={"fontSize": "0.875rem"}
            )
        )
    
    # Cria o container
    return dbc.Card([
        # Cabeçalho do gráfico
        dbc.CardBody([
            html.Div(header_content, className="mb-3")
        ], className="pb-2"),
        
        # Área do gráfico
        dbc.CardBody([
            html.Div([
                # Estado de carregamento
                html.Div([
                    html.Div(className="spinner-border spinner-border-sm me-2"),
                    "Carregando gráfico..."
                ], className="text-center text-muted", style={"height": f"{height}px", "display": "flex", "alignItems": "center", "justifyContent": "center"})
            ]) if loading else
            # Componente do gráfico
            dcc.Graph(
                id=chart_id,
                style={"height": f"{height}px"},
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d"],
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": title.lower().replace(" ", "_"),
                        "height": height,
                        "width": 800,
                        "scale": 2
                    }
                }
            )
        ], className="pt-0")
    ], 
    className="h-100 border-0 shadow-sm",
    style={
        "backgroundColor": "white",
        "borderRadius": "0.75rem",
        "transition": "all 0.2s ease-in-out"
    })


def create_chart_container_with_controls(title, chart_id, controls=None, subtitle=None, height=400):
    """
    Cria container de gráfico com controles adicionais.
    
    Args:
        title (str): Título do gráfico
        chart_id (str): ID do componente de gráfico
        controls (list, optional): Lista de componentes de controle
        subtitle (str, optional): Subtítulo explicativo
        height (int): Altura do gráfico
    
    Returns:
        dbc.Card: Container com controles
    """
    # Constrói cabeçalho com controles
    header_content = [
        # Título e controles em linha
        html.Div([
            # Título
            html.Div([
                html.H5(
                    title,
                    className="text-dark fw-bold mb-1",
                    style={"fontSize": "1.125rem"}
                ),
                subtitle and html.P(
                    subtitle,
                    className="text-muted small mb-0",
                    style={"fontSize": "0.875rem"}
                )
            ], className="flex-grow-1"),
            
            # Controles (se fornecidos)
            controls and html.Div(controls, className="ms-3")
        ], className="d-flex align-items-center justify-content-between")
    ]
    
    # Cria o container
    return dbc.Card([
        # Cabeçalho com controles
        dbc.CardBody([
            html.Div(header_content, className="mb-3")
        ], className="pb-2"),
        
        # Área do gráfico
        dbc.CardBody([
            dcc.Graph(
                id=chart_id,
                style={"height": f"{height}px"},
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d"],
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": title.lower().replace(" ", "_"),
                        "height": height,
                        "width": 800,
                        "scale": 2
                    }
                }
            )
        ], className="pt-0")
    ], 
    className="h-100 border-0 shadow-sm",
    style={
        "backgroundColor": "white",
        "borderRadius": "0.75rem",
        "transition": "all 0.2s ease-in-out"
    })


def create_chart_container_simple(title, chart_id, height=300):
    """
    Versão simplificada do container de gráfico.
    
    Args:
        title (str): Título do gráfico
        chart_id (str): ID do componente
        height (int): Altura do gráfico
    
    Returns:
        dbc.Card: Container simples
    """
    return create_chart_container(
        title=title,
        chart_id=chart_id,
        height=height
    )
