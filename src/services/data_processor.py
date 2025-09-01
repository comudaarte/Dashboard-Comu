"""
Serviço para processamento de dados históricos das APIs
Separa a lógica de backfill da lógica de webhooks em tempo real
"""

from typing import Dict, Any, Optional
from src.database.connection import get_session
from src.database.models import Transacao, Cliente, Assinatura
from src.services.webhook_handler import get_or_create_cliente, get_or_create_assinatura, salvar_transacao
from src.utils.mapeamento_backfill import MapeamentoBackfillTicto, MapeamentoBackfillGuru, converter_data_backfill
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class HistoricalDataProcessor:
    """
    Processador de dados históricos das APIs Ticto e Guru
    Reutiliza funções do webhook_handler mas tem lógica própria para backfill
    """
    
    def __init__(self):
        self.session = get_session()
    
    def process_ticto_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa dados históricos de order da Ticto usando o novo mapeamento
        APENAS para transações - não cria assinaturas
        """
        try:
            # Usa o novo mapeamento
            mapeamento = MapeamentoBackfillTicto.mapear_order_ticto(order_data)
            
            # 1. Cliente
            cliente = get_or_create_cliente(
                self.session,
                nome=mapeamento["cliente"]["nome"],
                email=mapeamento["cliente"]["email"],
                documento=mapeamento["cliente"]["documento"],
                data_criacao=mapeamento["cliente"]["data_criacao"]
            )
            
            # 2. Transação (APENAS transação, sem criar assinatura)
            id_transacao_origem = mapeamento["id_transacao_origem"]
            product_name = mapeamento["produto"]["nome"]
            
            # Verifica se já existe
            transacao_existente = self.session.query(Transacao).filter_by(
                id_transacao_origem=id_transacao_origem, 
                produto_nome=product_name
            ).first()
            
            if transacao_existente:
                # Atualiza campos relevantes
                transacao_existente.status = mapeamento["status"]
                transacao_existente.valor = mapeamento["valor"]
                transacao_existente.valor_bruto = mapeamento["valor_bruto"]
                transacao_existente.valor_liquido = mapeamento["valor_liquido"]
                transacao_existente.metodo_pagamento = mapeamento["metodo_pagamento"]
                transacao_existente.tipo_recusa = mapeamento["tipo_recusa"]
                transacao_existente.motivo_recusa = mapeamento["motivo_recusa"]
                transacao_existente.data_transacao = converter_data_backfill(mapeamento["data_transacao"])
                
                self.session.commit()
                return {"status": "transacao_atualizada", "transacao_id": transacao_existente.id}
            else:
                # Cria nova transação (SEM assinatura_id)
                nome_oferta = mapeamento.get("oferta", {}).get("nome")
                transacao_dict = {
                    "id_transacao_origem": id_transacao_origem,
                    "cliente_id": cliente.id,
                    "assinatura_id": None,  # Orders não criam assinaturas no backfill
                    "plataforma": "ticto",
                    "status": mapeamento["status"],
                    "valor": mapeamento["valor"],
                    "valor_bruto": mapeamento["valor_bruto"],
                    "valor_liquido": mapeamento["valor_liquido"],
                    "metodo_pagamento": mapeamento["metodo_pagamento"],
                    "data_transacao": converter_data_backfill(mapeamento["data_transacao"]),
                    "motivo_recusa": mapeamento["motivo_recusa"],
                    "tipo_recusa": mapeamento["tipo_recusa"],
                    "produto_nome": product_name,
                    "nome_oferta": nome_oferta,
                    "json_completo": {
                        "order_data": order_data,
                        "mapeamento": mapeamento,
                        "processed_by": "historical_data_processor"
                    }
                }
                
                transacao_id = salvar_transacao(transacao_dict)
                return {"status": "transacao_criada", "transacao_id": transacao_id}
                
        except Exception as e:
            logger.error(f"Erro ao processar order Ticto {order_data.get('id')}: {e}")
            return {"status": "erro", "motivo": str(e)}
    
    def process_ticto_subscription(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa dados históricos de subscription da Ticto usando o novo mapeamento
        APENAS para assinaturas - não cria transações
        """
        try:
            # Usa o novo mapeamento
            mapeamento = MapeamentoBackfillTicto.mapear_subscription_ticto(subscription_data)
            
            # 1. Cliente
            cliente = get_or_create_cliente(
                self.session,
                nome=mapeamento["cliente"]["nome"],
                email=mapeamento["cliente"]["email"],
                documento=mapeamento["cliente"]["documento"],
                data_criacao=mapeamento["cliente"]["data_criacao"]
            )
            
            # 2. Assinatura (APENAS assinatura, sem criar transação)
            id_assinatura_origem = mapeamento["id_assinatura_origem"]
            product_name = mapeamento["produto"]["nome"]
            
            # Verifica se já existe
            assinatura_existente = self.session.query(Assinatura).filter_by(
                id_assinatura_origem=id_assinatura_origem
            ).first()
            
            if assinatura_existente:
                # Atualiza campos relevantes
                assinatura_existente.status = mapeamento["status"]
                assinatura_existente.valor_mensal = mapeamento["valor_mensal"]
                assinatura_existente.valor_anual = mapeamento["valor_anual"]
                assinatura_existente.data_proxima_cobranca = converter_data_backfill(mapeamento["data_proxima_cobranca"])
                assinatura_existente.data_cancelamento = converter_data_backfill(mapeamento["data_cancelamento"])
                assinatura_existente.ultima_atualizacao = datetime.now()
                
                self.session.commit()
                return {"status": "assinatura_atualizada", "assinatura_id": assinatura_existente.id}
            else:
                # Cria nova assinatura (SEM transação associada)
                nome_oferta = subscription_data.get("offer", {}).get("name")
                assinatura = get_or_create_assinatura(
                    self.session,
                    id_assinatura_origem=id_assinatura_origem,
                    plataforma="ticto",
                    cliente_id=cliente.id,
                    produto_nome=product_name,
                    nome_oferta=nome_oferta,
                    status=mapeamento["status"],
                    data_inicio=converter_data_backfill(mapeamento["data_inicio"]),
                    data_proxima_cobranca=converter_data_backfill(mapeamento["data_proxima_cobranca"]),
                    data_cancelamento=converter_data_backfill(mapeamento["data_cancelamento"]),
                    data_expiracao_acesso=self._calcular_data_expiracao_ticto(subscription_data) or datetime.now() + timedelta(days=365),
                    valor_mensal=mapeamento["valor_mensal"],
                    valor_anual=mapeamento["valor_anual"],
                    ultima_atualizacao=datetime.now()
                )
                
                return {"status": "assinatura_criada", "assinatura_id": assinatura.id}
                
        except Exception as e:
            logger.error(f"Erro ao processar subscription Ticto {subscription_data.get('id')}: {e}")
            return {"status": "erro", "motivo": str(e)}
    
    def process_guru_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa dados históricos de order da Guru
        """
        try:
            # Implementar lógica similar para Guru
            # Por enquanto, retorna erro
            return {"status": "erro", "motivo": "Processamento Guru não implementado ainda"}
            
        except Exception as e:
            logger.error(f"Erro ao processar order Guru {order_data.get('id')}: {e}")
            return {"status": "erro", "motivo": str(e)}
    
    def _identificar_tipo_plano_ticto(self, product_id: Optional[str], offer_code: Optional[str]) -> str:
        """
        Identifica o tipo de plano baseado no product_id e offer_code
        """
        # Implementar lógica de identificação de plano
        # Por enquanto, retorna "anual" como padrão
        return "anual"
    
    def _process_ticto_subscription_from_order(self, order_data: Dict[str, Any], cliente: Cliente, tipo_plano: str) -> Optional[Assinatura]:
        """
        Processa assinatura a partir de dados de order
        """
        try:
            # Lógica para criar/atualizar assinatura baseada em order
            # Por enquanto, retorna None
            return None
        except Exception as e:
            logger.error(f"Erro ao processar assinatura de order: {e}")
            return None
    
    def _calcular_data_expiracao_ticto(self, subscription_data: Dict[str, Any]) -> Optional[datetime]:
        """
        Calcula data de expiração para assinatura Ticto
        """
        try:
            # Pega a data de início da assinatura
            data_inicio = converter_data_backfill(subscription_data.get("order", {}).get("created_at"))
            if not data_inicio:
                return None
            
            # Calcula baseado no intervalo
            interval = subscription_data.get("interval", 12)
            if interval == 12:  # Anual
                return data_inicio + timedelta(days=365)
            elif interval == 1:  # Mensal
                return data_inicio + timedelta(days=30)
            else:
                # Fallback: assume anual
                return data_inicio + timedelta(days=365)
                
        except Exception as e:
            logger.error(f"Erro ao calcular data de expiração: {e}")
            return None
    
    def close_session(self):
        """
        Fecha a sessão do banco de dados
        """
        if self.session:
            self.session.close() 