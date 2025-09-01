"""
Componente de Badge de Crescimento
=================================

Badge que exibe crescimento percentual com setas e cores.
Design baseado nas screenshots de referência.
"""

from dash import html


def create_growth_badge(growth_data):
    """
    Cria badge de crescimento com seta e percentual.
    
    Args:
        growth_data (dict): Dados de crescimento {'value': float, 'period': str}
    
    Returns:
        html.Div: Badge estilizado
    """
    value = growth_data.get("value", 0)
    period = growth_data.get("period", "")
    
    # Define se é crescimento positivo ou negativo
    is_positive = value > 0
    
    # Define ícone e cor baseado no valor
    if is_positive:
        arrow_icon = "fas fa-arrow-up"
        color_class = "text-success"
        bg_color = "#10B981"  # Verde para crescimento
    else:
        arrow_icon = "fas fa-arrow-down"
        color_class = "text-danger"
        bg_color = "#EF4444"  # Vermelho para queda
    
    # Cria o badge
    return html.Div([
        # Ícone da seta
        html.I(
            className=f"{arrow_icon} me-1",
            style={"fontSize": "0.75rem"}
        ),
        
        # Valor percentual
        html.Span(
            f"{abs(value):.1f}%",
            className="fw-bold me-1",
            style={"fontSize": "0.75rem"}
        ),
        
        # Período
        html.Small(
            period,
            className="text-muted",
            style={"fontSize": "0.625rem"}
        )
    ], 
    className="badge px-2 py-1",
    style={
        "backgroundColor": bg_color,
        "color": "white",
        "borderRadius": "0.375rem",
        "fontSize": "0.75rem",
        "fontWeight": "500"
    })


def create_growth_badge_simple(value, period=""):
    """
    Versão simplificada do badge de crescimento.
    
    Args:
        value (float): Valor do crescimento em percentual
        period (str): Período do crescimento
    
    Returns:
        html.Div: Badge simples
    """
    return create_growth_badge({
        "value": value,
        "period": period
    })


def create_growth_badge_with_icon(value, period, icon_class="fas fa-chart-line"):
    """
    Badge de crescimento com ícone customizado.
    
    Args:
        value (float): Valor do crescimento
        period (str): Período
        icon_class (str): Classe do ícone FontAwesome
    
    Returns:
        html.Div: Badge com ícone customizado
    """
    growth_data = {
        "value": value,
        "period": period
    }
    
    # Cria badge base
    badge = create_growth_badge(growth_data)
    
    # Adiciona ícone customizado
    custom_icon = html.I(
        className=f"{icon_class} me-1",
        style={"fontSize": "0.75rem"}
    )
    
    # Insere ícone no início
    badge.children.insert(0, custom_icon)
    
    return badge
