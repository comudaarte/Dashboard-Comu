"""
Layout integrado de autenticação com redirecionamento funcional
"""
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from .simple_login import create_simple_login_page
from .layouts.main_layout import create_main_layout_responsive

def create_integrated_auth_layout():
    """Cria layout integrado com autenticação completa"""
    return html.Div([
        # Store para armazenar token
        dcc.Store(id='auth-token', storage_type='local'),
        
        # URL para navegação
        dcc.Location(id='url', refresh=False),
        
        # Container principal
        html.Div(id='page-content')
    ])

def register_integrated_auth_callbacks(app):
    """Registra callbacks integrados para autenticação"""
    
    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')],
        [State('auth-token', 'data')]
    )
    def display_page(pathname, token):
        """Determina qual página mostrar baseado na rota e autenticação"""
        if pathname == '/login':
            return create_simple_login_page()
        elif pathname == '/dashboard' and token:
            # Usuário autenticado - mostrar dashboard
            return create_main_layout_responsive()
        elif token:
            # Usuário autenticado mas em rota inválida - redirecionar para dashboard
            return create_main_layout_responsive()
        else:
            # Usuário não autenticado - mostrar login
            return create_simple_login_page()
    
    @app.callback(
        Output('url', 'pathname'),
        [Input('auth-token', 'data')]
    )
    def redirect_based_on_auth(token):
        """Redireciona baseado no status de autenticação"""
        if not token:
            return '/login'
        return '/dashboard'
    
    @app.callback(
        [Output('login-alert', 'children'),
         Output('auth-token', 'data'),
         Output('url', 'pathname')],
        [Input('login-button', 'n_clicks')],
        [State('login-username', 'value'),
         State('login-password', 'value')]
    )
    def handle_login(n_clicks, username, password):
        """Manipula o processo de login com redirecionamento"""
        if n_clicks == 0:
            return dash.no_update, dash.no_update, dash.no_update
        
        if not username or not password:
            return dbc.Alert("Por favor, preencha todos os campos!", color="warning"), dash.no_update, dash.no_update
        
        try:
            import requests
            
            # Fazer requisição para API de login
            response = requests.post(
                "http://localhost:8000/auth/login",
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                
                # Sucesso - limpar alerta, armazenar token e redirecionar
                success_alert = dbc.Alert([
                    html.I(className="fas fa-check-circle me-2"),
                    "Login realizado com sucesso! Redirecionando..."
                ], color="success")
                
                return success_alert, token, "/dashboard"
            else:
                # Erro de credenciais
                error_alert = dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    "Usuário ou senha incorretos!"
                ], color="danger")
                return error_alert, dash.no_update, dash.no_update
                
        except requests.exceptions.RequestException as e:
            # Erro de conexão
            error_alert = dbc.Alert([
                html.I(className="fas fa-wifi me-2"),
                "Erro de conexão. Verifique se a API está rodando."
            ], color="danger")
            return error_alert, dash.no_update, dash.no_update
            
        except Exception as e:
            # Erro geral
            error_alert = dbc.Alert([
                html.I(className="fas fa-exclamation-circle me-2"),
                f"Erro inesperado: {str(e)}"
            ], color="danger")
            return error_alert, dash.no_update, dash.no_update
