"""
Layout final de autenticação sem conflitos
"""
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from .simple_login import create_simple_login_page
from .layouts.main_layout import create_main_layout_responsive

def create_final_auth_layout():
    """Cria layout final sem conflitos"""
    return html.Div([
        # Store para armazenar token
        dcc.Store(id='auth-token', storage_type='local'),
        
        # URL para navegação
        dcc.Location(id='url', refresh=False),
        
        # Container principal
        html.Div(id='page-content')
    ])

def register_final_auth_callbacks(app):
    """Registra callbacks finais sem conflitos"""
    
    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')],
        [State('auth-token', 'data')]
    )
    def display_page(pathname, token):
        """Determina qual página mostrar"""
        if pathname == '/login':
            return create_simple_login_page()
        elif pathname == '/dashboard' and token:
            return create_main_layout_responsive()
        elif token:
            return create_main_layout_responsive()
        else:
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
         Output('auth-token', 'data')],
        [Input('login-button', 'n_clicks')],
        [State('login-username', 'value'),
         State('login-password', 'value')]
    )
    def handle_login(n_clicks, username, password):
        """Manipula o processo de login"""
        if n_clicks == 0:
            return dash.no_update, dash.no_update
        
        if not username or not password:
            return dbc.Alert("Por favor, preencha todos os campos!", color="warning"), dash.no_update
        
        try:
            import requests
            
            response = requests.post(
                "http://localhost:8000/auth/login",
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                
                success_alert = dbc.Alert([
                    html.I(className="fas fa-check-circle me-2"),
                    "Login realizado com sucesso! Redirecionando..."
                ], color="success")
                
                return success_alert, token
            else:
                error_alert = dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    "Usuário ou senha incorretos!"
                ], color="danger")
                return error_alert, dash.no_update
                
        except Exception as e:
            error_alert = dbc.Alert([
                html.I(className="fas fa-exclamation-circle me-2"),
                f"Erro: {str(e)}"
            ], color="danger")
            return error_alert, dash.no_update
