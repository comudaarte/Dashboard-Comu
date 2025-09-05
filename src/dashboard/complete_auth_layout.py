"""
Layout completo de autenticação com redirecionamento
"""
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from .simple_login import create_simple_login_page
from .layouts.main_layout import create_main_layout_responsive

def create_complete_auth_layout():
    """Cria layout completo com autenticação e redirecionamento"""
    return html.Div([
        # Store para armazenar token
        dcc.Store(id='auth-token', storage_type='local'),
        
        # URL para navegação
        dcc.Location(id='url', refresh=False),
        
        # Container principal
        html.Div(id='page-content')
    ])

def register_complete_auth_callbacks(app):
    """Registra callbacks para o sistema completo de autenticação"""
    
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
