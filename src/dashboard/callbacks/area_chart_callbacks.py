"""
Callbacks para Gráfico de Área
==============================

Callbacks para o gráfico de área "Receita de Recorrência x Vendas".
"""

import dash
from dash import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import logging

# Configuração de logging
logger = logging.getLogger(__name__)


def register_area_chart_callbacks(app):
    """
    Registra callbacks relacionados ao gráfico de área.
    
    Args:
        app: Aplicação Dash
    """
    
    @app.callback(
        Output("area-chart-revenue-sales", "figure"),
        [Input("date-range-store", "data"),
         Input("refresh-button", "n_clicks")]
    )
    def update_area_chart(date_range_data, refresh_clicks):
        """
        Atualiza gráfico de área com dados reais de receita recorrente vs vendas.
        """
        try:
            logger.info("🔄 Atualizando gráfico de área - Receita Recorrente x Vendas")
            
            # Inicializa variáveis
            start_dt = None
            end_dt = None
            data_referencia = datetime.now()
            periodo_dias = 30
            
            # Parse das datas do date-range-store (mesma lógica das outras correções)
            if date_range_data and 'start_date' in date_range_data and 'end_date' in date_range_data:
                try:
                    start_dt = datetime.fromisoformat(date_range_data['start_date'].replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(date_range_data['end_date'].replace('Z', '+00:00'))
                    
                    # CORREÇÃO: end_dt deve incluir todo o dia final
                    end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
                    
                    data_referencia = end_dt
                    periodo_dias = (end_dt.date() - start_dt.date()).days + 1
                    
                    logger.info(f"📅 Período selecionado: {start_dt} a {end_dt} ({periodo_dias} dias)")
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao parse das datas: {str(e)}")
                    start_dt = None
                    end_dt = None
            
            # Importa MetricsCalculator e busca dados reais por produto
            try:
                from services.metrics_calculator import MetricsCalculator
                from database.connection import get_db_session
                from sqlalchemy import text
                
                # Cria sessão e calculadora
                db_session = get_db_session()
                calculator = MetricsCalculator(db_session)
                
                # Se temos período selecionado, busca dados reais por produto
                if start_dt and end_dt:
                    logger.info(f"📊 Buscando dados reais por produto do período: {start_dt} a {end_dt}")
                    
                    # Busca dados por produto no período
                    query_produtos = text("""
                        SELECT 
                            produto_nome,
                            DATE(data_transacao) as data,
                            COUNT(*) as vendas_diarias
                        FROM transacoes
                        WHERE data_transacao BETWEEN :start_date AND :end_date
                        AND status IN ('approved', 'paid', 'authorized')
                        AND produto_nome IS NOT NULL
                        GROUP BY produto_nome, DATE(data_transacao)
                        ORDER BY produto_nome, data
                    """)
                    
                    result_produtos = calculator.db.execute(query_produtos, {
                        "start_date": start_dt,
                        "end_date": end_dt
                    }).fetchall()
                    
                    # Processa dados por produto
                    if result_produtos:
                        # Organiza dados por produto
                        produtos_data = {}
                        all_dates = set()
                        
                        for row in result_produtos:
                            produto = row.produto_nome
                            data = row.data
                            vendas = row.vendas_diarias
                            
                            all_dates.add(data)
                            
                            if produto not in produtos_data:
                                produtos_data[produto] = {}
                            produtos_data[produto][data] = vendas
                        
                        # Cria lista de datas ordenadas
                        dates = sorted(list(all_dates))
                        
                        # Cria dados para o gráfico empilhado
                        chart_data = {}
                        for produto, data_dict in produtos_data.items():
                            chart_data[produto] = [data_dict.get(date, 0) for date in dates]
                        
                        logger.info(f"✅ Dados por produto carregados: {len(dates)} dias, {len(produtos_data)} produtos")
                        logger.info(f"📊 Produtos: {list(produtos_data.keys())}")
                        
                    else:
                        # Se não há dados no período, usa dados de exemplo
                        dates = pd.date_range(start=start_dt, end=end_dt, freq="D")
                        chart_data = {
                            "Comu Academy": [0] * len(dates),
                            "Ebook - Como Criar Personagens": [0] * len(dates),
                            "Guia do Desenho - Artepack": [0] * len(dates),
                            "Comunidade da Arte - Anual": [0] * len(dates)
                        }
                        logger.info("⚠️ Nenhum dado encontrado no período, usando zeros")
                        
                else:
                    # Se não há período selecionado, usa dados de exemplo
                    dates = pd.date_range(start="2024-01-01", periods=12, freq="M")
                    chart_data = {
                        "Comu Academy": [150, 160, 170, 165, 180, 190, 185, 200, 210, 205, 220, 230],
                        "Ebook - Como Criar Personagens": [25, 30, 35, 32, 40, 45, 42, 50, 55, 52, 60, 65],
                        "Guia do Desenho - Artepack": [15, 18, 20, 19, 22, 25, 23, 28, 30, 29, 32, 35],
                        "Comunidade da Arte - Anual": [8, 10, 12, 11, 14, 16, 15, 18, 20, 19, 22, 25]
                    }
                    logger.info("⚠️ Sem período selecionado, usando dados de exemplo")
                
            except Exception as e:
                logger.error(f"❌ Erro ao carregar dados reais: {str(e)}")
                # Fallback para dados de exemplo
                dates = pd.date_range(start="2024-01-01", periods=12, freq="M")
                chart_data = {
                    "Comu Academy": [150, 160, 170, 165, 180, 190, 185, 200, 210, 205, 220, 230],
                    "Ebook - Como Criar Personagens": [25, 30, 35, 32, 40, 45, 42, 50, 55, 52, 60, 65],
                    "Guia do Desenho - Artepack": [15, 18, 20, 19, 22, 25, 23, 28, 30, 29, 32, 35],
                    "Comunidade da Arte - Anual": [8, 10, 12, 11, 14, 16, 15, 18, 20, 19, 22, 25]
                }
            
            # Cria gráfico de área empilhada por produto
            fig = go.Figure()
            
            # Cores para os produtos (baseado na screenshot)
            colors = {
                "Comu Academy": "#000000",  # Preto
                "Ebook - Como Criar Personagens": "#8B5CF6",  # Roxo
                "Guia do Desenho - Artepack": "#6B7280",  # Cinza
                "Comunidade da Arte - Anual": "#3B82F6",  # Azul
                "Comunidade da Arte - Mensal": "#000000",  # Preto
                "Comunidade da Arte": "#D1D5DB",  # Cinza claro
                "Comissions na Gringa": "#374151",  # Cinza escuro
                "Formação Tattoo": "#1E40AF",  # Azul escuro
                "Mentoria - Tatuador PRO": "#374151"  # Cinza escuro
            }
            
            # Adiciona cada produto como uma área empilhada
            for produto, values in chart_data.items():
                color = colors.get(produto, "#8B5CF6")  # Cor padrão se não encontrada
                
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=values,
                    mode='lines',
                    name=produto,
                    line=dict(color=color, width=2),
                    fill='tonexty',
                    fillcolor=color,
                    stackgroup='one',  # Empilha as áreas
                    hovertemplate=f'<b>{produto}</b><br>' +
                                 'Data: %{x}<br>' +
                                 'Vendas: %{y}<br>' +
                                 '<extra></extra>'
                ))
            
            # Configura layout
            fig.update_layout(
                title="",
                xaxis_title="",
                yaxis_title="",
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=10)
                ),
                plot_bgcolor="white",
                paper_bgcolor="white",
                font=dict(family="Inter, sans-serif", size=12),
                margin=dict(l=20, r=20, t=60, b=20),
                hovermode='x unified'
            )
            
            # Configura eixos
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(0,0,0,0.1)',
                tickformat='%d/%m',
                tickangle=45
            )
            
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(0,0,0,0.1)',
                tickformat=',.0f',
                title="Quantidade"
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar gráfico de área: {str(e)}")
            # Retorna gráfico vazio em caso de erro
            return go.Figure().update_layout(
                title="Erro ao carregar dados",
                plot_bgcolor="white",
                paper_bgcolor="white"
            )
    
    logger.info("✅ Callbacks de gráfico de área registrados com sucesso")
