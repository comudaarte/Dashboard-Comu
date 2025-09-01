"""
Callbacks do Gráfico de Áreas
=============================

Callbacks para o gráfico "Receita de Recorrência x Vendas".
Gera dados sintéticos baseados nos produtos detectados no banco.
"""

from dash import callback, Input, Output
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


def register_area_chart_callbacks(app):
    """
    Registra callbacks do gráfico de áreas.
    
    Args:
        app: Aplicação Dash
    """
    
    @app.callback(
        Output("area-chart-revenue-sales", "figure"),
        [Input("dashboard-data-store", "data")]
    )
    def update_area_chart_revenue_sales(data):
        """
        Atualiza o gráfico de áreas "Receita de Recorrência x Vendas".
        """
        # Gera dados sintéticos para demonstração (baseado na screenshot)
        # Em produção, estes dados viriam do banco de dados
        
        # Período de análise (últimos 15 meses)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=450)
        
        # Gera datas mensais
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Produtos baseados na screenshot
        products = [
            "Comunidade da Arte - Mensal",
            "Comunidade da Arte - Anual", 
            "Comunidade da Arte",
            "Como Criar Personagens?",
            "Comissions na Gringa",
            "Formação Tattoo",
            "Mentoria - Tatuador PRO"
        ]
        
        # Cores para cada produto (baseado na screenshot)
        colors = [
            "#1f2937",  # Preto - Comunidade da Arte - Mensal
            "#8b5cf6",  # Roxo - Comunidade da Arte - Anual
            "#d1d5db",  # Cinza claro - Comunidade da Arte
            "#6b7280",  # Cinza médio - Como Criar Personagens?
            "#374151",  # Cinza escuro - Comissions na Gringa
            "#9ca3af",  # Cinza - Formação Tattoo
            "#4b5563"   # Cinza escuro 2 - Mentoria - Tatuador PRO
        ]
        
        fig = go.Figure()
        
        # Adiciona cada produto como área empilhada
        for i, product in enumerate(products):
            # Gera dados sintéticos com variações realistas
            np.random.seed(i + 42)  # Seed para dados consistentes
            
            # Base de receita por produto
            base_revenue = np.random.uniform(10, 80, len(date_range))
            
            # Adiciona tendências e sazonalidade
            trend = np.linspace(0, 20, len(date_range))
            seasonality = 10 * np.sin(2 * np.pi * np.arange(len(date_range)) / 365.25)
            noise = np.random.normal(0, 5, len(date_range))
            
            revenue_data = np.maximum(0, base_revenue + trend + seasonality + noise)
            
            # Suaviza os dados
            revenue_data = pd.Series(revenue_data).rolling(window=7, center=True).mean().fillna(method='bfill').fillna(method='ffill')
            
            # Converte cor hex para RGBA com transparência
            hex_color = colors[i % len(colors)]
            # Remove o # se presente
            hex_color = hex_color.lstrip('#')
            # Converte para RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            # Adiciona transparência (0.25 = 25%)
            rgba_color = f'rgba({r}, {g}, {b}, 0.25)'
            
            fig.add_trace(go.Scatter(
                x=date_range,
                y=revenue_data,
                mode='lines',
                name=product,
                fill='tonexty' if i > 0 else 'tozeroy',
                fillcolor=rgba_color,  # RGBA com transparência
                line=dict(
                    color=colors[i % len(colors)],
                    width=1.5
                ),
                stackgroup='one',
                hovertemplate=(
                    f"<b>{product}</b><br>"
                    "Data: %{x|%d/%m/%Y}<br>"
                    "Receita: R$ %{y:,.2f}<br>"
                    "<extra></extra>"
                )
            ))
        
        # Configurações do layout (baseado na screenshot)
        fig.update_layout(
            # Título e dimensões
            title=None,
            height=400,
            
            # Margens
            margin=dict(l=50, r=50, t=30, b=80),
            
            # Fundo
            plot_bgcolor='white',
            paper_bgcolor='white',
            
            # Grid
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#e5e7eb',
                tickformat='%m/%Y',
                tickangle=0,
                title=None,
                showline=True,
                linewidth=1,
                linecolor='#d1d5db'
            ),
            
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#e5e7eb',
                title=None,
                showline=True,
                linewidth=1,
                linecolor='#d1d5db',
                tickformat=',.0f'
            ),
            
            # Legenda (baseada na screenshot)
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(255,255,255,0)",
                bordercolor="rgba(255,255,255,0)",
                font=dict(size=11),
                itemsizing='constant'
            ),
            
            # Hover
            hovermode='x unified',
            
            # Responsividade
            autosize=True
        )
        
        # Remove zoom e pan para manter foco na visualização
        fig.update_layout(
            xaxis=dict(fixedrange=True),
            yaxis=dict(fixedrange=True)
        )
        
        return fig
