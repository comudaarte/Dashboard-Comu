"""
Layouts do Dashboard
===================

Módulo responsável pelos layouts responsivos do dashboard.
"""

from .main_layout import create_main_layout
from .header import create_header
from .main_metrics_section import create_main_metrics_section
from .charts_section import create_charts_section
from .performance_metrics_section import create_performance_metrics_section
from .area_chart_section import create_area_chart_section
from .final_metrics_grid import create_final_metrics_grid
from .metrics_grid import create_metrics_grid
from .kpi_section import create_kpi_section

__all__ = [
    "create_main_layout",
    "create_header",
    "create_main_metrics_section",
    "create_charts_section",
    "create_performance_metrics_section",
    "create_area_chart_section",
    "create_final_metrics_grid",
    "create_metrics_grid",
    "create_kpi_section"
]
