#!/usr/bin/env python3
"""
Aplicação Principal - Dashboard Comu
===================================

Servidor principal que executa tanto a API FastAPI quanto o Dashboard Dash.
"""

import asyncio
import threading
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Importa a API de webhooks
from .Api.webhooks import app as webhook_app

# Setup de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_main_app():
    """
    Cria a aplicação principal combinando API e Dashboard.
    """
    # Aplicação FastAPI principal
    main_app = FastAPI(
        title="Dashboard Comu - Sistema Completo",
        description="API de Webhooks + Dashboard Visual",
        version="1.0.0"
    )
    
    # Adiciona CORS
    main_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Monta a API de webhooks
    main_app.mount("/api", webhook_app)
    
    # Endpoint de saúde principal
    @main_app.get("/")
    def root():
        return {
            "service": "Dashboard Comu",
            "status": "online",
            "endpoints": {
                "api": "/api",
                "health": "/api/health",
                "dashboard": "http://localhost:8052"
            }
        }
    
    return main_app

def start_dashboard():
    """
    Inicia o dashboard Dash em thread separada.
    """
    try:
        logger.info("🚀 Iniciando Dashboard Dash...")
        
        from .dashboard.app import create_dashboard_app
        
        dashboard_app = create_dashboard_app()
        
        # Executa o dashboard em thread separada
        dashboard_app.run_server(
            host="0.0.0.0",
            port=8052,
            debug=False,
            dev_tools_hot_reload=False,
            dev_tools_ui=False,
            dev_tools_serve_dev_bundles=False
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar dashboard: {e}")

def start_api_server():
    """
    Inicia o servidor FastAPI.
    """
    logger.info("🚀 Iniciando API FastAPI...")
    
    app = create_main_app()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

def main():
    """
    Função principal que inicia tanto API quanto Dashboard.
    """
    logger.info("🚀 Iniciando Dashboard Comu - Sistema Completo")
    logger.info("=" * 60)
    
    # Inicia dashboard em thread separada
    dashboard_thread = threading.Thread(target=start_dashboard, daemon=True)
    dashboard_thread.start()
    
    logger.info("📊 Dashboard será disponibilizado em: http://localhost:8052")
    logger.info("🔗 API será disponibilizada em: http://localhost:8000")
    logger.info("=" * 60)
    
    # Inicia API no thread principal
    start_api_server()

if __name__ == "__main__":
    main()
