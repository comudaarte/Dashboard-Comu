"""
Layout Principal do Dashboard
============================

Layout principal que integra todos os componentes do dashboard.
Design responsivo baseado nas screenshots de referência.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
from .header import create_header_with_date_picker
from .main_metrics_section import create_main_metrics_section
from .charts_section import create_charts_section
from .performance_metrics_section import create_performance_metrics_section
from .area_chart_section import create_area_chart_section
from .final_metrics_grid import create_final_metrics_grid
from .metrics_grid import create_metrics_grid


def create_main_layout():
    """
    Cria o layout principal do dashboard.
    
    Returns:
        html.Div: Layout completo do dashboard
    """
    return html.Div([
        # Store para dados globais
        dcc.Store(id="dashboard-data-store"),
        dcc.Store(id="date-range-store"),
        
        # Header com seletor de datas
        create_header_with_date_picker(),
        
        # Container principal
        dbc.Container([
            # Seção principal de métricas (novo design)
            create_main_metrics_section(),
            
            # Seção de gráficos
            create_charts_section(),
            
            # Seção de métricas de performance
            create_performance_metrics_section(),
            
            # Seção de gráfico de áreas
            create_area_chart_section(),
            
            # Grid final de métricas (14 métricas)
            create_final_metrics_grid(),
            
            # Espaçamento inferior
            html.Div(style={"height": "2rem"})
            
        ], fluid=True, className="px-3")
        
    ], style={
        "backgroundColor": "#F8F9FA",
        "minHeight": "100vh",
        "fontFamily": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"
    })


def create_main_layout_with_loading():
    """
    Cria layout principal com estado de carregamento inicial.
    
    Returns:
        html.Div: Layout com loading
    """
    return html.Div([
        # Store para dados globais
        dcc.Store(id="dashboard-data-store"),
        dcc.Store(id="date-range-store"),
        
        # Header com seletor de datas
        create_header_with_date_picker(),
        
        # Container principal
        dbc.Container([
            # Loading spinner central
            html.Div([
                dbc.Spinner(
                    html.Div([
                        html.H4("Carregando Dashboard...", className="text-muted mb-3"),
                        html.P("Buscando dados das métricas...", className="text-muted")
                    ], className="text-center"),
                    size="lg",
                    color="primary"
                )
            ], className="d-flex justify-content-center align-items-center", style={"height": "50vh"})
            
        ], fluid=True, className="px-3")
        
    ], style={
        "backgroundColor": "#F8F9FA",
        "minHeight": "100vh",
        "fontFamily": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"
    })


def create_main_layout_with_error(error_message):
    """
    Cria layout principal com mensagem de erro.
    
    Args:
        error_message (str): Mensagem de erro a exibir
    
    Returns:
        html.Div: Layout com erro
    """
    return html.Div([
        # Store para dados globais
        dcc.Store(id="dashboard-data-store"),
        dcc.Store(id="date-range-store"),
        
        # Header com seletor de datas
        create_header_with_date_picker(),
        
        # Container principal
        dbc.Container([
            # Card de erro
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        # Ícone de erro
                        html.I(
                            className="fas fa-exclamation-triangle text-warning",
                            style={"fontSize": "3rem"}
                        ),
                        
                        # Título do erro
                        html.H4("Erro ao Carregar Dashboard", className="text-dark mt-3 mb-2"),
                        
                        # Mensagem de erro
                        html.P(
                            error_message,
                            className="text-muted mb-3"
                        ),
                        
                        # Botão de recarregar
                        dbc.Button([
                            html.I(className="fas fa-refresh me-2"),
                            "Tentar Novamente"
                        ], 
                        id="reload-dashboard-button",
                        color="primary",
                        className="mt-2")
                        
                    ], className="text-center")
                ])
            ], className="border-0 shadow-sm")
            
        ], fluid=True, className="px-3")
        
    ], style={
        "backgroundColor": "#F8F9FA",
        "minHeight": "100vh",
        "fontFamily": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"
    })


def create_main_layout_responsive():
    """
    Cria layout principal com breakpoints responsivos otimizados.
    
    Returns:
        html.Div: Layout responsivo
    """
    return html.Div([
        # Store para dados globais
        dcc.Store(id="dashboard-data-store"),
        dcc.Store(id="date-range-store"),
        
        # Header responsivo
        create_header_with_date_picker(),
        
        # Container responsivo
        dbc.Container([
            # Seção principal de métricas (novo design)
            dbc.Row([
                dbc.Col([
                    create_main_metrics_section()
                ], width=12)
            ], className="mb-4"),
            
            # Seção de gráficos (responsiva)
            dbc.Row([
                dbc.Col([
                    create_charts_section()
                ], width=12)
            ], className="mb-4"),
            
            # Seção de métricas de performance (responsiva)
            dbc.Row([
                dbc.Col([
                    create_performance_metrics_section()
                ], width=12)
            ], className="mb-4"),
            
            # Seção de gráfico de áreas (responsiva)
            dbc.Row([
                dbc.Col([
                    create_area_chart_section()
                ], width=12)
            ], className="mb-4"),
            
            # Grid final de métricas (responsivo)
            dbc.Row([
                dbc.Col([
                    create_final_metrics_grid()
                ], width=12)
            ], className="mb-4")
            
        ], 
        fluid=True, 
        className="px-2 px-md-3 px-lg-4",
        style={"maxWidth": "1400px"})
        
    ], style={
        "backgroundColor": "#F8F9FA",
        "minHeight": "100vh",
        "fontFamily": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"
    })
