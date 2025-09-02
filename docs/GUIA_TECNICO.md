# 🔧 GUIA TÉCNICO COMPLETO - Dashboard Comu

## 🎯 Visão Geral Técnica

Este guia documenta a arquitetura técnica completa do Dashboard Comu, incluindo design do sistema, APIs das plataformas Guru e Ticto, mapeamento de dados universal, segurança e configurações técnicas.

---

## 🏗️ ARQUITETURA DO SISTEMA

### **Visão Geral da Arquitetura**

```
Internet → Nginx (80/443) → FastAPI (8000) → Dashboard (8052)
                              ↓
                         PostgreSQL (5432)
```

### **Componentes Principais**

#### **1. API (FastAPI)**
- **Propósito**: Endpoints para recebimento de webhooks
- **Porta**: 8000
- **Funcionalidades**: 
  - Validação de payloads
  - Autenticação por token
  - Rate limiting
  - Logs estruturados

#### **2. Database (PostgreSQL)**
- **Versão**: 15
- **Banco**: metrics_db
- **Usuário**: metrics_user
- **Características**: JSONB para payloads originais

#### **3. Dashboard (Dash/Plotly)**
- **Framework**: Dash com Plotly
- **Porta**: 8052 (Docker) / 8050 (Local)
- **UI**: Bootstrap responsivo
- **Tema**: Inter + FontAwesome

#### **4. Docker & Infraestrutura**
- **Containerização**: Docker + Docker Compose
- **Proxy**: Nginx (produção)
- **Orquestração**: Docker Compose

---

## 📊 MODELO DE DADOS

### **Estrutura do Banco**

#### **Tabela: clientes**
```sql
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    documento VARCHAR(50) UNIQUE,
    data_criacao TIMESTAMP NOT NULL
);
```

#### **Tabela: assinaturas**
```sql
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
    valor_anual DECIMAL(10, 2),
    ultima_atualizacao TIMESTAMP
);
```

#### **Tabela: transacoes**
```sql
CREATE TABLE transacoes (
    id SERIAL PRIMARY KEY,
    id_transacao_origem VARCHAR(255) UNIQUE NOT NULL,
    assinatura_id INTEGER REFERENCES assinaturas(id),
    cliente_id INTEGER REFERENCES clientes(id),
    status VARCHAR(50),
    valor DECIMAL(10, 2),
    valor_bruto DECIMAL(10, 2),
    valor_liquido DECIMAL(10, 2),
    metodo_pagamento VARCHAR(50),
    data_transacao TIMESTAMP,
    motivo_recusa TEXT,
    json_completo JSONB
);
```

---

## 🔌 APIS E INTEGRAÇÃO

### **Plataforma Guru**

#### **Webhook de Transações**
```json
{
  "webhook_type": "transaction",
  "id": "9081534a-7512-4dab-9172-218c1dc1f263",
  "status": "approved",
  "api_token": "mLjcGjzKGnXme5b7gbuKMggL34Ecdt5NHGihxfWr",
  "contact": {
    "name": "Nome Contato",
    "email": "email@email.com",
    "doc": "01234567890"
  },
  "payment": {
    "total": 500,
    "method": "credit_card"
  },
  "product": {
    "id": "1587151083",
    "name": "Assinatura Mundipagg"
  },
  "subscription": {
    "id": "sub_123",
    "started_at": "2024-08-19T15:37:16.673Z"
  }
}
```

#### **Webhook de Assinaturas**
```json
{
  "webhook_type": "subscription",
  "subscription": {
    "id": "sub_123",
    "status": "active",
    "started_at": "2024-08-19T15:37:16.673Z",
    "next_charge": "2024-09-19T15:37:16.673Z"
  }
}
```

#### **Status Suportados**
- **Transações**: approved, waiting_payment, canceled, abandoned, refunded, paid
- **Assinaturas**: active, canceled, expired, inactive, pastdue, started, trial

#### **Métodos de Pagamento**
- credit_card, pix, paypal, applepay, google_pay, billet, bank_transfer, cryptocurrency, etc.

---

### **Plataforma Ticto**

#### **Webhook de Vendas**
```json
{
  "version": "2.0",
  "status": "authorized",
  "status_date": "2024-02-10 19:19:17",
  "payment_method": "credit_card",
  "token": "AqmMaY4OjKCdxSwIk1bsGLtlOzTvlJQmZ2w3nEC6Edqn5am7uJZ88tTp1RuN2T8MD4aWVWvqFzh4M6hFKvFr1EjM4u7zvgNbwuIc",
  "order": {
    "id": 797057,
    "hash": "TOC8C0E11002NKR132S",
    "transaction_hash": "TPC1D86F1002MAF0JRF",
    "paid_amount": 3990,
    "order_date": "2024-02-10 19:19:14"
  },
  "customer": {
    "name": "Julia Lazaro Barone",
    "email": "julia.lbarone@gmail.com",
    "cpf": "13123404790"
  },
  "item": {
    "product_name": "Comunidade da Arte",
    "offer_name": "Assinatura Mensal",
    "amount": 3990,
    "days_of_access": 30
  },
  "subscriptions": [
    {
      "id": 121783,
      "interval": 1,
      "next_charge": "2024-03-10 00:00:00"
    }
  ]
}
```

#### **Eventos Especiais**

##### **Carrinho Abandonado**
```json
{
  "status": "abandoned_cart",
  "name": "Nome Cliente",
  "email": "cliente@email.com",
  "product_name": "Produto",
  "created_at": "28/06/2025 01:38:52"
}
```

##### **Cartão Atualizado**
```json
{
  "status": "card_exchanged",
  "transaction": { "hash": "..." },
  "customer": { "email": "..." },
  "payment_method": "credit_card"
}
```

##### **Venda Reclamada**
```json
{
  "status": "claimed",
  "order": { "transaction_hash": "..." },
  "customer": { "email": "..." }
}
```

#### **Status Suportados**
- **Transações**: authorized, refused, waiting_payment, pix_created, pix_expired, bank_slip_created, bank_slip_delayed, subscription_canceled, subscription_delayed, refunded, chargeback, claimed, card_exchanged, abandoned_cart

#### **Métodos de Pagamento**
- credit_card, pix, bank_slip

---

## 🔄 MAPEAMENTO DE DADOS UNIVERSAL

### **Tabela: transacoes**

| Campo no DB | Guru | Ticto | Tipo | Observação |
|-------------|------|-------|------|------------|
| id_transacao_origem | id | order.transaction_hash | str | Guru: UUID, Ticto: hash |
| id_assinatura_origem | subscription.id | subscriptions[0].id | str/int | Guru: string, Ticto: int |
| plataforma | "guru" | "ticto" | str | Valor fixo |
| email_cliente | contact.email | customer.email | str | |
| valor_total | payment.total | order.paid_amount | float | Ticto: dividir por 100 |
| status | status | status | str | Normalizar valores |
| metodo_pagamento | payment.method | payment_method | str | |
| data_evento | dates.created_at | order.order_date | datetime | |
| json_completo | json | json | json | Payload original |

### **Tabela: clientes**

| Campo no DB | Guru | Ticto | Tipo | Observação |
|-------------|------|-------|------|------------|
| nome | contact.name | customer.name | str | |
| email | contact.email | customer.email | str | |
| documento | contact.doc | customer.cpf | str | |
| data_criacao | dates.created_at | order.order_date | datetime | |

### **Tabela: assinaturas**

| Campo no DB | Guru | Ticto | Tipo | Observação |
|-------------|------|-------|------|------------|
| id_assinatura_origem | subscription.id | subscriptions[0].id | str/int | |
| plataforma | "guru" | "ticto" | str | |
| produto_nome | product.name | item.product_name | str | |
| status | subscription.last_status | status | str | |
| data_inicio | subscription.started_at | order.order_date | datetime | |
| data_proxima_cobranca | subscription.next_charge | subscriptions[0].next_charge | datetime | |
| valor_mensal | payment.total | order.paid_amount | float | |

---

## 🛡️ SISTEMA DE SEGURANÇA

### **Componentes de Segurança**

#### **1. Autenticação por Token**
- **Guru**: Valida `payload.api_token` contra `GURU_ACCOUNT_TOKEN`
- **Ticto**: Valida `token` (nível raiz) contra lista de tokens válidos
- **Formato**: Tokens únicos por plataforma/account

#### **2. Validação de Payload**
- **Estrutura JSON**: Validação de campos obrigatórios
- **Tipos de dados**: Verificação de tipos corretos
- **Campos obrigatórios**: Validação específica por plataforma

#### **3. Rate Limiting**
- **Limite por minuto**: Configurável via variáveis de ambiente
- **Limite por hora**: Proteção contra spam
- **Por IP**: Controle individual por endereço IP

#### **4. Logs de Segurança**
- **Eventos de autenticação**: Sucesso/falha de validação
- **Tentativas de acesso**: IPs e timestamps
- **Rate limiting**: Logs de excedentes
- **Erros de validação**: Detalhes de falhas

### **Configuração de Segurança**

#### **Variáveis de Ambiente (.env)**
```env
# Tokens de Autenticação
GURU_ACCOUNT_TOKEN=seu_token_guru_aqui
TICTO_WEBHOOK_TOKENS=token1,token2,token3

# Chave Secreta da Aplicação
SECRET_KEY=chave_gerada_com_openssl_32_bytes

# Configurações de Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Hosts Permitidos
ALLOWED_HOSTS=localhost,dashboard.suaempresa.com.br
```

#### **Geração de SECRET_KEY**
```bash
# Gerar chave secreta segura
openssl rand -hex 32
```

---

## 🔧 CONFIGURAÇÕES TÉCNICAS

### **Docker Compose**

#### **Desenvolvimento (docker-compose.yml)**
```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: metrics_db
      POSTGRES_USER: metrics_user
      POSTGRES_PASSWORD: asdfghjkl
    ports:
      - "5432:5432"
  
  api:
    build: .
    command: python -m src.main
    ports:
      - "8000:8000"  # API FastAPI
      - "8052:8052"  # Dashboard Dash
    depends_on:
      - db
```

#### **Produção (docker-compose.prod.yml)**
```yaml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
  
  api:
    build: .
    expose:
      - "8000"
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

### **Nginx (Produção)**

#### **Configuração (nginx/nginx.conf)**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }
    
    upstream dashboard {
        server api:8052;
    }
    
    server {
        listen 80;
        server_name dashboard.suaempresa.com.br;
        
        location / {
            proxy_pass http://dashboard;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /api/ {
            proxy_pass http://api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

---

## 📊 SISTEMA DE BACKFILL

### **Arquitetura de Backfill**

#### **1. Webhook Handler**
- **Propósito**: Processa webhooks em tempo real
- **Responsabilidades**: Validação, roteamento, processamento de eventos
- **Características**: Otimizado para processamento rápido

#### **2. Historical Data Processor**
- **Propósito**: Processa dados históricos das APIs
- **Responsabilidades**: Conversão, processamento em lote, idempotência
- **Características**: Otimizado para grandes volumes

#### **3. Funções Compartilhadas**
- **get_or_create_cliente()**: Criação/recuperação de clientes
- **get_or_create_assinatura()**: Criação/atualização de assinaturas
- **salvar_transacao()**: Salvamento de transações

### **Scripts de Backfill**

#### **Guru**
```bash
# Teste com 5 dados
docker-compose exec api python src/scripts/test_backfill_5_dados_guru.py

# Backfill completo
docker-compose exec api python src/scripts/backfill_guru.py
```

#### **Ticto**
```bash
# Teste com 5 dados
docker-compose exec api python src/scripts/test_backfill_5_dados.py

# Backfill completo
docker-compose exec api python src/scripts/backfill_ticto_completo.py
```

---

## 🧪 TESTES E VALIDAÇÃO

### **Testes de Segurança**
```bash
# Verificar configuração de segurança
docker-compose exec api python src/scripts/check_security_config.py

# Testar sistema de segurança
docker-compose exec api python src/scripts/test_security.py
```

### **Testes de Validação**
```bash
# Testar validação de payloads
docker-compose exec api python src/scripts/test_sync_validation_simple.py

# Testar APIs
docker-compose exec api python src/scripts/test_guru_api.py
```

### **Testes de Integração**
```bash
# Testar integração dashboard
docker-compose exec api python src/scripts/test_integracao_dashboard.py

# Testar métricas
docker-compose exec api python src/scripts/test_metrics_calculator.py
```

---

## 📝 LOGS E MONITORAMENTO

### **Logs Estruturados**
- **Processamento de webhooks**: Sucesso/falha, payload, tempo
- **Erros de validação**: Campo, valor, motivo
- **Métricas calculadas**: Valor, fórmula, tempo de execução
- **Performance de queries**: Tempo, complexidade, otimizações

### **Métricas de Sistema**
- **Taxa de sucesso de webhooks**: Por plataforma, por status
- **Tempo de processamento**: Média, pico, distribuição
- **Uso de recursos**: CPU, memória, disco, rede
- **Erros por plataforma**: Categorização e frequência

---

## 🔮 PRÓXIMOS PASSOS TÉCNICOS

### **Melhorias de Arquitetura**
1. **Cache Redis**: Para métricas frequentemente acessadas
2. **Message Queue**: Para processamento assíncrono de webhooks
3. **Microserviços**: Separação de responsabilidades
4. **API Gateway**: Centralização de autenticação e rate limiting

### **Monitoramento e Observabilidade**
1. **Prometheus + Grafana**: Métricas de sistema
2. **ELK Stack**: Logs centralizados
3. **Tracing distribuído**: Jaeger ou Zipkin
4. **Health checks**: Endpoints de saúde para cada serviço

---

## 📚 DOCUMENTAÇÃO RELACIONADA

- **`README.md`** - Visão geral e status do projeto
- **`GUIA_IMPLEMENTACAO.md`** - Implementação das métricas
- **`GUIA_OPERACAO.md`** - Deploy e operação

---

**🔧 ARQUITETURA TÉCNICA COMPLETA - SISTEMA ESCALÁVEL E SEGURO!**

**Status**: ✅ **IMPLEMENTADO**  
**Última atualização**: 28/08/2025  
**Autor**: Dashboard Comu Team
