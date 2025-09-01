# Arquitetura de Backfill Histórico

## Visão Geral

A arquitetura foi redesenhada para separar claramente o processamento de **webhooks em tempo real** do **backfill histórico**, mantendo a consistência dos dados e reutilizando funções comuns.

## Estrutura da Arquitetura

### 1. **Webhook Handler** (`src/services/webhook_handler.py`)
- **Propósito**: Processa webhooks em tempo real das plataformas Ticto e Guru
- **Responsabilidades**:
  - Validação de payloads de webhook
  - Roteamento baseado em status
  - Processamento de eventos especiais
  - Criação/atualização de clientes, assinaturas e transações
- **Características**:
  - Otimizado para processamento rápido
  - Lida com eventos em tempo real
  - Validações específicas para webhooks

### 2. **Historical Data Processor** (`src/services/data_processor.py`)
- **Propósito**: Processa dados históricos das APIs para backfill
- **Responsabilidades**:
  - Conversão de dados da API para formato interno
  - Processamento de orders e subscriptions históricas
  - Idempotência para evitar duplicatas
  - Logging detalhado para auditoria
- **Características**:
  - Otimizado para processamento em lote
  - Lida com grandes volumes de dados
  - Validações específicas para dados históricos

### 3. **Funções Compartilhadas**
Ambos os serviços reutilizam funções comuns do `webhook_handler.py`:
- `get_or_create_cliente()`: Criação/recuperação de clientes
- `get_or_create_assinatura()`: Criação/atualização de assinaturas
- `salvar_transacao()`: Salvamento de transações
- `converter_data()`: Conversão de datas
- `mapear_transacao_ticto()`: Mapeamento de dados Ticto

## Vantagens da Nova Arquitetura

### 1. **Separação de Responsabilidades**
- **Webhooks**: Focados em eventos em tempo real
- **Backfill**: Focados em dados históricos
- **Funções comuns**: Reutilizáveis entre ambos

### 2. **Manutenibilidade**
- Mudanças no processamento de webhooks não afetam o backfill
- Mudanças no backfill não afetam os webhooks
- Código mais organizado e fácil de entender

### 3. **Consistência de Dados**
- Ambos usam as mesmas funções de salvamento
- Mesma estrutura de dados no banco
- Mesmas validações de integridade

### 4. **Flexibilidade**
- Pode ter lógicas específicas para cada tipo de processamento
- Fácil adição de novas plataformas
- Fácil implementação de novos tipos de dados

## Fluxo de Dados

### Webhook em Tempo Real
```
Webhook Ticto/Guru → webhook_handler.py → Banco de Dados
```

### Backfill Histórico
```
API Ticto/Guru → data_processor.py → Banco de Dados
```

## Scripts de Backfill

### 1. **Teste** (`src/scripts/test_backfill_v2.py`)
- Processa apenas uma página de dados
- Usado para validação e testes
- Logs detalhados para debugging

### 2. **Produção** (`src/scripts/backfill_ticto.py`)
- Processa todas as páginas de dados
- Usado para backfill completo
- Logs de progresso e estatísticas

## Implementação Atual

### ✅ **Implementado**
- Estrutura básica do `HistoricalDataProcessor`
- Script de teste V2
- Reutilização de funções do `webhook_handler`
- Processamento de orders e subscriptions Ticto

### 🔄 **Em Desenvolvimento**
- Lógica de identificação de tipos de plano
- Cálculo de datas de expiração
- Processamento de assinaturas a partir de orders
- Implementação para Guru

### 📋 **Próximos Passos**
1. Completar a implementação do `HistoricalDataProcessor`
2. Implementar processamento para Guru
3. Adicionar filtros de data para backfill
4. Implementar retry logic para falhas de API
5. Adicionar validações específicas para dados históricos

## Exemplo de Uso

### Webhook (Tempo Real)
```python
from services.webhook_handler import processar_ticto

# Processa webhook em tempo real
result = processar_ticto(webhook_payload)
```

### Backfill (Histórico)
```python
from services.data_processor import HistoricalDataProcessor

# Processa dados históricos
processor = HistoricalDataProcessor()
result = processor.process_ticto_order(order_data)
```

## Benefícios para o Projeto

1. **Escalabilidade**: Pode processar grandes volumes de dados históricos sem afetar webhooks
2. **Confiabilidade**: Separação clara reduz riscos de bugs
3. **Performance**: Otimizações específicas para cada tipo de processamento
4. **Manutenção**: Código mais organizado e fácil de manter
5. **Testes**: Pode testar backfill independentemente dos webhooks 