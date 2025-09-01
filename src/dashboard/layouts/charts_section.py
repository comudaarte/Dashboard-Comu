"""
Seção de Gráficos do Dashboard
=============================

Seção com gráficos de barras, linhas e outras visualizações.
Design baseado nas screenshots de referência.
"""

import dash_bootstrap_components as dbc
from dash import html
from ..components.chart_container import create_chart_container


def create_charts_section():
    """
    Cria a seção de gráficos principais conforme screenshot.
    
    Returns:
        dbc.Container: Container com gráficos alinhados
    """
    return dbc.Container([
        # Grid de 3 gráficos lado a lado (conforme screenshot)
        dbc.Row([
            # Gráfico 1: Compras por produtos
            dbc.Col([
                create_chart_container(
                    title="Compras por produtos",
                    chart_id="purchases-by-product-chart",
                    height=320
                )
            ], width=12, lg=4, className="mb-4"),
            
            # Gráfico 2: Receita por produto
            dbc.Col([
                create_chart_container(
                    title="Receita por produto",
                    chart_id="revenue-by-product-chart",
                    height=320
                )
            ], width=12, lg=4, className="mb-4"),
            
            # Gráfico 3: Número de vendas por produto x data
            dbc.Col([
                create_chart_container(
                    title="Número de vendas por produto x data",
                    chart_id="sales-by-date-chart",
                    height=320
                )
            ], width=12, lg=4, className="mb-4")
        ], className="g-3")
        
    ], fluid=True)


def create_charts_section_loading():
    """
    Cria seção de gráficos com estado de carregamento conforme screenshot.
    
    Returns:
        dbc.Container: Container com gráficos em loading
    """
    return dbc.Container([
        # Grid de 3 gráficos lado a lado em loading
        dbc.Row([
            # Gráfico 1: Loading
            dbc.Col([
                create_chart_container(
                    title="Compras por produtos",
                    chart_id="purchases-by-product-chart",
                    height=320,
                    loading=True
                )
            ], width=12, lg=4, className="mb-4"),
            
            # Gráfico 2: Loading
            dbc.Col([
                create_chart_container(
                    title="Receita por produto",
                    chart_id="revenue-by-product-chart",
                    height=320,
                    loading=True
                )
            ], width=12, lg=4, className="mb-4"),
            
            # Gráfico 3: Loading
            dbc.Col([
                create_chart_container(
                    title="Número de vendas por produto x data",
                    chart_id="sales-by-date-chart",
                    height=320,
                    loading=True
                )
            ], width=12, lg=4, className="mb-4")
        ], className="g-3")
        
    ], fluid=True)


def create_charts_section_with_data(charts_data):
    """
    Cria seção de gráficos com dados reais conforme screenshot.
    
    Args:
        charts_data (dict): Dados dos gráficos
    
    Returns:
        dbc.Container: Container com gráficos populados
    """
    return dbc.Container([
        # Grid de 3 gráficos lado a lado com dados
        dbc.Row([
            # Gráfico 1: Compras por produtos
            dbc.Col([
                create_chart_container(
                    title="Compras por produtos",
                    chart_id="purchases-by-product-chart",
                    height=320
                )
            ], width=12, lg=4, className="mb-4"),
            
            # Gráfico 2: Receita por produto
            dbc.Col([
                create_chart_container(
                    title="Receita por produto",
                    chart_id="revenue-by-product-chart",
                    height=320
                )
            ], width=12, lg=4, className="mb-4"),
            
            # Gráfico 3: Número de vendas por produto x data
            dbc.Col([
                create_chart_container(
                    title="Número de vendas por produto x data",
                    chart_id="sales-by-date-chart",
                    height=320
                )
            ], width=12, lg=4, className="mb-4")
        ], className="g-3")
        
    ], fluid=True)
