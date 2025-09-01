# Dashboard Comu - Sistema de Métricas Unificado

## Visão Geral

Sistema de dashboard unificado para consolidação e análise de dados de assinaturas e transações das plataformas **Guru** e **Ticto**. O projeto implementa um pipeline ETL completo com processamento de webhooks em tempo real para fornecer métricas de negócio consolidadas.

## 🚀 Funcionalidades

- **Processamento de Webhooks:** Recebimento e processamento em tempo real de eventos das plataformas Guru e Ticto
- **Normalização de Dados:** Unificação de dados de diferentes plataformas em um modelo canônico
- **Métricas de Negócio:** Cálculo automático de MRR, ARR, Churn, LTV, CAC e outras métricas
- **Dashboard Interativo:** Visualização de dados via Dash/Plotly
- **Gestão de Assinaturas:** Controle de status, cancelamentos, renovações e expirações
- **Auditoria Completa:** Armazenamento de payloads originais para rastreabilidade

## 🏗️ Arquitetura

```
Webhooks (Guru/Ticto) → FastAPI Endpoints → Data Transformation → PostgreSQL → Dashboard
```

### Componentes Principais

- **API (FastAPI):** Endpoints para recebimento de webhooks
- **Database (PostgreSQL):** Armazenamento unificado com JSONB para payloads
- **Services:** Lógica de negócio e processamento de dados
- **Dashboard (Dash):** Interface de visualização e métricas
- **Docker:** Containerização completa do ambiente

## 📊 Métricas Suportadas

### Métricas Principais
- **MRR (Monthly Recurring Revenue):** Receita recorrente mensal
- **ARR (Annual Recurring Revenue):** Receita recorrente anual
- **Churn Rate:** Taxa de cancelamento
- **LTV (Lifetime Value):** Valor do cliente ao longo do tempo
- **CAC (Customer Acquisition Cost):** Custo de aquisição
- **Ticket Médio:** Valor médio por transação

### Status de Transações
- **Guru:** approved, waiting_payment, canceled, abandoned, refunded, paid
- **Ticto:** authorized, refused, waiting_payment, pix_created, pix_expired, bank_slip_created, bank_slip_delayed, subscription_canceled, subscription_delayed, refunded, chargeback, claimed, card_exchanged, abandoned_cart

### Métodos de Pagamento
- **Guru:** 30+ métodos (credit_card, pix, paypal, applepay, etc.)
- **Ticto:** credit_card, pix, bank_slip

## 🛠️ Tecnologias

### Backend
- **FastAPI:** Framework web para APIs
- **SQLAlchemy:** ORM para banco de dados
- **PostgreSQL:** Banco de dados principal
- **Alembic:** Migrações de banco de dados
- **Docker:** Containerização

### Frontend
- **Dash:** Framework para dashboards
- **Plotly:** Visualizações interativas
- **Bootstrap:** Componentes de UI

### Infraestrutura
- **Docker Compose:** Orquestração de containers
- **PostgreSQL:** Banco de dados
- **Nginx:** Proxy reverso (produção)

## 📁 Estrutura do Projeto

```
Dashboard Comu/
├── src/
│   ├── Api/                    # Endpoints FastAPI
│   ├── dashboard/              # Aplicação Dash
│   │   ├── layouts/           # Componentes de layout
│   │   ├── components/        # Componentes reutilizáveis
│   │   ├── callbacks/         # Lógica de interatividade
│   │   └── assets/           # Arquivos estáticos
│   ├── database/              # Modelos e migrações
│   ├── services/              # Lógica de negócio
│   ├── scripts/               # Scripts utilitários
│   │   └── export/           # Scripts de exportação
│   └── utils/                 # Utilitários e mapeamentos
├── docs/                      # Documentação consolidada
├── tests/                     # Testes automatizados
│   └── integration/          # Testes de integração
├── Jsons (exemplos)/          # Exemplos de payloads
├── docker-compose.yml         # Configuração Docker
├── Dockerfile                 # Container da aplicação
└── requirements.txt           # Dependências Python
```

## 🚀 Instalação e Execução

### Pré-requisitos
- Docker e Docker Compose
- Git

### 1. Clone o repositório
```bash
git clone <repository-url>
cd Dashboard-Comu
```

### 2. Execute com Docker Compose
```bash
docker-compose up -d
```

### 3. Acesse a aplicação
- **API:** http://localhost:8000
- **Dashboard:** http://localhost:8052 (Docker) ou http://localhost:8050 (Local)
- **Health Check:** http://localhost:8000/health

### 4. Execução
- **Docker (Automático):** `docker-compose up -d` - API e Dashboard iniciam juntos
- **Local:** `python simple_dashboard.py`
- **Configurável:** `python run_dashboard.py --help`

## 📚 Documentação

### Documentação Principal
- **[Documentação Completa](docs/README.md)** - Índice centralizado de toda documentação
- **Dashboard Completo:** `docs/documentacao_dashboard_completa.md` - Documentação completa do dashboard
- **Métricas Faltantes:** `docs/metricas_faltantes_implementacao.md` - Análise das métricas que precisam ser implementadas
- **Métricas de Negócio:** `docs/documentacao_metricas.md`
- **Mapeamento Universal:** `docs/mapeamento_dados_universal.md`
- **Documentação Guru:** `docs/documentacao_guru.md`
- **Documentação Ticto:** `docs/documentacao_ticto.md`

### Resumo das Métricas
- **✅ Implementadas**: 5 métricas (MRR, ARR, Churn, LTV, CAC)
- **❌ Faltando**: 20 métricas (incluindo MRA, Growth, ARPU, etc.)
- **📊 Total Dashboard**: 25 métricas exibidas

### Comandos Úteis
```bash
# Acessar banco de dados
docker-compose exec db psql -U metrics_user -d metrics_db

# Executar migrações
docker-compose exec api bash
cd src
alembic upgrade head

# Logs da aplicação
docker-compose logs -f api
```

## 🔧 Configuração de Webhooks

### Guru
- **URL:** `https://seudominio.com/webhook/guru`
- **Método:** POST
- **Autenticação:** Via API token

### Ticto
- **URL:** `https://seudominio.com/webhook/ticto`
- **Método:** POST
- **Autenticação:** Via token

## 📊 Estrutura do Banco de Dados

### Tabelas Principais
- **clientes:** Informações dos clientes
- **assinaturas:** Estado atual das assinaturas
- **transacoes:** Log de eventos financeiros

### Campos Chave
- `data_expiracao_acesso`: Determina se cliente está ativo
- `json_completo`: Payload original para auditoria
- `valor_mensal`/`valor_anual`: Valores normalizados por plano

## 🧪 Testes

### Casos de Teste Implementados
- [x] Venda realizada -> Cancelamento de assinatura
- [x] Venda Realizada -> Assinatura atrasada
- [x] Métrica de Abandono de Carrinho

### Casos de Teste Pendentes
- [ ] Cartão Atualizado - card_exchanged
- [ ] Pix Criado - Pix expirado
- [ ] Boleto Criado - Boleto Expirado
- [ ] Métrica "Claimed" - Venda reclamada
- [ ] Assinatura Cancelada -> Retomada

## 🔄 Fluxo de Dados

1. **Recepção:** Webhooks recebidos via endpoints FastAPI
2. **Validação:** Verificação de payload e campos obrigatórios
3. **Transformação:** Normalização conforme mapeamentos
4. **Armazenamento:** Inserção/atualização no PostgreSQL
5. **Métricas:** Cálculo automático de métricas de negócio
6. **Visualização:** Dashboard atualizado em tempo real

## 📈 Métricas de Negócio

### Cálculo de MRR
```sql
SELECT SUM(valor_mensal)
FROM assinaturas
WHERE data_expiracao_acesso >= :data_referencia
  AND status NOT IN ('refunded', 'chargeback')
```

### Cálculo de Churn
```sql
-- Taxa de churn = (cancelados / ativos_inicio) * 100
```

## 🛡️ Segurança

- **Validação de Payload:** Verificação de campos obrigatórios
- **Idempotência:** Prevenção de processamento duplicado
- **Auditoria:** Log completo de todos os eventos
- **HTTPS:** Comunicação criptografada (produção)

## 📝 Logs e Monitoramento

### Logs Estruturados
- Processamento de webhooks
- Erros de validação
- Métricas calculadas
- Performance de queries

### Métricas de Sistema
- Taxa de sucesso de webhooks
- Tempo de processamento
- Uso de recursos
- Erros por plataforma

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para dúvidas ou suporte:
- Abra uma issue no GitHub
- Consulte a documentação em `docs/`
- Verifique os exemplos em `Jsons (exemplos)/`

---

**Desenvolvido para a Comunidade da Arte** 🎨 