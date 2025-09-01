#!/usr/bin/env python3
"""
Script de Teste da Integração
============================

Script para testar a integração entre dashboard e MetricsCalculator.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.dashboard.services.dashboard_data_service import DashboardDataService
from src.database.connection import get_db_session
from datetime import datetime, timedelta


def test_integration():
    """
    Testa a integração entre dashboard e MetricsCalculator.
    """
    print("🧪 Testando integração Dashboard + MetricsCalculator...")
    
    try:
        # Cria sessão do banco
        db_session = get_db_session()
        print("✅ Conexão com banco estabelecida")
        
        # Cria serviço de dados
        dashboard_service = DashboardDataService(db_session)
        print("✅ Serviço de dados criado")
        
        # Testa carregamento de dados
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        dashboard_data = dashboard_service.get_dashboard_data(start_date, end_date)
        print("✅ Dados do dashboard carregados")
        
        # Exibe métricas principais
        print(f"📊 MRR Total: R$ {dashboard_data['mrr_total']:,.2f}")
        print(f"📊 ARR Total: R$ {dashboard_data['arr_total']:,.2f}")
        print(f"📊 Churn Rate: {dashboard_data['churn_rate_total']:.2f}%")
        print(f"📊 LTV Total: R$ {dashboard_data['ltv_total']:,.2f}")
        print(f"📊 Fonte dos dados: {dashboard_data['data_source']}")
        
        # Fecha sessão
        db_session.close()
        print("✅ Teste de integração concluído com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de integração: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)
