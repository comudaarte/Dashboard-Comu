"""
Layout básico de autenticação para o Dashboard
"""
import dash
from dash import html, dcc
from .simple_login import create_simple_login_page
from .layouts.main_layout import create_main_layout_responsive

def create_basic_auth_layout():
    """Cria layout básico que sempre mostra a tela de login"""
    return html.Div([
        # Store para armazenar token
        dcc.Store(id='auth-token', storage_type='local'),
        
        # URL para navegação
        dcc.Location(id='url', refresh=False),
        
        # Container principal - sempre mostra login por enquanto
        create_simple_login_page()
    ])
