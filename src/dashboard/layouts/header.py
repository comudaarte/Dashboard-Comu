"""
Header do Dashboard
==================

Header roxo com logo da Comunidade da Arte e seletor de datas.
Design baseado nas screenshots de referência.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


def create_header():
    """
    Cria o header roxo com logo e seletor de datas.
    
    Returns:
        dbc.Navbar: Header responsivo com branding e controles
    """
    return dbc.Navbar(
        dbc.Container([
            # Logo (lado esquerdo)
            dbc.NavbarBrand([
                # Logo da empresa
                html.Img(
                    src="/assets/logo_comu.png",
                    style={
                        "height": "40px",
                        "width": "auto",
                        "maxWidth": "200px"
                    }
                )
            ], className="text-white"),
            
            # Seletor de datas (lado direito)
            dbc.Button([
                # Ícone de calendário
                html.I(
                    className="fas fa-calendar me-2",
                    style={"fontSize": "1rem"}
                ),
                
                # Texto do botão
                html.Span(
                    "Selecionar intervalo de datas",
                    style={"fontSize": "0.875rem"}
                )
            ], 
            id="date-picker-button",
            color="light", 
            className="text-primary border-0 shadow-sm",
            style={
                "borderRadius": "0.5rem",
                "fontWeight": "500",
                "padding": "0.5rem 1rem"
            })
        ]),
        
        # Estilo do navbar
        color="primary",
        dark=True,
        className="mb-4 shadow-sm",
        style={
            "backgroundColor": "#8B5CF6",  # Roxo principal
            "borderRadius": "0",
            "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
        }
    )


def create_date_picker_modal():
    """
    Cria modal para seleção de datas.
    
    Returns:
        dbc.Modal: Modal com seletor de datas
    """
    return dbc.Modal([
        dbc.ModalHeader([
            dbc.ModalTitle("Selecionar Período de Análise"),
            dbc.Button(
                html.I(className="fas fa-times"),
                id="close-date-modal",
                className="btn-close",
                n_clicks=0
            )
        ]),
        
        dbc.ModalBody([
            html.P(
                "Escolha o intervalo de datas para análise das métricas:",
                className="text-muted mb-3"
            ),
            
            # Seletor de datas
            dcc.DatePickerRange(
                id="date-range-picker",
                start_date_placeholder_text="Data Inicial",
                end_date_placeholder_text="Data Final",
                calendar_orientation="horizontal",
                clearable=True,
                className="w-100"
            ),
            
            # Botões de período rápido
            html.Div([
                html.P("Períodos rápidos:", className="text-muted mb-2"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Últimos 7 dias",
                            id="quick-7-days",
                            color="outline-primary",
                            size="sm",
                            className="w-100"
                        )
                    ], width=3),
                    
                    dbc.Col([
                        dbc.Button(
                            "Últimos 30 dias",
                            id="quick-30-days",
                            color="outline-primary",
                            size="sm",
                            className="w-100"
                        )
                    ], width=3),
                    
                    dbc.Col([
                        dbc.Button(
                            "Últimos 90 dias",
                            id="quick-90-days",
                            color="outline-primary",
                            size="sm",
                            className="w-100"
                        )
                    ], width=3),
                    
                    dbc.Col([
                        dbc.Button(
                            "Este ano",
                            id="quick-this-year",
                            color="outline-primary",
                            size="sm",
                            className="w-100"
                        )
                    ], width=3)
                ], className="g-2")
            ], className="mt-3")
        ]),
        
        dbc.ModalFooter([
            dbc.Button(
                "Cancelar",
                id="cancel-date-selection",
                color="secondary",
                outline=True
            ),
            dbc.Button(
                "Aplicar",
                id="apply-date-selection",
                color="primary"
            )
        ])
    ],
    id="date-picker-modal",
    is_open=False,
    size="lg",
    centered=True
    )


def create_header_with_date_picker():
    """
    Cria header completo com seletor de datas integrado.
    
    Returns:
        html.Div: Container com header e modal
    """
    return html.Div([
        create_header(),
        create_date_picker_modal()
    ])
