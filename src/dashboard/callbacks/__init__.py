"""
Callbacks do Dashboard
=====================

Módulo responsável pela interatividade e atualizações do dashboard.
"""

from .metrics_callbacks import register_metrics_callbacks
from .charts_callbacks import register_charts_callbacks
from .date_callbacks import register_date_callbacks
from .area_chart_callbacks import register_area_chart_callbacks


def register_all_callbacks(app):
    """
    Registra todos os callbacks do dashboard.
    
    Args:
        app: Aplicação Dash
    """
    register_metrics_callbacks(app)
    register_charts_callbacks(app)
    register_date_callbacks(app)
    register_area_chart_callbacks(app)


__all__ = [
    "register_metrics_callbacks",
    "register_charts_callbacks", 
    "register_date_callbacks",
    "register_area_chart_callbacks",
    "register_all_callbacks"
]
