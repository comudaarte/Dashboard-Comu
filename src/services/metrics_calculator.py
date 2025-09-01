"""
Calculador de Métricas para Dashboard de Assinaturas
===================================================

Este módulo implementa todas as métricas essenciais para o dashboard de assinaturas,
incluindo MRR, ARR, Churn Rate, LTV, CAC e outras métricas de negócio.

Autor: Dashboard Comu
Data: 2024
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy import text, func, and_, or_, extract
from sqlalchemy.orm import Session

# Configuração de logging
logger = logging.getLogger(__name__)

class MetricsCalculator:
    """
    Calculador centralizado de métricas de negócio para assinaturas.
    
    Este calculador implementa todas as métricas essenciais seguindo
    as regras de negócio específicas do projeto:
    - MRR/ARR baseado nos valores salvos corretamente por tipo de plano
    - Churn Rate baseado em cancelamentos e data_proxima_cobranca
    - LTV calculado com taxa de churn real
    - Métricas de crescimento e retenção
    """
    
    def __init__(self, db_session: Session):
        """
        Inicializa o calculador com a sessão do banco de dados.
        
        Args:
            db_session: Sessão SQLAlchemy configurada
        """
        self.db = db_session
        self.logger = logging.getLogger(__name__)
    
    def calculate_mrr(self, data_referencia: datetime = None) -> Dict[str, Any]:
        """
        Calcula MRR (Monthly Recurring Revenue) baseado na nova lógica correta.
        
        A lógica implementada:
        - Para planos anuais: usa valor_anual / 12 (campo valor_anual preenchido)
        - Para planos mensais: usa valor_mensal (campo valor_mensal preenchido)
        - Considera apenas assinaturas ativas na data de referência
        
        Args:
            data_referencia: Data para calcular o MRR (padrão: hoje)
            
        Returns:
            Dict com MRR total, por plataforma, por tipo de plano e detalhes
        """
        if data_referencia is None:
            data_referencia = datetime.now()
        
        self.logger.info(f"Calculando MRR para data: {data_referencia}")
        
        try:
            # Query otimizada para calcular MRR
            query = text("""
                SELECT 
                    plataforma,
                    COUNT(*) as total_assinaturas,
                    
                    -- MRR de planos mensais (valor_mensal preenchido)
                    COUNT(CASE WHEN valor_mensal IS NOT NULL THEN 1 END) as assinaturas_mensais,
                    COALESCE(SUM(valor_mensal), 0) as mrr_mensal,
                    
                    -- MRR de planos anuais (valor_anual preenchido, dividido por 12)
                    COUNT(CASE WHEN valor_anual IS NOT NULL THEN 1 END) as assinaturas_anuais,
                    COALESCE(SUM(valor_anual / 12.0), 0) as mrr_anual,
                    
                    -- MRR total
                    COALESCE(SUM(valor_mensal), 0) + COALESCE(SUM(valor_anual / 12.0), 0) as mrr_total
                    
                FROM assinaturas 
                WHERE 
                    -- Assinaturas ativas na data de referência
                    data_expiracao_acesso >= :data_ref
                    
                    -- Exclui assinaturas reembolsadas ou com chargeback
                    AND status NOT IN ('refunded', 'chargeback')
                    
                    -- Assinaturas que têm valor (mensal OU anual)
                    AND (valor_mensal IS NOT NULL OR valor_anual IS NOT NULL)
                    
                GROUP BY plataforma
                ORDER BY plataforma
            """)
            
            result = self.db.execute(query, {"data_ref": data_referencia}).fetchall()
            
            # Processa resultados
            mrr_total = Decimal('0')
            mrr_por_plataforma = {}
            detalhes = {
                "data_referencia": data_referencia.isoformat(),
                "total_assinaturas_ativas": 0,
                "breakdown_por_plataforma": {},
                "breakdown_por_tipo": {
                    "mensal": {"assinaturas": 0, "mrr": Decimal('0')},
                    "anual": {"assinaturas": 0, "mrr": Decimal('0')}
                }
            }
            
            for row in result:
                plataforma = row.plataforma
                mrr_plataforma = Decimal(str(row.mrr_total))
                mrr_total += mrr_plataforma
                
                # Dados por plataforma
                mrr_por_plataforma[plataforma] = float(mrr_plataforma)
                detalhes["breakdown_por_plataforma"][plataforma] = {
                    "mrr_total": float(mrr_plataforma),
                    "mrr_mensal": float(row.mrr_mensal),
                    "mrr_anual": float(row.mrr_anual),
                    "assinaturas_total": row.total_assinaturas,
                    "assinaturas_mensais": row.assinaturas_mensais,
                    "assinaturas_anuais": row.assinaturas_anuais
                }
                
                # Acumula totais por tipo
                detalhes["total_assinaturas_ativas"] += row.total_assinaturas
                detalhes["breakdown_por_tipo"]["mensal"]["assinaturas"] += row.assinaturas_mensais
                detalhes["breakdown_por_tipo"]["mensal"]["mrr"] += Decimal(str(row.mrr_mensal))
                detalhes["breakdown_por_tipo"]["anual"]["assinaturas"] += row.assinaturas_anuais
                detalhes["breakdown_por_tipo"]["anual"]["mrr"] += Decimal(str(row.mrr_anual))
            
            # Converte Decimals para float no resultado final
            detalhes["breakdown_por_tipo"]["mensal"]["mrr"] = float(detalhes["breakdown_por_tipo"]["mensal"]["mrr"])
            detalhes["breakdown_por_tipo"]["anual"]["mrr"] = float(detalhes["breakdown_por_tipo"]["anual"]["mrr"])
            
            resultado = {
                "mrr_total": float(mrr_total),
                "mrr_por_plataforma": mrr_por_plataforma,
                "detalhes": detalhes
            }
            
            self.logger.info(f"MRR calculado com sucesso: R$ {mrr_total:.2f}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular MRR: {str(e)}")
            raise
    
    def calculate_arr(self, data_referencia: datetime = None) -> Dict[str, Any]:
        """
        Calcula ARR (Annual Recurring Revenue) baseado no MRR.
        
        Args:
            data_referencia: Data para calcular o ARR (padrão: hoje)
            
        Returns:
            Dict com ARR total, por plataforma e detalhes
        """
        mrr_data = self.calculate_mrr(data_referencia)
        
        resultado = {
            "arr_total": mrr_data["mrr_total"] * 12,
            "arr_por_plataforma": {
                plataforma: mrr * 12 
                for plataforma, mrr in mrr_data["mrr_por_plataforma"].items()
            },
            "detalhes": {
                **mrr_data["detalhes"],
                "multiplicador_arr": 12
            }
        }
        
        self.logger.info(f"ARR calculado: R$ {resultado['arr_total']:.2f}")
        return resultado
    
    def calculate_churn_rate(self, periodo_dias: int = 30) -> Dict[str, Any]:
        """
        Calcula a taxa de churn (cancelamento) CORRIGIDA - exclui PIX expirados.
        
        CORREÇÃO CRÍTICA: Exclui cancelamentos por PIX não pago (Guru), que não representam
        churn real, apenas abandono de checkout.
        
        A lógica corrigida:
        - Considera APENAS cancelamentos de assinaturas que JÁ FORAM ATIVAS
        - Exclui PIX expirados (cancelamentos em <= 72h)
        - Taxa = (Cancelamentos reais no período / Assinaturas ativas no início) * 100
        
        Args:
            periodo_dias: Período para análise (padrão: 30 dias)
            
        Returns:
            Dict com taxa de churn corrigida, detalhes por plataforma e estatísticas
        """
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=periodo_dias)
        
        self.logger.info(f"Calculando Churn Rate CORRIGIDO (exclui PIX expirado) para período: {data_inicio} - {data_fim}")
        
        try:
            # Query para calcular churn
            query = text("""
                WITH assinaturas_ativas_inicio AS (
                    -- Assinaturas ativas no início do período
                    SELECT 
                        plataforma,
                        COUNT(*) as ativas_inicio
                    FROM assinaturas 
                    WHERE 
                        data_inicio <= :data_inicio
                        AND data_expiracao_acesso > :data_inicio
                        AND status NOT IN ('refunded', 'chargeback')
                    GROUP BY plataforma
                ),
                cancelamentos_reais_periodo AS (
                    -- APENAS cancelamentos de assinaturas que JÁ FORAM ATIVAS
                    -- Exclui PIX expirados (que vão direto de inactive → canceled)
                    SELECT 
                        plataforma,
                        COUNT(*) as cancelamentos
                    FROM assinaturas 
                    WHERE 
                        -- Cancelamentos efetivos
                        status IN ('canceled', 'subscription_canceled')
                        
                        -- Data de cancelamento no período
                        AND ultima_atualizacao BETWEEN :data_inicio AND :data_fim
                        
                        -- FILTRO CRÍTICO: Exclui PIX expirados (< 72h de vida)
                        AND EXTRACT(EPOCH FROM (ultima_atualizacao - data_inicio))/3600 > 72
                    GROUP BY plataforma
                ),
                cancelamentos_pix_expirado AS (
                    -- Para LOG: PIX expirados que estamos excluindo
                    SELECT 
                        plataforma,
                        COUNT(*) as pix_expirados
                    FROM assinaturas 
                    WHERE 
                        status IN ('canceled', 'subscription_canceled')
                        AND ultima_atualizacao BETWEEN :data_inicio AND :data_fim
                        AND EXTRACT(EPOCH FROM (ultima_atualizacao - data_inicio))/3600 <= 72
                    GROUP BY plataforma
                )
                SELECT 
                    COALESCE(a.plataforma, c.plataforma) as plataforma,
                    COALESCE(a.ativas_inicio, 0) as ativas_inicio,
                    COALESCE(c.cancelamentos, 0) as cancelamentos,
                    COALESCE(p.pix_expirados, 0) as pix_expirados_excluidos,
                    
                    -- Taxa de churn corrigida
                    CASE 
                        WHEN COALESCE(a.ativas_inicio, 0) > 0 
                        THEN (COALESCE(c.cancelamentos, 0) * 100.0) / a.ativas_inicio
                        ELSE 0 
                    END as churn_rate
                    
                FROM assinaturas_ativas_inicio a
                FULL OUTER JOIN cancelamentos_reais_periodo c ON a.plataforma = c.plataforma
                LEFT JOIN cancelamentos_pix_expirado p ON a.plataforma = p.plataforma
                ORDER BY plataforma
            """)
            
            result = self.db.execute(query, {
                "data_inicio": data_inicio,
                "data_fim": data_fim
            }).fetchall()
            
            # Processa resultados
            churn_total = Decimal('0')
            total_ativas_inicio = 0
            total_cancelamentos = 0
            total_pix_expirados = 0
            churn_por_plataforma = {}
            detalhes = {
                "periodo": {
                    "data_inicio": data_inicio.isoformat(),
                    "data_fim": data_fim.isoformat(),
                    "dias": periodo_dias
                },
                "correcao_aplicada": {
                    "filtro": "Excluídos cancelamentos em <= 72h (PIX expirado)",
                    "motivacao": "PIX expirados não representam churn real, apenas abandono de checkout"
                },
                "breakdown_por_plataforma": {}
            }
            
            for row in result:
                plataforma = row.plataforma
                ativas_inicio = row.ativas_inicio
                cancelamentos = row.cancelamentos
                pix_expirados = row.pix_expirados_excluidos
                churn_rate = float(row.churn_rate)
                
                total_ativas_inicio += ativas_inicio
                total_cancelamentos += cancelamentos
                total_pix_expirados += pix_expirados
                
                churn_por_plataforma[plataforma] = churn_rate
                detalhes["breakdown_por_plataforma"][plataforma] = {
                    "ativas_inicio_periodo": ativas_inicio,
                    "cancelamentos_periodo": cancelamentos,
                    "pix_expirados_excluidos": pix_expirados,
                    "churn_rate": churn_rate
                }
                
                if pix_expirados > 0:
                    self.logger.info(f"[{plataforma}] PIX expirados excluídos do churn: {pix_expirados}")
            
            # Calcula churn total
            if total_ativas_inicio > 0:
                churn_total = (total_cancelamentos * 100.0) / total_ativas_inicio
            
            # Taxa de renovação (inverso do churn)
            renewal_rate = 100.0 - float(churn_total)
            
            resultado = {
                "churn_rate_total": float(churn_total),
                "renewal_rate_total": renewal_rate,
                "churn_por_plataforma": churn_por_plataforma,
                "total_ativas_inicio": total_ativas_inicio,
                "total_cancelamentos": total_cancelamentos,
                "total_pix_expirados_excluidos": total_pix_expirados,
                "detalhes": detalhes
            }
            
            self.logger.info(f"Churn Rate CORRIGIDO calculado: {churn_total:.2f}% (excluiu {total_pix_expirados} PIX expirados)")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular Churn Rate: {str(e)}")
            raise
    
    def calculate_ltv(self, data_referencia: datetime = None) -> Dict[str, Any]:
        """
        Calcula LTV (Lifetime Value) baseado na taxa de churn real.
        
        Fórmula: LTV = (Ticket Médio / Taxa de Churn Mensal)
        Onde:
        - Ticket Médio = Média dos valores anuais das assinaturas ativas
        - Taxa de Churn Mensal = Taxa de churn dos últimos 30 dias
        
        Args:
            data_referencia: Data para calcular o LTV (padrão: hoje)
            
        Returns:
            Dict com LTV total, por plataforma e breakdown de cálculo
        """
        if data_referencia is None:
            data_referencia = datetime.now()
        
        self.logger.info(f"Calculando LTV para data: {data_referencia}")
        
        try:
            # Obtém churn rate dos últimos 30 dias
            churn_data = self.calculate_churn_rate(30)
            
            # Query para calcular ticket médio anual
            query = text("""
                SELECT 
                    plataforma,
                    COUNT(*) as total_assinaturas,
                    
                    -- Ticket médio anual (para planos anuais, usa valor_anual; para mensais, usa valor_mensal * 12)
                    AVG(
                        CASE 
                            WHEN valor_anual IS NOT NULL THEN valor_anual
                            WHEN valor_mensal IS NOT NULL THEN valor_mensal * 12
                            ELSE 0
                        END
                    ) as ticket_medio_anual
                    
                FROM assinaturas 
                WHERE 
                    -- Assinaturas ativas na data de referência
                    data_expiracao_acesso >= :data_ref
                    AND status NOT IN ('refunded', 'chargeback')
                    AND (valor_mensal IS NOT NULL OR valor_anual IS NOT NULL)
                    
                GROUP BY plataforma
                ORDER BY plataforma
            """)
            
            result = self.db.execute(query, {"data_ref": data_referencia}).fetchall()
            
            ltv_por_plataforma = {}
            detalhes = {
                "data_referencia": data_referencia.isoformat(),
                "metodo_calculo": "ticket_medio_anual / (churn_rate_mensal / 100)",
                "breakdown_por_plataforma": {}
            }
            
            total_ticket_medio = Decimal('0')
            total_assinaturas = 0
            
            for row in result:
                plataforma = row.plataforma
                ticket_medio = float(row.ticket_medio_anual) if row.ticket_medio_anual else 0
                churn_rate = churn_data["churn_por_plataforma"].get(plataforma, 0)
                
                # Calcula LTV
                if churn_rate > 0:
                    ltv = ticket_medio / (churn_rate / 100)
                else:
                    # Se churn rate é 0, assume uma taxa mínima de 1% para evitar divisão por zero
                    ltv = ticket_medio / 0.01
                
                ltv_por_plataforma[plataforma] = ltv
                detalhes["breakdown_por_plataforma"][plataforma] = {
                    "ticket_medio_anual": ticket_medio,
                    "churn_rate_mensal": churn_rate,
                    "ltv_calculado": ltv,
                    "total_assinaturas": row.total_assinaturas
                }
                
                # Acumula para cálculo do LTV total
                total_ticket_medio += Decimal(str(ticket_medio)) * row.total_assinaturas
                total_assinaturas += row.total_assinaturas
            
            # Calcula LTV total ponderado
            if total_assinaturas > 0:
                ticket_medio_geral = float(total_ticket_medio / total_assinaturas)
                churn_total = churn_data["churn_rate_total"]
                
                if churn_total > 0:
                    ltv_total = ticket_medio_geral / (churn_total / 100)
                else:
                    ltv_total = ticket_medio_geral / 0.01
            else:
                ltv_total = 0
                ticket_medio_geral = 0
            
            resultado = {
                "ltv_total": ltv_total,
                "ltv_por_plataforma": ltv_por_plataforma,
                "ticket_medio_anual_geral": ticket_medio_geral,
                "churn_rate_utilizado": churn_data["churn_rate_total"],
                "detalhes": detalhes
            }
            
            self.logger.info(f"LTV calculado: R$ {ltv_total:.2f}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular LTV: {str(e)}")
            raise
    
    def calculate_cac(self, periodo_dias: int = 30, custo_marketing: float = None) -> Dict[str, Any]:
        """
        Calcula CAC (Customer Acquisition Cost).
        
        Fórmula: CAC = Custo Total de Marketing / Número de Novos Clientes
        
        Args:
            periodo_dias: Período para análise (padrão: 30 dias)
            custo_marketing: Custo de marketing no período (se não informado, retorna estrutura para preenchimento)
            
        Returns:
            Dict com CAC calculado ou estrutura para informar custos
        """
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=periodo_dias)
        
        self.logger.info(f"Calculando CAC para período: {data_inicio} - {data_fim}")
        
        try:
            # Query para contar novos clientes
            query = text("""
                SELECT 
                    plataforma,
                    COUNT(DISTINCT cliente_id) as novos_clientes
                FROM assinaturas 
                WHERE 
                    data_inicio BETWEEN :data_inicio AND :data_fim
                    AND status NOT IN ('refunded', 'chargeback')
                GROUP BY plataforma
                ORDER BY plataforma
            """)
            
            result = self.db.execute(query, {
                "data_inicio": data_inicio,
                "data_fim": data_fim
            }).fetchall()
            
            total_novos_clientes = sum(row.novos_clientes for row in result)
            
            detalhes = {
                "periodo": {
                    "data_inicio": data_inicio.isoformat(),
                    "data_fim": data_fim.isoformat(),
                    "dias": periodo_dias
                },
                "novos_clientes_total": total_novos_clientes,
                "breakdown_por_plataforma": {}
            }
            
            for row in result:
                detalhes["breakdown_por_plataforma"][row.plataforma] = {
                    "novos_clientes": row.novos_clientes
                }
            
            if custo_marketing is not None and total_novos_clientes > 0:
                cac_total = custo_marketing / total_novos_clientes
                
                resultado = {
                    "cac_total": cac_total,
                    "custo_marketing_informado": custo_marketing,
                    "novos_clientes_periodo": total_novos_clientes,
                    "detalhes": detalhes
                }
            else:
                resultado = {
                    "cac_total": None,
                    "custo_marketing_informado": custo_marketing,
                    "novos_clientes_periodo": total_novos_clientes,
                    "detalhes": detalhes,
                    "instrucoes": "Para calcular o CAC, forneça o custo_marketing do período"
                }
            
            self.logger.info(f"CAC calculado - Novos clientes: {total_novos_clientes}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular CAC: {str(e)}")
            raise
    
    # ============================================================================
    # FASE 1: MÉTRICAS BÁSICAS - IMPLEMENTAÇÃO
    # ============================================================================
    
    def calculate_active_subscriptions(self, data_referencia: datetime = None) -> Dict[str, Any]:
        """
        Calcula total de assinaturas ativas.
        
        Args:
            data_referencia: Data de referência para cálculos (padrão: hoje)
            
        Returns:
            Dict com total de assinaturas ativas e breakdown por plataforma
        """
        if data_referencia is None:
            data_referencia = datetime.now()
            
        self.logger.info(f"Calculando assinaturas ativas para data: {data_referencia}")
        
        try:
            query = text("""
                SELECT 
                    plataforma,
                    COUNT(*) as total_ativas
                FROM assinaturas 
                WHERE 
                    data_expiracao_acesso >= :data_ref
                    AND status NOT IN ('refunded', 'chargeback')
                    AND (valor_mensal IS NOT NULL OR valor_anual IS NOT NULL)
                GROUP BY plataforma
                ORDER BY plataforma
            """)
            
            result = self.db.execute(query, {"data_ref": data_referencia}).fetchall()
            
            total_ativas = sum(row.total_ativas for row in result)
            
            detalhes = {
                "data_referencia": data_referencia.isoformat(),
                "total_assinaturas_ativas": total_ativas,
                "breakdown_por_plataforma": {}
            }
            
            for row in result:
                detalhes["breakdown_por_plataforma"][row.plataforma] = {
                    "total_ativas": row.total_ativas
                }
            
            resultado = {
                "total_ativas": total_ativas,
                "detalhes": detalhes
            }
            
            self.logger.info(f"Assinaturas ativas calculadas: {total_ativas}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular assinaturas ativas: {str(e)}")
            raise
    
    def calculate_canceled_subscriptions(self) -> Dict[str, Any]:
        """
        Calcula total de assinaturas canceladas.
        
        Returns:
            Dict com total de assinaturas canceladas e breakdown por plataforma
        """
        self.logger.info("Calculando assinaturas canceladas")
        
        try:
            query = text("""
                SELECT 
                    plataforma,
                    COUNT(*) as total_canceladas
                FROM assinaturas 
                WHERE 
                    status IN ('canceled', 'subscription_canceled')
                GROUP BY plataforma
                ORDER BY plataforma
            """)
            
            result = self.db.execute(query).fetchall()
            
            total_canceladas = sum(row.total_canceladas for row in result)
            
            detalhes = {
                "total_assinaturas_canceladas": total_canceladas,
                "breakdown_por_plataforma": {}
            }
            
            for row in result:
                detalhes["breakdown_por_plataforma"][row.plataforma] = {
                    "total_canceladas": row.total_canceladas
                }
            
            resultado = {
                "total_canceladas": total_canceladas,
                "detalhes": detalhes
            }
            
            self.logger.info(f"Assinaturas canceladas calculadas: {total_canceladas}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular assinaturas canceladas: {str(e)}")
            raise
    
    def calculate_total_sales(self, data_referencia: datetime = None) -> Dict[str, Any]:
        """
        Calcula total de vendas realizadas.
        
        Args:
            data_referencia: Data de referência para cálculos (padrão: hoje)
            
        Returns:
            Dict com total de vendas e breakdown por plataforma
        """
        if data_referencia is None:
            data_referencia = datetime.now()
            
        self.logger.info(f"Calculando total de vendas para data: {data_referencia}")
        
        try:
            query = text("""
                SELECT 
                    plataforma,
                    COUNT(*) as total_vendas
                FROM transacoes 
                WHERE 
                    status = 'approved'
                    AND data_transacao <= :data_ref
                GROUP BY plataforma
                ORDER BY plataforma
            """)
            
            result = self.db.execute(query, {"data_ref": data_referencia}).fetchall()
            
            total_vendas = sum(row.total_vendas for row in result)
            
            detalhes = {
                "data_referencia": data_referencia.isoformat(),
                "total_vendas": total_vendas,
                "breakdown_por_plataforma": {}
            }
            
            for row in result:
                detalhes["breakdown_por_plataforma"][row.plataforma] = {
                    "total_vendas": row.total_vendas
                }
            
            resultado = {
                "total_vendas": total_vendas,
                "detalhes": detalhes
            }
            
            self.logger.info(f"Total de vendas calculado: {total_vendas}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular total de vendas: {str(e)}")
            raise
    
    def calculate_unique_customers(self, data_referencia: datetime = None) -> Dict[str, Any]:
        """
        Calcula total de clientes únicos.
        
        Args:
            data_referencia: Data de referência para cálculos (padrão: hoje)
            
        Returns:
            Dict com total de clientes únicos e breakdown por plataforma
        """
        if data_referencia is None:
            data_referencia = datetime.now()
            
        self.logger.info(f"Calculando clientes únicos para data: {data_referencia}")
        
        try:
            query = text("""
                SELECT 
                    plataforma,
                    COUNT(DISTINCT cliente_id) as total_clientes_unicos
                FROM assinaturas 
                WHERE 
                    data_inicio <= :data_ref
                    AND status NOT IN ('refunded', 'chargeback')
                GROUP BY plataforma
                ORDER BY plataforma
            """)
            
            result = self.db.execute(query, {"data_ref": data_referencia}).fetchall()
            
            total_clientes_unicos = sum(row.total_clientes_unicos for row in result)
            
            detalhes = {
                "data_referencia": data_referencia.isoformat(),
                "total_clientes_unicos": total_clientes_unicos,
                "breakdown_por_plataforma": {}
            }
            
            for row in result:
                detalhes["breakdown_por_plataforma"][row.plataforma] = {
                    "total_clientes_unicos": row.total_clientes_unicos
                }
            
            resultado = {
                "total_clientes_unicos": total_clientes_unicos,
                "detalhes": detalhes
            }
            
            self.logger.info(f"Clientes únicos calculados: {total_clientes_unicos}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular clientes únicos: {str(e)}")
            raise
    
    def calculate_mrr_growth(self, periodo_dias: int = 30) -> Dict[str, Any]:
        """
        Calcula crescimento percentual do MRR.
        
        Args:
            periodo_dias: Período para análise (padrão: 30 dias)
            
        Returns:
            Dict com crescimento percentual e valores comparativos
        """
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=periodo_dias)
        
        self.logger.info(f"Calculando crescimento MRR para período: {data_inicio} - {data_fim}")
        
        try:
            # MRR atual
            mrr_atual = self.calculate_mrr(data_fim)
            
            # MRR há X dias atrás
            mrr_anterior = self.calculate_mrr(data_inicio)
            
            mrr_atual_valor = mrr_atual["mrr_total"]
            mrr_anterior_valor = mrr_anterior["mrr_total"]
            
            # Calcula crescimento percentual
            if mrr_anterior_valor > 0:
                crescimento_percentual = ((mrr_atual_valor - mrr_anterior_valor) / mrr_anterior_valor) * 100
            else:
                crescimento_percentual = 0
            
            resultado = {
                "periodo_dias": periodo_dias,
                "data_inicio": data_inicio.isoformat(),
                "data_fim": data_fim.isoformat(),
                "mrr_atual": mrr_atual_valor,
                "mrr_anterior": mrr_anterior_valor,
                "crescimento_percentual": crescimento_percentual,
                "crescimento_absoluto": mrr_atual_valor - mrr_anterior_valor,
                "tendencia": "crescimento" if crescimento_percentual > 0 else "queda" if crescimento_percentual < 0 else "estavel"
            }
            
            self.logger.info(f"Crescimento MRR calculado: {crescimento_percentual:.2f}%")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular crescimento MRR: {str(e)}")
            raise
    
    def calculate_mrr_by_plan_type(self, tipo_plano: str, data_referencia: datetime = None) -> Dict[str, Any]:
        """
        Calcula MRR por tipo de plano (mensal ou anual).
        
        Args:
            tipo_plano: 'mensal' ou 'anual'
            data_referencia: Data de referência para cálculos (padrão: hoje)
            
        Returns:
            Dict com MRR do tipo de plano específico
        """
        if data_referencia is None:
            data_referencia = datetime.now()
            
        if tipo_plano not in ['mensal', 'anual']:
            raise ValueError("tipo_plano deve ser 'mensal' ou 'anual'")
            
        self.logger.info(f"Calculando MRR para plano {tipo_plano} na data: {data_referencia}")
        
        try:
            if tipo_plano == 'mensal':
                # Para planos mensais, usa valor_mensal diretamente
                query = text("""
                    SELECT 
                        plataforma,
                        COUNT(*) as total_assinaturas,
                        SUM(valor_mensal) as mrr_total
                    FROM assinaturas 
                    WHERE 
                        data_expiracao_acesso >= :data_ref
                        AND status NOT IN ('refunded', 'chargeback')
                        AND valor_mensal IS NOT NULL
                    GROUP BY plataforma
                    ORDER BY plataforma
                """)
            else:
                # Para planos anuais, divide valor_anual por 12
                query = text("""
                    SELECT 
                        plataforma,
                        COUNT(*) as total_assinaturas,
                        SUM(valor_anual / 12) as mrr_total
                    FROM assinaturas 
                    WHERE 
                        data_expiracao_acesso >= :data_ref
                        AND status NOT IN ('refunded', 'chargeback')
                        AND valor_anual IS NOT NULL
                    GROUP BY plataforma
                    ORDER BY plataforma
                """)
            
            result = self.db.execute(query, {"data_ref": data_referencia}).fetchall()
            
            mrr_total = sum(Decimal(str(row.mrr_total)) for row in result if row.mrr_total)
            
            detalhes = {
                "tipo_plano": tipo_plano,
                "data_referencia": data_referencia.isoformat(),
                "mrr_total": mrr_total,
                "breakdown_por_plataforma": {}
            }
            
            for row in result:
                detalhes["breakdown_por_plataforma"][row.plataforma] = {
                    "total_assinaturas": row.total_assinaturas,
                    "mrr": Decimal(str(row.mrr_total)) if row.mrr_total else Decimal('0')
                }
            
            resultado = {
                "tipo_plano": tipo_plano,
                "mrr_total": mrr_total,
                "detalhes": detalhes
            }
            
            self.logger.info(f"MRR para plano {tipo_plano} calculado: R$ {mrr_total:.2f}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular MRR para plano {tipo_plano}: {str(e)}")
            raise
    
    def calculate_arr_by_plan_type(self, tipo_plano: str, data_referencia: datetime = None) -> Dict[str, Any]:
        """
        Calcula ARR por tipo de plano (mensal ou anual).
        
        Args:
            tipo_plano: 'mensal' ou 'anual'
            data_referencia: Data de referência para cálculos (padrão: hoje)
            
        Returns:
            Dict com ARR do tipo de plano específico
        """
        if data_referencia is None:
            data_referencia = datetime.now()
            
        if tipo_plano not in ['mensal', 'anual']:
            raise ValueError("tipo_plano deve ser 'mensal' ou 'anual'")
            
        self.logger.info(f"Calculando ARR para plano {tipo_plano} na data: {data_referencia}")
        
        try:
            # Calcula MRR do tipo de plano
            mrr_data = self.calculate_mrr_by_plan_type(tipo_plano, data_referencia)
            
            # ARR = MRR × 12
            arr_total = mrr_data["mrr_total"] * 12
            
            resultado = {
                "tipo_plano": tipo_plano,
                "arr_total": arr_total,
                "mrr_base": mrr_data["mrr_total"],
                "detalhes": mrr_data["detalhes"]
            }
            
            self.logger.info(f"ARR para plano {tipo_plano} calculado: R$ {arr_total:.2f}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular ARR para plano {tipo_plano}: {str(e)}")
            raise
    
    # ============================================================================
    # FASE 2: MÉTRICAS DE PERFORMANCE - IMPLEMENTAÇÃO
    # ============================================================================
    
    def calculate_arpu(self, data_referencia: datetime = None) -> Dict[str, Any]:
        """
        Calcula ARPU (Average Revenue Per User) - Receita média por usuário.
        
        Fórmula: ARPU = MRR Total / Número de Clientes Ativos
        
        Args:
            data_referencia: Data de referência para cálculos (padrão: hoje)
            
        Returns:
            Dict com ARPU total, por plataforma e breakdown de cálculo
        """
        if data_referencia is None:
            data_referencia = datetime.now()
            
        self.logger.info(f"Calculando ARPU para data: {data_referencia}")
        
        try:
            # Obtém MRR e clientes ativos
            mrr_data = self.calculate_mrr(data_referencia)
            clientes_data = self.calculate_unique_customers(data_referencia)
            
            mrr_total = mrr_data["mrr_total"]
            total_clientes = clientes_data["total_clientes_unicos"]
            
            # Calcula ARPU
            if total_clientes > 0:
                arpu_total = mrr_total / total_clientes
            else:
                arpu_total = 0
            
            # Calcula ARPU por plataforma
            arpu_por_plataforma = {}
            for plataforma, mrr in mrr_data["mrr_por_plataforma"].items():
                clientes_plataforma = clientes_data["detalhes"]["breakdown_por_plataforma"].get(plataforma, {}).get("total_clientes_unicos", 0)
                if clientes_plataforma > 0:
                    arpu_por_plataforma[plataforma] = mrr / clientes_plataforma
                else:
                    arpu_por_plataforma[plataforma] = 0
            
            resultado = {
                "arpu_total": arpu_total,
                "arpu_por_plataforma": arpu_por_plataforma,
                "mrr_base": mrr_total,
                "total_clientes_base": total_clientes,
                "formula": "ARPU = MRR Total / Total de Clientes Ativos",
                "detalhes": {
                    "data_referencia": data_referencia.isoformat(),
                    "breakdown_por_plataforma": {}
                }
            }
            
            # Adiciona breakdown por plataforma
            for plataforma in arpu_por_plataforma:
                resultado["detalhes"]["breakdown_por_plataforma"][plataforma] = {
                    "arpu": arpu_por_plataforma[plataforma],
                    "mrr": mrr_data["mrr_por_plataforma"].get(plataforma, 0),
                    "clientes": clientes_data["detalhes"]["breakdown_por_plataforma"].get(plataforma, {}).get("total_clientes_unicos", 0)
                }
            
            self.logger.info(f"ARPU calculado: R$ {arpu_total:.2f}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular ARPU: {str(e)}")
            raise
    
    def calculate_retention_rate(self, periodo_dias: int = 30) -> Dict[str, Any]:
        """
        Calcula Taxa de Retenção (Retention Rate).
        
        Fórmula: Retention Rate = 100% - Taxa de Churn
        
        Args:
            periodo_dias: Período para análise (padrão: 30 dias)
            
        Returns:
            Dict com taxa de retenção e detalhes
        """
        self.logger.info(f"Calculando Retention Rate para período: {periodo_dias} dias")
        
        try:
            # Obtém churn rate
            churn_data = self.calculate_churn_rate(periodo_dias)
            
            retention_rate_total = churn_data["renewal_rate_total"]
            retention_por_plataforma = {}
            
            # Calcula retenção por plataforma
            for plataforma, churn_rate in churn_data["churn_por_plataforma"].items():
                retention_por_plataforma[plataforma] = 100.0 - churn_rate
            
            resultado = {
                "retention_rate_total": retention_rate_total,
                "retention_por_plataforma": retention_por_plataforma,
                "churn_rate_base": churn_data["churn_rate_total"],
                "formula": "Retention Rate = 100% - Churn Rate",
                "periodo_dias": periodo_dias,
                "detalhes": churn_data["detalhes"]
            }
            
            self.logger.info(f"Retention Rate calculado: {retention_rate_total:.2f}%")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular Retention Rate: {str(e)}")
            raise
    
    def calculate_annual_revenue(self, data_referencia: datetime = None) -> Dict[str, Any]:
        """
        Calcula Receita Anual Total da Empresa.
        
        Fórmula: Receita Anual = ARR Total + Receitas Não-Recorrentes (se houver)
        
        Args:
            data_referencia: Data de referência para cálculos (padrão: hoje)
            
        Returns:
            Dict com receita anual total e breakdown
        """
        if data_referencia is None:
            data_referencia = datetime.now()
            
        self.logger.info(f"Calculando Receita Anual para data: {data_referencia}")
        
        try:
            # Obtém ARR
            arr_data = self.calculate_arr(data_referencia)
            
            # Busca receitas não-recorrentes (vendas pontuais)
            query = text("""
                SELECT 
                    plataforma,
                    COUNT(*) as total_vendas_pontuais,
                    COALESCE(SUM(valor), 0) as receita_pontual
                FROM transacoes 
                WHERE 
                    status = 'approved'
                    AND data_transacao <= :data_ref
                    AND assinatura_id IS NULL  -- Vendas sem assinatura (pontuais)
                GROUP BY plataforma
                ORDER BY plataforma
            """)
            
            result = self.db.execute(query, {"data_ref": data_referencia}).fetchall()
            
            receita_pontual_total = sum(Decimal(str(row.receita_pontual)) for row in result if row.receita_pontual)
            arr_total = arr_data["arr_total"]
            
            # Receita anual = ARR + Receitas pontuais
            receita_anual_total = arr_total + float(receita_pontual_total)
            
            resultado = {
                "receita_anual_total": receita_anual_total,
                "arr_componente": arr_total,
                "receita_pontual_componente": float(receita_pontual_total),
                "formula": "Receita Anual = ARR + Receitas Pontuais",
                "detalhes": {
                    "data_referencia": data_referencia.isoformat(),
                    "breakdown_por_plataforma": {},
                    "vendas_pontuais": {}
                }
            }
            
            # Adiciona breakdown por plataforma
            for row in result:
                plataforma = row.plataforma
                resultado["detalhes"]["breakdown_por_plataforma"][plataforma] = {
                    "arr": arr_data["arr_por_plataforma"].get(plataforma, 0),
                    "receita_pontual": float(row.receita_pontual) if row.receita_pontual else 0,
                    "receita_total": arr_data["arr_por_plataforma"].get(plataforma, 0) + float(row.receita_pontual) if row.receita_pontual else 0
                }
                
                resultado["detalhes"]["vendas_pontuais"][plataforma] = {
                    "total_vendas": row.total_vendas_pontuais,
                    "valor_total": float(row.receita_pontual) if row.receita_pontual else 0
                }
            
            self.logger.info(f"Receita Anual calculada: R$ {receita_anual_total:,.2f}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular Receita Anual: {str(e)}")
            raise
    
    def calculate_profit_margin(self, custos_operacionais: float = None, data_referencia: datetime = None) -> Dict[str, Any]:
        """
        Calcula Margem de Lucro.
        
        Fórmula: Margem de Lucro = (Receita - Custos) / Receita × 100
        
        Args:
            custos_operacionais: Custos operacionais totais (se não informado, retorna estrutura para preenchimento)
            data_referencia: Data de referência para cálculos (padrão: hoje)
            
        Returns:
            Dict com margem de lucro calculada ou estrutura para informar custos
        """
        if data_referencia is None:
            data_referencia = datetime.now()
            
        self.logger.info(f"Calculando Margem de Lucro para data: {data_referencia}")
        
        try:
            # Obtém receita anual
            receita_data = self.calculate_annual_revenue(data_referencia)
            receita_total = receita_data["receita_anual_total"]
            
            if custos_operacionais is not None and receita_total > 0:
                lucro_bruto = receita_total - custos_operacionais
                margem_lucro = (lucro_bruto / receita_total) * 100
                
                resultado = {
                    "margem_lucro_percentual": margem_lucro,
                    "margem_lucro_decimal": margem_lucro / 100,
                    "receita_total": receita_total,
                    "custos_operacionais": custos_operacionais,
                    "lucro_bruto": lucro_bruto,
                    "formula": "Margem = (Receita - Custos) / Receita × 100",
                    "detalhes": {
                        "data_referencia": data_referencia.isoformat(),
                        "breakdown_receita": receita_data["detalhes"]
                    }
                }
            else:
                resultado = {
                    "margem_lucro_percentual": None,
                    "margem_lucro_decimal": None,
                    "receita_total": receita_total,
                    "custos_operacionais": custos_operacionais,
                    "lucro_bruto": None,
                    "formula": "Margem = (Receita - Custos) / Receita × 100",
                    "instrucoes": "Para calcular a margem de lucro, forneça os custos_operacionais",
                    "detalhes": {
                        "data_referencia": data_referencia.isoformat(),
                        "breakdown_receita": receita_data["detalhes"]
                    }
                }
            
            self.logger.info(f"Margem de Lucro calculada: {resultado.get('margem_lucro_percentual', 'N/A')}%")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular Margem de Lucro: {str(e)}")
            raise
    
    def calculate_roi(self, investimento_total: float = None, periodo_dias: int = 365, data_referencia: datetime = None) -> Dict[str, Any]:
        """
        Calcula ROI (Return on Investment) Geral.
        
        Fórmula: ROI = (Receita - Investimento) / Investimento × 100
        
        Args:
            investimento_total: Investimento total realizado (se não informado, retorna estrutura para preenchimento)
            periodo_dias: Período para análise (padrão: 365 dias)
            data_referencia: Data de referência para cálculos (padrão: hoje)
            
        Returns:
            Dict com ROI calculado ou estrutura para informar investimento
        """
        if data_referencia is None:
            data_referencia = datetime.now()
            
        self.logger.info(f"Calculando ROI para período: {periodo_dias} dias")
        
        try:
            # Obtém receita do período
            if periodo_dias == 365:
                receita_data = self.calculate_annual_revenue(data_referencia)
                receita_periodo = receita_data["receita_anual_total"]
            else:
                # Para períodos diferentes de 1 ano, calcula proporcional
                receita_data = self.calculate_annual_revenue(data_referencia)
                receita_periodo = (receita_data["receita_anual_total"] / 365) * periodo_dias
            
            if investimento_total is not None and investimento_total > 0:
                retorno_liquido = receita_periodo - investimento_total
                roi_percentual = (retorno_liquido / investimento_total) * 100
                
                resultado = {
                    "roi_percentual": roi_percentual,
                    "roi_decimal": roi_percentual / 100,
                    "receita_periodo": receita_periodo,
                    "investimento_total": investimento_total,
                    "retorno_liquido": retorno_liquido,
                    "periodo_dias": periodo_dias,
                    "formula": "ROI = (Receita - Investimento) / Investimento × 100",
                    "detalhes": {
                        "data_referencia": data_referencia.isoformat(),
                        "breakdown_receita": receita_data["detalhes"]
                    }
                }
            else:
                resultado = {
                    "roi_percentual": None,
                    "roi_decimal": None,
                    "receita_periodo": receita_periodo,
                    "investimento_total": investimento_total,
                    "retorno_liquido": None,
                    "periodo_dias": periodo_dias,
                    "formula": "ROI = (Receita - Investimento) / Investimento × 100",
                    "instrucoes": "Para calcular o ROI, forneça o investimento_total",
                    "detalhes": {
                        "data_referencia": data_referencia.isoformat(),
                        "breakdown_receita": receita_data["detalhes"]
                    }
                }
            
            self.logger.info(f"ROI calculado: {resultado.get('roi_percentual', 'N/A')}%")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular ROI: {str(e)}")
            raise
    
    def calculate_subscriptions_by_month(self, ano: int = None) -> Dict[str, Any]:
        """
        Calcula assinaturas por mês para um ano específico.
        
        Args:
            ano: Ano para análise (padrão: ano atual)
            
        Returns:
            Dict com assinaturas por mês e estatísticas
        """
        if ano is None:
            ano = datetime.now().year
            
        self.logger.info(f"Calculando assinaturas por mês para ano: {ano}")
        
        try:
            query = text("""
                SELECT 
                    EXTRACT(MONTH FROM data_inicio) as mes,
                    COUNT(*) as total_assinaturas,
                    COUNT(CASE WHEN status NOT IN ('refunded', 'chargeback') THEN 1 END) as assinaturas_validas,
                    COUNT(CASE WHEN status IN ('canceled', 'subscription_canceled') THEN 1 END) as assinaturas_canceladas
                FROM assinaturas 
                WHERE 
                    EXTRACT(YEAR FROM data_inicio) = :ano
                GROUP BY EXTRACT(MONTH FROM data_inicio)
                ORDER BY mes
            """)
            
            result = self.db.execute(query, {"ano": ano}).fetchall()
            
            meses = {
                1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
                5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
                9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
            }
            
            assinaturas_por_mes = {}
            total_ano = 0
            total_validas_ano = 0
            total_canceladas_ano = 0
            
            for row in result:
                mes_num = int(row.mes)
                mes_nome = meses[mes_num]
                
                assinaturas_por_mes[mes_nome] = {
                    "mes_numero": mes_num,
                    "total_assinaturas": row.total_assinaturas,
                    "assinaturas_validas": row.assinaturas_validas,
                    "assinaturas_canceladas": row.assinaturas_canceladas,
                    "taxa_cancelamento_mes": (row.assinaturas_canceladas / row.total_assinaturas * 100) if row.total_assinaturas > 0 else 0
                }
                
                total_ano += row.total_assinaturas
                total_validas_ano += row.assinaturas_validas
                total_canceladas_ano += row.assinaturas_canceladas
            
            # Preenche meses sem dados
            for mes_num, mes_nome in meses.items():
                if mes_nome not in assinaturas_por_mes:
                    assinaturas_por_mes[mes_nome] = {
                        "mes_numero": mes_num,
                        "total_assinaturas": 0,
                        "assinaturas_validas": 0,
                        "assinaturas_canceladas": 0,
                        "taxa_cancelamento_mes": 0
                    }
            
            resultado = {
                "ano": ano,
                "total_assinaturas_ano": total_ano,
                "total_validas_ano": total_validas_ano,
                "total_canceladas_ano": total_canceladas_ano,
                "taxa_cancelamento_ano": (total_canceladas_ano / total_ano * 100) if total_ano > 0 else 0,
                "assinaturas_por_mes": assinaturas_por_mes,
                "detalhes": {
                    "meses_ordenados": sorted(assinaturas_por_mes.items(), key=lambda x: x[1]["mes_numero"])
                }
            }
            
            self.logger.info(f"Assinaturas por mês calculadas para {ano}: {total_ano} total")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular assinaturas por mês: {str(e)}")
            raise
    
    def calculate_average_ticket(self, data_referencia: datetime = None) -> Dict[str, Any]:
        """
        Calcula Ticket Médio Geral (valor médio por transação/assinatura).
        
        Args:
            data_referencia: Data de referência para cálculos (padrão: hoje)
            
        Returns:
            Dict com ticket médio geral e breakdown
        """
        if data_referencia is None:
            data_referencia = datetime.now()
            
        self.logger.info(f"Calculando Ticket Médio Geral para data: {data_referencia}")
        
        try:
            # Query para calcular ticket médio
            query = text("""
                SELECT 
                    plataforma,
                    COUNT(*) as total_transacoes,
                    COALESCE(AVG(valor), 0) as ticket_medio,
                    COALESCE(SUM(valor), 0) as receita_total
                FROM transacoes 
                WHERE 
                    status = 'approved'
                    AND data_transacao <= :data_ref
                GROUP BY plataforma
                ORDER BY plataforma
            """)
            
            result = self.db.execute(query, {"data_ref": data_referencia}).fetchall()
            
            ticket_medio_geral = 0
            total_transacoes_geral = 0
            receita_total_geral = 0
            ticket_por_plataforma = {}
            
            for row in result:
                plataforma = row.plataforma
                ticket_medio = float(row.ticket_medio) if row.ticket_medio else 0
                total_transacoes = row.total_transacoes
                receita_total = float(row.receita_total) if row.receita_total else 0
                
                ticket_por_plataforma[plataforma] = {
                    "ticket_medio": ticket_medio,
                    "total_transacoes": total_transacoes,
                    "receita_total": receita_total
                }
                
                total_transacoes_geral += total_transacoes
                receita_total_geral += receita_total
            
            # Calcula ticket médio geral ponderado
            if total_transacoes_geral > 0:
                ticket_medio_geral = receita_total_geral / total_transacoes_geral
            
            resultado = {
                "ticket_medio_geral": ticket_medio_geral,
                "total_transacoes_geral": total_transacoes_geral,
                "receita_total_geral": receita_total_geral,
                "ticket_por_plataforma": ticket_por_plataforma,
                "formula": "Ticket Médio = Receita Total / Total de Transações",
                "detalhes": {
                    "data_referencia": data_referencia.isoformat(),
                    "breakdown_por_plataforma": ticket_por_plataforma
                }
            }
            
            self.logger.info(f"Ticket Médio Geral calculado: R$ {ticket_medio_geral:.2f}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular Ticket Médio Geral: {str(e)}")
            raise
     
    # ============================================================================
    # FASE 3: MÉTRICAS AVANÇADAS - IMPLEMENTAÇÃO
    # ============================================================================
    
    def calculate_cpl(self, periodo_dias: int = 30, custo_marketing: float = None) -> Dict[str, Any]:
         """
         Calcula CPL (Cost Per Lead) - Custo por lead gerado.
         
         Fórmula: CPL = Custo Total de Marketing / Número de Leads Gerados
         
         Args:
             periodo_dias: Período para análise (padrão: 30 dias)
             custo_marketing: Custo de marketing no período (se não informado, retorna estrutura para preenchimento)
             
         Returns:
             Dict com CPL calculado ou estrutura para informar custos
         """
         data_fim = datetime.now()
         data_inicio = data_fim - timedelta(days=periodo_dias)
         
         self.logger.info(f"Calculando CPL para período: {data_inicio} - {data_fim}")
         
         try:
             # Query para contar leads gerados (assinaturas criadas no período)
             query = text("""
                 SELECT 
                     plataforma,
                     COUNT(*) as total_leads
                 FROM assinaturas 
                 WHERE 
                     data_inicio BETWEEN :data_inicio AND :data_fim
                 GROUP BY plataforma
                 ORDER BY plataforma
             """)
             
             result = self.db.execute(query, {
                 "data_inicio": data_inicio,
                 "data_fim": data_fim
             }).fetchall()
             
             total_leads = sum(row.total_leads for row in result)
             
             detalhes = {
                 "periodo": {
                     "data_inicio": data_inicio.isoformat(),
                     "data_fim": data_fim.isoformat(),
                     "dias": periodo_dias
                 },
                 "total_leads_periodo": total_leads,
                 "breakdown_por_plataforma": {}
             }
             
             for row in result:
                 detalhes["breakdown_por_plataforma"][row.plataforma] = {
                     "leads_gerados": row.total_leads
                 }
             
             if custo_marketing is not None and total_leads > 0:
                 cpl_total = custo_marketing / total_leads
                 
                 resultado = {
                     "cpl_total": cpl_total,
                     "custo_marketing_informado": custo_marketing,
                     "total_leads_periodo": total_leads,
                     "detalhes": detalhes
                 }
             else:
                 resultado = {
                     "cpl_total": None,
                     "custo_marketing_informado": custo_marketing,
                     "total_leads_periodo": total_leads,
                     "detalhes": detalhes,
                     "instrucoes": "Para calcular o CPL, forneça o custo_marketing do período"
                 }
             
             self.logger.info(f"CPL calculado - Total leads: {total_leads}")
             return resultado
             
         except Exception as e:
             self.logger.error(f"Erro ao calcular CPL: {str(e)}")
             raise
    
    def calculate_nps(self, data_referencia: datetime = None) -> Dict[str, Any]:
        """
        Calcula NPS (Net Promoter Score) baseado em dados de satisfação.
        
        Fórmula: NPS = % Promotores - % Detratores
        Onde:
        - Promotores: Clientes com score 9-10
        - Neutros: Clientes com score 7-8  
        - Detratores: Clientes com score 0-6
        
        Args:
            data_referencia: Data de referência para cálculos (padrão: hoje)
            
        Returns:
            Dict com NPS calculado e breakdown
        """
        if data_referencia is None:
            data_referencia = datetime.now()
            
        self.logger.info(f"Calculando NPS para data: {data_referencia}")
        
        try:
            # Query para calcular NPS baseado em dados disponíveis
            # Como não temos scores diretos, usamos métricas indiretas
            query = text("""
                 SELECT 
                     plataforma,
                     COUNT(*) as total_clientes,
                     
                     -- Promotores: Clientes ativos há mais de 6 meses (alta satisfação)
                     COUNT(CASE 
                         WHEN data_inicio <= :data_ref - INTERVAL '6 months'
                         AND data_expiracao_acesso >= :data_ref
                         AND status NOT IN ('canceled', 'subscription_canceled', 'refunded', 'chargeback')
                         THEN 1 
                     END) as promotores,
                     
                     -- Neutros: Clientes ativos há 1-6 meses
                     COUNT(CASE 
                         WHEN data_inicio > :data_ref - INTERVAL '6 months'
                         AND data_inicio <= :data_ref - INTERVAL '1 month'
                         AND data_expiracao_acesso >= :data_ref
                         AND status NOT IN ('canceled', 'subscription_canceled', 'refunded', 'chargeback')
                         THEN 1 
                     END) as neutros,
                     
                     -- Detratores: Clientes cancelados no último ano
                     COUNT(CASE 
                         WHEN status IN ('canceled', 'subscription_canceled')
                         AND ultima_atualizacao >= :data_ref - INTERVAL '12 months'
                         THEN 1 
                     END) as detratores
                     
                 FROM assinaturas 
                 WHERE 
                     data_inicio <= :data_ref
                 GROUP BY plataforma
                 ORDER BY plataforma
            """)
            
            result = self.db.execute(query, {"data_ref": data_referencia}).fetchall()
            
            nps_por_plataforma = {}
            total_promotores = 0
            total_neutros = 0
            total_detratores = 0
            total_clientes = 0
            
            for row in result:
                plataforma = row.plataforma
                promotores = row.promotores
                neutros = row.neutros
                detratores = row.detratores
                total_plataforma = row.total_clientes
                
                # Calcula NPS para a plataforma
                if total_plataforma > 0:
                    pct_promotores = (promotores / total_plataforma) * 100
                    pct_detratores = (detratores / total_plataforma) * 100
                    nps_plataforma = pct_promotores - pct_detratores
                else:
                    nps_plataforma = 0
                
                nps_por_plataforma[plataforma] = nps_plataforma
                
                # Acumula totais
                total_promotores += promotores
                total_neutros += neutros
                total_detratores += detratores
                total_clientes += total_plataforma
            
            # Calcula NPS total
            if total_clientes > 0:
                pct_promotores_total = (total_promotores / total_clientes) * 100
                pct_detratores_total = (total_detratores / total_clientes) * 100
                nps_total = pct_promotores_total - pct_detratores_total
            else:
                nps_total = 0
            
            resultado = {
                "nps_total": nps_total,
                "nps_por_plataforma": nps_por_plataforma,
                "breakdown_total": {
                    "total_clientes": total_clientes,
                    "promotores": total_promotores,
                    "neutros": total_neutros,
                    "detratores": total_detratores,
                    "pct_promotores": pct_promotores_total if total_clientes > 0 else 0,
                    "pct_neutros": (total_neutros / total_clientes * 100) if total_clientes > 0 else 0,
                    "pct_detratores": pct_detratores_total if total_clientes > 0 else 0
                },
                "metodo_calculo": "Baseado em tempo de permanência e status das assinaturas",
                "detalhes": {
                    "data_referencia": data_referencia.isoformat(),
                    "breakdown_por_plataforma": {}
                }
            }
            
            # Adiciona breakdown por plataforma
            for row in result:
                plataforma = row.plataforma
                resultado["detalhes"]["breakdown_por_plataforma"][plataforma] = {
                    "total_clientes": row.total_clientes,
                    "promotores": row.promotores,
                    "neutros": row.neutros,
                    "detratores": row.detratores,
                    "nps": nps_por_plataforma[plataforma]
                }
            
            self.logger.info(f"NPS calculado: {nps_total:.1f}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular NPS: {str(e)}")
            raise
    
    def calculate_mra(self, data_referencia: datetime = None) -> Dict[str, Any]:
         """
         Calcula MRA (Monthly Recurring Average) - Média de receita recorrente mensal.
         
         Fórmula: MRA = Soma de todas as receitas recorrentes / Número de meses
         
         Args:
             data_referencia: Data de referência para cálculos (padrão: hoje)
             
         Returns:
             Dict com MRA calculado e breakdown
         """
         if data_referencia is None:
             data_referencia = datetime.now()
             
         self.logger.info(f"Calculando MRA para data: {data_referencia}")
         
         try:
             # Query para calcular MRA baseado no histórico de assinaturas
             query = text("""
                 SELECT 
                     plataforma,
                     COUNT(*) as total_assinaturas,
                     
                     -- MRA baseado em valores mensais e anuais
                     AVG(
                         CASE 
                             WHEN valor_mensal IS NOT NULL THEN valor_mensal
                             WHEN valor_anual IS NOT NULL THEN valor_anual / 12.0
                             ELSE 0
                         END
                     ) as mra_medio,
                     
                     -- Soma total de receita recorrente
                     SUM(
                         CASE 
                             WHEN valor_mensal IS NOT NULL THEN valor_mensal
                             WHEN valor_anual IS NOT NULL THEN valor_anual / 12.0
                             ELSE 0
                         END
                     ) as receita_recorrente_total
                     
                 FROM assinaturas 
                 WHERE 
                     data_inicio <= :data_ref
                     AND status NOT IN ('refunded', 'chargeback')
                     AND (valor_mensal IS NOT NULL OR valor_anual IS NOT NULL)
                 GROUP BY plataforma
                 ORDER BY plataforma
             """)
             
             result = self.db.execute(query, {"data_ref": data_referencia}).fetchall()
             
             mra_por_plataforma = {}
             total_receita_recorrente = Decimal('0')
             total_assinaturas = 0
             
             for row in result:
                 plataforma = row.plataforma
                 mra_medio = float(row.mra_medio) if row.mra_medio else 0
                 receita_recorrente = float(row.receita_recorrente_total) if row.receita_recorrente_total else 0
                 
                 mra_por_plataforma[plataforma] = {
                     "mra_medio": mra_medio,
                     "receita_recorrente_total": receita_recorrente,
                     "total_assinaturas": row.total_assinaturas
                 }
                 
                 total_receita_recorrente += Decimal(str(receita_recorrente))
                 total_assinaturas += row.total_assinaturas
             
             # Calcula MRA total
             if total_assinaturas > 0:
                 mra_total = float(total_receita_recorrente / total_assinaturas)
             else:
                 mra_total = 0
             
             resultado = {
                 "mra_total": mra_total,
                 "mra_por_plataforma": mra_por_plataforma,
                 "total_receita_recorrente": float(total_receita_recorrente),
                 "total_assinaturas": total_assinaturas,
                 "formula": "MRA = Soma Receitas Recorrentes / Total Assinaturas",
                 "detalhes": {
                     "data_referencia": data_referencia.isoformat(),
                     "breakdown_por_plataforma": mra_por_plataforma
                 }
             }
             
             self.logger.info(f"MRA calculado: R$ {mra_total:.2f}")
             return resultado
             
         except Exception as e:
             self.logger.error(f"Erro ao calcular MRA: {str(e)}")
             raise
    
    def calculate_conversion_rate(self, periodo_dias: int = 30) -> Dict[str, Any]:
         """
         Calcula Taxa de Conversão (Lead to Customer).
         
         Fórmula: Taxa de Conversão = (Novos Clientes / Total de Leads) × 100
         
         Args:
             periodo_dias: Período para análise (padrão: 30 dias)
             
         Returns:
             Dict com taxa de conversão e breakdown
         """
         data_fim = datetime.now()
         data_inicio = data_fim - timedelta(days=periodo_dias)
         
         self.logger.info(f"Calculando Taxa de Conversão para período: {data_inicio} - {data_fim}")
         
         try:
             # Query para calcular conversão
             query = text("""
                 SELECT 
                     plataforma,
                     COUNT(*) as total_leads,
                     COUNT(CASE WHEN status NOT IN ('canceled', 'subscription_canceled', 'refunded', 'chargeback') THEN 1 END) as clientes_convertidos
                 FROM assinaturas 
                 WHERE 
                     data_inicio BETWEEN :data_inicio AND :data_fim
                 GROUP BY plataforma
                 ORDER BY plataforma
             """)
             
             result = self.db.execute(query, {
                 "data_inicio": data_inicio,
                 "data_fim": data_fim
             }).fetchall()
             
             conversao_por_plataforma = {}
             total_leads = 0
             total_convertidos = 0
             
             for row in result:
                 plataforma = row.plataforma
                 total_leads_plataforma = row.total_leads
                 convertidos_plataforma = row.clientes_convertidos
                 
                 # Calcula taxa de conversão para a plataforma
                 if total_leads_plataforma > 0:
                     taxa_conversao = (convertidos_plataforma / total_leads_plataforma) * 100
                 else:
                     taxa_conversao = 0
                 
                 conversao_por_plataforma[plataforma] = {
                     "taxa_conversao": taxa_conversao,
                     "total_leads": total_leads_plataforma,
                     "clientes_convertidos": convertidos_plataforma
                 }
                 
                 total_leads += total_leads_plataforma
                 total_convertidos += convertidos_plataforma
             
             # Calcula taxa de conversão total
             if total_leads > 0:
                 taxa_conversao_total = (total_convertidos / total_leads) * 100
             else:
                 taxa_conversao_total = 0
             
             resultado = {
                 "taxa_conversao_total": taxa_conversao_total,
                 "conversao_por_plataforma": conversao_por_plataforma,
                 "total_leads_periodo": total_leads,
                 "total_convertidos_periodo": total_convertidos,
                 "formula": "Taxa de Conversão = (Clientes Convertidos / Total de Leads) × 100",
                 "detalhes": {
                     "periodo": {
                         "data_inicio": data_inicio.isoformat(),
                         "data_fim": data_fim.isoformat(),
                         "dias": periodo_dias
                     },
                     "breakdown_por_plataforma": conversao_por_plataforma
                 }
             }
             
             self.logger.info(f"Taxa de Conversão calculada: {taxa_conversao_total:.2f}%")
             return resultado
             
         except Exception as e:
             self.logger.error(f"Erro ao calcular Taxa de Conversão: {str(e)}")
             raise
     
    def calculate_customer_health_score(self, data_referencia: datetime = None) -> Dict[str, Any]:
         """
         Calcula Customer Health Score baseado em múltiplos indicadores.
         
         Score baseado em:
         - Tempo de permanência
         - Frequência de pagamentos
         - Status da assinatura
         - Valor da assinatura
         
         Args:
             data_referencia: Data de referência para cálculos (padrão: hoje)
             
         Returns:
             Dict com health score e breakdown
         """
         if data_referencia is None:
             data_referencia = datetime.now()
             
         self.logger.info(f"Calculando Customer Health Score para data: {data_referencia}")
         
         try:
             # Query para calcular health score
             query = text("""
                 SELECT 
                     plataforma,
                     COUNT(*) as total_clientes,
                     
                     -- Clientes com alta saúde (score 8-10)
                     COUNT(CASE 
                         WHEN data_inicio <= :data_ref - INTERVAL '6 months'
                         AND data_expiracao_acesso >= :data_ref + INTERVAL '3 months'
                         AND status NOT IN ('canceled', 'subscription_canceled', 'refunded', 'chargeback')
                         AND (valor_anual IS NOT NULL OR valor_mensal IS NOT NULL)
                         THEN 1 
                     END) as alta_saude,
                     
                     -- Clientes com saúde média (score 5-7)
                     COUNT(CASE 
                         WHEN data_inicio > :data_ref - INTERVAL '6 months'
                         AND data_inicio <= :data_ref - INTERVAL '1 month'
                         AND data_expiracao_acesso >= :data_ref
                         AND status NOT IN ('canceled', 'subscription_canceled', 'refunded', 'chargeback')
                         THEN 1 
                     END) as saude_media,
                     
                     -- Clientes com baixa saúde (score 0-4)
                     COUNT(CASE 
                         WHEN (data_expiracao_acesso < :data_ref + INTERVAL '1 month'
                               OR status IN ('canceled', 'subscription_canceled'))
                         AND ultima_atualizacao >= :data_ref - INTERVAL '3 months'
                         THEN 1 
                     END) as baixa_saude
                     
                 FROM assinaturas 
                 WHERE 
                     data_inicio <= :data_ref
                 GROUP BY plataforma
                 ORDER BY plataforma
             """)
             
             result = self.db.execute(query, {"data_ref": data_referencia}).fetchall()
             
             health_por_plataforma = {}
             total_alta_saude = 0
             total_saude_media = 0
             total_baixa_saude = 0
             total_clientes = 0
             
             for row in result:
                 plataforma = row.plataforma
                 alta_saude = row.alta_saude
                 saude_media = row.saude_media
                 baixa_saude = row.baixa_saude
                 total_plataforma = row.total_clientes
                 
                 # Calcula health score para a plataforma (0-100)
                 if total_plataforma > 0:
                     # Peso: Alta saúde = 9, Média = 6, Baixa = 2
                     score_plataforma = ((alta_saude * 9) + (saude_media * 6) + (baixa_saude * 2)) / total_plataforma
                     score_percentual = (score_plataforma / 9) * 100  # Normaliza para 0-100
                 else:
                     score_percentual = 0
                 
                 health_por_plataforma[plataforma] = {
                     "health_score": score_percentual,
                     "alta_saude": alta_saude,
                     "saude_media": saude_media,
                     "baixa_saude": baixa_saude,
                     "total_clientes": total_plataforma
                 }
                 
                 # Acumula totais
                 total_alta_saude += alta_saude
                 total_saude_media += saude_media
                 total_baixa_saude += baixa_saude
                 total_clientes += total_plataforma
             
             # Calcula health score total
             if total_clientes > 0:
                 score_total = ((total_alta_saude * 9) + (total_saude_media * 6) + (total_baixa_saude * 2)) / total_clientes
                 health_score_total = (score_total / 9) * 100
             else:
                 health_score_total = 0
             
             resultado = {
                 "health_score_total": health_score_total,
                 "health_por_plataforma": health_por_plataforma,
                 "breakdown_total": {
                     "total_clientes": total_clientes,
                     "alta_saude": total_alta_saude,
                     "saude_media": total_saude_media,
                     "baixa_saude": total_baixa_saude,
                     "pct_alta_saude": (total_alta_saude / total_clientes * 100) if total_clientes > 0 else 0,
                     "pct_saude_media": (total_saude_media / total_clientes * 100) if total_clientes > 0 else 0,
                     "pct_baixa_saude": (total_baixa_saude / total_clientes * 100) if total_clientes > 0 else 0
                 },
                 "escala": "0-100 (0-40: Baixa, 41-70: Média, 71-100: Alta)",
                 "detalhes": {
                     "data_referencia": data_referencia.isoformat(),
                     "breakdown_por_plataforma": health_por_plataforma
                 }
             }
             
             self.logger.info(f"Customer Health Score calculado: {health_score_total:.1f}/100")
             return resultado
             
         except Exception as e:
             self.logger.error(f"Erro ao calcular Customer Health Score: {str(e)}")
             raise
     
    def calculate_revenue_growth_rate(self, periodo_dias: int = 365) -> Dict[str, Any]:
         """
         Calcula Revenue Growth Rate (Taxa de Crescimento da Receita).
         
         Fórmula: Growth Rate = ((Receita Atual - Receita Anterior) / Receita Anterior) × 100
         
         Args:
             periodo_dias: Período para análise (padrão: 365 dias)
             
         Returns:
             Dict com growth rate e breakdown
         """
         data_fim = datetime.now()
         data_inicio = data_fim - timedelta(days=periodo_dias)
         
         self.logger.info(f"Calculando Revenue Growth Rate para período: {data_inicio} - {data_fim}")
         
         try:
             # Obtém receita atual e anterior
             receita_atual_data = self.calculate_annual_revenue(data_fim)
             receita_anterior_data = self.calculate_annual_revenue(data_inicio)
             
             receita_atual = receita_atual_data["receita_anual_total"]
             receita_anterior = receita_anterior_data["receita_anual_total"]
             
             # Calcula growth rate
             if receita_anterior > 0:
                 growth_rate = ((receita_atual - receita_anterior) / receita_anterior) * 100
             else:
                 growth_rate = 0
             
             # Calcula growth rate por plataforma
             growth_por_plataforma = {}
             for plataforma in ["guru", "ticto"]:
                 receita_atual_plataforma = receita_atual_data["detalhes"]["breakdown_por_plataforma"].get(plataforma, {}).get("receita_total", 0)
                 receita_anterior_plataforma = receita_anterior_data["detalhes"]["breakdown_por_plataforma"].get(plataforma, {}).get("receita_total", 0)
                 
                 if receita_anterior_plataforma > 0:
                     growth_plataforma = ((receita_atual_plataforma - receita_anterior_plataforma) / receita_anterior_plataforma) * 100
                 else:
                     growth_plataforma = 0
                 
                 growth_por_plataforma[plataforma] = growth_plataforma
             
             resultado = {
                 "growth_rate_total": growth_rate,
                 "growth_por_plataforma": growth_por_plataforma,
                 "receita_atual": receita_atual,
                 "receita_anterior": receita_anterior,
                 "crescimento_absoluto": receita_atual - receita_anterior,
                 "periodo_dias": periodo_dias,
                 "formula": "Growth Rate = ((Receita Atual - Receita Anterior) / Receita Anterior) × 100",
                 "detalhes": {
                     "data_inicio": data_inicio.isoformat(),
                     "data_fim": data_fim.isoformat(),
                     "breakdown_por_plataforma": growth_por_plataforma
                 }
             }
             
             self.logger.info(f"Revenue Growth Rate calculado: {growth_rate:.2f}%")
             return resultado
             
         except Exception as e:
             self.logger.error(f"Erro ao calcular Revenue Growth Rate: {str(e)}")
             raise
     
    def calculate_customer_acquisition_velocity(self, periodo_dias: int = 30) -> Dict[str, Any]:
         """
         Calcula Customer Acquisition Velocity (Velocidade de Aquisição de Clientes).
         
         Fórmula: Velocity = Novos Clientes / Período em dias
         
         Args:
             periodo_dias: Período para análise (padrão: 30 dias)
             
         Returns:
             Dict com velocity e breakdown
         """
         data_fim = datetime.now()
         data_inicio = data_fim - timedelta(days=periodo_dias)
         
         self.logger.info(f"Calculando Customer Acquisition Velocity para período: {data_inicio} - {data_fim}")
         
         try:
             # Obtém dados de novos clientes
             cac_data = self.calculate_cac(periodo_dias)
             novos_clientes = cac_data["novos_clientes_periodo"]
             
             # Calcula velocity
             velocity_total = novos_clientes / periodo_dias
             
             # Calcula velocity por plataforma
             velocity_por_plataforma = {}
             for plataforma, dados in cac_data["detalhes"]["breakdown_por_plataforma"].items():
                 novos_clientes_plataforma = dados["novos_clientes"]
                 velocity_plataforma = novos_clientes_plataforma / periodo_dias
                 velocity_por_plataforma[plataforma] = velocity_plataforma
             
             resultado = {
                 "velocity_total": velocity_total,
                 "velocity_por_plataforma": velocity_por_plataforma,
                 "novos_clientes_periodo": novos_clientes,
                 "periodo_dias": periodo_dias,
                 "formula": "Velocity = Novos Clientes / Período em Dias",
                 "unidade": "clientes/dia",
                 "detalhes": {
                     "periodo": {
                         "data_inicio": data_inicio.isoformat(),
                         "data_fim": data_fim.isoformat(),
                         "dias": periodo_dias
                     },
                     "breakdown_por_plataforma": velocity_por_plataforma
                 }
             }
             
             self.logger.info(f"Customer Acquisition Velocity calculado: {velocity_total:.2f} clientes/dia")
             return resultado
             
         except Exception as e:
             self.logger.error(f"Erro ao calcular Customer Acquisition Velocity: {str(e)}")
             raise
    
    def get_dashboard_metrics(self, data_referencia: datetime = None, periodo_analise: int = 30) -> Dict[str, Any]:
        """
        Retorna todas as métricas consolidadas para o dashboard.
        
        Args:
            data_referencia: Data de referência para cálculos (padrão: hoje)
            periodo_analise: Período em dias para análises temporais (padrão: 30)
            
        Returns:
            Dict com todas as métricas calculadas e prontas para o dashboard
        """
        if data_referencia is None:
            data_referencia = datetime.now()
        
        self.logger.info(f"Calculando métricas consolidadas para dashboard - Data: {data_referencia}")
        
        try:
            # Calcula todas as métricas
            mrr_data = self.calculate_mrr(data_referencia)
            arr_data = self.calculate_arr(data_referencia)
            churn_data = self.calculate_churn_rate(periodo_analise)
            ltv_data = self.calculate_ltv(data_referencia)
            cac_data = self.calculate_cac(periodo_analise)
            
            # Consolida métricas principais
            metricas_principais = {
                "mrr": {
                    "valor": mrr_data["mrr_total"],
                    "moeda": "BRL",
                    "descricao": "Monthly Recurring Revenue"
                },
                "arr": {
                    "valor": arr_data["arr_total"],
                    "moeda": "BRL",
                    "descricao": "Annual Recurring Revenue"
                },
                "churn_rate": {
                    "valor": churn_data["churn_rate_total"],
                    "unidade": "%",
                    "descricao": f"Taxa de Churn ({periodo_analise} dias)"
                },
                "renewal_rate": {
                    "valor": churn_data["renewal_rate_total"],
                    "unidade": "%",
                    "descricao": "Taxa de Renovação"
                },
                "ltv": {
                    "valor": ltv_data["ltv_total"],
                    "moeda": "BRL",
                    "descricao": "Customer Lifetime Value"
                },
                "total_assinaturas_ativas": {
                    "valor": mrr_data["detalhes"]["total_assinaturas_ativas"],
                    "unidade": "unidades",
                    "descricao": "Total de Assinaturas Ativas"
                }
            }
            
            # Métricas por plataforma
            metricas_por_plataforma = {}
            for plataforma in ["guru", "ticto"]:
                metricas_por_plataforma[plataforma] = {
                    "mrr": mrr_data["mrr_por_plataforma"].get(plataforma, 0),
                    "arr": arr_data["arr_por_plataforma"].get(plataforma, 0),
                    "churn_rate": churn_data["churn_por_plataforma"].get(plataforma, 0),
                    "ltv": ltv_data["ltv_por_plataforma"].get(plataforma, 0)
                }
            
            # Métricas por tipo de plano
            breakdown_tipo_plano = mrr_data["detalhes"]["breakdown_por_tipo"]
            
            resultado = {
                "data_calculo": datetime.now().isoformat(),
                "data_referencia": data_referencia.isoformat(),
                "periodo_analise_dias": periodo_analise,
                
                "metricas_principais": metricas_principais,
                "metricas_por_plataforma": metricas_por_plataforma,
                "breakdown_por_tipo_plano": breakdown_tipo_plano,
                
                "detalhes_completos": {
                    "mrr": mrr_data,
                    "arr": arr_data,
                    "churn": churn_data,
                    "ltv": ltv_data,
                    "cac": cac_data
                }
            }
            
            self.logger.info("Métricas consolidadas calculadas com sucesso")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular métricas consolidadas: {str(e)}")
            raise

    def validate_data_integrity(self) -> Dict[str, Any]:
        """
        Valida a integridade dos dados para cálculo de métricas.
        
        Returns:
            Dict com resultado da validação e estatísticas
        """
        self.logger.info("Executando validação de integridade dos dados")
        
        try:
            validation_query = text("""
                SELECT 
                    -- Estatísticas gerais
                    COUNT(*) as total_assinaturas,
                    COUNT(CASE WHEN valor_mensal IS NOT NULL THEN 1 END) as com_valor_mensal,
                    COUNT(CASE WHEN valor_anual IS NOT NULL THEN 1 END) as com_valor_anual,
                    COUNT(CASE WHEN valor_mensal IS NULL AND valor_anual IS NULL THEN 1 END) as sem_valores,
                    
                    -- Validações por plataforma
                    COUNT(CASE WHEN plataforma = 'guru' THEN 1 END) as guru_total,
                    COUNT(CASE WHEN plataforma = 'ticto' THEN 1 END) as ticto_total,
                    
                    -- Status das assinaturas
                    COUNT(CASE WHEN status IN ('canceled', 'subscription_canceled') THEN 1 END) as canceladas,
                    COUNT(CASE WHEN status IN ('refunded', 'chargeback') THEN 1 END) as reembolsadas,
                    COUNT(CASE WHEN status NOT IN ('canceled', 'subscription_canceled', 'refunded', 'chargeback') THEN 1 END) as ativas
                    
                FROM assinaturas
            """)
            
            result = self.db.execute(validation_query).fetchone()
            
            # Calcula percentuais
            total = result.total_assinaturas
            validation_result = {
                "total_assinaturas": total,
                "integridade_valores": {
                    "com_valor_mensal": result.com_valor_mensal,
                    "com_valor_anual": result.com_valor_anual,
                    "sem_valores": result.sem_valores,
                    "percentual_sem_valores": (result.sem_valores / total * 100) if total > 0 else 0
                },
                "distribuicao_plataforma": {
                    "guru": result.guru_total,
                    "ticto": result.ticto_total
                },
                "distribuicao_status": {
                    "ativas": result.ativas,
                    "canceladas": result.canceladas,
                    "reembolsadas": result.reembolsadas
                },
                "alertas": []
            }
            
            # Gera alertas se necessário
            if result.sem_valores > 0:
                validation_result["alertas"].append(
                    f"Encontradas {result.sem_valores} assinaturas sem valor_mensal nem valor_anual"
                )
            
            if result.sem_valores / total > 0.05:  # Mais de 5%
                validation_result["alertas"].append(
                    "CRÍTICO: Mais de 5% das assinaturas estão sem valores definidos"
                )
            
            self.logger.info(f"Validação concluída - {len(validation_result['alertas'])} alertas gerados")
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Erro na validação de integridade: {str(e)}")
            raise

    # ============================================================================
    # FASE 4: MÉTRICAS DE SEGMENTAÇÃO TEMPORAL
    # ============================================================================
    
    def calculate_subscriptions_current_month(self, data_referencia: datetime = None) -> Dict[str, Any]:
        """
        Calcula assinaturas criadas no mês atual.
        
        Args:
            data_referencia: Data de referência (padrão: hoje)
            
        Returns:
            Dict com total de assinaturas do mês atual e breakdown
        """
        if data_referencia is None:
            data_referencia = datetime.now()
        
        # Define início e fim do mês atual
        inicio_mes = data_referencia.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if data_referencia.month == 12:
            fim_mes = data_referencia.replace(year=data_referencia.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            fim_mes = data_referencia.replace(month=data_referencia.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        self.logger.info(f"Calculando assinaturas do mês atual: {inicio_mes.strftime('%B/%Y')}")
        
        try:
            # Query para assinaturas do mês atual
            query = text("""
                SELECT 
                    COUNT(*) as total_assinaturas,
                    COUNT(CASE WHEN plataforma = 'guru' THEN 1 END) as guru,
                    COUNT(CASE WHEN plataforma = 'ticto' THEN 1 END) as ticto,
                    COUNT(CASE WHEN valor_mensal IS NOT NULL THEN 1 END) as planos_mensais,
                    COUNT(CASE WHEN valor_anual IS NOT NULL THEN 1 END) as planos_anuais,
                    COUNT(CASE WHEN status NOT IN ('canceled', 'subscription_canceled', 'refunded', 'chargeback') THEN 1 END) as ativas,
                    COUNT(CASE WHEN status IN ('canceled', 'subscription_canceled') THEN 1 END) as canceladas
                FROM assinaturas 
                WHERE data_inicio >= :inicio_mes 
                AND data_inicio < :fim_mes
            """)
            
            result = self.db.execute(query, {
                "inicio_mes": inicio_mes,
                "fim_mes": fim_mes
            }).fetchone()
            
            resultado = {
                "total_assinaturas_mes_atual": result.total_assinaturas,
                "mes_referencia": inicio_mes.strftime("%B/%Y"),
                "periodo": {
                    "inicio": inicio_mes.isoformat(),
                    "fim": fim_mes.isoformat()
                },
                "breakdown_por_plataforma": {
                    "guru": result.guru,
                    "ticto": result.ticto
                },
                "breakdown_por_tipo": {
                    "planos_mensais": result.planos_mensais,
                    "planos_anuais": result.planos_anuais
                },
                "breakdown_por_status": {
                    "ativas": result.ativas,
                    "canceladas": result.canceladas
                },
                "formula": "COUNT(*) FROM assinaturas WHERE data_inicio >= início_mês_atual",
                "unidade": "assinaturas"
            }
            
            self.logger.info(f"Assinaturas do mês atual: {result.total_assinaturas}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular assinaturas do mês atual: {str(e)}")
            raise
    
    def calculate_subscriptions_previous_month(self, data_referencia: datetime = None) -> Dict[str, Any]:
        """
        Calcula assinaturas criadas no mês anterior.
        
        Args:
            data_referencia: Data de referência (padrão: hoje)
            
        Returns:
            Dict com total de assinaturas do mês anterior e breakdown
        """
        if data_referencia is None:
            data_referencia = datetime.now()
        
        # Define início e fim do mês anterior
        if data_referencia.month == 1:
            inicio_mes_anterior = data_referencia.replace(year=data_referencia.year - 1, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            inicio_mes_anterior = data_referencia.replace(month=data_referencia.month - 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        fim_mes_anterior = data_referencia.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        self.logger.info(f"Calculando assinaturas do mês anterior: {inicio_mes_anterior.strftime('%B/%Y')}")
        
        try:
            # Query para assinaturas do mês anterior
            query = text("""
                SELECT 
                    COUNT(*) as total_assinaturas,
                    COUNT(CASE WHEN plataforma = 'guru' THEN 1 END) as guru,
                    COUNT(CASE WHEN plataforma = 'ticto' THEN 1 END) as ticto,
                    COUNT(CASE WHEN valor_mensal IS NOT NULL THEN 1 END) as planos_mensais,
                    COUNT(CASE WHEN valor_anual IS NOT NULL THEN 1 END) as planos_anuais,
                    COUNT(CASE WHEN status NOT IN ('canceled', 'subscription_canceled', 'refunded', 'chargeback') THEN 1 END) as ativas,
                    COUNT(CASE WHEN status IN ('canceled', 'subscription_canceled') THEN 1 END) as canceladas
                FROM assinaturas 
                WHERE data_inicio >= :inicio_mes 
                AND data_inicio < :fim_mes
            """)
            
            result = self.db.execute(query, {
                "inicio_mes": inicio_mes_anterior,
                "fim_mes": fim_mes_anterior
            }).fetchone()
            
            resultado = {
                "total_assinaturas_mes_anterior": result.total_assinaturas,
                "mes_referencia": inicio_mes_anterior.strftime("%B/%Y"),
                "periodo": {
                    "inicio": inicio_mes_anterior.isoformat(),
                    "fim": fim_mes_anterior.isoformat()
                },
                "breakdown_por_plataforma": {
                    "guru": result.guru,
                    "ticto": result.ticto
                },
                "breakdown_por_tipo": {
                    "planos_mensais": result.planos_mensais,
                    "planos_anuais": result.planos_anuais
                },
                "breakdown_por_status": {
                    "ativas": result.ativas,
                    "canceladas": result.canceladas
                },
                "formula": "COUNT(*) FROM assinaturas WHERE data_inicio >= início_mês_anterior",
                "unidade": "assinaturas"
            }
            
            self.logger.info(f"Assinaturas do mês anterior: {result.total_assinaturas}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular assinaturas do mês anterior: {str(e)}")
            raise