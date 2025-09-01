# Webhook handler service 

from utils.validators import validar_payload_guru, validar_payload_ticto
from utils.helpers import mapear_transacao_ticto, mapear_transacao_guru, identificar_tipo_plano_guru, identificar_tipo_plano_ticto, identificar_tipo_produto_ticto, identificar_tipo_produto_guru, tipo_venda_recusada_ticto
from database.models import Transacao, Cliente, Assinatura
from database.connection import get_session
from sqlalchemy.exc import NoResultFound
from datetime import datetime, timedelta

def get_or_create_cliente(session, nome, email, documento, data_criacao):
    cliente = session.query(Cliente).filter_by(email=email).first()
    if cliente:
        return cliente
    cliente = Cliente(
        nome=nome,
        email=email,
        documento=documento,
        data_criacao=converter_data(data_criacao)
    )
    session.add(cliente)
    session.commit()
    return cliente

def calcular_valor_mensal_guru(payload):
    """
    Calcula o valor mensal correto baseado no ID do produto.
    Para planos anuais, divide o valor total por 12.
    Para planos mensais, usa o valor total.
    """
    valor_total = payload["payment"].get("total", 0)
    product_id = payload.get("product", {}).get("id")
    
    # Identifica o tipo de plano
    tipo_plano = identificar_tipo_plano_guru(product_id)
    
    if tipo_plano == "anual":
        valor_mensal = valor_total / 12
        print(f"[GURU] Plano anual detectado (ID: {product_id}), valor total: R$ {valor_total}, valor mensal: R$ {valor_mensal:.2f}")
        return valor_mensal
    elif tipo_plano == "mensal":
        valor_mensal = valor_total
        print(f"[GURU] Plano mensal detectado (ID: {product_id}), valor mensal: R$ {valor_mensal}")
        return valor_mensal
    else:
        # Fallback: assume mensal se não conseguir identificar
        print(f"[GURU] Plano não identificado (ID: {product_id}), usando valor total como mensal: R$ {valor_total}")
        return valor_total

def calcular_data_expiracao_guru(payload):
    """
    Calcula a data de expiração para assinaturas Guru.
    Usa confirmed_at como referência para o início do ciclo.
    """
    # 1. Pega a data de confirmação
    data_confirmacao = converter_data(payload["dates"].get("confirmed_at"))
    product_id = payload.get("product", {}).get("id")
    tipo_plano = identificar_tipo_plano_guru(product_id)

    # --- CORREÇÃO: garantir que subscription é dict ou None ---
    subscription = payload.get("subscription")
    if isinstance(subscription, list):
        subscription = None
    # --- Fim correção ---

    if data_confirmacao:
        if tipo_plano == "anual":
            dias = 365
            print(f"[GURU] Plano anual detectado (ID: {product_id}), confirmed_at, usando {dias} dias")
        elif tipo_plano == "mensal":
            dias = 30
            print(f"[GURU] Plano mensal detectado (ID: {product_id}), confirmed_at, usando {dias} dias")
        else:
            dias = subscription.get("charged_every_days", 30) if subscription else 30
            print(f"[GURU] Plano não identificado (ID: {product_id}), confirmed_at, usando {dias} dias")
        return data_confirmacao + timedelta(days=dias)

    # 2. Fallback: usa started_at
    data_inicio = converter_data(subscription.get("started_at") if subscription else None)
    if data_inicio:
        if tipo_plano == "anual":
            dias = 365
        elif tipo_plano == "mensal":
            dias = 30
        else:
            dias = subscription.get("charged_every_days", 30) if subscription else 30
        return data_inicio + timedelta(days=dias)

    # 3. Último fallback: data atual + 30 dias
    return datetime.now() + timedelta(days=30)

def get_or_create_assinatura(session, id_assinatura_origem, plataforma, cliente_id, produto_nome, nome_oferta, status, data_inicio, data_proxima_cobranca, data_cancelamento, data_expiracao_acesso, valor_mensal, valor_anual, ultima_atualizacao):
    # Garante que o id_assinatura_origem é string
    id_assinatura_origem = str(id_assinatura_origem) if id_assinatura_origem is not None else None
    assinatura = session.query(Assinatura).filter_by(id_assinatura_origem=id_assinatura_origem).first()
    if assinatura:
        # Validação de integridade: verifica se dados do webhook são mais recentes
        webhook_data_atualizacao = converter_data(ultima_atualizacao)

        # CORREÇÃO: Garante que ambas as datas tenham timezone antes da comparação
        if webhook_data_atualizacao and assinatura.ultima_atualizacao:
            from datetime import timezone
            
            # Garante que webhook_data_atualizacao tenha timezone
            if webhook_data_atualizacao.tzinfo is None:
                webhook_data_atualizacao = webhook_data_atualizacao.replace(tzinfo=timezone.utc)
            
            # Garante que assinatura.ultima_atualizacao tenha timezone
            if assinatura.ultima_atualizacao.tzinfo is None:
                assinatura_data_with_tz = assinatura.ultima_atualizacao.replace(tzinfo=timezone.utc)
            else:
                assinatura_data_with_tz = assinatura.ultima_atualizacao

            if webhook_data_atualizacao < assinatura_data_with_tz:
                print(f"[SYNC] ⚠️ Webhook com data anterior ignorado: {webhook_data_atualizacao} < {assinatura_data_with_tz}")
                return assinatura  # Retorna sem atualizar
        
        assinatura.plataforma = plataforma
        assinatura.cliente_id = cliente_id
        assinatura.produto_nome = produto_nome
        assinatura.nome_oferta = nome_oferta
        assinatura.status = status
        # NÃO atualizar data_inicio em updates!
        # assinatura.data_inicio = converter_data(data_inicio)
        assinatura.data_proxima_cobranca = converter_data(data_proxima_cobranca)
        
        # Lógica para data_cancelamento
        if status in ["active", "uncanceled"]:
            # Se voltou a ficar ativa, limpa data_cancelamento
            if assinatura.data_cancelamento:
                assinatura.data_cancelamento = None
                print(f"[DB] data_cancelamento limpo para assinatura ativa: {assinatura.id}")
        elif status != "active" and not assinatura.data_cancelamento:
            # Se ficou inativa e ainda não tem data_cancelamento, preenche
            assinatura.data_cancelamento = converter_data(data_cancelamento) or converter_data(ultima_atualizacao)
            print(f"[DB] data_cancelamento preenchido: {assinatura.data_cancelamento}")
        
        assinatura.data_expiracao_acesso = converter_data(data_expiracao_acesso)
        assinatura.valor_mensal = valor_mensal
        assinatura.valor_anual = valor_anual
        assinatura.ultima_atualizacao = converter_data(ultima_atualizacao)
        session.commit()
        print(f"[DB] Assinatura atualizada: ID {assinatura.id}, valor mensal: {valor_mensal}, valor anual: {valor_anual}")
        print(f"[SYNC] ✅ Webhook atualizou assinatura do backfill: {assinatura.id_assinatura_origem}")
        return assinatura
    assinatura = Assinatura(
        id_assinatura_origem=id_assinatura_origem,
        plataforma=plataforma,
        cliente_id=cliente_id,
        produto_nome=produto_nome,
        nome_oferta=nome_oferta,
        status=status,
        data_inicio=converter_data(data_inicio),
        data_proxima_cobranca=converter_data(data_proxima_cobranca),
        data_cancelamento=converter_data(data_cancelamento) if status not in ["active", "uncanceled"] else None,
        data_expiracao_acesso=converter_data(data_expiracao_acesso),
        valor_mensal=valor_mensal,
        valor_anual=valor_anual,
        ultima_atualizacao=converter_data(ultima_atualizacao)
    )
    session.add(assinatura)
    session.commit()
    print(f"[DB] Nova assinatura criada: ID {assinatura.id}, valor mensal: {valor_mensal}, valor anual: {valor_anual}")
    return assinatura

def converter_data(valor):
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        # Timestamp (segundos) - converte para timezone-aware
        from datetime import timezone
        return datetime.fromtimestamp(valor, tz=timezone.utc)
    if isinstance(valor, str):
        try:
            # Tenta converter string ISO - garante timezone-aware
            if valor.endswith('Z'):
                valor = valor.replace('Z', '+00:00')
            elif '+' not in valor and '-' in valor and 'T' in valor:
                # Assume UTC se não tem timezone
                valor = valor + '+00:00'
            return datetime.fromisoformat(valor)
        except Exception:
            pass
        try:
            # Tenta converter formato brasileiro: 'DD/MM/YYYY HH:MM:SS'
            dt = datetime.strptime(valor, "%d/%m/%Y %H:%M:%S")
            # Assume UTC para datas brasileiras
            from datetime import timezone
            return dt.replace(tzinfo=timezone.utc)
        except Exception:
            pass
    return valor

def salvar_transacao(transacao_dict: dict):
    session = get_session()
    try:
        transacao = Transacao(**transacao_dict)
        session.add(transacao)
        session.commit()
        print("[DB] Transação salva com sucesso!")
    except Exception as e:
        session.rollback()
        print("[DB] Erro ao salvar transação:", e)
        return False
    finally:
        session.close()
    return True

def processar_guru_transacao(payload: dict) -> dict:
    # Se o payload estiver aninhado, extrai o payload real
    if "payload" in payload:
        payload = payload["payload"]
        
    if not validar_payload_guru(payload):
        return {"status": "erro", "motivo": "Payload inválido"}
    print("[GURU] Payload recebido:", payload)
    transacao_map = mapear_transacao_guru(payload)
    print("[GURU] Transação mapeada:", transacao_map)
    session = get_session()
    try:
        # 1. Cliente
        cliente = get_or_create_cliente(
            session,
            nome=payload["contact"].get("name"),
            email=payload["contact"].get("email"),
            documento=payload["contact"].get("doc"),
            data_criacao=payload["dates"].get("created_at")
        )
        # Identifica tipo especial de produto Guru
        product_id = str(payload.get("product", {}).get("id"))
        is_order_bump = payload.get("is_order_bump", 0)
        tipo_produto = identificar_tipo_produto_guru(product_id, is_order_bump)
        payload["tipo_produto_guru"] = tipo_produto
        # Extrai valores bruto e líquido
        valor_bruto = payload.get("payment", {}).get("total")
        valor_liquido = payload.get("payment", {}).get("net")
        # Extrai taxa de reembolso do marketplace_value
        taxa_reembolso = payload.get("payment", {}).get("marketplace_value")
        # Define o status primeiro
        status = transacao_map["status"]
        # Extrai motivo de recusa/refund se houver
        # Para reembolsos, prioriza o refund_reason como motivo_recusa
        if status == "refunded":
            motivo_recusa = payload.get("payment", {}).get("refund_reason")
        else:
            motivo_recusa = (
                payload.get("payment", {}).get("refuse_reason")
                or payload.get("payment", {}).get("refund_reason")
                or None
            )
        id_transacao = transacao_map["id_transacao_origem"]
        confirmed_at = payload.get("dates", {}).get("confirmed_at")
        # Busca transação existente com produto_nome (para order bumps/upsells)
        transacao = session.query(Transacao).filter_by(id_transacao_origem=id_transacao, produto_nome=transacao_map.get("produto_nome")).first()
        if transacao:
            # Validação de integridade: verifica se dados do webhook são mais recentes
            webhook_data_transacao = converter_data(transacao_map["data_evento"])
            
            # Garante que ambas as datas tenham timezone antes da comparação
            if webhook_data_transacao and transacao.data_transacao:
                # Se a data do banco não tem timezone, assume UTC
                from datetime import timezone
                if transacao.data_transacao.tzinfo is None:
                    transacao_data_with_tz = transacao.data_transacao.replace(tzinfo=timezone.utc)
                else:
                    transacao_data_with_tz = transacao.data_transacao
                
                if webhook_data_transacao < transacao_data_with_tz:
                    print(f"[SYNC] ⚠️ Webhook com data anterior ignorado: {webhook_data_transacao} < {transacao_data_with_tz}")
                    return {"status": "ignorado", "motivo": "Webhook com data anterior aos dados existentes"}
            
            # Atualiza transação existente se o status mudou OU se há taxa de reembolso
            status_mudou = transacao.status != status
            taxa_disponivel = taxa_reembolso is not None
            
            if status_mudou or taxa_disponivel:
                if status_mudou:
                    transacao.status = status
                if taxa_disponivel:
                    transacao.taxa_reembolso = taxa_reembolso
                # Atualiza motivo_recusa se status mudou para refunded ou se há motivo disponível
                if status_mudou and status == "refunded":
                    transacao.motivo_recusa = motivo_recusa
                elif motivo_recusa and not transacao.motivo_recusa:
                    transacao.motivo_recusa = motivo_recusa
                transacao.valor_liquido = valor_liquido
                transacao.valor_bruto = valor_bruto
                transacao.data_transacao = converter_data(transacao_map["data_evento"])
                session.commit()
                
                mudancas = []
                if status_mudou:
                    mudancas.append(f"status: {transacao.status} -> {status}")
                if taxa_disponivel:
                    mudancas.append(f"taxa_reembolso: {taxa_reembolso}")
                if status_mudou and status == "refunded" and motivo_recusa:
                    mudancas.append(f"motivo_recusa: {motivo_recusa}")
                
                print(f"[DB] Transação atualizada: {id_transacao}, mudanças: {', '.join(mudancas)}")
                print(f"[SYNC] ✅ Webhook atualizou transação do backfill: {id_transacao} - {transacao_map.get('produto_nome')}")
                return {"status": "atualizada", "transacao_id": transacao.id, "mudancas": mudancas}
            else:
                print(f"[DB] Transação já existente, sem mudanças: {id_transacao}")
                return {"status": "ja_existente", "transacao_id": transacao.id}
        else:
            # Busca assinatura relacionada se existir no payload
            assinatura_id = None
            subscription_data = payload.get("subscription")
            if subscription_data and isinstance(subscription_data, dict):
                subscription_origem_id = subscription_data.get("id")
                if subscription_origem_id:
                    assinatura = session.query(Assinatura).filter_by(id_assinatura_origem=subscription_origem_id).first()
                    if assinatura:
                        assinatura_id = assinatura.id
                        print(f"[DB] Transação relacionada à assinatura {assinatura_id} (origem: {subscription_origem_id})")
            
            # Cria nova transação (pode ser aguardando pagamento ou já confirmada)
            transacao_dict = {
                "id_transacao_origem": id_transacao,
                "assinatura_id": assinatura_id,  # Agora relaciona com assinatura se existir
                "cliente_id": cliente.id,
                "plataforma": "guru",
                "status": status,
                "valor": transacao_map["valor_total"],
                "valor_bruto": valor_bruto,
                "valor_liquido": valor_liquido,
                "taxa_reembolso": taxa_reembolso,
                "metodo_pagamento": transacao_map["metodo_pagamento"],
                "data_transacao": converter_data(transacao_map["data_evento"]),
                "motivo_recusa": motivo_recusa,
                "produto_nome": transacao_map.get("produto_nome"),
                "nome_oferta": transacao_map.get("nome_oferta"),
                "json_completo": payload
            }
            sucesso = salvar_transacao(transacao_dict)
            if sucesso:
                return {"status": "criada", "transacao": transacao_dict}
            else:
                return {"status": "erro", "motivo": "Falha ao salvar no banco"}
    except Exception as e:
        print("[GURU] Erro no processamento:", e)
        return {"status": "erro", "motivo": str(e)}
    finally:
        session.close()

def processar_guru_assinatura(payload: dict) -> dict:
    session = get_session()
    try:
        subscriber = payload.get("subscriber", {})
        nome = subscriber.get("name")
        email = subscriber.get("email")
        documento = subscriber.get("doc")
        
        # Corrigido: busca data_criacao em campos que realmente existem
        data_criacao = (
            payload.get("dates", {}).get("started_at") or 
            subscriber.get("created_at") or 
            datetime.now()
        )
        
        if not email:
            return {"status": "erro", "motivo": "Assinante sem email"}
        cliente = get_or_create_cliente(session, nome, email, documento, data_criacao)
        id_assinatura_origem = payload.get("id") or payload.get("subscription_code")
        plataforma = "guru"
        produto_nome = payload.get("name") or payload.get("product", {}).get("name")
        invoice_status = payload.get("current_invoice", {}).get("status")
        cancel_at_cycle_end = payload.get("cancel_at_cycle_end", 0)
        cancel_reason = payload.get("cancel_reason")
        # Ajuste: força status canceled se cancelamento de renovação
        if invoice_status == "waiting_payment":
            status = "waiting_payment"
        elif cancel_at_cycle_end == 1 or cancel_reason:
            status = "canceled"
        else:
            status = payload.get("last_status")
        data_inicio = payload.get("dates", {}).get("started_at")
        data_proxima_cobranca = payload.get("dates", {}).get("next_cycle_at")
        # Ajuste: preenche data_cancelamento mesmo se dates.canceled_at vier vazio
        data_cancelamento = payload.get("dates", {}).get("canceled_at")
        if (not data_cancelamento or data_cancelamento == "") and (cancel_at_cycle_end == 1 or cancel_reason):
            # Usa a data do último status como data de cancelamento
            data_cancelamento = payload.get("dates", {}).get("last_status_at")
        data_expiracao_acesso = payload.get("dates", {}).get("cycle_end_date") or payload.get("dates", {}).get("next_cycle_at")
        valor_total = payload.get("current_invoice", {}).get("value")
        # CORREÇÃO: Pega o product_id do last_transaction em vez do nível raiz
        last_transaction = payload.get("last_transaction", {})
        product_id = last_transaction.get("product", {}).get("id") or payload.get("product", {}).get("id")
        
        # Usa a nova função para calcular valores corretamente
        from utils.helpers import calcular_valores_assinatura_por_tipo
        valor_mensal, valor_anual = calcular_valores_assinatura_por_tipo(
            valor_total, product_id, "guru"
        )
        ultima_atualizacao = payload.get("dates", {}).get("last_status_at")
        # Extrai nome_oferta do payload
        nome_oferta = payload.get("product", {}).get("offer", {}).get("name")
        assinatura = get_or_create_assinatura(
            session,
            id_assinatura_origem=id_assinatura_origem,
            plataforma=plataforma,
            cliente_id=cliente.id,
            produto_nome=produto_nome,
            nome_oferta=nome_oferta,
            status=status,
            data_inicio=data_inicio,
            data_proxima_cobranca=data_proxima_cobranca,
            data_cancelamento=data_cancelamento,
            data_expiracao_acesso=data_expiracao_acesso,
            valor_mensal=valor_mensal,
            valor_anual=valor_anual,
            ultima_atualizacao=ultima_atualizacao
        )
        return {"status": "processado_guru_assinatura", "assinatura_id": assinatura.id}
    except Exception as e:
        print("[GURU] Erro no processamento de assinatura:", e)
        return {"status": "erro", "motivo": str(e)}
    finally:
        session.close()

def processar_assinatura_guru(payload: dict) -> dict:
    """
    Processa assinatura da Guru com dados enriquecidos de transações
    """
    session = get_session()
    try:
        # Extrai dados básicos
        subscription = payload.get("subscription", {})
        contact = payload.get("contact", {})
        product = payload.get("product", {})
        enriched_values = payload.get("enriched_values", {})
        
        # Dados do cliente
        nome = contact.get("name")
        email = contact.get("email")
        documento = contact.get("doc")
        
        # Corrigido: busca data_criacao em campos que realmente existem
        data_criacao = (
            subscription.get("created_at") or 
            subscription.get("started_at") or
            contact.get("created_at") or 
            datetime.now()
        )
        
        # Garante que data_criacao seja sempre válida
        if not data_criacao:
            data_criacao = datetime.now()
            print(f"⚠️ data_criacao não encontrada, usando data atual: {data_criacao}")
        
        print(f"📅 Data de criação do cliente: {data_criacao}")
        
        if not email:
            return {"status": "erro", "motivo": "Assinante sem email"}
        
        # Cria ou busca cliente
        cliente = get_or_create_cliente(session, nome, email, documento, data_criacao)
        
        # Dados da assinatura
        id_assinatura_origem = subscription.get("subscription_code")
        plataforma = "guru"
        produto_nome = product.get("name")
        status = subscription.get("last_status", "active")
        
        # Datas
        data_inicio = subscription.get("started_at")
        data_proxima_cobranca = subscription.get("next_cycle_at")
        # CORREÇÃO: Usa data_cancelamento dos dados enriquecidos do backfill
        data_cancelamento = enriched_values.get("data_cancelamento") or subscription.get("cancelled_at")
        data_expiracao_acesso = subscription.get("cycle_end_date")
        ultima_atualizacao = subscription.get("updated_at")
        
        # Valores enriquecidos
        valor_mensal = enriched_values.get("valor_mensal")
        valor_anual = enriched_values.get("valor_anual")
        
        # Se não houver valores enriquecidos, calcula baseado no tipo de plano
        if valor_mensal is None and valor_anual is None:
            product_id = product.get("id")
            if product_id:
                from utils.helpers import calcular_valores_assinatura_por_tipo
                # Usa o valor total do produto como base
                valor_produto = product.get("total_value") or product.get("unit_value")
                if valor_produto:
                    valor_mensal, valor_anual = calcular_valores_assinatura_por_tipo(
                        valor_produto, product_id, "guru"
                    )
        
        # Debug: verifica se os valores estão corretos
        print(f"[GURU-HIBRIDO] Valores enriquecidos - Mensal: {valor_mensal}, Anual: {valor_anual}")
        print(f"[GURU-HIBRIDO] Tipo dos valores - Mensal: {type(valor_mensal)}, Anual: {type(valor_anual)}")
        
        # Nome da oferta
        # CORREÇÃO: Usa nome_oferta dos dados enriquecidos do backfill
        nome_oferta = enriched_values.get("nome_oferta") or product.get("offer", {}).get("name")
        
        print(f"[GURU-HIBRIDO] Processando assinatura {id_assinatura_origem}")
        print(f"[GURU-HIBRIDO] Cliente: {nome} ({email})")
        print(f"[GURU-HIBRIDO] Produto: {produto_nome}")
        print(f"[GURU-HIBRIDO] Status: {status}")
        print(f"[GURU-HIBRIDO] Valores - Mensal: R$ {valor_mensal}, Anual: R$ {valor_anual}")
        print(f"[GURU-HIBRIDO] Nome Oferta: {nome_oferta}")
        
        # Cria ou atualiza assinatura
        assinatura = get_or_create_assinatura(
            session,
            id_assinatura_origem=id_assinatura_origem,
            plataforma=plataforma,
            cliente_id=cliente.id,
            produto_nome=produto_nome,
            nome_oferta=nome_oferta,
            status=status,
            data_inicio=data_inicio,
            data_proxima_cobranca=data_proxima_cobranca,
            data_cancelamento=data_cancelamento,
            data_expiracao_acesso=data_expiracao_acesso,
            valor_mensal=valor_mensal,
            valor_anual=valor_anual,
            ultima_atualizacao=ultima_atualizacao
        )
        
        return {"status": "processado_guru_assinatura_hibrido", "assinatura_id": assinatura.id}
        
    except Exception as e:
        print("[GURU-HIBRIDO] Erro no processamento de assinatura:", e)
        import traceback
        traceback.print_exc()
        return {"status": "erro", "motivo": str(e)}
    finally:
        session.close()

def calcular_valor_mensal_ticto(payload):
    """
    Calcula o valor mensal correto baseado no ID do produto do Ticto.
    Para planos anuais, divide o valor total por 12.
    Para planos mensais, usa o valor total.
    """
    valor_total = payload["order"].get("paid_amount", 0) / 100  # Converte de centavos para reais
    product_id = payload.get("item", {}).get("product_id")
    offer_code = payload.get("item", {}).get("offer_code")
    
    # Identifica o tipo de plano
    tipo_plano = identificar_tipo_plano_ticto(product_id, offer_code)
    
    if tipo_plano == "anual":
        valor_mensal = valor_total / 12
        print(f"[TICTO] Plano anual detectado (ID: {product_id}, Offer: {offer_code}), valor total: R$ {valor_total}, valor mensal: R$ {valor_mensal:.2f}")
        return valor_mensal
    elif tipo_plano == "mensal":
        valor_mensal = valor_total
        print(f"[TICTO] Plano mensal detectado (ID: {product_id}, Offer: {offer_code}), valor mensal: R$ {valor_mensal}")
        return valor_mensal
    else:
        # Fallback: assume mensal se não conseguir identificar
        print(f"[TICTO] Plano não identificado (ID: {product_id}, Offer: {offer_code}), usando valor total como mensal: R$ {valor_total}")
        return valor_total

def calcular_valores_assinatura_ticto(payload):
    """
    Calcula os valores de assinatura para Ticto usando a nova função.
    Retorna: (valor_mensal, valor_anual)
    """
    valor_total = payload["order"].get("paid_amount", 0) / 100  # Converte de centavos para reais
    product_id = payload.get("item", {}).get("product_id")
    offer_code = payload.get("item", {}).get("offer_code")
    
    from utils.helpers import calcular_valores_assinatura_por_tipo
    return calcular_valores_assinatura_por_tipo(valor_total, product_id, "ticto")

def calcular_data_expiracao_ticto(payload):
    data_confirmacao = converter_data(payload["order"].get("order_date"))
    product_id = payload.get("item", {}).get("product_id")
    offer_code = payload.get("item", {}).get("offer_code")
    tipo_plano  = identificar_tipo_plano_ticto(product_id, offer_code)
    tipo_produto = identificar_tipo_produto_ticto(offer_code)

    # Se for vitalício, retorna data muito distante
    if tipo_produto == "ebook_vitalicio":
        return data_confirmacao + timedelta(days=365*50) if data_confirmacao else datetime.now() + timedelta(days=365*50)
    # Se for orderbump/ebook, retorna a própria data de compra
    if tipo_produto == "orderbump_ebook":
        return data_confirmacao or datetime.now()

    # 1. Tenta usar data de início + período baseado no tipo de plano
    if data_confirmacao:
        if tipo_plano == "anual":
            dias = 365
            print(f"[TICTO] Plano anual detectado (ID: {product_id}, Offer: {offer_code}), order_date, usando {dias} dias")
        elif tipo_plano == "mensal":
            dias = 30
            print(f"[TICTO] Plano mensal detectado (ID: {product_id}, Offer: {offer_code}), order_date, usando {dias} dias")
        else:
            dias = payload.get("item", {}).get("days_of_access")
            if dias is None:
                dias = 30
            print(f"[TICTO] Plano não identificado (ID: {product_id}, Offer: {offer_code}), order_date, usando {dias} dias")
        return data_confirmacao + timedelta(days=dias)
    # Fallback: data atual + 30 dias
    return datetime.now() + timedelta(days=30)

def atualizar_assinatura_chargeback_refund(payload, status_evento):
    session = get_session()
    try:
        assinatura_id = str(payload.get("subscriptions", [{}])[0].get("id"))
        assinatura = session.query(Assinatura).filter_by(id_assinatura_origem=assinatura_id).first()
        if assinatura:
            assinatura.status = status_evento
            # Ajusta a data de expiração para a data do evento
            data_evento = payload.get("status_date") or payload.get("order", {}).get("order_date")
            assinatura.data_expiracao_acesso = converter_data(data_evento)
            session.commit()
            print(f"[DB] Assinatura {assinatura_id} atualizada para {status_evento} e expirada em {assinatura.data_expiracao_acesso}")
            return True
        else:
            print(f"[DB] Assinatura {assinatura_id} não encontrada para chargeback/refund")
            return False
    except Exception as e:
        print("[TICTO] Erro ao atualizar assinatura para chargeback/refund:", e)
        return False
    finally:
        session.close()

def processar_ticto(payload: dict) -> dict:
    if not validar_payload_ticto(payload):
        return {"status": "erro", "motivo": "Payload inválido"}
    print("[TICTO] Payload recebido:", payload)
    
    status = payload.get("status", "")
    
    if status in ["chargeback", "refunded"]:
        atualizar_assinatura_chargeback_refund(payload, status)
        return processar_transacao_ticto(payload)
        
    # Define status de transações e assinaturas da Ticto
    status_transacoes = ["authorized", "refused", "waiting_payment", "pix_created", "pix_expired", 
                        "bank_slip_created", "bank_slip_delayed", "refunded", "chargeback", "claimed", "abandoned_cart"]
    status_assinaturas = ["authorized", "subscription_canceled", "subscription_delayed", "card_exchanged", "uncanceled"]
    
    # Tratamento específico para eventos especiais
    if status == "abandoned_cart":
        return processar_carrinho_abandonado_ticto(payload)
    elif status in ["card_exchanged", "claimed"]:
        return processar_evento_especial_ticto(payload)
    elif status in ["pix_created", "pix_expired", "bank_slip_created", "bank_slip_delayed"]:
        return processar_evento_pagamento_ticto(payload)
    
    if status == "authorized":
        # Só cria assinatura se for produto de assinatura (mensal/anual)
        product_id = payload.get("item", {}).get("product_id")
        offer_code = payload.get("item", {}).get("offer_code")
        tipo_plano = identificar_tipo_plano_ticto(product_id, offer_code)
        if tipo_plano in ("anual", "mensal"):
            resultado_assinatura = processar_assinatura_ticto(payload)
        else:
            resultado_assinatura = {"status": "ignorado", "motivo": "Produto não é assinatura"}
        resultado_transacao = processar_transacao_ticto(payload)
        return {
            "assinatura": resultado_assinatura,
            "transacao": resultado_transacao
        }

    elif status in status_transacoes:
        return processar_transacao_ticto(payload)
    elif status in status_assinaturas:
        return processar_assinatura_ticto(payload)
    else:
        return {"status": "erro", "motivo": f"Status não reconhecido: {status}"}
    


def processar_transacao_ticto(payload: dict) -> dict:
    """
    Processa webhooks da Ticto que são apenas transações (não criam/atualizam assinaturas).
    """
    print("[TICTO] Processando transação")
    transacao_map = mapear_transacao_ticto(payload)
    print("[TICTO] Transação mapeada:", transacao_map)
    session = get_session()
    try:
        # 1. Cliente
        cliente = get_or_create_cliente(
            session,
            nome=payload["customer"].get("name"),
            email=payload["customer"].get("email"),
            documento=payload["customer"].get("cpf") or payload["customer"].get("cnpj"),
            data_criacao=payload["order"].get("order_date")
        )

        # Extrai valores bruto e líquido
        valor_bruto = transacao_map.get("valor_bruto")
        if valor_bruto is None:
            valor_bruto = payload.get("item", {}).get("amount", 0) / 100  # Converte de centavos para reais
        valor_liquido = None
        try:
            valor_liquido = float(str(payload.get("producer", {}).get("cms", "0")).replace(",", "."))
        except Exception:
            valor_liquido = None

        # Classificação de recusa (se aplicável)
        tipo_recusa = payload.get("tipo_recusa")
        motivo_recusa = payload.get("motivo_recusa")
        if transacao_map.get("status") == "refused" and not tipo_recusa:
            tipo_recusa = tipo_venda_recusada_ticto(payload)
            print(f"[TICTO] Tipo de recusa classificado: {tipo_recusa}")

        id_transacao = transacao_map["id_transacao_origem"]
        product_id = payload.get("item", {}).get("product_id")
        product_name = payload.get("item", {}).get("product_name")

        # Busca por transação com mesmo id_transacao_origem E produto_nome (para order bumps/upsells)
        transacao = session.query(Transacao).filter_by(id_transacao_origem=id_transacao, produto_nome=product_name).first()
        if transacao:
            # Validação de integridade: verifica se dados do webhook são mais recentes
            webhook_data_transacao = converter_data(payload.get("status_date") or transacao_map["data_evento"])
            if webhook_data_transacao and transacao.data_transacao and webhook_data_transacao < transacao.data_transacao:
                print(f"[SYNC] ⚠️ Webhook com data anterior ignorado: {webhook_data_transacao} < {transacao.data_transacao}")
                return {"status": "ignorado", "motivo": "Webhook com data anterior aos dados existentes"}
            
            # Atualiza status e campos relevantes
            mudou = False
            if transacao.status != transacao_map["status"]:
                transacao.status = transacao_map["status"]
                mudou = True
            if transacao.valor != transacao_map["valor_total"]:
                transacao.valor = transacao_map["valor_total"]
                mudou = True
            if transacao.valor_bruto != valor_bruto:
                transacao.valor_bruto = valor_bruto
                mudou = True
            if transacao.valor_liquido != valor_liquido:
                transacao.valor_liquido = valor_liquido
                mudou = True
            if transacao.metodo_pagamento != transacao_map["metodo_pagamento"]:
                transacao.metodo_pagamento = transacao_map["metodo_pagamento"]
                mudou = True
            if transacao.data_transacao != converter_data(payload.get("status_date") or transacao_map["data_evento"]):
                transacao.data_transacao = converter_data(payload.get("status_date") or transacao_map["data_evento"])
                mudou = True
            if transacao.tipo_recusa != tipo_recusa:
                transacao.tipo_recusa = tipo_recusa
                mudou = True
            # Atualiza nome_oferta se disponível
            nome_oferta = transacao_map.get("nome_oferta")
            if nome_oferta and transacao.nome_oferta != nome_oferta:
                transacao.nome_oferta = nome_oferta
                mudou = True
            # Atualiza o json_completo sempre
            transacao.json_completo = {**payload, "tipo_recusa": tipo_recusa} if tipo_recusa else payload
            session.commit()
            print(f"[DB] Transação já existente, atualizada: {id_transacao} (product_name: {product_name})")
            print(f"[SYNC] ✅ Webhook atualizou transação do backfill: {id_transacao} - {product_name}")
            return {"status": "transacao_atualizada", "transacao_id": transacao.id}
        else:
            # Cria nova transação
            transacao_dict = {
                "id_transacao_origem": id_transacao,
                "assinatura_id": None,  # Transações não criam assinaturas
                "cliente_id": cliente.id,
                "plataforma": "ticto",
                "status": transacao_map["status"],
                "valor": transacao_map["valor_total"],
                "valor_bruto": valor_bruto,
                "valor_liquido": valor_liquido,
                "metodo_pagamento": transacao_map["metodo_pagamento"],
                "data_transacao": converter_data(payload.get("status_date") or transacao_map["data_evento"]),
                "motivo_recusa": motivo_recusa,
                "json_completo": {**payload, "tipo_recusa": tipo_recusa} if tipo_recusa else payload,
                "tipo_recusa": tipo_recusa,
                "produto_nome": product_name,  # Usar o nome do produto
                "nome_oferta": transacao_map.get("nome_oferta")  # Adicionar nome da oferta
            }
            sucesso = salvar_transacao(transacao_dict)
            if sucesso:
                return {"status": "transacao_criada", "transacao": transacao_dict}
            else:
                return {"status": "erro", "motivo": "Falha ao salvar transacao"}
    except Exception as e:
        print("[TICTO] Erro no processamento de transacao:", e)
        return {"status": "erro", "motivo": str(e)}
    finally:
        session.close()

def processar_assinatura_ticto(payload: dict) -> dict:
    """
    Processa webhooks da Ticto que criam/atualizam assinaturas.
    """
    print("[TICTO] Processando assinatura")
    transacao_map = mapear_transacao_ticto(payload)
    print("[TICTO] Transação mapeada:", transacao_map)
    session = get_session()
    try:
        # 1. Cliente
        cliente = get_or_create_cliente(
            session,
            nome=payload["customer"].get("name"),
            email=payload["customer"].get("email"),
            documento=payload["customer"].get("cpf") or payload["customer"].get("cnpj"),
            data_criacao=payload["order"].get("order_date")
        )

        # 2. Identifica tipo de plano e calcula valores
        product_id = payload.get("item", {}).get("product_id")
        offer_code = payload.get("item", {}).get("offer_code")
        valor_total = payload["item"].get("amount", 0) / 100  # Converte de centavos para reais
        
        # Usa a nova função para calcular valores corretamente
        from utils.helpers import calcular_valores_assinatura_por_tipo
        valor_mensal, valor_anual = calcular_valores_assinatura_por_tipo(
            valor_total, product_id, "ticto"
        )

        # 3. Calcula data de expiração
        data_expiracao = calcular_data_expiracao_ticto(payload)
        print(f"[TICTO] Data de expiração calculada: {data_expiracao}")

        # 4. Determina status da assinatura baseado no status do webhook
        status_assinatura = payload.get("status")
        if status_assinatura == "authorized":
            status_assinatura = "active"  # Converte para status padrão do sistema
        
        # 5. Assinatura
        nome_oferta = payload.get("item", {}).get("offer_name")
        assinatura = get_or_create_assinatura(
            session,
            id_assinatura_origem=str(payload["subscriptions"][0].get("id")) if payload.get("subscriptions") else None,
            plataforma="ticto",
            cliente_id=cliente.id,
            produto_nome=payload.get("item", {}).get("product_name"),
            nome_oferta=nome_oferta,
            status=status_assinatura,
            data_inicio=payload.get("status_date") or payload["order"].get("order_date"),
            data_proxima_cobranca=payload["subscriptions"][0].get("next_charge") if payload.get("subscriptions") else None,
            data_cancelamento=payload["subscriptions"][0].get("canceled_at") if payload.get("subscriptions") else None,
            data_expiracao_acesso=data_expiracao,
            valor_mensal=valor_mensal,
            valor_anual=valor_anual,
            ultima_atualizacao=payload.get("status_date")
        )
        
        # 6. Cria também a transação associada à assinatura
        transacao_dict = {
            "id_transacao_origem": payload.get("order", {}).get("transaction_hash") or payload.get("order", {}).get("hash"),
            "assinatura_id": assinatura.id,  # Associa à assinatura criada
            "cliente_id": cliente.id,
            "plataforma": "ticto",
            "status": payload.get("status"),
            "valor": valor_total,
            "valor_bruto": valor_total,
            "valor_liquido": float(str(payload.get("producer", {}).get("cms", "0")).replace(",", ".")) if payload.get("producer", {}).get("cms") else None,
            "metodo_pagamento": payload.get("payment_method"),
            "data_transacao": converter_data(payload.get("status_date") or payload["order"].get("order_date")),
            "motivo_recusa": None,
            "json_completo": payload,
            "tipo_recusa": None,
            "produto_nome": payload.get("item", {}).get("product_name")
        }
        sucesso = salvar_transacao(transacao_dict)
        
        return {"status": "assinatura_processada", "assinatura_id": assinatura.id, "transacao_criada": sucesso}
    except Exception as e:
        print("[TICTO] Erro no processamento de assinatura:", e)
        return {"status": "erro", "motivo": str(e)}
    finally:
        session.close()

def processar_carrinho_abandonado_ticto(payload: dict) -> dict:
    """
    Processa webhook de carrinho abandonado da Ticto.
    """
    print("[TICTO] Processando carrinho abandonado")
    session = get_session()
    try:
        # Cria cliente se não existir
        cliente = get_or_create_cliente(
            session,
            nome=payload.get("name"),
            email=payload.get("email"),
            documento=payload.get("document"),
            data_criacao=payload.get("created_at")
        )
        
        # Registra apenas a transação (não cria assinatura)
        transacao_dict = {
            "id_transacao_origem": f"abandoned_{payload.get('email', 'unknown')}_{payload.get('created_at', 'unknown')}",
            "assinatura_id": None,
            "cliente_id": cliente.id,
            "plataforma": "ticto",
            "status": "abandoned_cart",
            "valor": 0,
            "valor_bruto": 0,
            "valor_liquido": 0,
            "metodo_pagamento": None,
            "data_transacao": converter_data(payload.get("created_at")),
            "motivo_recusa": "Carrinho abandonado",
            "json_completo": payload
        }
        sucesso = salvar_transacao(transacao_dict)
        if sucesso:
            return {"status": "carrinho_abandonado_processado", "transacao": transacao_dict}
        else:
            return {"status": "erro", "motivo": "Falha ao salvar carrinho abandonado"}
    except Exception as e:
        print("[TICTO] Erro no processamento de carrinho abandonado:", e)
        return {"status": "erro", "motivo": str(e)}
    finally:
        session.close()

def processar_evento_especial_ticto(payload: dict) -> dict:
    """
    Processa eventos especiais da Ticto (card_exchanged, claimed).
    """
    print(f"[TICTO] Processando evento especial: {payload.get('status')}")
    if payload.get("status") == "card_exchanged":
        print("[TICTO] Evento 'card_exchanged' recebido e ignorado para transações.")
        return {"status": "ignorado", "motivo": "Evento de cartão atualizado não impacta transações"}
    session = get_session()
    try:
        email = payload.get("customer", {}).get("email")
        if not email:
            return {"status": "erro", "motivo": "Email do cliente não encontrado"}
        cliente = session.query(Cliente).filter_by(email=email).first()
        if not cliente:
            return {"status": "erro", "motivo": "Cliente não encontrado"}

        valor = payload.get("item", {}).get("amount", 0)  # Webhook real - valor já em reais
        valor_bruto = valor
        try:
            valor_liquido = float(str(payload.get("producer", {}).get("cms", "0")).replace(",", "."))
        except Exception:
            valor_liquido = None
        product_name = payload.get("item", {}).get("product_name")
        transaction_hash = payload.get("transaction", {}).get("hash") or payload.get("order", {}).get("transaction_hash")

        # Atualiza transação existente se status for 'claimed'
        if payload.get("status") == "claimed":
            transacao = session.query(Transacao).filter_by(id_transacao_origem=transaction_hash, produto_nome=product_name).first()
            if transacao:
                transacao.status = payload.get("status")
                transacao.valor = valor
                transacao.valor_bruto = valor_bruto
                transacao.valor_liquido = valor_liquido
                transacao.metodo_pagamento = payload.get("payment_method")
                transacao.data_transacao = converter_data(payload.get("status_date") or payload.get("order", {}).get("order_date"))
                transacao.json_completo = payload
                session.commit()
                print(f"[DB] Transação já existente, atualizada: {transaction_hash} (product_name: {product_name})")
                print(f"[SYNC] ✅ Webhook atualizou transação do backfill: {transaction_hash} - {product_name}")
                return {"status": "transacao_atualizada", "transacao_id": transacao.id}
        # Se não encontrou ou não for 'claimed', cria nova transação
        nome_oferta = payload.get("item", {}).get("offer_name")
        transacao_dict = {
            "id_transacao_origem": transaction_hash,
            "assinatura_id": None,
            "cliente_id": cliente.id,
            "plataforma": "ticto",
            "status": payload.get("status"),
            "valor": valor,
            "valor_bruto": valor_bruto,
            "valor_liquido": valor_liquido,
            "metodo_pagamento": payload.get("payment_method"),
            "data_transacao": converter_data(payload.get("status_date") or payload.get("order", {}).get("order_date")),
            "motivo_recusa": None,
            "json_completo": payload,
            "produto_nome": product_name,
            "nome_oferta": nome_oferta
        }
        sucesso = salvar_transacao(transacao_dict)
        if sucesso:
            return {"status": "evento_especial_processado", "transacao": transacao_dict}
        else:
            return {"status": "erro", "motivo": "Falha ao salvar evento especial"}
    except Exception as e:
        print("[TICTO] Erro no processamento de evento especial:", e)
        return {"status": "erro", "motivo": str(e)}
    finally:
        session.close()

def processar_evento_pagamento_ticto(payload: dict) -> dict:
    """
    Processa eventos de pagamento da Ticto (PIX, boleto).
    """
    print(f"[TICTO] Processando evento de pagamento: {payload.get('status')}")
    session = get_session()
    try:
        # Busca transação existente para atualizar
        transaction_hash = payload.get("order", {}).get("transaction_hash")
        if not transaction_hash:
            return {"status": "erro", "motivo": "Hash da transação não encontrado"}
        product_name = payload.get("item", {}).get("product_name")
        # Busca transação existente pelo hash e nome do produto
        transacao = session.query(Transacao).filter_by(id_transacao_origem=transaction_hash, produto_nome=product_name).first()
        if transacao:
            # Validação de integridade: verifica se dados do webhook são mais recentes
            webhook_data_transacao = converter_data(payload.get("status_date") or payload.get("order", {}).get("order_date"))
            if webhook_data_transacao and transacao.data_transacao and webhook_data_transacao < transacao.data_transacao:
                print(f"[SYNC] ⚠️ Webhook com data anterior ignorado: {webhook_data_transacao} < {transacao.data_transacao}")
                return {"status": "ignorado", "motivo": "Webhook com data anterior aos dados existentes"}
            
            # Atualiza status da transação existente
            transacao.status = payload.get("status")
            transacao.data_transacao = converter_data(payload.get("status_date") or payload.get("order", {}).get("order_date"))
            session.commit()
            print(f"[SYNC] ✅ Webhook atualizou transação do backfill: {transaction_hash} - {product_name}")
            return {"status": "transacao_atualizada", "transacao_id": transacao.id}
        else:
            # Cria nova transação se não existir
            cliente = get_or_create_cliente(
                session,
                nome=payload["customer"].get("name"),
                email=payload["customer"].get("email"),
                documento=payload["customer"].get("cpf") or payload["customer"].get("cnpj"),
                data_criacao=payload["order"].get("order_date")
            )
            nome_oferta = payload.get("item", {}).get("offer_name")
            transacao_dict = {
                "id_transacao_origem": transaction_hash,
                "assinatura_id": None,
                "cliente_id": cliente.id,
                "plataforma": "ticto",
                "status": payload.get("status"),
                "valor": payload.get("order", {}).get("paid_amount", 0) / 100,
                "valor_bruto": payload.get("order", {}).get("paid_amount", 0) / 100,
                "valor_liquido": None,
                "metodo_pagamento": payload.get("payment_method"),
                "data_transacao": converter_data(payload.get("status_date") or payload.get("order", {}).get("order_date")),
                "motivo_recusa": None,
                "json_completo": payload,
                "produto_nome": product_name,
                "nome_oferta": nome_oferta
            }
            sucesso = salvar_transacao(transacao_dict)
            if sucesso:
                return {"status": "evento_pagamento_processado", "transacao": transacao_dict}
            else:
                return {"status": "erro", "motivo": "Falha ao salvar evento de pagamento"}
    except Exception as e:
        print("[TICTO] Erro no processamento de evento de pagamento:", e)
        return {"status": "erro", "motivo": str(e)}
    finally:
        session.close() 