"""
Callbacks para Métricas Finais
==============================

Callbacks para o grid final de métricas (MRR, ARR, Assinaturas, etc.).
"""

import dash
from dash import Input, Output, State
from datetime import datetime, timedelta
import logging

# Configuração de logging
logger = logging.getLogger(__name__)


def register_final_metrics_callbacks(app):
    """
    Registra callbacks relacionados às métricas finais.
    
    Args:
        app: Aplicação Dash
    """
    
    @app.callback(
        [Output("mrr-total", "children"),
         Output("arr-total", "children"),
         Output("mra", "children"),
         Output("mrr-growth", "children"),
         Output("mrr-mensal", "children"),
         Output("arr-mensal", "children"),
         Output("assinaturas-ativas", "children"),
         Output("assinaturas-canceladas", "children"),
         Output("mrr-anual", "children"),
         Output("arr-anual", "children"),
         Output("churn-rate", "children"),
         Output("retention-rate", "children"),
         Output("assinaturas-mes-atual", "children"),
         Output("assinaturas-mes-passado", "children")],
        [Input("date-range-store", "data"),
         Input("refresh-button", "n_clicks")]
    )
    def update_final_metrics(date_range_data, refresh_clicks):
        """
        Atualiza todas as métricas finais com dados reais.
        """
        try:
            logger.info("🔄 Atualizando métricas finais")
            
            # Inicializa variáveis
            start_dt = None
            end_dt = None
            data_referencia = datetime.now()
            periodo_dias = 30
            
            # Parse das datas do date-range-store (mesma lógica das outras correções)
            if date_range_data and 'start_date' in date_range_data and 'end_date' in date_range_data:
                try:
                    start_dt = datetime.fromisoformat(date_range_data['start_date'].replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(date_range_data['end_date'].replace('Z', '+00:00'))
                    
                    # CORREÇÃO: end_dt deve incluir todo o dia final
                    end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
                    
                    data_referencia = end_dt
                    periodo_dias = (end_dt.date() - start_dt.date()).days + 1
                    
                    logger.info(f"📅 Período selecionado: {start_dt} a {end_dt} ({periodo_dias} dias)")
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao parse das datas: {str(e)}")
                    start_dt = None
                    end_dt = None
            
            # Importa MetricsCalculator e busca dados reais
            try:
                from services.metrics_calculator import MetricsCalculator
                from database.connection import get_db_session
                from sqlalchemy import text
                
                # Cria sessão e calculadora
                db_session = get_db_session()
                calculator = MetricsCalculator(db_session)
                
                # Se temos período selecionado, busca dados reais do período
                if start_dt and end_dt:
                    logger.info(f"📊 Buscando métricas finais do período: {start_dt} a {end_dt}")
                    
                    # 1. MRR Total (Monthly Recurring Revenue) - CORRIGIDO: usar filtro de datas
                    query_mrr_total = text("""
                        SELECT SUM(valor_liquido) as mrr_total
                        FROM transacoes
                        WHERE data_transacao BETWEEN :start_date AND :end_date
                        AND status IN ('approved', 'paid', 'authorized')
                        AND valor_liquido > 0
                    """)
                    
                    result_mrr_total = calculator.db.execute(query_mrr_total, {
                        "start_date": start_dt,
                        "end_date": end_dt
                    }).fetchone()
                    
                    mrr_total = float(result_mrr_total.mrr_total) if result_mrr_total and result_mrr_total.mrr_total else 0
                    
                    # 2. ARR Total (Annual Recurring Revenue) = MRR * 12
                    arr_total = mrr_total * 12
                    
                    # 3. MRA (Monthly Recurrence Average) - CORRIGIDO: usar filtro de datas
                    mra = mrr_total
                    
                    # 4. MRR Growth - CORRIGIDO: comparar com período anterior
                    periodo_dias = (end_dt.date() - start_dt.date()).days + 1
                    periodo_anterior_start = start_dt - timedelta(days=periodo_dias)
                    periodo_anterior_end = start_dt - timedelta(microseconds=1)
                    
                    query_mrr_anterior = text("""
                        SELECT SUM(valor_liquido) as mrr_anterior
                        FROM transacoes
                        WHERE data_transacao BETWEEN :start_date AND :end_date
                        AND status IN ('approved', 'paid', 'authorized')
                        AND valor_liquido > 0
                    """)
                    
                    result_mrr_anterior = calculator.db.execute(query_mrr_anterior, {
                        "start_date": periodo_anterior_start,
                        "end_date": periodo_anterior_end
                    }).fetchone()
                    
                    mrr_anterior = float(result_mrr_anterior.mrr_anterior) if result_mrr_anterior and result_mrr_anterior.mrr_anterior else 0
                    
                    if mrr_anterior > 0:
                        mrr_growth = ((mrr_total - mrr_anterior) / mrr_anterior) * 100
                    else:
                        mrr_growth = 0.0
                    
                    # 5. MRR Mensal - CORRIGIDO: usar filtro de datas (mesmo que zerado)
                    query_mrr_mensal = text("""
                        SELECT SUM(valor_liquido) as mrr_mensal
                        FROM transacoes
                        WHERE data_transacao BETWEEN :start_date AND :end_date
                        AND status IN ('approved', 'paid', 'authorized')
                        AND (produto_nome ILIKE '%mensal%' OR produto_nome ILIKE '%monthly%')
                        AND valor_liquido > 0
                    """)
                    
                    result_mrr_mensal = calculator.db.execute(query_mrr_mensal, {
                        "start_date": start_dt,
                        "end_date": end_dt
                    }).fetchone()
                    
                    mrr_mensal = float(result_mrr_mensal.mrr_mensal) if result_mrr_mensal and result_mrr_mensal.mrr_mensal else 0
                    
                    # 6. ARR Mensal = MRR Mensal * 12
                    arr_mensal = mrr_mensal * 12
                    
                    # 7. Assinaturas Ativas
                    query_ativas = text("""
                        SELECT COUNT(DISTINCT a.id) as ativas
                        FROM assinaturas a
                        WHERE a.data_expiracao_acesso > :data_referencia
                        AND a.status = 'active'
                    """)
                    
                    result_ativas = calculator.db.execute(query_ativas, {
                        "data_referencia": data_referencia
                    }).fetchone()
                    
                    assinaturas_ativas = result_ativas.ativas if result_ativas else 0
                    
                    # 8. Assinaturas Canceladas
                    query_canceladas = text("""
                        SELECT COUNT(DISTINCT a.id) as canceladas
                        FROM assinaturas a
                        WHERE a.data_cancelamento IS NOT NULL
                        AND a.data_cancelamento BETWEEN :start_date AND :end_date
                    """)
                    
                    result_canceladas = calculator.db.execute(query_canceladas, {
                        "start_date": start_dt,
                        "end_date": end_dt
                    }).fetchone()
                    
                    assinaturas_canceladas = result_canceladas.canceladas if result_canceladas else 0
                    
                    # 9. MRR Anual - CORRIGIDO: detectar planos anuais por valor alto ou duração longa
                    # Primeiro tenta por nome, depois por valor alto (acima de R$ 200)
                    query_mrr_anual = text("""
                        SELECT SUM(valor_liquido) as mrr_anual
                        FROM transacoes
                        WHERE data_transacao BETWEEN :start_date AND :end_date
                        AND status IN ('approved', 'paid', 'authorized')
                        AND (
                            produto_nome ILIKE '%anual%' OR 
                            produto_nome ILIKE '%yearly%' OR 
                            produto_nome ILIKE '%year%' OR
                            valor_liquido > 200
                        )
                        AND valor_liquido > 0
                    """)
                    
                    result_mrr_anual = calculator.db.execute(query_mrr_anual, {
                        "start_date": start_dt,
                        "end_date": end_dt
                    }).fetchone()
                    
                    mrr_anual = float(result_mrr_anual.mrr_anual) if result_mrr_anual and result_mrr_anual.mrr_anual else 0
                    
                    # 10. ARR Anual = MRR Anual * 12
                    arr_anual = mrr_anual * 12
                    
                    # 11. Churn Rate - CORRIGIDO: calcular baseado nos cancelamentos do período
                    # Churn Rate = (Assinaturas Canceladas no Período / Total de Assinaturas Ativas) * 100
                    if assinaturas_ativas > 0:
                        churn_rate = (assinaturas_canceladas / assinaturas_ativas) * 100
                    else:
                        churn_rate = 0.0
                    
                    # 12. Retention Rate = 100 - Churn Rate
                    retention_rate = 100 - churn_rate
                    
                    # 13. Assinaturas esse mês - CORRIGIDO: excluir PIX gerados (só assinaturas com transação aprovada)
                    mes_atual_start = data_referencia.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    mes_atual_end = data_referencia.replace(hour=23, minute=59, second=59, microsecond=999999)
                    
                    query_mes_atual = text("""
                        SELECT COUNT(DISTINCT a.id) as mes_atual
                        FROM assinaturas a
                        INNER JOIN transacoes t ON a.id = t.assinatura_id
                        WHERE a.data_inicio BETWEEN :start_date AND :end_date
                        AND t.status IN ('approved', 'paid', 'authorized')
                        AND t.valor_liquido > 0
                    """)
                    
                    result_mes_atual = calculator.db.execute(query_mes_atual, {
                        "start_date": mes_atual_start,
                        "end_date": mes_atual_end
                    }).fetchone()
                    
                    assinaturas_mes_atual = result_mes_atual.mes_atual if result_mes_atual else 0
                    
                    # 14. Assinaturas do mês passado - CORRIGIDO: excluir PIX gerados
                    mes_passado_end = mes_atual_start - timedelta(microseconds=1)
                    mes_passado_start = mes_passado_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    
                    query_mes_passado = text("""
                        SELECT COUNT(DISTINCT a.id) as mes_passado
                        FROM assinaturas a
                        INNER JOIN transacoes t ON a.id = t.assinatura_id
                        WHERE a.data_inicio BETWEEN :start_date AND :end_date
                        AND t.status IN ('approved', 'paid', 'authorized')
                        AND t.valor_liquido > 0
                    """)
                    
                    result_mes_passado = calculator.db.execute(query_mes_passado, {
                        "start_date": mes_passado_start,
                        "end_date": mes_passado_end
                    }).fetchone()
                    
                    assinaturas_mes_passado = result_mes_passado.mes_passado if result_mes_passado else 0
                    
                    logger.info(f"✅ Métricas finais carregadas: MRR={mrr_total:.2f}, ARR={arr_total:.2f}, Ativas={assinaturas_ativas}")
                    
                else:
                    # Se não há período selecionado, usa valores padrão
                    mrr_total = 0
                    arr_total = 0
                    mra = 0
                    mrr_growth = 0
                    mrr_mensal = 0
                    arr_mensal = 0
                    assinaturas_ativas = 0
                    assinaturas_canceladas = 0
                    mrr_anual = 0
                    arr_anual = 0
                    churn_rate = 0
                    retention_rate = 0
                    assinaturas_mes_atual = 0
                    assinaturas_mes_passado = 0
                    
                    logger.info("⚠️ Sem período selecionado, usando valores padrão")
                
            except Exception as e:
                logger.error(f"❌ Erro ao carregar métricas finais: {str(e)}")
                # Fallback para valores padrão
                mrr_total = 0
                arr_total = 0
                mra = 0
                mrr_growth = 0
                mrr_mensal = 0
                arr_mensal = 0
                assinaturas_ativas = 0
                assinaturas_canceladas = 0
                mrr_anual = 0
                arr_anual = 0
                churn_rate = 0
                retention_rate = 0
                assinaturas_mes_atual = 0
                assinaturas_mes_passado = 0
            
            # Formata os valores para exibição
            def format_currency(value):
                return f"R$ {value:,.2f}".replace(",", " ").replace(".", ",")
            
            def format_number(value):
                return f"{int(value):,}".replace(",", " ")
            
            def format_percentage(value):
                return f"{value:.1f}%"
            
            return (
                format_currency(mrr_total),      # mrr-total
                format_currency(arr_total),      # arr-total
                format_number(mra),              # mra
                format_percentage(mrr_growth),   # mrr-growth
                format_currency(mrr_mensal),     # mrr-mensal
                format_currency(arr_mensal),     # arr-mensal
                format_number(assinaturas_ativas), # assinaturas-ativas
                format_number(assinaturas_canceladas), # assinaturas-canceladas
                format_currency(mrr_anual),      # mrr-anual
                format_currency(arr_anual),      # arr-anual
                format_percentage(churn_rate),   # churn-rate
                format_percentage(retention_rate), # retention-rate
                format_number(assinaturas_mes_atual), # assinaturas-mes-atual
                format_number(assinaturas_mes_passado) # assinaturas-mes-passado
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar métricas finais: {str(e)}")
            # Retorna valores padrão em caso de erro
            return (
                "R$ 0,00", "R$ 0,00", "0", "0,0%",
                "R$ 0,00", "R$ 0,00", "0", "0",
                "R$ 0,00", "R$ 0,00", "0,0%", "0,0%",
                "0", "0"
            )
    
    logger.info("✅ Callbacks de métricas finais registrados com sucesso")
