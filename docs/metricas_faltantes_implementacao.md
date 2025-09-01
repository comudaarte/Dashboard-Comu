# Métricas Faltantes - Análise de Implementação

## Visão Geral

Este documento identifica as métricas que estão sendo exibidas no dashboard mas **NÃO estão implementadas** no `MetricsCalculator`. A análise compara as métricas visuais do dashboard com as funções disponíveis no backend.

## 📊 Métricas Implementadas vs Exibidas

### ✅ Métricas IMPLEMENTADAS no MetricsCalculator

**Localização**: `src/services/metrics_calculator.py`

#### 1. MRR (Monthly Recurring Revenue)
- **Função**: `calculate_mrr()`
- **Status**: ✅ Implementada
- **Dashboard**: ✅ Exibida em múltiplas seções

#### 2. ARR (Annual Recurring Revenue)
- **Função**: `calculate_arr()`
- **Status**: ✅ Implementada
- **Dashboard**: ✅ Exibida em múltiplas seções

#### 3. Churn Rate
- **Função**: `calculate_churn_rate()`
- **Status**: ✅ Implementada (com correção para PIX expirados)
- **Dashboard**: ✅ Exibida no grid final

#### 4. LTV (Lifetime Value)
- **Função**: `calculate_ltv()`
- **Status**: ✅ Implementada
- **Dashboard**: ✅ Exibida na seção principal

#### 5. CAC (Customer Acquisition Cost)
- **Função**: `calculate_cac()`
- **Status**: ✅ Implementada
- **Dashboard**: ✅ Exibida na seção de performance

### ❌ Métricas FALTANDO Implementação

#### 1. Recorrência - MRA (Monthly Recurrence Average)
- **Dashboard**: Exibida no grid final
- **Status**: ❌ **NÃO IMPLEMENTADA**
- **Definição**: Média de recorrência mensal dos clientes
- **Fórmula**: `MRA = Total de Assinaturas Ativas / Período em Meses`

#### 2. MRR - Growth (%)
- **Dashboard**: Exibida no grid final
- **Status**: ❌ **NÃO IMPLEMENTADA**
- **Definição**: Percentual de crescimento do MRR
- **Fórmula**: `Growth = ((MRR Atual - MRR Anterior) / MRR Anterior) × 100`

#### 3. MRR - (Plano Mensal)
- **Dashboard**: Exibida no grid final
- **Status**: ❌ **NÃO IMPLEMENTADA**
- **Definição**: MRR apenas de planos mensais
- **Fórmula**: `SUM(valor_mensal)` para assinaturas ativas

#### 4. ARR - (Plano Mensal)
- **Dashboard**: Exibida no grid final
- **Status**: ❌ **NÃO IMPLEMENTADA**
- **Definição**: ARR apenas de planos mensais
- **Fórmula**: `MRR Mensal × 12`

#### 5. MRR - (Plano Anual)
- **Dashboard**: Exibida no grid final
- **Status**: ❌ **NÃO IMPLEMENTADA**
- **Definição**: MRR apenas de planos anuais
- **Fórmula**: `SUM(valor_anual / 12)` para assinaturas ativas

#### 6. ARR - (Plano Anual)
- **Dashboard**: Exibida no grid final
- **Status**: ❌ **NÃO IMPLEMENTADA**
- **Definição**: ARR apenas de planos anuais
- **Fórmula**: `MRR Anual × 12`

#### 7. Retention Rate (%)
- **Dashboard**: Exibida no grid final
- **Status**: ❌ **NÃO IMPLEMENTADA**
- **Definição**: Taxa de retenção de clientes
- **Fórmula**: `100 - Churn Rate`

#### 8. Assinaturas Ativas
- **Dashboard**: Exibida no grid final (destacada)
- **Status**: ❌ **NÃO IMPLEMENTADA**
- **Definição**: Total de assinaturas com acesso vigente
- **Fórmula**: `COUNT(*) WHERE data_expiracao_acesso >= hoje`

#### 9. Assinaturas Canceladas
- **Dashboard**: Exibida no grid final
- **Status**: ❌ **NÃO IMPLEMENTADA**
- **Definição**: Total de assinaturas canceladas
- **Fórmula**: `COUNT(*) WHERE status IN ('canceled', 'subscription_canceled')`

#### 10. Assinaturas esse mês
- **Dashboard**: Exibida no grid final
- **Status**: ❌ **NÃO IMPLEMENTADA**
- **Definição**: Novas assinaturas no mês atual
- **Fórmula**: `COUNT(*) WHERE data_inicio >= inicio_mes_atual`

#### 11. Assinaturas do Mês Passado
- **Dashboard**: Exibida no grid final
- **Status**: ❌ **NÃO IMPLEMENTADA**
- **Definição**: Novas assinaturas no mês anterior
- **Fórmula**: `COUNT(*) WHERE data_inicio BETWEEN inicio_mes_anterior AND fim_mes_anterior`

#### 12. ARPU (Average Revenue Per User)
- **Dashboard**: Exibida na seção de performance
- **Status**: ❌ **NÃO IMPLEMENTADA**
- **Definição**: Receita média por usuário
- **Fórmula**: `MRR Total / Total de Assinaturas Ativas`

#### 13. CPL (Cost Per Lead)
- **Dashboard**: Exibida na seção de performance
- **Status**: ❌ **NÃO IMPLEMENTADA**
- **Definição**: Custo por lead gerado
- **Fórmula**: `Custo Marketing / Total de Leads`

#### 14. NPS (Net Promoter Score)
- **Dashboard**: Exibida na seção de performance
- **Status**: ❌ **NÃO IMPLEMENTADA**
- **Definição**: Score de satisfação do cliente
- **Fórmula**: `% Promotores - % Detratores`

#### 15. Receita média mensal
- **Dashboard**: Exibida na seção de performance
- **Status**: ❌ **NÃO IMPLEMENTADA**
- **Definição**: Receita média mensal por assinatura
- **Fórmula**: `MRR Total / Total de Assinaturas Ativas`

#### 16. Receita Anual da Empresa
- **Dashboard**: Exibida na seção de performance
- **Status**: ❌ **NÃO IMPLEMENTADA**
- **Definição**: Receita total anual projetada
- **Fórmula**: `ARR Total`

#### 17. ROI Geral
- **Dashboard**: Exibida na seção de performance
- **Status**: ❌ **NÃO IMPLEMENTADA**
- **Definição**: Retorno sobre investimento
- **Fórmula**: `((Receita - Custo) / Custo) × 100`

#### 18. Margem de Lucro
- **Dashboard**: Exibida na seção de performance
- **Status**: ❌ **NÃO IMPLEMENTADA**
- **Definição**: Margem de lucro percentual
- **Fórmula**: `((Receita - Custo) / Receita) × 100`

#### 19. Faturamento Total
- **Dashboard**: Exibida na seção principal
- **Status**: ❌ **NÃO IMPLEMENTADA**
- **Definição**: Faturamento total consolidado
- **Fórmula**: `MRR Total + Receitas Únicas`

#### 20. Quantidade de Vendas
- **Dashboard**: Exibida na seção principal
- **Status**: ❌ **NÃO IMPLEMENTADA**
- **Definição**: Total de vendas realizadas
- **Fórmula**: `COUNT(*) FROM transacoes WHERE status = 'approved'`

#### 21. Quantidade de Alunos
- **Dashboard**: Exibida na seção principal
- **Status**: ❌ **NÃO IMPLEMENTADA**
- **Definição**: Total de alunos únicos
- **Fórmula**: `COUNT(DISTINCT cliente_id) FROM assinaturas`

## 🔧 Implementação Necessária

### Prioridade ALTA (Métricas Críticas)

#### 1. Métricas de Contagem Básica
```python
def calculate_active_subscriptions(self, data_referencia: datetime = None) -> int:
    """Calcula total de assinaturas ativas"""
    
def calculate_canceled_subscriptions(self) -> int:
    """Calcula total de assinaturas canceladas"""
    
def calculate_monthly_subscriptions(self, mes: int = None, ano: int = None) -> int:
    """Calcula assinaturas de um mês específico"""
```

#### 2. Métricas de Crescimento
```python
def calculate_mrr_growth(self, periodo_dias: int = 30) -> float:
    """Calcula crescimento percentual do MRR"""
    
def calculate_mrr_by_plan_type(self, tipo_plano: str) -> Dict[str, Any]:
    """Calcula MRR por tipo de plano (mensal/anual)"""
```

#### 3. Métricas de Performance
```python
def calculate_arpu(self, data_referencia: datetime = None) -> float:
    """Calcula Average Revenue Per User"""
    
def calculate_retention_rate(self, periodo_dias: int = 30) -> float:
    """Calcula taxa de retenção"""
```

### Prioridade MÉDIA (Métricas de Negócio)

#### 4. Métricas Financeiras
```python
def calculate_total_revenue(self, data_referencia: datetime = None) -> float:
    """Calcula faturamento total"""
    
def calculate_profit_margin(self, custos: float = 0) -> float:
    """Calcula margem de lucro"""
    
def calculate_roi(self, custos: float = 0) -> float:
    """Calcula ROI"""
```

#### 5. Métricas de Cliente
```python
def calculate_unique_customers(self, data_referencia: datetime = None) -> int:
    """Calcula total de clientes únicos"""
    
def calculate_mra(self, periodo_meses: int = 12) -> float:
    """Calcula Monthly Recurrence Average"""
```

### Prioridade BAIXA (Métricas Avançadas)

#### 6. Métricas de Marketing
```python
def calculate_cpl(self, custo_marketing: float = 0) -> float:
    """Calcula Cost Per Lead"""
    
def calculate_nps(self) -> float:
    """Calcula Net Promoter Score (requer dados de pesquisa)"""
```

## 📋 Plano de Implementação

### Fase 1: Métricas Básicas (Semana 1)
- [ ] `calculate_active_subscriptions()`
- [ ] `calculate_canceled_subscriptions()`
- [ ] `calculate_monthly_subscriptions()`
- [ ] `calculate_unique_customers()`

### Fase 2: Métricas de Crescimento (Semana 2)
- [ ] `calculate_mrr_growth()`
- [ ] `calculate_mrr_by_plan_type()`
- [ ] `calculate_arr_by_plan_type()`
- [ ] `calculate_retention_rate()`

### Fase 3: Métricas de Performance (Semana 3)
- [ ] `calculate_arpu()`
- [ ] `calculate_total_revenue()`
- [ ] `calculate_mra()`
- [ ] `calculate_profit_margin()`

### Fase 4: Métricas Avançadas (Semana 4)
- [ ] `calculate_roi()`
- [ ] `calculate_cpl()`
- [ ] `calculate_nps()`
- [ ] Integração completa com dashboard

## 🧪 Testes Necessários

### Testes Unitários
```python
def test_calculate_active_subscriptions():
    """Testa cálculo de assinaturas ativas"""
    
def test_calculate_mrr_growth():
    """Testa cálculo de crescimento MRR"""
    
def test_calculate_arpu():
    """Testa cálculo de ARPU"""
```

### Testes de Integração
```python
def test_dashboard_metrics_integration():
    """Testa integração com dashboard"""
    
def test_metrics_consistency():
    """Testa consistência entre métricas relacionadas"""
```

## 📊 Impacto no Dashboard

### Métricas com Dados Sintéticos Atuais
- **Grid Final**: 14 métricas com dados fixos
- **Seção Principal**: 4 métricas com dados fixos
- **Seção Performance**: 8 métricas com dados fixos

### Métricas com Dados Reais (Após Implementação)
- **Grid Final**: 14 métricas com dados dinâmicos
- **Seção Principal**: 4 métricas com dados dinâmicos
- **Seção Performance**: 8 métricas com dados dinâmicos

## 🔄 Integração com Callbacks

### Callbacks a Implementar
```python
# src/dashboard/callbacks/metrics_callbacks.py

@app.callback(
    Output("final-metrics-grid", "children"),
    [Input("dashboard-data-store", "data")]
)
def update_final_metrics_grid(data):
    """Atualiza grid final com métricas reais"""
    
@app.callback(
    Output("main-metrics-section", "children"),
    [Input("dashboard-data-store", "data")]
)
def update_main_metrics_section(data):
    """Atualiza seção principal com métricas reais"""
```

## 📈 Benefícios da Implementação

### 1. Dados Reais
- Substituição de dados sintéticos por dados reais
- Métricas atualizadas em tempo real
- Análise histórica precisa

### 2. Interatividade
- Filtros de data funcionais
- Comparações temporais
- Drill-down por plataforma

### 3. Tomada de Decisão
- Métricas confiáveis para decisões
- Alertas baseados em dados reais
- Relatórios automáticos

## 🚀 Próximos Passos

1. **Implementar métricas básicas** (Fase 1)
2. **Criar testes unitários** para cada métrica
3. **Integrar com callbacks** do dashboard
4. **Validar dados** com stakeholders
5. **Documentar** novas funcionalidades

---

**Status**: 20 métricas faltando implementação  
**Prioridade**: ALTA para métricas básicas  
**Estimativa**: 4 semanas para implementação completa  
**Última atualização**: 28/08/2025
