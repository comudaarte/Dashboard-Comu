# Resumo da Exportação do Banco de Dados

**Data/Hora da Exportação:** 03/09/2025 15:06:24
**Timestamp:** 20250903_150622
**Total de Registros Exportados:** 2,761

## Tabelas Exportadas:

### 1. Clientes (clientes.csv)
- Informações básicas dos clientes
- Campos: id, nome, email, documento, data_criacao

### 2. Assinaturas (assinaturas.csv)
- Dados das assinaturas dos clientes
- Campos: id, id_assinatura_origem, plataforma, cliente_id, produto_nome, nome_oferta, status, data_inicio, data_proxima_cobranca, data_cancelamento, data_expiracao_acesso, valor_mensal, valor_anual, ultima_atualizacao

### 3. Transações (transacoes.csv)
- Histórico de transações financeiras
- Campos: id, id_transacao_origem, assinatura_id, cliente_id, plataforma, status, valor, valor_liquido, valor_bruto, taxa_reembolso, metodo_pagamento, data_transacao, motivo_recusa, json_completo, tipo_recusa, produto_nome, nome_oferta

## Observações:
- Todos os arquivos estão em formato CSV com encoding UTF-8
- O campo 'json_completo' da tabela transações contém dados adicionais em formato JSON
- Os relacionamentos entre tabelas são mantidos através dos campos de ID
