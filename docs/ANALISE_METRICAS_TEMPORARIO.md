# Análise Detalhada de Métricas - Dashboard Comu

## 📊 Resumo Executivo

**Total de Métricas no Dashboard**: 25 métricas  
**Métricas Implementadas**: 5 (20%)  
**Métricas Faltando**: 20 (80%)  
**Status**: Dashboard funcional com dados sintéticos

---

## ✅ MÉTRICAS IMPLEMENTADAS (5)

### 1. MRR (Monthly Recurring Revenue)
- **Localização**: `src/services/metrics_calculator.py` - `calculate_mrr()`
- **Dashboard**: Exibida em múltiplas seções
- **Definição**: Receita recorrente mensal baseada em assinaturas ativas
- **Fórmula**: `SUM(valor_mensal) + SUM(valor_anual / 12)` para assinaturas ativas
- **Status**: ✅ **FUNCIONAL**
- **Dados**: Reais do banco de dados

### 2. ARR (Annual Recurring Revenue)
- **Localização**: `src/services/metrics_calculator.py` - `calculate_arr()`
- **Dashboard**: Exibida em múltiplas seções
- **Definição**: Receita anual recorrente projetada
- **Fórmula**: `MRR × 12`
- **Status**: ✅ **FUNCIONAL**
- **Dados**: Reais do banco de dados

### 3. Churn Rate
- **Localização**: `src/services/metrics_calculator.py` - `calculate_churn_rate()`
- **Dashboard**: Exibida no grid final
- **Definição**: Taxa de cancelamento (com correção para PIX expirados)
- **Fórmula**: `(Cancelamentos Reais / Assinaturas Ativas Início) × 100`
- **Status**: ✅ **FUNCIONAL** (com correção para PIX)
- **Dados**: Reais do banco de dados

### 4. LTV (Lifetime Value)
- **Localização**: `src/services/metrics_calculator.py` - `calculate_ltv()`
- **Dashboard**: Exibida na seção principal
- **Definição**: Valor médio que um cliente gera ao longo da vida útil
- **Fórmula**: `Ticket Médio Anual ÷ (Taxa de Churn Mensal ÷ 100)`
- **Status**: ✅ **FUNCIONAL**
- **Dados**: Reais do banco de dados

### 5. CAC (Customer Acquisition Cost)
- **Localização**: `src/services/metrics_calculator.py` - `calculate_cac()`
- **Dashboard**: Exibida na seção de performance
- **Definição**: Custo para adquirir um novo cliente
- **Fórmula**: `Custo Marketing ÷ Novos Clientes`
- **Status**: ✅ **FUNCIONAL**
- **Dados**: Reais do banco de dados

---

## ❌ MÉTRICAS FALTANDO IMPLEMENTAÇÃO (20)

### 📈 Métricas de Crescimento

#### 6. MRR - Growth (%)
- **Dashboard**: Grid final, primeira linha
- **Definição**: Percentual de crescimento do MRR
- **Fórmula**: `((MRR Atual - MRR Anterior) / MRR Anterior) × 100`
- **Prioridade**: 🔴 **ALTA**
- **Impacto**: Crítico para análise de crescimento

#### 7. Recorrência - MRA (Monthly Recurrence Average)
- **Dashboard**: Grid final, primeira linha
- **Definição**: Média de recorrência mensal dos clientes
- **Fórmula**: `Total de Assinaturas Ativas / Período em Meses`
- **Prioridade**: 🟡 **MÉDIA**
- **Impacto**: Importante para análise de retenção

### 💰 Métricas por Tipo de Plano

#### 8. MRR - (Plano Mensal)
- **Dashboard**: Grid final, segunda linha
- **Definição**: MRR apenas de planos mensais
- **Fórmula**: `SUM(valor_mensal)` para assinaturas ativas
- **Prioridade**: 🔴 **ALTA**
- **Impacto**: Análise segmentada por tipo de plano

#### 9. ARR - (Plano Mensal)
- **Dashboard**: Grid final, segunda linha
- **Definição**: ARR apenas de planos mensais
- **Fórmula**: `MRR Mensal × 12`
- **Prioridade**: 🔴 **ALTA**
- **Impacto**: Projeção anual por tipo de plano

#### 10. MRR - (Plano Anual)
- **Dashboard**: Grid final, terceira linha
- **Definição**: MRR apenas de planos anuais
- **Fórmula**: `SUM(valor_anual / 12)` para assinaturas ativas
- **Prioridade**: 🔴 **ALTA**
- **Impacto**: Análise segmentada por tipo de plano

#### 11. ARR - (Plano Anual)
- **Dashboard**: Grid final, terceira linha
- **Definição**: ARR apenas de planos anuais
- **Fórmula**: `MRR Anual × 12`
- **Prioridade**: 🔴 **ALTA**
- **Impacto**: Projeção anual por tipo de plano

### 👥 Métricas de Assinaturas

#### 12. Assinaturas Ativas
- **Dashboard**: Grid final, segunda linha (DESTACADA - Fundo roxo)
- **Definição**: Total de assinaturas com acesso vigente
- **Fórmula**: `COUNT(*) WHERE data_expiracao_acesso >= hoje`
- **Prioridade**: 🔴 **ALTA**
- **Impacto**: Métrica principal do dashboard

#### 13. Assinaturas Canceladas
- **Dashboard**: Grid final, segunda linha
- **Definição**: Total de assinaturas canceladas
- **Fórmula**: `COUNT(*) WHERE status IN ('canceled', 'subscription_canceled')`
- **Prioridade**: 🟡 **MÉDIA**
- **Impacto**: Análise de perdas

#### 14. Assinaturas esse mês
- **Dashboard**: Grid final, quarta linha
- **Definição**: Novas assinaturas no mês atual
- **Fórmula**: `COUNT(*) WHERE data_inicio >= inicio_mes_atual`
- **Prioridade**: 🟡 **MÉDIA**
- **Impacto**: Análise de aquisição

#### 15. Assinaturas do Mês Passado
- **Dashboard**: Grid final, quarta linha
- **Definição**: Novas assinaturas no mês anterior
- **Fórmula**: `COUNT(*) WHERE data_inicio BETWEEN inicio_mes_anterior AND fim_mes_anterior`
- **Prioridade**: 🟡 **MÉDIA**
- **Impacto**: Comparação temporal

### 📊 Métricas de Performance

#### 16. Retention Rate (%)
- **Dashboard**: Grid final, terceira linha
- **Definição**: Taxa de retenção de clientes
- **Fórmula**: `100 - Churn Rate`
- **Prioridade**: 🟡 **MÉDIA**
- **Impacto**: Complemento ao churn rate

#### 17. ARPU (Average Revenue Per User)
- **Dashboard**: Seção de performance, primeira linha
- **Definição**: Receita média por usuário
- **Fórmula**: `MRR Total / Total de Assinaturas Ativas`
- **Prioridade**: 🔴 **ALTA**
- **Impacto**: Análise de valor por cliente

#### 18. Receita média mensal
- **Dashboard**: Seção de performance, primeira linha
- **Definição**: Receita média mensal por assinatura
- **Fórmula**: `MRR Total / Total de Assinaturas Ativas`
- **Prioridade**: 🟡 **MÉDIA**
- **Impacto**: Análise de ticket médio

#### 19. Receita Anual da Empresa
- **Dashboard**: Seção de performance, segunda linha
- **Definição**: Receita total anual projetada
- **Fórmula**: `ARR Total`
- **Prioridade**: 🟡 **MÉDIA**
- **Impacto**: Visão anual consolidada

#### 20. ROI Geral
- **Dashboard**: Seção de performance, segunda linha
- **Definição**: Retorno sobre investimento
- **Fórmula**: `((Receita - Custo) / Custo) × 100`
- **Prioridade**: 🟡 **MÉDIA**
- **Impacto**: Análise de rentabilidade

#### 21. Margem de Lucro
- **Dashboard**: Seção de performance, segunda linha
- **Definição**: Margem de lucro percentual
- **Fórmula**: `((Receita - Custo) / Receita) × 100`
- **Prioridade**: 🟡 **MÉDIA**
- **Impacto**: Análise de lucratividade

#### 22. CPL (Cost Per Lead)
- **Dashboard**: Seção de performance, primeira linha
- **Definição**: Custo por lead gerado
- **Fórmula**: `Custo Marketing / Total de Leads`
- **Prioridade**: 🟢 **BAIXA**
- **Impacto**: Análise de marketing

#### 23. NPS (Net Promoter Score)
- **Dashboard**: Seção de performance, primeira linha
- **Definição**: Score de satisfação do cliente
- **Fórmula**: `% Promotores - % Detratores`
- **Prioridade**: 🟢 **BAIXA**
- **Impacto**: Análise de satisfação

### 💼 Métricas Principais

#### 24. Faturamento Total
- **Dashboard**: Seção principal, card principal
- **Definição**: Faturamento total consolidado
- **Fórmula**: `Soma de todas as vendas status "aprovado" em "transacoes"`
- **Prioridade**: 🔴 **ALTA**
- **Impacto**: Métrica principal do dashboard

#### 25. Quantidade de Vendas
- **Dashboard**: Seção principal, card secundário
- **Definição**: Total de vendas realizadas
- **Fórmula**: `COUNT(*) FROM transacoes WHERE status = 'approved'`
- **Prioridade**: 🔴 **ALTA**
- **Impacto**: Volume de transações

#### 26. Quantidade de Alunos
- **Dashboard**: Seção principal, card secundário
- **Definição**: Total de alunos únicos
- **Fórmula**: `COUNT(DISTINCT cliente_id) FROM assinaturas`
- **Prioridade**: 🔴 **ALTA**
- **Impacto**: Base de clientes

---

## 🎯 PLANO DE IMPLEMENTAÇÃO

### Fase 1: Métricas Básicas (Semana 1) - 🔴 ALTA PRIORIDADE
1. **Assinaturas Ativas** - Métrica destacada no dashboard
2. **Faturamento Total** - Card principal
3. **Quantidade de Vendas** - Card secundário
4. **Quantidade de Alunos** - Card secundário
5. **MRR Growth** - Análise de crescimento

### Fase 2: Métricas por Tipo (Semana 2) - 🔴 ALTA PRIORIDADE
1. **MRR - (Plano Mensal)**
2. **ARR - (Plano Mensal)**
3. **MRR - (Plano Anual)**
4. **ARR - (Plano Anual)**

### Fase 3: Métricas de Performance (Semana 3) - 🟡 MÉDIA PRIORIDADE
1. **ARPU** - Receita por usuário
2. **Retention Rate** - Taxa de retenção
3. **Assinaturas por mês** - Análise temporal
4. **Receita Anual da Empresa** - Visão consolidada

### Fase 4: Métricas Avançadas (Semana 4) - 🟢 BAIXA PRIORIDADE
1. **ROI Geral** - Retorno sobre investimento
2. **Margem de Lucro** - Lucratividade
3. **CPL** - Custo por lead
4. **NPS** - Satisfação do cliente

---

## 📊 IMPACTO NO DASHBOARD

### Atual (Dados Sintéticos)
- **Grid Final**: 14 métricas com valores fixos
- **Seção Principal**: 4 métricas com valores fixos
- **Seção Performance**: 8 métricas com valores fixos
- **Interatividade**: Limitada

### Futuro (Dados Reais)
- **Grid Final**: 14 métricas dinâmicas
- **Seção Principal**: 4 métricas dinâmicas
- **Seção Performance**: 8 métricas dinâmicas
- **Interatividade**: Completa com filtros funcionais

---

## 🔧 IMPLEMENTAÇÃO TÉCNICA

### Funções a Criar no MetricsCalculator
```python
# Métricas básicas
def calculate_active_subscriptions(self) -> int
def calculate_total_revenue(self) -> float
def calculate_total_sales(self) -> int
def calculate_unique_customers(self) -> int
def calculate_mrr_growth(self) -> float

# Métricas por tipo
def calculate_mrr_by_plan_type(self, tipo: str) -> float
def calculate_arr_by_plan_type(self, tipo: str) -> float

# Métricas de performance
def calculate_arpu(self) -> float
def calculate_retention_rate(self) -> float
def calculate_monthly_subscriptions(self, mes: int, ano: int) -> int
```

### Callbacks a Implementar
```python
# src/dashboard/callbacks/metrics_callbacks.py
def update_final_metrics_grid(data)
def update_main_metrics_section(data)
def update_performance_metrics_section(data)
```

---

## 📈 BENEFÍCIOS DA IMPLEMENTAÇÃO

### 1. Dados Reais
- Substituição de dados sintéticos
- Métricas atualizadas em tempo real
- Análise histórica precisa

### 2. Interatividade
- Filtros de data funcionais
- Comparações temporais
- Drill-down por plataforma

### 3. Tomada de Decisão
- Métricas confiáveis
- Alertas baseados em dados reais
- Relatórios automáticos

---

**Status**: Dashboard funcional com dados sintéticos  
**Próximo**: Implementação das métricas básicas (Fase 1)  
**Estimativa**: 4 semanas para implementação completa  
**Última atualização**: 28/08/2025
