"""
Callbacks para o sistema de login
"""
import dash
from dash import callback, Input, Output, State, html
import dash_bootstrap_components as dbc
import requests

def register_login_callbacks(app):
    """Registra callbacks para o sistema de login"""
    
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
                
                # Sucesso - limpar alerta e armazenar token
                success_alert = dbc.Alert([
                    html.I(className="fas fa-check-circle me-2"),
                    "Login realizado com sucesso! Token salvo."
                ], color="success")
                
                return success_alert, token
            else:
                # Erro de credenciais
                error_alert = dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    "Usuário ou senha incorretos!"
                ], color="danger")
                return error_alert, dash.no_update
                
        except requests.exceptions.RequestException as e:
            # Erro de conexão
            error_alert = dbc.Alert([
                html.I(className="fas fa-wifi me-2"),
                "Erro de conexão. Verifique se a API está rodando."
            ], color="danger")
            return error_alert, dash.no_update
            
        except Exception as e:
            # Erro geral
            error_alert = dbc.Alert([
                html.I(className="fas fa-exclamation-circle me-2"),
                f"Erro inesperado: {str(e)}"
            ], color="danger")
            return error_alert, dash.no_update
