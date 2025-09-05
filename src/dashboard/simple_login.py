"""
Componente de login simples para o Dashboard
"""
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime

def create_simple_login_form():
    """Cria formulário de login simples"""
    return dbc.Card([
        dbc.CardHeader([
            html.H4("🔐 Login - Dashboard Comu", className="text-center mb-0")
        ]),
        dbc.CardBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Usuário", html_for="login-username"),
                        dbc.Input(
                            id="login-username",
                            type="text",
                            placeholder="Digite seu usuário",
                            className="mb-3"
                        )
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Senha", html_for="login-password"),
                        dbc.Input(
                            id="login-password",
                            type="password",
                            placeholder="Digite sua senha",
                            className="mb-3"
                        )
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Entrar",
                            id="login-button",
                            color="primary",
                            className="w-100 mb-3",
                            n_clicks=0
                        )
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Div(id="login-alert", className="mb-3")
                    ])
                ])
            ])
        ]),
        dbc.CardFooter([
            html.Small([
                "Dashboard Comu - Sistema de Métricas",
                html.Br(),
                "Versão 1.0 - " + datetime.now().strftime("%Y")
            ], className="text-muted text-center")
        ])
    ], className="shadow")

def create_simple_login_page():
    """Cria página de login simples"""
    return html.Div([
        # Container principal
        html.Div([
            dbc.Row([
                dbc.Col([
                    create_simple_login_form()
                ], width=12, className="d-flex justify-content-center")
            ])
        ], className="min-vh-100 d-flex align-items-center justify-content-center", 
           style={"background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"})
    ])
