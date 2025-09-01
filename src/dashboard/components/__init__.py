"""
Componentes do Dashboard
=======================

Módulo responsável pelos componentes reutilizáveis do dashboard.
"""

from .metric_card import create_metric_card
from .growth_badge import create_growth_badge
from .chart_container import create_chart_container

__all__ = [
    "create_metric_card",
    "create_growth_badge",
    "create_chart_container"
]
