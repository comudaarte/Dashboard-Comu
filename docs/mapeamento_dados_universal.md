# Documentação Universal de Mapeamento de Dados e Métricas

## Visão Geral do Projeto

Este projeto consolida, normaliza e analisa dados de assinaturas e transações das plataformas **Guru** e **Ticto** em um banco de dados unificado. O sistema permite ingestão histórica, processamento de webhooks em tempo real, cálculo de métricas de negócio e visualização via dashboard. Toda a lógica de negócio, regras de status e cálculo de métricas está documentada aqui para servir de referência única para desenvolvedores e IAs.

---

## Estrutura de Dados Unificada

### Entidades Principais

#### 1. **clientes**
- **Descrição:** Representa cada pessoa que já realizou uma compra ou assinatura.
- **Campos:**
  - `id`: Identificador único interno
  - `nome`: Nome do cliente
  - `email`: E-mail do cliente (chave única)
  - `documento`: CPF ou CNPJ
  - `data_criacao`: Data da primeira compra/assinatura

#### 2. **assinaturas**
- **Descrição:** Representa o estado atual de cada assinatura de cada cliente, incluindo status, datas e valor.
- **Campos:**
  - `id`: Identificador único interno
  - `id_assinatura_origem`: ID da assinatura na plataforma de origem (string para Guru, int para Ticto)
  - `plataforma`: "guru" ou "ticto"
  - `cliente_id`: FK para clientes
  - `produto_nome`: Nome do produto/assinatura
  - `status`: Estado atual ("active", "canceled", "refunded", "chargeback", etc)
  - `data_inicio`: Data de início da assinatura
  - `data_proxima_cobranca`: Próxima data de cobrança (se aplicável)
  - `data_cancelamento`: Data do cancelamento (se houver)
  - `data_expiracao_acesso`: Data em que o cliente perde o acesso (chave para saber se está ativo)
  - `valor_mensal`: Valor mensal da assinatura
  - `valor_anual`: Valor anual da assinatura (se aplicável)
  - `ultima_atualizacao`: Última atualização do registro

#### 3. **transacoes**
- **Descrição:** Log imutável de todos os eventos financeiros (pagamentos, cancelamentos, reembolsos, chargebacks, etc).
- **Campos:**
  - `id`: Identificador único interno
  - `id_transacao_origem`: ID da transação na plataforma de origem (string para Guru, hash para Ticto)
  - `assinatura_id`: FK para assinaturas (pode ser nulo para eventos não vinculados a assinatura)
  - `cliente_id`: FK para clientes
  - `status`: Status do evento financeiro ("paid", "refused", "refunded", "chargeback", etc)
  - `valor`: Valor da transação
  - `valor_bruto`: Valor bruto (quando disponível)
  - `valor_liquido`: Valor líquido (quando disponível)
  - `metodo_pagamento`: Método de pagamento
  - `data_transacao`: Data do evento
  - `motivo_recusa`: Motivo do erro/recusa (se houver)
  - `json_completo`: Payload original do evento (JSONB)

---

### Mapeamento de Campos Unificados (Guru x Ticto)

#### Tabela: transacoes

| Campo no DB             | Guru (json)                | Ticto (json) / Webhook                | Tipo         | Observação/Transformação                |
|------------------------ |--------------------------- |--------------------------------------- |------------- |-----------------------------------------|
| id_transacao_origem     | id                         | order.transaction_hash                 | str          | Guru: string UUID, Ticto: string hash   |
| id_assinatura_origem    | subscription.id            | subscriptions[0].id                    | str/int      | Guru: string, Ticto: int                |
| plataforma              | "guru" (fixo)              | "ticto" (fixo)                         | str          | Valor fixo                              |
| email_cliente           | contact.email              | customer.email                         | str          |                                         |
| valor_total             | payment.total              | order.paid_amount / transaction.paid_amount | float    | Ticto: dividir por 100 (vem em centavos)|
| status                  | status                     | status                                 | str          | Normalizar valores                      |
| metodo_pagamento        | payment.method             | payment_method                         | str          |                                         |
| data_evento             | dates.created_at           | order.order_date / status_date         | datetime     | Guru: timestamp, Ticto: string          |
| json_completo           | json                       | json                                   | json         | Payload original                        |

#### Tabela: clientes

| Campo no DB             | Guru (json)                | Ticto (json) / Webhook                | Tipo         | Observação/Transformação                |
|------------------------ |--------------------------- |--------------------------------------- |------------- |-----------------------------------------|
| nome                    | contact.name               | customer.name                          | str          |                                         |
| email                   | contact.email              | customer.email                         | str          |                                         |
| documento               | contact.doc                | customer.cpf / customer.cnpj           | str          |                                         |
| data_criacao            | dates.created_at           | order.order_date                       | datetime     |                                         |

#### Tabela: assinaturas

| Campo no DB             | Guru (json)                | Ticto (json) / Webhook                | Tipo         | Observação/Transformação                |
|------------------------ |--------------------------- |--------------------------------------- |------------- |-----------------------------------------|
| id_assinatura_origem    | subscription.id            | subscriptions[0].id                    | str/int      |                                         |
| plataforma              | "guru" (fixo)              | "ticto" (fixo)                         | str          |                                         |
| cliente_email           | contact.email              | customer.email                         | str          |                                         |
| produto_nome            | product.name               | item.product_name                      | str          |                                         |
| status                  | subscription.last_status   | status                                 | str          |                                         |
| data_inicio             | subscription.started_at    | order.order_date                       | datetime     |                                         |
| data_proxima_cobranca   | subscription.next_charge   | subscriptions[0].next_charge           | datetime     |                                         |
| data_cancelamento       | subscription.canceled_at   | subscriptions[0].canceled_at           | datetime     |                                         |
| valor_mensal            | payment.total              | order.paid_amount / transaction.paid_amount | float    |                                         |
| ultima_atualizacao      | dates.updated_at           | status_date                            | datetime     |                                         |

---

#### Status de Transações

##### Guru (payment.method)
- **applepay**: Apple Pay
- **baloto**: Baloto (Colômbia)
- **bank_transfer**: Transferência bancária
- **billet**: Boleto bancário
- **credit_card**: Cartão de crédito
- **cryptocurrency**: Criptomoeda
- **efecty**: Efecty (Colômbia)
- **free**: Gratuito
- **google_pay**: Google Pay
- **ideal**: iDEAL (Holanda)
- **mbway**: MB WAY (Portugal)
- **multibanco**: Multibanco (Portugal)
- **multicaja**: Multicaja (Chile)
- **nupay**: NuPay
- **other**: Outros métodos
- **oxxo**: OXXO (México)
- **pagoefectivo**: PagoEfectivo (Peru)
- **paypal**: PayPal
- **personal_credit**: Crédito pessoal
- **pix**: PIX (Brasil)
- **samsung_pay**: Samsung Pay
- **safetypay**: SafetyPay
- **sencillito**: Sencillito (Chile)
- **servipag**: Servipag (Chile)
- **sepa**: SEPA (Europa)
- **spei**: SPEI (México)
- **wallet**: Carteira digital
- **webpay**: WebPay (Chile)

##### Ticto (payment_method)
- **credit_card**: Cartão de crédito
- **pix**: PIX (Brasil)
- **bank_slip**: Boleto bancário

---

#### Status de Assinaturas

##### Guru (last_status)
- **active**: Assinatura ativa
- **canceled**: Assinatura cancelada
- **expired**: Assinatura expirada
- **inactive**: Assinatura inativa
- **pastdue**: Assinatura em atraso
- **started**: Assinatura iniciada
- **trial**: Período de teste
- **trial canceled**: Teste cancelado

##### Ticto (status)
**Status de Transações:**
- **authorized**: Transação autorizada
- **refused**: Transação recusada
- **waiting_payment**: Aguardando pagamento
- **pix_created**: PIX criado
- **pix_expired**: PIX expirado
- **bank_slip_created**: Boleto criado
- **bank_slip_delayed**: Boleto em atraso
- **refunded**: Reembolsado
- **chargeback**: Chargeback
- **claimed**: Reclamado
- **abandoned_cart**: Carrinho abandonado

**Status de Assinaturas:**
- **authorized**: Assinatura ativa (converte para "active" no sistema)
- **subscription_canceled**: Assinatura cancelada
- **subscription_delayed**: Assinatura em atraso
- **card_exchanged**: Cartão atualizado
- **uncanceled**: Assinatura retomada

---

#### Observações Gerais
- Valores em centavos (Ticto): dividir por 100.
- Datas: converter para datetime.
- Status: normalizar valores equivalentes.
- Campos opcionais: tratar ausência/nulos. 
- **Normalização de Status:**
  - Guru "approved" = Ticto "authorized"
  - Guru "waiting_payment" = Ticto "waiting_payment"
  - Guru "canceled" = Ticto "subscription_canceled"
  - Guru "refunded" = Ticto "refunded"
  - Guru "chargeback" = Ticto "chargeback"

---

## Lógica de Processamento e Armazenamento

### 1. Ingestão de Dados
- **Histórico:**
  - Um script de backfill consome todas as transações históricas das APIs Guru e Ticto.
  - Cada transação é transformada conforme o mapeamento e inserida nas tabelas corretas.
  - O JSON original é sempre armazenado para auditoria.
- **Webhooks:**
  - Eventos em tempo real (pagamento, cancelamento, reembolso, chargeback, eventos especiais) são recebidos via endpoints FastAPI.
  - Cada evento é processado de forma idempotente (não gera duplicidade).
  - O estado das assinaturas e clientes é atualizado conforme as regras abaixo.

### 2. Gestão de Assinaturas Ativas
- O campo **data_expiracao_acesso** em `assinaturas` é a chave para saber se o cliente está ativo.
- **Regra principal:**
  - O cliente é considerado ativo se `data_expiracao_acesso` for maior ou igual à data de referência (ex: hoje).
- **Cancelamento:**
  - Se o cliente cancelar a assinatura, o status é atualizado para "canceled", mas a data de expiração NÃO é alterada. O cliente mantém o acesso até o fim do ciclo já pago.
- **Reembolsos e chargebacks:**
  - Se a assinatura receber um evento de reembolso ou chargeback, o acesso é encerrado imediatamente: o status é atualizado para `refunded` ou `chargeback` e o campo `data_expiracao_acesso` é ajustado para a data do evento.
- **Renovação:**
  - Em cada renovação, a data de expiração é estendida conforme o plano (ex: +30 dias para mensal, +365 dias para anual).
- **Exemplo de fluxo:**
  1. Cliente compra assinatura anual em 01/01/2025 → `data_expiracao_acesso` = 01/01/2026
  2. Cliente cancela em 05/01/2025 → status = "canceled", mas `data_expiracao_acesso` continua 01/01/2026
  3. Cliente recebe reembolso em 10/01/2025 → status = "refunded", `data_expiracao_acesso` = 10/01/2025

### 3. Lógica de Métricas

#### **MRR (Receita Recorrente Mensal)**
- Soma dos valores mensais pagos por todos os clientes ativos no mês de referência.
- Exclui vendas pontuais e eventos não recorrentes.
- **Cálculo do valor mensal:**
  - **Guru:** Baseado no `product.id`:
    - ID `1741887379` (Plano Anual): `valor_total / 12`
    - ID `1741871695` (Plano Mensal): `valor_total`
  - **Ticto:** Baseado no `item.product_id`:
    - ID `41146` (Plano Anual): `valor_total / 12`
    - ID `41145` (Plano Mensal): `valor_total`
- **SQL Exemplo:**
```sql
SELECT SUM(valor_mensal)
FROM assinaturas
WHERE data_expiracao_acesso >= :data_referencia
  AND status NOT IN ('refunded', 'chargeback')
```
- **Explicação:** Apenas assinaturas com acesso vigente e sem reembolso/chargeback são consideradas.

#### **ARR (Receita Anual Recorrente)**
- ARR = MRR × 12

#### **Taxa de Churn (%)**
- Mede a proporção de clientes que cancelaram em relação ao total de ativos no período anterior.
- **Fórmula:**
  - Taxa de Churn = (Total de clientes que cancelaram ÷ Total de clientes ativos no último período) × 100
- **Nota:** Cancelamento só conta se o cliente não renovar após o fim do ciclo.

#### **Taxa de Renovação (%)**
- Taxa de Renovação = 100% - Taxa de Churn

#### **LTV (Lifetime Value)**
- LTV = LT (Lifetime) × Ticket médio
- LT = 1 ÷ Taxa de churn
- **Ticket médio:** Faturamento ÷ Número de clientes que compraram no período

#### **CAC (Custo de Aquisição de Cliente)**
- CAC = Total investido em marketing ÷ Número de novos clientes conquistados no período

#### **Ticket Médio**
- Ticket Médio = Faturamento ÷ Número de clientes que compraram no período

---

## Fluxo de Dados
```
Webhooks/API (Guru/Ticto) → Endpoints FastAPI → Transformação (utils/mapeamento.py) → Banco de Dados Unificado (PostgreSQL) → Dashboard (Dash/Plotly)
```
## Fluxo de Dados Detalhado

1. **Recepção:** Webhooks/API (Guru/Ticto) enviam eventos para endpoints FastAPI.
2. **Transformação:** Os dados são normalizados usando os dicionários em `utils/mapeamento.py`.
3. **Armazenamento:**
   - Dados normalizados são inseridos/atualizados nas tabelas do banco (PostgreSQL).
   - O JSON original é salvo em campo do tipo JSONB.
4. **Atualização de Estado:**
   - Assinaturas e clientes têm seus status e datas atualizados conforme as regras de negócio.
5. **Consulta e Métricas:**
   - O dashboard consulta o banco para calcular e exibir as métricas em tempo real.
---

## Observações Técnicas e Regras de Negócio

- **Valores em centavos (Ticto):** Sempre dividir por 100 ao armazenar.
- **Valores em reais (Guru):** Já vêm como float.
- **Datas:** Converter para datetime com timezone (UTC recomendado).
- **Status:** Sempre normalizar para equivalência entre plataformas (ex: "paid" = "approved").
- **Idempotência:** Antes de inserir/atualizar, verifique se o evento já foi processado (usar IDs únicos).
- **Auditoria:** O campo `json_completo` deve sempre armazenar o payload original.
- **Relacionamentos:** Use FKs entre clientes, assinaturas e transações para garantir integridade.
- **Campos opcionais:** Trate ausência/nulos de forma robusta (ex: `canceled_at` pode ser null, `assinatura_id` pode ser null em transações pontuais ou eventos especiais).
- **Eventos especiais Ticto:**
  - **Carrinho abandonado:** Cria cliente e transação com valor 0, não cria assinatura.
  - **Cartão atualizado:** status = "card_exchanged"
  - **Reclamado:** status = "claimed"
  - **PIX/Boleto:** status = "pix_created", "pix_expired", "bank_slip_created", "bank_slip_delayed"
- **Cancelamento:** Não encerra acesso imediatamente, apenas marca status.
- **Reembolso/chargeback:** Encerra acesso na data do evento.
- **Renovação:** Estende data de expiração.

---

## Exemplos de Dados e Casos de Uso

- Consulte a pasta `Jsons (exemplos)/` para exemplos reais de payloads Guru e Ticto.
- Use os exemplos para testar ingestão, transformação e cálculo de métricas.
- Simule eventos de cancelamento, reembolso, renovação, carrinho abandonado, cartão trocado, etc, para validar a lógica de status e acesso.

---

## Documentação das Plataformas

### Guru
- **Documentação Completa:** `docs/documentacao_guru.md`
- **Status de Transações:** approved, waiting_payment, canceled, abandoned, refunded, paid
- **Status de Assinaturas:** active, canceled, expired, inactive, pastdue, started, trial, trial canceled
- **Métodos de Pagamento:** 30+ métodos incluindo credit_card, pix, paypal, applepay, etc.
- **Webhook Types:** transaction, subscription
- **Valores:** Float em reais
- **Datas:** ISO 8601 format

### Ticto
- **Documentação Completa:** `docs/documentacao_ticto.md`
- **Status de Transações:** authorized, refused, waiting_payment, pix_created, pix_expired, bank_slip_created, bank_slip_delayed, refunded, chargeback, claimed, abandoned_cart
- **Status de Assinaturas:** authorized (active), subscription_canceled, subscription_delayed, card_exchanged, uncanceled
- **Métodos de Pagamento:** credit_card, pix, bank_slip
- **Webhook Type:** Sempre "transaction" (diferenciação por status)
- **Valores:** Integer em centavos (dividir por 100)
- **Datas:** String "YYYY-MM-DD HH:MM:SS"
- **Eventos Especiais:**
  - **Carrinho abandonado:** status = "abandoned_cart"
  - **Cartão atualizado:** status = "card_exchanged"
  - **Reclamado:** status = "claimed"
  - **PIX/Boleto:** status = "pix_created", "pix_expired", "bank_slip_created", "bank_slip_delayed"

### Mapeamento de Status
- **Guru "approved"** = **Ticto "authorized"**
- **Guru "waiting_payment"** = **Ticto "waiting_payment"**
- **Guru "canceled"** = **Ticto "subscription_canceled"**
- **Guru "refunded"** = **Ticto "refunded"**
- **Guru "chargeback"** = **Ticto "chargeback"**

---

## Referências e Arquivos Relacionados
- Planejamento detalhado: `Planejamento Projeto Dashboard (Google).md`
- Arquitetura e diretrizes: `CLAUDE.md`
- Mapeamento de campos: `docs/mapeamento_campos.md`, `utils/mapeamento.py`
- Documentação Guru: `docs/documentacao_guru.md`
- Documentação Ticto: `docs/documentacao_ticto.md`
- Métricas de negócio: documentação interna deste arquivo

---

**Este documento é a referência principal para toda a lógica de dados, status, métricas e regras de negócio do projeto. Qualquer dúvida ou alteração deve ser refletida aqui para garantir consistência e rastreabilidade.** 