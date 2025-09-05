"""
Layout simples de autenticação para o Dashboard
"""
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from .auth_components import create_login_page
from .layouts.main_layout import create_main_layout_responsive

def create_simple_auth_layout():
    """Cria layout simples com autenticação"""
    return html.Div([
        # Store para armazenar token
        dcc.Store(id='auth-token', storage_type='local'),
        
        # URL para navegação
        dcc.Location(id='url', refresh=False),
        
        # Container principal
        html.Div(id='page-content')
    ])

def register_simple_auth_callbacks(app):
    """Registra callbacks simples para autenticação"""
    
    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')],
        [State('auth-token', 'data')]
    )
    def display_page(pathname, token):
        """Determina qual página mostrar"""
        if pathname == '/login':
            return create_login_page()
        elif token:
            # Usuário autenticado - mostrar dashboard
            return create_main_layout_responsive()
        else:
            # Usuário não autenticado - mostrar login
            return create_login_page()
    
    @app.callback(
        Output('url', 'pathname'),
        [Input('auth-token', 'data')]
    )
    def redirect_based_on_auth(token):
        """Redireciona baseado no status de autenticação"""
        if not token:
            return '/login'
        return '/'
    
    @app.callback(
        Output('auth-token', 'data'),
        [Input('login-button', 'n_clicks')],
        [State('login-username', 'value'),
         State('login-password', 'value')]
    )
    def handle_login(n_clicks, username, password):
        """Manipula o processo de login"""
        if n_clicks == 0:
            return dash.no_update
        
        if not username or not password:
            return dash.no_update
        
        try:
            import requests
            
            # Fazer requisição para API de login
            response = requests.post(
                "http://localhost:8000/auth/login",
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                return token
            else:
                return dash.no_update
                
        except Exception as e:
            print(f"Erro no login: {e}")
            return dash.no_update
