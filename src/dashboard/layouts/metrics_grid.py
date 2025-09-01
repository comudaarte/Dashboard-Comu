"""
Grid de Métricas (Compatibilidade)
=================================

Arquivo de compatibilidade para manter imports funcionando.
As funcionalidades principais foram movidas para final_metrics_grid.py.
"""

import dash_bootstrap_components as dbc
from dash import html


def create_metrics_grid():
    """
    Função de compatibilidade - retorna grid vazio.
    As métricas principais estão em final_metrics_grid.py.
    
    Returns:
        html.Div: Container vazio para compatibilidade
    """
    return html.Div([
        html.Div([
            html.H6("Métricas", className="text-muted"),
            html.P("Grid de métricas movido para final_metrics_grid.py", className="text-muted small")
        ], className="text-center p-4")
    ], className="mb-4")


def create_metrics_grid_legacy():
    """
    Função legada para compatibilidade com código existente.
    
    Returns:
        html.Div: Container vazio
    """
    return create_metrics_grid()
