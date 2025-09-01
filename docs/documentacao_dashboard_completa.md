# Documentação Completa do Dashboard - Comunidade da Arte

## Visão Geral

O Dashboard da Comunidade da Arte é uma aplicação web completa desenvolvida em **Dash/Plotly** que consolida e visualiza dados de assinaturas das plataformas **Guru** e **Ticto**. O sistema oferece uma visão unificada e em tempo real das métricas de negócio essenciais.

## 🏗️ Arquitetura do Dashboard

### Stack Tecnológico

**Frontend:**
- **Dash**: Framework principal para dashboards interativos
- **Plotly**: Biblioteca de visualizações gráficas
- **Dash Bootstrap Components**: Componentes de UI responsivos
- **HTML/CSS**: Estrutura e estilização customizada

**Backend:**
- **FastAPI**: API REST para webhooks e dados
- **PostgreSQL**: Banco de dados principal
- **SQLAlchemy**: ORM para acesso aos dados
- **Alembic**: Migrações de banco de dados

**Infraestrutura:**
- **Docker**: Containerização completa
- **Docker Compose**: Orquestração de serviços
- **Nginx**: Proxy reverso (produção)

### Estrutura de Arquivos

```
src/dashboard/
├── app.py                    # Aplicação principal Dash
├── layouts/                  # Componentes de layout
│   ├── __init__.py
│   ├── main_layout.py       # Layout principal responsivo
│   ├── header.py            # Header com logo e filtros
│   ├── main_metrics_section.py    # Seção principal de métricas
│   ├── charts_section.py    # Seção de gráficos
│   ├── performance_metrics_section.py  # Métricas de performance
│   ├── area_chart_section.py      # Gráfico de áreas
│   └── final_metrics_grid.py      # Grid final de métricas
├── components/              # Componentes reutilizáveis
│   ├── __init__.py
│   ├── metric_card.py      # Cards de métricas
│   ├── growth_badge.py     # Badges de crescimento
│   └── chart_container.py  # Containers de gráficos
├── callbacks/              # Lógica de interatividade
│   ├── __init__.py
│   ├── date_callbacks.py   # Callbacks de filtros de data
│   ├── chart_callbacks.py  # Callbacks dos gráficos
│   └── area_chart_callbacks.py  # Callbacks do gráfico de áreas
└── assets/                 # Arquivos estáticos
    └── logo_comu.png       # Logo da empresa
```

## 📊 Seções do Dashboard

### 1. Header (Navegação Superior)

**Localização**: `src/dashboard/layouts/header.py`

**Componentes:**
- **Logo**: `logo_comu.png` (40px altura)
- **Seletor de Datas**: Filtro de período para análise
- **Tema**: Fundo roxo (#8B5CF6) com texto branco

**Funcionalidades:**
- Filtro de período de análise
- Responsivo para mobile/desktop
- Integração com callbacks de data

### 2. Seção Principal de Métricas

**Localização**: `src/dashboard/layouts/main_metrics_section.py`

**Layout:**
- **Card Principal**: "Faturamento Total" (50% largura)
  - Valor principal em destaque
  - Badges "Esse Mês" e "Esse Ano" alinhados horizontalmente
  - Subtítulo com receita bruta
- **Cards Secundários** (50% largura):
  - "Quantidade Vendas" (card único)
  - "Qnt. de Alunos" e "LTV Geral" (cards lado a lado)

**Métricas Exibidas:**
- Faturamento Total (R$)
- Quantidade de Vendas
- Quantidade de Alunos
- LTV Geral

### 3. Seção de Gráficos

**Localização**: `src/dashboard/layouts/charts_section.py`

**Layout**: 3 gráficos lado a lado (lg=4 cada)

**Gráficos:**
1. **Compras por produtos** - Gráfico de barras
2. **Receita por produto** - Gráfico de barras
3. **Número de vendas por produto x data** - Gráfico de linha

**Características:**
- Altura: 320px
- Responsivo
- Interativo (hover, zoom, pan)
- Export para PNG

### 4. Seção de Métricas de Performance

**Localização**: `src/dashboard/layouts/performance_metrics_section.py`

**Layout:**
- **Primeira linha**: 5 métricas pequenas centralizadas
- **Segunda linha**: 3 métricas grandes com badges de crescimento

**Métricas da Primeira Linha:**
- ARPU (Average Revenue Per User)
- CAC (Customer Acquisition Cost)
- CPL (Cost Per Lead)
- NPS (Net Promoter Score)
- Receita média mensal

**Métricas da Segunda Linha:**
- Receita Anual da Empresa (com badge de crescimento)
- ROI Geral (com badge de crescimento)
- Margem de Lucro (com badge de crescimento)

### 5. Seção de Gráfico de Áreas

**Localização**: `src/dashboard/layouts/area_chart_section.py`

**Gráfico**: "Receita de recorrência x vendas"
- **Tipo**: Gráfico de área empilhada
- **Dados**: 7 produtos com cores distintas
- **Período**: Últimos 15 meses
- **Altura**: 400px

**Produtos Analisados:**
1. Comunidade da Arte - Mensal (Preto)
2. Comunidade da Arte - Anual (Roxo)
3. Comunidade da Arte (Cinza claro)
4. Como Criar Personagens? (Cinza médio)
5. Comissions na Gringa (Cinza escuro)
6. Formação Tattoo (Cinza)
7. Mentoria - Tatuador PRO (Cinza escuro 2)

### 6. Grid Final de Métricas

**Localização**: `src/dashboard/layouts/final_metrics_grid.py`

**Layout**: 4 linhas com 14 métricas totais

**Primeira Linha (4 métricas):**
- MRR - (TOTAL)
- ARR - (TOTAL)
- Recorrência - MRA (Monthly Recurrence Average)
- MRR - Growth (%)

**Segunda Linha (4 métricas):**
- MRR - (Plano Mensal)
- ARR - (Plano Mensal)
- **Assinaturas Ativas** (DESTACADO - Fundo roxo)
- Assinaturas Canceladas

**Terceira Linha (4 métricas):**
- MRR - (Plano Anual)
- ARR - (Plano Anual)
- Churn Rate (%)
- Retention Rate (%)

**Quarta Linha (2 métricas grandes):**
- Assinaturas esse mês
- Assinaturas do Mês Passado

## 🔧 Componentes Reutilizáveis

### Metric Card
**Localização**: `src/dashboard/components/metric_card.py`

**Funcionalidades:**
- Exibição de título, valor e subtítulo
- Badge de crescimento opcional
- Cores customizáveis
- Destaque visual opcional

### Growth Badge
**Localização**: `src/dashboard/components/growth_badge.py`

**Funcionalidades:**
- Indicador de crescimento/queda
- Setas direcionais
- Cores baseadas no valor
- Formatação de percentual

### Chart Container
**Localização**: `src/dashboard/components/chart_container.py`

**Funcionalidades:**
- Container padronizado para gráficos
- Título e subtítulo
- Estado de carregamento
- Configurações de export

## 📈 Callbacks e Interatividade

### Date Callbacks
**Localização**: `src/dashboard/callbacks/date_callbacks.py`

**Funcionalidades:**
- Filtro de período de análise
- Atualização automática de métricas
- Persistência de seleção
- Validação de datas

### Chart Callbacks
**Localização**: `src/dashboard/callbacks/chart_callbacks.py`

**Funcionalidades:**
- Geração de gráficos dinâmicos
- Dados baseados em filtros
- Configurações de visualização
- Tratamento de dados vazios

### Area Chart Callbacks
**Localização**: `src/dashboard/callbacks/area_chart_callbacks.py`

**Funcionalidades:**
- Gráfico de área empilhada
- Dados sintéticos para demonstração
- Cores personalizadas por produto
- Hover interativo

## 🎨 Design e UX

### Paleta de Cores
- **Primária**: #8B5CF6 (Roxo)
- **Secundária**: #F8F9FA (Cinza claro)
- **Texto**: #1F2937 (Cinza escuro)
- **Destaque**: #8B5CF6 (Roxo para cards especiais)

### Tipografia
- **Fonte**: Inter, -apple-system, BlinkMacSystemFont, sans-serif
- **Tamanhos**: 0.875rem (pequeno), 1.5rem (médio), 2rem (grande)
- **Pesos**: 400 (normal), 700 (bold)

### Responsividade
- **Mobile**: 1 coluna (width=12)
- **Tablet**: 2 colunas (md=6)
- **Desktop**: 4 colunas (lg=3)
- **Breakpoints**: Bootstrap 5

### Animações e Transições
- Hover effects nos cards
- Transições suaves
- Loading states
- Feedback visual

## 🚀 Execução e Deploy

### Desenvolvimento Local
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar dashboard
python src/dashboard/app.py
```

### Docker (Recomendado)
```bash
# Construir e executar
docker-compose up --build -d

# Acessar dashboard
http://localhost:8052
```

### Portas
- **Dashboard**: 8052 (Docker) / 8050 (Local)
- **API**: 8000
- **Banco**: 5432

## 📊 Integração com Dados

### Fonte de Dados
- **Banco**: PostgreSQL via SQLAlchemy
- **Tabelas**: `assinaturas`, `clientes`, `transacoes`
- **Plataformas**: Guru e Ticto
- **Tempo real**: Via webhooks

### Métricas Calculadas
- **MRR/ARR**: Baseado em `valor_mensal` e `valor_anual`
- **Churn**: Baseado em `status` e `data_expiracao_acesso`
- **LTV**: Calculado com churn rate real
- **Crescimento**: Comparação temporal

### Cache e Performance
- Dados em tempo real
- Queries otimizadas
- Índices no banco
- Lazy loading de gráficos

## 🔍 Monitoramento e Logs

### Logs Estruturados
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Dashboard iniciado com sucesso")
```

### Métricas de Performance
- Tempo de carregamento
- Uso de memória
- Queries executadas
- Erros e exceções

### Health Checks
- Status do banco de dados
- Conectividade com APIs
- Disponibilidade de serviços
- Validação de dados

## 🛠️ Manutenção e Atualizações

### Estrutura Modular
- Componentes independentes
- Fácil adição de novas métricas
- Configuração centralizada
- Versionamento de layouts

### Backup e Recuperação
- Backup automático do banco
- Versionamento de código
- Rollback de mudanças
- Documentação de alterações

### Escalabilidade
- Arquitetura stateless
- Load balancing ready
- Cache distribuído
- Microserviços ready

## 📚 Recursos Adicionais

### Documentação Relacionada
- `docs/documentacao_metricas.md` - Métricas implementadas
- `docs/implementacao_dashboard_visual.md` - Implementação visual
- `docs/mapeamento_dados_universal.md` - Mapeamento de dados

### Scripts Úteis
- `src/scripts/test_metrics_calculator.py` - Testes de métricas
- `src/scripts/exemplo_uso_metricas.py` - Exemplos de uso

### APIs Disponíveis
- `GET /health` - Status da aplicação
- `GET /metrics` - Métricas em JSON
- `POST /webhook/guru` - Webhook Guru
- `POST /webhook/ticto` - Webhook Ticto

---

**Última atualização**: 28/08/2025  
**Versão**: 1.0  
**Autor**: Dashboard Comu Team
