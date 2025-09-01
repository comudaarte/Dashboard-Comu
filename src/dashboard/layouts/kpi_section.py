"""
Seção KPI (Compatibilidade)
===========================

Arquivo de compatibilidade para manter imports funcionando.
As funcionalidades principais foram movidas para main_metrics_section.py.
"""

import dash_bootstrap_components as dbc
from dash import html


def create_kpi_section():
    """
    Função de compatibilidade - retorna seção vazia.
    As métricas principais estão em main_metrics_section.py.
    
    Returns:
        html.Div: Container vazio para compatibilidade
    """
    return html.Div([
        html.Div([
            html.H6("KPIs", className="text-muted"),
            html.P("Seção KPI movida para main_metrics_section.py", className="text-muted small")
        ], className="text-center p-4")
    ], className="mb-4")


def create_kpi_section_legacy():
    """
    Função legada para compatibilidade com código existente.
    
    Returns:
        html.Div: Container vazio
    """
    return create_kpi_section()
