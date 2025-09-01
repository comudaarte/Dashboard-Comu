# Documentação das Métricas - Dashboard Comu

## Visão Geral

Este documento detalha a implementação completa do sistema de métricas para o Dashboard de Assinaturas da Comunidade da Arte. O sistema calcula automaticamente todas as métricas essenciais de negócio baseado nos dados consolidados das plataformas Guru e Ticto.

## Arquitetura do Sistema de Métricas

### Componentes Principais

```
src/services/metrics_calculator.py    # Calculador principal
src/scripts/test_metrics_calculator.py # Testes e validação
src/scripts/exemplo_uso_metricas.py   # Exemplos práticos
```

### Classe Principal: `MetricsCalculator`

```python
from src.database.connection import get_session
from src.services.metrics_calculator import MetricsCalculator

# Inicialização
db_session = get_session()
calculator = MetricsCalculator(db_session)

# Uso básico
metrics = calculator.get_dashboard_metrics()
```

## Métricas Implementadas

### 1. 💰 MRR (Monthly Recurring Revenue)

**Definição**: Receita recorrente mensal baseada em assinaturas ativas.

**Lógica de Cálculo**:
```sql
-- Para planos mensais: usa valor_mensal
-- Para planos anuais: usa valor_anual / 12
SELECT 
    COALESCE(SUM(valor_mensal), 0) + COALESCE(SUM(valor_anual / 12.0), 0) as mrr_total
FROM assinaturas 
WHERE 
    data_expiracao_acesso >= :data_referencia
    AND status NOT IN ('refunded', 'chargeback')
    AND (valor_mensal IS NOT NULL OR valor_anual IS NOT NULL)
```

**API**:
```python
mrr_data = calculator.calculate_mrr(data_referencia=None)

# Resultado:
{
    "mrr_total": 16056.38,
    "mrr_por_plataforma": {"guru": 16056.38, "ticto": 0.0},
    "detalhes": {
        "breakdown_por_tipo": {
            "mensal": {"assinaturas": 26, "mrr": 777.40},
            "anual": {"assinaturas": 512, "mrr": 15278.98}
        }
    }
}
```

**Regras de Negócio**:
- ✅ Inclui apenas assinaturas com acesso vigente
- ✅ Exclui reembolsos e chargebacks
- ✅ Diferencia planos mensais e anuais corretamente
- ✅ Considera apenas valores preenchidos no banco

---

### 2. 📈 ARR (Annual Recurring Revenue)

**Definição**: Receita anual recorrente projetada.

**Fórmula**: `ARR = MRR × 12`

**API**:
```python
arr_data = calculator.calculate_arr(data_referencia=None)

# Resultado:
{
    "arr_total": 192676.60,
    "arr_por_plataforma": {"guru": 192676.60, "ticto": 0.0}
}
```

---

### 3. 📉 Taxa de Churn (CORRIGIDA)

**Definição**: Percentual de clientes que cancelaram no período, **EXCLUINDO PIX expirados**.

**CORREÇÃO CRÍTICA**: Esta métrica foi corrigida para excluir cancelamentos por PIX não pago, que não representam churn real, apenas abandono de checkout.

**Lógica de Cálculo Corrigida**:
```sql
-- Taxa = (Cancelamentos REAIS no período / Assinaturas ativas no início) × 100
-- EXCLUI: PIX expirados (cancelamentos em <= 72h)
WITH assinaturas_ativas_inicio AS (
    SELECT plataforma, COUNT(*) as ativas_inicio
    FROM assinaturas 
    WHERE 
        data_inicio <= :data_inicio
        AND data_expiracao_acesso > :data_inicio
        AND status NOT IN ('refunded', 'chargeback')
),
cancelamentos_reais_periodo AS (
    -- APENAS cancelamentos de assinaturas que JÁ FORAM ATIVAS
    SELECT plataforma, COUNT(*) as cancelamentos
    FROM assinaturas 
    WHERE 
        status IN ('canceled', 'subscription_canceled')
        AND ultima_atualizacao BETWEEN :data_inicio AND :data_fim
        -- FILTRO CRÍTICO: Exclui PIX expirados (< 72h de vida)
        AND EXTRACT(EPOCH FROM (ultima_atualizacao - data_inicio))/3600 > 72
)
SELECT 
    (cancelamentos * 100.0) / ativas_inicio as churn_rate_corrigido
FROM assinaturas_ativas_inicio a
JOIN cancelamentos_reais_periodo c ON a.plataforma = c.plataforma
```

**API (Corrigida)**:
```python
# O método principal já inclui a correção para PIX expirados
churn_data = calculator.calculate_churn_rate(periodo_dias=30)

# Resultado (já com correção aplicada):
{
    "churn_rate_total": 30.35,
    "renewal_rate_total": 69.65,
    "churn_por_plataforma": {"guru": 30.35},
    "total_ativas_inicio": 257,
    "total_cancelamentos": 78,             # Cancelamentos reais (sem PIX expirado)
    "total_pix_expirados_excluidos": 5,   # PIX expirados que foram excluídos
    "detalhes": {
        "correcao_aplicada": {
            "filtro": "Excluídos cancelamentos em <= 72h (PIX expirado)",
            "motivacao": "PIX expirados não representam churn real, apenas abandono de checkout"
        }
    }
}
```

**Status de Cancelamento por Plataforma**:
- **Guru**: `'canceled'`
- **Ticto**: `'subscription_canceled'`

**⚠️ PROBLEMA IDENTIFICADO E CORRIGIDO**:

**Cenário PIX Guru**:
1. **PIX gerado** → Status vira `inactive` imediatamente
2. **PIX expira** (3 dias depois) → Status vira `canceled` 
3. **NUNCA foram assinaturas ativas** → Não deveriam contar no churn

**Impacto**: PIX expirados estavam inflando artificialmente a taxa de churn.

**Solução**: Filtro de 72h para excluir cancelamentos por PIX não pago.

**Resultado**: Redução média de 1-2% na taxa de churn (dados reais: 32.30% → 30.35%).

---

### 4. 💎 LTV (Lifetime Value)

**Definição**: Valor médio que um cliente gera ao longo de sua vida útil.

**Fórmula**: `LTV = Ticket Médio Anual ÷ (Taxa de Churn Mensal ÷ 100)`

**Lógica de Cálculo**:
```sql
-- Ticket médio anual
SELECT AVG(
    CASE 
        WHEN valor_anual IS NOT NULL THEN valor_anual
        WHEN valor_mensal IS NOT NULL THEN valor_mensal * 12
        ELSE 0
    END
) as ticket_medio_anual
FROM assinaturas 
WHERE data_expiracao_acesso >= :data_ref
```

**API**:
```python
ltv_data = calculator.calculate_ltv(data_referencia=None)

# Resultado:
{
    "ltv_total": 703.59,
    "ltv_por_plataforma": {"guru": 703.59},
    "ticket_medio_anual_geral": 358.13,
    "churn_rate_utilizado": 50.90
}
```

---

### 5. 👥 CAC (Customer Acquisition Cost)

**Definição**: Custo para adquirir um novo cliente.

**Fórmula**: `CAC = Custo Total de Marketing ÷ Número de Novos Clientes`

**API**:
```python
# Sem custo de marketing (apenas conta novos clientes)
cac_data = calculator.calculate_cac(periodo_dias=30)

# Com custo de marketing
cac_data = calculator.calculate_cac(periodo_dias=30, custo_marketing=10000)

# Resultado:
{
    "cac_total": 24.15,  # R$ 10.000 ÷ 414 clientes
    "novos_clientes_periodo": 414,
    "custo_marketing_informado": 10000
}
```

---

### 6. 🏆 Métricas Consolidadas

**API Principal para Dashboard**:
```python
dashboard_metrics = calculator.get_dashboard_metrics(
    data_referencia=None,
    periodo_analise=30
)

# Resultado estruturado para dashboard:
{
    "metricas_principais": {
        "mrr": {"valor": 16056.38, "moeda": "BRL"},
        "arr": {"valor": 192676.60, "moeda": "BRL"},
        "churn_rate": {"valor": 50.90, "unidade": "%"},
        "ltv": {"valor": 703.59, "moeda": "BRL"},
        "total_assinaturas_ativas": {"valor": 538, "unidade": "unidades"}
    },
    "metricas_por_plataforma": {
        "guru": {"mrr": 16056.38, "churn_rate": 50.90},
        "ticto": {"mrr": 0.0, "churn_rate": 0.0}
    }
}
```

## Validação e Integridade

### Sistema de Validação Automática

```python
validation = calculator.validate_data_integrity()

# Verifica:
# - Total de assinaturas vs com valores preenchidos
# - Distribuição por plataforma
# - Status das assinaturas
# - Gera alertas automáticos
```

### Alertas Implementados

- 🔴 **CRÍTICO**: Mais de 5% das assinaturas sem valores
- 🔴 **CRÍTICO**: Taxa de churn muito alta (>10%)
- 🟡 **ATENÇÃO**: Poucos dados para análise confiável
- 🟡 **ATENÇÃO**: LTV baixo

## Estrutura de Dados

### Tabela: `assinaturas`

**Colunas utilizadas para métricas**:
```sql
id                      -- PK
plataforma             -- 'guru' | 'ticto'
status                 -- Status da assinatura
data_inicio           -- Data de criação da assinatura
data_expiracao_acesso -- Data de expiração do acesso
ultima_atualizacao    -- Data da última modificação
valor_mensal          -- Valor mensal (apenas para planos mensais)
valor_anual           -- Valor anual (apenas para planos anuais)
cliente_id            -- ID do cliente
```

### Lógica de Valores por Tipo de Plano

**Implementação correta**:
- **Planos Mensais**: `valor_mensal` preenchido, `valor_anual = NULL`
- **Planos Anuais**: `valor_anual` preenchido, `valor_mensal = NULL`

**Identificação de Tipo**:
- Via `product_id` usando função `calcular_valores_assinatura_por_tipo()`
- IDs definidos em `src/utils/helpers.py`

## Casos de Uso Práticos

### 1. Relatório Mensal
```python
from datetime import datetime
from src.scripts.exemplo_uso_metricas import exemplo_relatorio_mensal

exemplo_relatorio_mensal()
```

### 2. Análise de Crescimento
```python
from src.scripts.exemplo_uso_metricas import exemplo_analise_crescimento

exemplo_analise_crescimento()
```

### 3. Análise CAC vs LTV
```python
from src.scripts.exemplo_uso_metricas import exemplo_analise_cac_ltv

exemplo_analise_cac_ltv()
```

### 4. Sistema de Alertas
```python
from src.scripts.exemplo_uso_metricas import exemplo_alertas_negocio

exemplo_alertas_negocio()
```

## Testes e Validação

### Executar Testes Completos
```bash
# Via Docker
docker-compose exec api python src/scripts/test_metrics_calculator.py

# Localmente
python src/scripts/test_metrics_calculator.py
```

### Executar Exemplos
```bash
# Via Docker
docker-compose exec api python src/scripts/exemplo_uso_metricas.py

# Localmente
python src/scripts/exemplo_uso_metricas.py
```

## Performance e Otimização

### Queries Otimizadas
- ✅ **CTEs** para queries complexas
- ✅ **Índices** nas colunas de data e status
- ✅ **Agregações** no banco de dados
- ✅ **Filtros** aplicados antes dos JOINs

### Caching (Futuro)
- Implementar cache Redis para métricas calculadas
- TTL de 15 minutos para métricas em tempo real
- Invalidação por eventos de webhook

## Troubleshooting

### Problemas Comuns

**1. ImportError: cannot import name 'get_db_session'**
```
Solução: Usar 'get_session' em vez de 'get_db_session'
from src.database.connection import get_session
```

**2. Column 'data_criacao' does not exist**
```
Solução: Usar nomes corretos das colunas:
- data_inicio (não data_criacao)
- ultima_atualizacao (não data_atualizacao)
```

**3. MRR retornando 0**
```
Verificar:
- Se há assinaturas com data_expiracao_acesso >= hoje
- Se valor_mensal ou valor_anual estão preenchidos
- Se status não é 'refunded' ou 'chargeback'
```

**4. Churn Rate muito alto**
```
Possíveis causas:
- Dados de teste/migração
- Período de análise inadequado
- Status incorretos na base
```

### Logs e Debugging

```python
import logging
logging.basicConfig(level=logging.INFO)

# Logs automáticos em todas as funções
calculator = MetricsCalculator(db_session)
# 2025-08-20 13:22:27,276 - src.services.metrics_calculator - INFO - MRR calculado com sucesso: R$ 16056.38
```

## Integração com Dashboard

### Estrutura para Componentes Dash

```python
# Exemplo de integração com Plotly Dash
import plotly.graph_objects as go
from dash import dcc, html

def create_mrr_card(metrics):
    return html.Div([
        html.H3("MRR"),
        html.H1(f"R$ {metrics['metricas_principais']['mrr']['valor']:,.2f}"),
        html.P("Monthly Recurring Revenue")
    ])

def create_churn_chart(metrics):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = metrics['metricas_principais']['churn_rate']['valor'],
        title = {'text': "Taxa de Churn (%)"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "red" if metrics['metricas_principais']['churn_rate']['valor'] > 10 else "green"},
            'steps': [
                {'range': [0, 5], 'color': "lightgreen"},
                {'range': [5, 10], 'color': "yellow"},
                {'range': [10, 100], 'color': "lightcoral"}
            ]
        }
    ))
    return dcc.Graph(figure=fig)
```

## Roadmap e Melhorias Futuras

### Versão Atual (v1.0)
- ✅ Métricas básicas (MRR, ARR, Churn, LTV, CAC)
- ✅ Validação de integridade
- ✅ Testes automatizados
- ✅ Exemplos de uso

### Próximas Versões

**v1.1 - Métricas Avançadas**
- Net MRR Growth
- Cohort Analysis
- Customer Segmentation
- Revenue Forecast

**v1.2 - Dashboard Visual**
- Interface Dash/Plotly
- Gráficos interativos
- Filtros temporais
- Export de relatórios

**v1.3 - Alertas e Automação**
- Alertas automáticos via email/Slack
- Relatórios agendados
- APIs REST
- Webhooks de métricas

**v1.4 - Analytics Avançado**
- Machine Learning para previsões
- Detecção de anomalias
- Análise de comportamento
- Otimização de retenção

## Conclusão

O sistema de métricas está **100% funcional e testado** com dados reais. A implementação segue as melhores práticas de:

- ✅ **Arquitetura modular**
- ✅ **Queries otimizadas**
- ✅ **Testes abrangentes**
- ✅ **Documentação completa**
- ✅ **Tratamento de erros**
- ✅ **Logging detalhado**

**Status**: Pronto para integração com dashboard visual e produção.

---

**Última atualização**: 20/08/2025  
**Versão**: 1.0  
**Autor**: Dashboard Comu Team
