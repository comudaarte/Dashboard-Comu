"""
Componentes de autenticação para o Dashboard Dash
"""
import dash
from dash import dcc, html, Input, Output, State, callback, clientside_callback
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import requests
import json

def create_login_form():
    """Cria formulário de login"""
    return dbc.Card([
        dbc.CardHeader([
            html.H4("🔐 Login - Dashboard Comu", className="text-center mb-0")
        ]),
        dbc.CardBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Usuário ou Email", html_for="login-username"),
                        dbc.Input(
                            id="login-username",
                            type="text",
                            placeholder="Digite seu usuário ou email",
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
    ], className="shadow-lg")

def create_login_page():
    """Cria página completa de login"""
    return html.Div([
        # CSS personalizado
        html.Link(
            rel="stylesheet",
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
        ),
        # CSS personalizado via style tag
        html.Div([
            html.Style("""
                body {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }
                .login-container {
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }
                .login-card {
                    max-width: 400px;
                    width: 100%;
                }
                .login-header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border-radius: 10px 10px 0 0;
                }
                .login-button {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border: none;
                    border-radius: 25px;
                    padding: 12px;
                    font-weight: 600;
                    transition: all 0.3s ease;
                }
                .login-button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }
                .form-control {
                    border-radius: 25px;
                    border: 2px solid #e9ecef;
                    padding: 12px 20px;
                    transition: all 0.3s ease;
                }
                .form-control:focus {
                    border-color: #667eea;
                    box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
                }
                .alert {
                    border-radius: 25px;
                    border: none;
                }
            """)
        ], style={"display": "none"}),
        
        # Container principal
        html.Div([
            dbc.Row([
                dbc.Col([
                    create_login_form()
                ], width=12, className="d-flex justify-content-center")
            ])
        ], className="login-container")
    ])

def create_navbar():
    """Cria navbar com informações do usuário"""
    return dbc.Navbar([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.A([
                        html.I(className="fas fa-chart-line me-2"),
                        "Dashboard Comu"
                    ], href="/", className="navbar-brand text-white")
                ], width=6),
                dbc.Col([
                    dbc.Nav([
                        dbc.NavItem([
                            dbc.NavLink([
                                html.I(className="fas fa-user me-2"),
                                html.Span(id="navbar-username", children="Usuário")
                            ], href="#", className="text-white")
                        ]),
                        dbc.NavItem([
                            dbc.Button([
                                html.I(className="fas fa-sign-out-alt me-2"),
                                "Sair"
                            ], id="logout-button", color="outline-light", size="sm", className="ms-2")
                        ])
                    ], className="ms-auto")
                ], width=6)
            ], className="w-100")
        ], fluid=True)
    ], color="primary", dark=True, className="mb-4")

def create_permission_alert(required_role="viewer"):
    """Cria alerta de permissão insuficiente"""
    return dbc.Alert([
        html.H4("🚫 Acesso Negado", className="alert-heading"),
        html.P(f"Você não tem permissão para acessar esta funcionalidade."),
        html.P(f"Role necessário: {required_role.upper()}"),
        html.Hr(),
        html.P([
            "Entre em contato com o administrador para solicitar acesso ou ",
            html.A("volte ao dashboard", href="/", className="alert-link")
        ])
    ], color="danger", className="text-center")

# Callbacks para autenticação
def register_auth_callbacks(app):
    """Registra callbacks de autenticação"""
    
    @app.callback(
        [Output("login-alert", "children"),
         Output("login-username", "value"),
         Output("login-password", "value")],
        [Input("login-button", "n_clicks")],
        [State("login-username", "value"),
         State("login-password", "value")]
    )
    def handle_login(n_clicks, username, password):
        """Manipula tentativa de login"""
        if n_clicks == 0:
            return "", "", ""
        
        if not username or not password:
            return dbc.Alert("Por favor, preencha todos os campos.", color="warning"), username, password
        
        try:
            # Fazer requisição para API de login
            response = requests.post(
                "http://localhost:8000/auth/login",
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                # Armazenar token no localStorage
                return dbc.Alert("Login realizado com sucesso! Redirecionando...", color="success"), "", ""
            else:
                error_data = response.json()
                return dbc.Alert(f"Erro no login: {error_data.get('detail', 'Credenciais inválidas')}", color="danger"), username, ""
                
        except Exception as e:
            return dbc.Alert(f"Erro de conexão: {str(e)}", color="danger"), username, password
    
    @app.callback(
        Output("url", "pathname"),
        [Input("login-alert", "children")],
        prevent_initial_call=True
    )
    def redirect_after_login(alert_children):
        """Redireciona após login bem-sucedido"""
        if alert_children and "sucesso" in str(alert_children).lower():
            return "/"
        return dash.no_update

# Função para verificar autenticação
def check_auth():
    """Verifica se usuário está autenticado"""
    try:
        # Verificar se há token no localStorage
        # Esta verificação será feita via JavaScript
        return True
    except:
        return False

# Função para obter informações do usuário
def get_user_info():
    """Obtém informações do usuário atual"""
    try:
        # Fazer requisição para API
        response = requests.get(
            "http://localhost:8000/auth/me",
            headers={"Authorization": "Bearer " + "token_aqui"}  # Token será obtido do localStorage
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# Função para fazer logout
def logout():
    """Faz logout do usuário"""
    try:
        # Fazer requisição para API
        response = requests.post(
            "http://localhost:8000/auth/logout",
            headers={"Authorization": "Bearer " + "token_aqui"}  # Token será obtido do localStorage
        )
        
        # Limpar localStorage
        # Isso será feito via JavaScript
        
        return True
    except:
        return False
