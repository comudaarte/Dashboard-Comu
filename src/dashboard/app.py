"""
Aplicação Principal do Dashboard
===============================

Aplicação Dash principal que integra todos os componentes do dashboard.
"""

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from .layouts.main_layout import create_main_layout_responsive
from .callbacks import register_all_callbacks
from .auth_components import create_login_page, register_auth_callbacks
from .final_auth_layout import create_final_auth_layout, register_final_auth_callbacks


def create_dashboard_app():
    """
    Cria e configura a aplicação Dash do dashboard.
    
    Returns:
        dash.Dash: Aplicação configurada
    """
    # Cria a aplicação Dash
    app = dash.Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,  # Bootstrap para componentes
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",  # FontAwesome
            "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"  # Fonte Inter
        ],
        external_scripts=[
            "https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.24.1/plotly.min.js"
        ],
        suppress_callback_exceptions=True,
        title="Dashboard Comu - Métricas de Assinaturas",
        update_title="Carregando...",
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"},
            {"name": "description", "content": "Dashboard de métricas de assinaturas da Comunidade da Arte"},
            {"name": "author", "content": "Dashboard Comu Team"},
            {"property": "og:title", "content": "Dashboard Comu"},
            {"property": "og:description", "content": "Métricas de assinaturas em tempo real"},
            {"property": "og:type", "content": "website"}
        ]
    )
    
    # Configura o layout principal final
    app.layout = create_final_auth_layout()
    
    # Registra callbacks de autenticação final
    register_final_auth_callbacks(app)
    
    # Registra todos os callbacks
    register_all_callbacks(app)
    
    # Configurações adicionais
    app.config.suppress_callback_exceptions = True
    
    return app


def create_dashboard_app_with_config(config=None):
    """
    Cria aplicação Dash com configurações customizadas.
    
    Args:
        config (dict, optional): Configurações customizadas
    
    Returns:
        dash.Dash: Aplicação configurada
    """
    # Configurações padrão
    default_config = {
        "external_stylesheets": [
            dbc.themes.BOOTSTRAP,
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
            "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
        ],
        "external_scripts": [
            "https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.24.1/plotly.min.js"
        ],
        "suppress_callback_exceptions": True,
        "title": "Dashboard Comu - Métricas de Assinaturas",
        "update_title": "Carregando..."
    }
    
    # Mescla configurações
    if config:
        default_config.update(config)
    
    # Cria a aplicação
    app = dash.Dash(__name__, **default_config)
    
    # Configura o layout
    app.layout = create_main_layout_responsive()
    
    # Registra callbacks
    register_all_callbacks(app)
    
    return app


def run_dashboard_app(host="0.0.0.0", port=8050, debug=False):
    """
    Executa a aplicação do dashboard.
    
    Args:
        host (str): Host para executar
        port (int): Porta para executar
        debug (bool): Modo debug
    """
    app = create_dashboard_app()
    
    print(f"🚀 Iniciando Dashboard Comu...")
    print(f"📊 Acesse: http://{host}:{port}")
    print(f"🔧 Debug: {'Ativado' if debug else 'Desativado'}")
    
    app.run_server(
        host=host,
        port=port,
        debug=debug,
        dev_tools_hot_reload=debug
    )


if __name__ == "__main__":
    # Executa o dashboard
    run_dashboard_app(debug=True)