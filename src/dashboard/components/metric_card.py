"""
Componente de Card de Métrica
============================

Card reutilizável para exibir métricas do dashboard.
Design baseado nas screenshots de referência.
"""

import dash_bootstrap_components as dbc
from dash import html
from .growth_badge import create_growth_badge


def create_metric_card(title, value, subtitle=None, growth=None, color="white", highlight=False):
    """
    Cria um card de métrica reutilizável.
    
    Args:
        title (str): Título do card
        value (str): Valor principal da métrica
        subtitle (str, optional): Subtítulo explicativo
        growth (dict, optional): Dados de crescimento {'value': float, 'period': str}
        color (str): Cor de fundo do card
        highlight (bool): Se deve destacar o card (ex: roxo para assinaturas ativas)
    
    Returns:
        dbc.Card: Card de métrica estilizado
    """
    # Define classes base do card
    card_classes = "h-100 border-0 shadow-sm"
    
    # Adiciona destaque se necessário
    if highlight:
        card_classes += " border-primary border-2"
        bg_color = "#8B5CF6"  # Roxo principal
        text_color = "text-white"
    else:
        bg_color = color
        text_color = "text-dark"
    
    # Constrói conteúdo do card
    card_content = [
        # Título
        html.H6(title, className=f"text-muted mb-2 {text_color}", style={"fontSize": "0.875rem"}),
        
        # Valor principal
        html.H3(value, className=f"fw-bold mb-1 {text_color}", style={"fontSize": "1.75rem"}),
    ]
    
    # Adiciona subtítulo se fornecido
    if subtitle:
        card_content.append(
            html.P(subtitle, className=f"text-muted small mb-2 {text_color}")
        )
    
    # Adiciona badge de crescimento se fornecido
    if growth:
        card_content.append(
            create_growth_badge(growth)
        )
    
    # Cria o card
    return dbc.Card(
        dbc.CardBody(card_content, className="p-3"),
        className=card_classes,
        style={
            "backgroundColor": bg_color,
            "borderRadius": "0.75rem",
            "transition": "all 0.2s ease-in-out"
        }
    )


def create_metric_card_simple(title, value, color="white"):
    """
    Versão simplificada do card de métrica.
    
    Args:
        title (str): Título do card
        value (str): Valor da métrica
        color (str): Cor de fundo
    
    Returns:
        dbc.Card: Card simples
    """
    return create_metric_card(
        title=title,
        value=value,
        color=color
    )


def create_metric_card_with_growth(title, value, growth_value, growth_period, color="white"):
    """
    Card de métrica com badge de crescimento.
    
    Args:
        title (str): Título do card
        value (str): Valor da métrica
        growth_value (float): Valor do crescimento em percentual
        growth_period (str): Período do crescimento
        color (str): Cor de fundo
    
    Returns:
        dbc.Card: Card com crescimento
    """
    growth_data = {
        "value": growth_value,
        "period": growth_period
    }
    
    return create_metric_card(
        title=title,
        value=value,
        growth=growth_data,
        color=color
    )
