# CLAUDE.md

Este documento é a referência principal para desenvolvedores e IA sobre o projeto de dashboard de assinaturas da Comunidade da Arte.

## Visão Geral do Projeto

Este é um dashboard analítico de assinaturas que consolida dados das plataformas Guru e Ticto em um sistema unificado de inteligência de negócios. O projeto implementa um pipeline ETL completo, com processamento de webhooks em tempo real, para fornecer métricas consolidadas e gestão de assinaturas.

---

## Plano de Ação e Arquitetura

### 1. Análise e Mapeamento de Dados (Schema Unificado)
- Estudar exemplos de JSON e documentações das plataformas.
- Definir as entidades principais: Clientes, Assinaturas e Transações.
- Criar um mapeamento "de-para" dos campos de cada plataforma para o modelo unificado (ver seção de mapeamento de campos no arquivo universal).

### 2. Design e Criação do Banco de Dados Central
- Utilizar PostgreSQL, aproveitando o tipo JSONB para payloads originais.
- Estrutura sugerida:
```sql
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    documento VARCHAR(50) UNIQUE,
    data_criacao TIMESTAMP NOT NULL
);
CREATE TABLE assinaturas (
    id SERIAL PRIMARY KEY,
    id_assinatura_origem VARCHAR(255) UNIQUE NOT NULL,
    plataforma VARCHAR(50) NOT NULL,
    cliente_id INTEGER REFERENCES clientes(id),
    produto_nome VARCHAR(255),
    status VARCHAR(50) NOT NULL,
    data_inicio TIMESTAMP,
    data_proxima_cobranca TIMESTAMP,
    data_cancelamento TIMESTAMP,
    data_expiracao_acesso TIMESTAMP,
    valor_mensal DECIMAL(10, 2),
    ultima_atualizacao TIMESTAMP
);
CREATE TABLE transacoes (
    id SERIAL PRIMARY KEY,
    id_transacao_origem VARCHAR(255) UNIQUE NOT NULL,
    assinatura_id INTEGER REFERENCES assinaturas(id),
    cliente_id INTEGER REFERENCES clientes(id),
    status VARCHAR(50),
    valor DECIMAL(10, 2),
    metodo_pagamento VARCHAR(50),
    data_transacao TIMESTAMP,
    motivo_recusa TEXT,
    json_completo JSONB
);
```

### 3. Ingestão de Dados Históricos (Backfill)
- Script Python para consumir APIs Guru/Ticto, transformar e inserir dados conforme o mapeamento.
- Garantir idempotência: checar existência de `id_transacao_origem` antes de inserir.

### 4. Webhooks e Lógica de Atualização (Resolvendo o "Impasse")
- Serviço FastAPI para receber webhooks.
- Lógica principal:
  - Cancelamento: só altera status, não encerra acesso imediatamente.
  - Reembolso/chargeback: encerra acesso na data do evento.
  - PIX/Boleto expirado: apenas atualiza status da transação existente, não cria nova venda.
  - Idempotência: sempre checar se evento já foi processado.

### 5. Cálculo de Métricas
- Módulo Python para calcular MRR, churn, CAC, LTV, etc, diretamente do banco.
- Exemplo de função:
```python
def get_mrr():
    # SELECT SUM(valor_mensal) FROM assinaturas WHERE status = 'active'
    ...
```

### 6. Dashboard Visual (Dash/Plotly)
- Interface web para exibir KPIs, gráficos de churn, evolução de receita, etc.
- Atualização automática dos dados.

### 7. Deploy e Boas Práticas
- Produção: Gunicorn para Dash e FastAPI, Nginx como proxy reverso, systemd para gerenciamento.
- Segurança: HTTPS obrigatório.
- Monitoramento: Sentry, Prometheus, Flower para Celery.

---

## Lógica de Negócio e Estratégias
- Cancelamento não encerra acesso imediatamente, apenas marca status.
- Reembolso/chargeback encerra acesso na data do evento.
- Renovação estende data de expiração.
- Carrinho abandonado, cartão trocado, eventos especiais: tratados conforme regras específicas.
- Sempre armazenar o JSON original para auditoria.

---

## Comandos de Desenvolvimento

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables (copy from .env.example)
cp .env.example .env
```

### Running the Application
```bash
# Start the dashboard (Dash/Plotly)
python dashboard/app.py

# Start the API server (FastAPI)
uvicorn Api.webhooks:app --reload --port 8000

# Start Celery worker for background tasks
celery -A services.webhook_handler worker --loglevel=info

# Start Celery monitoring (Flower)
celery -A services.webhook_handler flower --port=5555
```

### Development Tools
```bash
# Code formatting
black .

# Linting
flake8 .

# Run tests
pytest tests/

# Run async tests
pytest tests/ -v --asyncio-mode=auto
```

### Database Operations
```bash
# Database migrations (when implemented)
alembic upgrade head
alembic revision --autogenerate -m "description"
```

## Architecture Overview

### Core Business Logic
The project solves complex subscription management challenges:

1. **Dual Platform Integration**: Normalizes data from Guru and Ticto payment platforms
2. **Subscription Lifecycle Management**: Handles cancellation vs access expiration logic
3. **Duplicate Prevention**: PIX expiration events update existing transactions rather than creating duplicates
4. **Real-time Processing**: Webhook-driven updates for immediate business insights

### Data Flow Architecture
```
Webhooks (Guru/Ticto) → API Endpoints → Data Transformation → Unified Database → Dashboard
```

### Directory Structure
- **`Api/`**: FastAPI endpoints for webhook handling and external platform integration
- **`dashboard/`**: Dash application with components, layouts, and callbacks
- **`database/`**: SQLAlchemy models, migrations, and connection management  
- **`services/`**: Business logic layer (webhook processing, data transformation, metrics calculation)
- **`utils/`**: Cross-platform field mapping and utility functions
- **`tests/`**: Test suite (pytest + async support)

## Data Architecture

### Unified Data Model
Three core entities with normalized fields across platforms:

1. **`clientes`** (customers)
2. **`assinaturas`** (subscriptions) 
3. **`transacoes`** (transactions)

### Platform Field Mapping
The `utils/mapeamento.py` file contains critical field mappings between platforms:

```python
# Example: Transaction value handling
"valor_total": {
    "guru": "payment.total",        # Direct value in reais
    "ticto": "order.paid_amount",   # Value in centavos (divide by 100)
    "tipo": "float",
    "transformacao": "ticto: dividir por 100"
}
```

### Key Data Transformations
- **Ticto amounts**: Divide by 100 (centavos → reais)
- **Date normalization**: Convert all timestamps to `datetime` objects
- **Status mapping**: Normalize status values across platforms
- **JSON preservation**: Store original payloads for audit/evolution

## Webhook Event Types

### Guru Platform
- `approved` - Payment approved
- `waiting_payment` - Awaiting payment
- `canceled` - Subscription canceled

### Ticto Platform  
- `paid` - Payment successful
- `subscription_canceled` - Subscription cancelled
- `refused` - Payment declined
- `pix_expired` - PIX payment expired
- `overdue` - Payment overdue

## Technology Stack

### Core Frameworks
- **Dashboard**: Dash 2.14.0 + Plotly 5.18.0 + Bootstrap Components
- **API**: FastAPI 0.104.1 + Uvicorn (async)
- **Database**: PostgreSQL with AsyncPG + SQLAlchemy 2.0.23
- **Task Queue**: Celery 5.3.4 + Redis 5.0.1 + Flower monitoring
- **Data Processing**: Pandas 2.1.4 + NumPy 1.26.2

### Production Stack
- **Monitoring**: Sentry SDK + Prometheus metrics
- **Deployment**: Docker Compose ready
- **Database Migrations**: Alembic 1.12.1
- **HTTP Clients**: HTTPX + AIOHTTP for external API calls

## Sample Data Structure

The `Jsons (exemplos)/` directory contains real-world examples:

### Guru JSON Structure
```json
{
  "id": "uuid-format",
  "contact": {"email": "...", "name": "..."},
  "payment": {"total": 49.90, "method": "credit_card"},
  "subscription": {"id": "sub_...", "status": "active"},
  "dates": {"created_at": timestamp}
}
```

### Ticto Webhook Structure  
```json
{
  "id_transaction": "hash-format",
  "customer": {"email": "...", "name": "..."},
  "order": {"paid_amount": 4990, "order_date": "YYYY-MM-DD HH:MM:SS"},
  "status": "paid",
  "payment_method": "credit_card"
}
```

## Business Logic Considerations

### Complex Subscription States
- **Cancelled vs Expired**: Users can cancel billing but retain access until natural expiration
- **Multi-platform Reconciliation**: Same customer may exist on both platforms
- **Event Deduplication**: PIX expiration should update, not duplicate transactions

### Webhook Processing Strategy
1. **Idempotency**: Prevent duplicate processing of same webhook event
2. **Async Processing**: Use Celery for heavy data transformation
3. **Error Recovery**: Store failed webhooks for retry processing
4. **Audit Trail**: Preserve original webhook payloads

## Development Guidelines

### Code Organization
- Keep platform-specific logic in separate modules (`Api/guru.py`, `Api/ticto.py`)
- Use the mapping dictionaries in `utils/mapeamento.py` for all data transformation
- Implement async patterns for database operations and external API calls
- Store original JSON payloads for debugging and future evolution

### Testing Strategy
- Test webhook handlers with sample JSON data from `Jsons (exemplos)/`
- Mock external API calls to Guru/Ticto platforms
- Validate data transformations using the mapping dictionaries
- Test async database operations with pytest-asyncio

### Database Best Practices
- Use PostgreSQL JSONB for storing original webhook payloads
- Index frequently queried fields (email, platform, status, dates)
- Handle timezone-aware datetime objects consistently
- Implement proper foreign key relationships between entities

## Monitoring and Observability

### Metrics to Track
- Webhook processing success/failure rates
- Data transformation errors by platform
- Dashboard query performance
- Subscription lifecycle events

### Error Handling
- Sentry integration for production error tracking
- Structured logging for webhook processing
- Prometheus metrics for system health
- Celery task monitoring via Flower

## Project Status

This is an early-stage project with:
- ✅ **Architecture planned**: Complete field mapping and data flow design
- ✅ **Dependencies selected**: Production-ready technology stack  
- ✅ **Sample data analyzed**: Real webhook examples documented
- ⏳ **Implementation pending**: Core business logic and UI components
- ⏳ **Database schema**: Models and migrations need implementation
- ⏳ **Testing**: Test suite needs development

The project demonstrates sophisticated planning with clear focus on data normalization, real-time processing, and comprehensive business metrics for subscription analytics.