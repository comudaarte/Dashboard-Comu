# Calculador de Métricas - Guia Rápido

## Início Rápido

```python
from src.database.connection import get_session
from src.services.metrics_calculator import MetricsCalculator

# Inicializar
db_session = get_session()
calculator = MetricsCalculator(db_session)

# Obter todas as métricas para dashboard
metrics = calculator.get_dashboard_metrics()
print(f"MRR: R$ {metrics['metricas_principais']['mrr']['valor']:,.2f}")
```

## Métricas Disponíveis

| Métrica | Método | Retorno |
|---------|---------|---------|
| **MRR** | `calculate_mrr()` | Receita mensal recorrente |
| **ARR** | `calculate_arr()` | Receita anual recorrente |
| **Churn** | `calculate_churn_rate(30)` | Taxa de cancelamento |
| **LTV** | `calculate_ltv()` | Valor do cliente |
| **CAC** | `calculate_cac(30, custo)` | Custo de aquisição |
| **Todas** | `get_dashboard_metrics()` | Métricas consolidadas |

## Testes

```bash
# Executar testes completos
docker-compose exec api python src/scripts/test_metrics_calculator.py

# Executar exemplos práticos
docker-compose exec api python src/scripts/exemplo_uso_metricas.py
```

## Documentação Completa

📖 **Documentação detalhada**: `docs/documentacao_metricas.md`

## Status

✅ **100% Funcional** - Testado com dados reais  
✅ **Pronto para Dashboard** - APIs prontas para integração  
✅ **Documentação Completa** - Guias e exemplos disponíveis  

## Próximos Passos

1. ✅ Métricas implementadas e testadas
2. 🎯 **PRÓXIMO**: Dashboard visual (Dash/Plotly)
3. 🎯 **PRÓXIMO**: Interface de visualização
