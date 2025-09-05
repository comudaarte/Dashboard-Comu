"""
Layout de autenticação para o Dashboard
"""
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from .auth_components import create_login_page, create_navbar
from .layouts.main_layout import create_main_layout_responsive

def create_auth_layout():
    """Cria layout principal com autenticação"""
    return html.Div([
        # Store para armazenar token e informações do usuário
        dcc.Store(id='auth-token', storage_type='local'),
        dcc.Store(id='user-info', storage_type='local'),
        
        # URL para navegação
        dcc.Location(id='url', refresh=False),
        
        # Container principal
        html.Div(id='page-content', className='min-vh-100')
    ])

def register_auth_layout_callbacks(app):
    """Registra callbacks para o layout de autenticação"""
    
    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')],
        [State('auth-token', 'data')]
    )
    def display_page(pathname, token):
        """Determina qual página mostrar baseado na autenticação"""
        if pathname == '/login':
            return create_login_page()
        elif token:
            # Usuário autenticado - mostrar dashboard
            return html.Div([
                create_navbar(),
                create_main_layout_responsive()
            ])
        else:
            # Usuário não autenticado - redirecionar para login
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
        [Output('auth-token', 'data'),
         Output('user-info', 'data')],
        [Input('login-button', 'n_clicks')],
        [State('login-username', 'value'),
         State('login-password', 'value')]
    )
    def handle_login(n_clicks, username, password):
        """Manipula o processo de login"""
        if n_clicks == 0:
            return dash.no_update, dash.no_update
        
        if not username or not password:
            return dash.no_update, dash.no_update
        
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
                
                # Obter informações do usuário
                user_response = requests.get(
                    "http://localhost:8000/auth/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    return token, user_data
                else:
                    return dash.no_update, dash.no_update
            else:
                return dash.no_update, dash.no_update
                
        except Exception as e:
            print(f"Erro no login: {e}")
            return dash.no_update, dash.no_update
    
    @app.callback(
        [Output('auth-token', 'data', allow_duplicate=True),
         Output('user-info', 'data', allow_duplicate=True)],
        [Input('logout-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def handle_logout(n_clicks):
        """Manipula o logout"""
        if n_clicks:
            return None, None
        return dash.no_update, dash.no_update
    
    @app.callback(
        Output('navbar-username', 'children'),
        [Input('user-info', 'data')]
    )
    def update_navbar_username(user_info):
        """Atualiza o nome do usuário na navbar"""
        if user_info:
            return user_info.get('username', 'Usuário')
        return 'Usuário'
