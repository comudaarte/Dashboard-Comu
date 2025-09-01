"""
Callbacks de Gráficos
====================

Callbacks para atualização de gráficos do dashboard.
"""

from dash import callback, Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd


def register_charts_callbacks(app):
    """
    Registra callbacks relacionados aos gráficos.
    
    Args:
        app: Aplicação Dash
    """
    
    @app.callback(
        Output("purchases-by-product-chart", "figure"),
        [Input("dashboard-data-store", "data")]
    )
    def update_purchases_by_product_chart(data):
        """
        Atualiza gráfico de compras por produto.
        """
        if not data or "purchases_by_product" not in data:
            # Dados de exemplo
            products = ["Produto A", "Produto B", "Produto C", "Produto D"]
            purchases = [120, 85, 95, 110]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=products,
                    y=purchases,
                    marker_color="#8B5CF6",
                    text=purchases,
                    textposition="auto"
                )
            ])
        else:
            # Dados reais
            products_data = data["purchases_by_product"]
            products = list(products_data.keys())
            purchases = list(products_data.values())
            
            fig = go.Figure(data=[
                go.Bar(
                    x=products,
                    y=purchases,
                    marker_color="#8B5CF6",
                    text=purchases,
                    textposition="auto"
                )
            ])
        
        fig.update_layout(
            title="",
            xaxis_title="Produtos",
            yaxis_title="Número de Compras",
            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Inter, sans-serif", size=12),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        return fig
    
    @app.callback(
        Output("revenue-by-product-chart", "figure"),
        [Input("dashboard-data-store", "data")]
    )
    def update_revenue_by_product_chart(data):
        """
        Atualiza gráfico de receita por produto.
        """
        if not data or "revenue_by_product" not in data:
            # Dados de exemplo
            products = ["Produto A", "Produto B", "Produto C", "Produto D"]
            revenue = [15000, 12000, 18000, 14000]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=products,
                    y=revenue,
                    marker_color="#10B981",
                    text=[f"R$ {r:,.0f}" for r in revenue],
                    textposition="auto"
                )
            ])
        else:
            # Dados reais
            revenue_data = data["revenue_by_product"]
            products = list(revenue_data.keys())
            revenue = list(revenue_data.values())
            
            fig = go.Figure(data=[
                go.Bar(
                    x=products,
                    y=revenue,
                    marker_color="#10B981",
                    text=[f"R$ {r:,.0f}" for r in revenue],
                    textposition="auto"
                )
            ])
        
        fig.update_layout(
            title="",
            xaxis_title="Produtos",
            yaxis_title="Receita (R$)",
            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Inter, sans-serif", size=12),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        return fig
    
    @app.callback(
        Output("sales-by-date-chart", "figure"),
        [Input("dashboard-data-store", "data")]
    )
    def update_sales_by_date_chart(data):
        """
        Atualiza gráfico de vendas por data.
        """
        if not data or "sales_by_date" not in data:
            # Dados de exemplo
            dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="M")
            sales = [12000, 15000, 18000, 16000, 20000, 22000, 19000, 25000, 28000, 26000, 30000, 32000]
            
            fig = go.Figure(data=[
                go.Scatter(
                    x=dates,
                    y=sales,
                    mode="lines+markers",
                    line=dict(color="#8B5CF6", width=3),
                    marker=dict(size=6, color="#8B5CF6")
                )
            ])
        else:
            # Dados reais
            sales_data = data["sales_by_date"]
            dates = pd.to_datetime(list(sales_data.keys()))
            sales = list(sales_data.values())
            
            fig = go.Figure(data=[
                go.Scatter(
                    x=dates,
                    y=sales,
                    mode="lines+markers",
                    line=dict(color="#8B5CF6", width=3),
                    marker=dict(size=6, color="#8B5CF6")
                )
            ])
        
        fig.update_layout(
            title="",
            xaxis_title="Data",
            yaxis_title="Vendas (R$)",
            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Inter, sans-serif", size=12),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        return fig
    
    @app.callback(
        Output("recurring-revenue-chart", "figure"),
        [Input("dashboard-data-store", "data"),
         Input("recurring-revenue-period", "value")]
    )
    def update_recurring_revenue_chart(data, period):
        """
        Atualiza gráfico de receita recorrente.
        """
        if not data or "recurring_revenue" not in data:
            # Dados de exemplo
            months = 12 if period == "12m" else (6 if period == "6m" else 24)
            dates = pd.date_range(start="2024-01-01", periods=months, freq="M")
            mrr = [15000, 16000, 17000, 16500, 18000, 19000, 18500, 20000, 21000, 20500, 22000, 23000][:months]
            
            fig = go.Figure(data=[
                go.Scatter(
                    x=dates,
                    y=mrr,
                    mode="lines+markers",
                    line=dict(color="#8B5CF6", width=3),
                    marker=dict(size=6, color="#8B5CF6"),
                    fill="tonexty"
                )
            ])
        else:
            # Dados reais
            recurring_data = data["recurring_revenue"]
            dates = pd.to_datetime(list(recurring_data.keys()))
            mrr = list(recurring_data.values())
            
            fig = go.Figure(data=[
                go.Scatter(
                    x=dates,
                    y=mrr,
                    mode="lines+markers",
                    line=dict(color="#8B5CF6", width=3),
                    marker=dict(size=6, color="#8B5CF6"),
                    fill="tonexty"
                )
            ])
        
        fig.update_layout(
            title="",
            xaxis_title="Data",
            yaxis_title="MRR (R$)",
            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Inter, sans-serif", size=12),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        return fig
    
    @app.callback(
        Output("churn-rate-chart", "figure"),
        [Input("dashboard-data-store", "data")]
    )
    def update_churn_rate_chart(data):
        """
        Atualiza gráfico de taxa de churn.
        """
        if not data or "churn_rate" not in data:
            # Dados de exemplo
            dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="M")
            churn = [5.2, 4.8, 5.5, 4.9, 5.1, 4.7, 5.3, 4.6, 5.0, 4.8, 4.9, 4.5]
            
            fig = go.Figure(data=[
                go.Scatter(
                    x=dates,
                    y=churn,
                    mode="lines+markers",
                    line=dict(color="#EF4444", width=3),
                    marker=dict(size=6, color="#EF4444")
                )
            ])
        else:
            # Dados reais
            churn_data = data["churn_rate"]
            dates = pd.to_datetime(list(churn_data.keys()))
            churn = list(churn_data.values())
            
            fig = go.Figure(data=[
                go.Scatter(
                    x=dates,
                    y=churn,
                    mode="lines+markers",
                    line=dict(color="#EF4444", width=3),
                    marker=dict(size=6, color="#EF4444")
                )
            ])
        
        fig.update_layout(
            title="",
            xaxis_title="Data",
            yaxis_title="Taxa de Churn (%)",
            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Inter, sans-serif", size=12),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        return fig
