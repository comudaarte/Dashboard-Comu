"""
Seção de Métricas de Performance
===============================

Seção com métricas de performance baseada na segunda screenshot.
Layout: 5 métricas pequenas em cima + 3 métricas grandes com badges embaixo.
"""

import dash_bootstrap_components as dbc
from dash import html


def create_performance_metrics_section():
    """
    Cria a seção de métricas de performance conforme screenshot.
    
    Returns:
        dbc.Container: Container com métricas de performance
    """
    return dbc.Container([
        # Título da seção
        html.Div([
            html.H4(
                "Métricas de Performance",
                className="text-dark fw-bold mb-4",
                style={"fontSize": "1.5rem", "textAlign": "center"}
            )
        ], className="mb-4"),
        
        # Primeira linha: 5 métricas pequenas (centralizadas)
        html.Div([
            dbc.Row([
                # ARPU
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("ARPU", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                            html.H4("1 223", className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                        ], className="p-3")
                    ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "minHeight": "80px"})
                ], width=6, md=4, lg=2, className="mb-3"),
                
                # CAC Geral
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("CAC Geral", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                            html.H4("1 223", className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                        ], className="p-3")
                    ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "minHeight": "80px"})
                ], width=6, md=4, lg=2, className="mb-3"),
                
                # CPL Geral
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("CPL Geral", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                            html.H4("1 223", className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                        ], className="p-3")
                    ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "minHeight": "80px"})
                ], width=6, md=4, lg=2, className="mb-3"),
                
                # NPS Geral
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("NPS Geral", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                            html.H4("1 223", className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                        ], className="p-3")
                    ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "minHeight": "80px"})
                ], width=6, md=4, lg=2, className="mb-3"),
                
                # Receita média mensal
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Receita média mensal", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                            html.H4("1 223", className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                        ], className="p-3")
                    ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "minHeight": "80px"})
                ], width=6, md=4, lg=2, className="mb-3")
            ], className="justify-content-center g-3")
        ], className="mb-4"),
        
        # Segunda linha: 3 métricas grandes com badges
        dbc.Row([
            # Receita Anual da Empresa
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Receita Anual da Empresa", className="text-muted mb-3", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H3("R$ 1 223,00", className="fw-bold text-dark mb-3", style={"fontSize": "2rem", "textAlign": "center"}),
                        # Badge de crescimento
                        html.Div([
                            html.Span([
                                html.I(className="fas fa-arrow-up me-1", style={"fontSize": "0.75rem", "color": "white"}), 
                                "7,9%"
                            ], 
                            className="badge", 
                            style={
                                "backgroundColor": "#8B5CF6", 
                                "color": "white", 
                                "fontSize": "0.75rem", 
                                "fontWeight": "500", 
                                "padding": "6px 12px", 
                                "borderRadius": "12px"
                            })
                        ], className="text-center")
                    ], className="p-4")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "minHeight": "140px"})
            ], width=12, lg=4, className="mb-3"),
            
            # ROI Geral
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("ROI Geral", className="text-muted mb-3", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H3("122 300,00%", className="fw-bold text-dark mb-3", style={"fontSize": "2rem", "textAlign": "center"}),
                        # Badge de crescimento
                        html.Div([
                            html.Span([
                                html.I(className="fas fa-arrow-up me-1", style={"fontSize": "0.75rem", "color": "white"}), 
                                "7,9%"
                            ], 
                            className="badge", 
                            style={
                                "backgroundColor": "#8B5CF6", 
                                "color": "white", 
                                "fontSize": "0.75rem", 
                                "fontWeight": "500", 
                                "padding": "6px 12px", 
                                "borderRadius": "12px"
                            })
                        ], className="text-center")
                    ], className="p-4")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "minHeight": "140px"})
            ], width=12, lg=4, className="mb-3"),
            
            # Margem de Lucro
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Margem de Lucro", className="text-muted mb-3", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H3("122 300,00%", className="fw-bold text-dark mb-3", style={"fontSize": "2rem", "textAlign": "center"}),
                        # Badge de crescimento
                        html.Div([
                            html.Span([
                                html.I(className="fas fa-arrow-up me-1", style={"fontSize": "0.75rem", "color": "white"}), 
                                "7,9%"
                            ], 
                            className="badge", 
                            style={
                                "backgroundColor": "#8B5CF6", 
                                "color": "white", 
                                "fontSize": "0.75rem", 
                                "fontWeight": "500", 
                                "padding": "6px 12px", 
                                "borderRadius": "12px"
                            })
                        ], className="text-center")
                    ], className="p-4")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "minHeight": "140px"})
            ], width=12, lg=4, className="mb-3")
        ], className="justify-content-center")
        
    ], fluid=True, className="py-4")


def create_performance_metrics_section_with_data(performance_data):
    """
    Cria seção de métricas de performance com dados reais.
    
    Args:
        performance_data (dict): Dados das métricas de performance
    
    Returns:
        dbc.Container: Container com métricas populadas
    """
    return dbc.Container([
        # Título da seção
        html.Div([
            html.H4(
                "Métricas de Performance",
                className="text-dark fw-bold mb-4",
                style={"fontSize": "1.5rem", "textAlign": "center"}
            )
        ], className="mb-4"),
        
        # Primeira linha: 5 métricas pequenas com dados (centralizadas)
        html.Div([
            dbc.Row([
                # ARPU
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("ARPU", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                            html.H4(performance_data.get('arpu', '1 223'), className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                        ], className="p-3")
                    ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "minHeight": "80px"})
                ], width=6, md=4, lg=2, className="mb-3"),
                
                # CAC Geral
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("CAC Geral", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                            html.H4(performance_data.get('cac_geral', '1 223'), className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                        ], className="p-3")
                    ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "minHeight": "80px"})
                ], width=6, md=4, lg=2, className="mb-3"),
                
                # CPL Geral
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("CPL Geral", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                            html.H4(performance_data.get('cpl_geral', '1 223'), className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                        ], className="p-3")
                    ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "minHeight": "80px"})
                ], width=6, md=4, lg=2, className="mb-3"),
                
                # NPS Geral
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("NPS Geral", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                            html.H4(performance_data.get('nps_geral', '1 223'), className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                        ], className="p-3")
                    ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "minHeight": "80px"})
                ], width=6, md=4, lg=2, className="mb-3"),
                
                # Receita média mensal
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Receita média mensal", className="text-muted mb-2", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                            html.H4(performance_data.get('receita_media_mensal', '1 223'), className="fw-bold text-dark mb-0", style={"fontSize": "1.5rem", "textAlign": "center"})
                        ], className="p-3")
                    ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "minHeight": "80px"})
                ], width=6, md=4, lg=2, className="mb-3")
            ], className="justify-content-center g-3")
        ], className="mb-4"),
        
        # Segunda linha: 3 métricas grandes com badges e dados
        dbc.Row([
            # Receita Anual da Empresa
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Receita Anual da Empresa", className="text-muted mb-3", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H3(performance_data.get('receita_anual', 'R$ 1 223,00'), className="fw-bold text-dark mb-3", style={"fontSize": "2rem", "textAlign": "center"}),
                        # Badge de crescimento
                        html.Div([
                            html.Span([
                                html.I(className="fas fa-arrow-up me-1", style={"fontSize": "0.75rem", "color": "white"}), 
                                performance_data.get('receita_anual_growth', '7,9%')
                            ], 
                            className="badge", 
                            style={
                                "backgroundColor": "#8B5CF6", 
                                "color": "white", 
                                "fontSize": "0.75rem", 
                                "fontWeight": "500", 
                                "padding": "6px 12px", 
                                "borderRadius": "12px"
                            })
                        ], className="text-center")
                    ], className="p-4")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "minHeight": "140px"})
            ], width=12, lg=4, className="mb-3"),
            
            # ROI Geral
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("ROI Geral", className="text-muted mb-3", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H3(performance_data.get('roi_geral', '122 300,00%'), className="fw-bold text-dark mb-3", style={"fontSize": "2rem", "textAlign": "center"}),
                        # Badge de crescimento
                        html.Div([
                            html.Span([
                                html.I(className="fas fa-arrow-up me-1", style={"fontSize": "0.75rem", "color": "white"}), 
                                performance_data.get('roi_geral_growth', '7,9%')
                            ], 
                            className="badge", 
                            style={
                                "backgroundColor": "#8B5CF6", 
                                "color": "white", 
                                "fontSize": "0.75rem", 
                                "fontWeight": "500", 
                                "padding": "6px 12px", 
                                "borderRadius": "12px"
                            })
                        ], className="text-center")
                    ], className="p-4")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "minHeight": "140px"})
            ], width=12, lg=4, className="mb-3"),
            
            # Margem de Lucro
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Margem de Lucro", className="text-muted mb-3", style={"fontSize": "0.875rem", "fontWeight": "400", "textAlign": "center"}),
                        html.H3(performance_data.get('margem_lucro', '122 300,00%'), className="fw-bold text-dark mb-3", style={"fontSize": "2rem", "textAlign": "center"}),
                        # Badge de crescimento
                        html.Div([
                            html.Span([
                                html.I(className="fas fa-arrow-up me-1", style={"fontSize": "0.75rem", "color": "white"}), 
                                performance_data.get('margem_lucro_growth', '7,9%')
                            ], 
                            className="badge", 
                            style={
                                "backgroundColor": "#8B5CF6", 
                                "color": "white", 
                                "fontSize": "0.75rem", 
                                "fontWeight": "500", 
                                "padding": "6px 12px", 
                                "borderRadius": "12px"
                            })
                        ], className="text-center")
                    ], className="p-4")
                ], className="h-100 border-0 shadow-sm", style={"borderRadius": "12px", "minHeight": "140px"})
            ], width=12, lg=4, className="mb-3")
        ], className="justify-content-center")
        
    ], fluid=True, className="py-4")
