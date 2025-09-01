# Scripts de Backfill e Testes - Ticto e Guru

Este diretório contém os scripts para realizar o backfill histórico de dados das APIs Ticto e Guru, além de testes de validação.

## 📁 Estrutura dos Arquivos

```
src/scripts/
├── __init__.py                           # Módulo Python
├── backfill_utils.py                    # Utilitários comuns (logs, retry, validação)
├── ticto_api_client.py                  # Cliente da API Ticto
├── backfill_ticto.py                    # Script principal de backfill Ticto
├── test_backfill_5_dados.py             # Teste rápido com 5 dados Ticto
├── guru_api_client.py                   # Cliente da API Guru
├── backfill_guru.py                     # Script principal de backfill Guru
├── test_backfill_5_dados_guru.py        # Teste rápido com 5 dados Guru
├── test_guru_api.py                     # Teste de conectividade Guru
├── test_sync_validation_simple.py       # Teste de validação de sincronização
└── README.md                            # Esta documentação
```

## 🔧 Configuração

### 1. Variáveis de Ambiente

Adicione as credenciais no arquivo `.env`:

```env
# Ticto
TICTO_CLIENT_ID=seu_client_id_aqui
TICTO_CLIENT_SECRET=seu_client_secret_aqui

# Guru
GURU_USER_TOKEN=seu_user_token_aqui
GURU_ACCOUNT_TOKEN=seu_account_token_aqui
```

### 2. Dependências

Certifique-se de que todas as dependências estão instaladas:

```bash
pip install -r requirements.txt
```

## 🚀 Como Usar

### Ticto

#### 1. Teste Rápido (5 dados)

Execute um teste rápido com apenas 5 orders e 5 subscriptions:

```bash
docker-compose exec api python src/scripts/test_backfill_5_dados.py
```

#### 2. Teste de Validação de Sincronização

Testa se a validação de integridade entre webhooks e backfill está funcionando:

```bash
docker-compose exec api python src/scripts/test_sync_validation_simple.py
```

#### 3. Backfill Completo

Após validar os testes, execute o backfill completo:

```bash
docker-compose exec api python src/scripts/backfill_ticto.py
```

### Guru

#### 1. Teste Rápido (5 dados)

Execute um teste rápido com apenas 5 transactions e 5 subscriptions:

```bash
docker-compose exec api python src/scripts/test_backfill_5_dados_guru.py
```

Este teste:
- Busca 5 transações dos últimos 7 dias
- Busca 5 assinaturas
- Processa os dados e insere no banco
- Gera logs e backup dos dados

#### 2. Teste de Conectividade

Testa a conectividade com a API da Guru:

```bash
docker-compose exec api python src/scripts/test_guru_api.py
```

Este teste:
- Verifica autenticação com a API Guru
- Testa busca de transações e assinaturas
- Mostra exemplos dos dados retornados
- Oferece teste opcional de backfill

#### 3. Backfill Completo

Execute o backfill completo da Guru:

```bash
docker-compose exec api python src/scripts/backfill_guru.py
```

Ou com datas específicas:

```bash
docker-compose exec api python src/scripts/backfill_guru.py --start-date 2024-01-01 --end-date 2024-12-31
```

## 📊 Estrutura dos Dados

### Ticto

#### Orders (Transações)

Os dados de orders da API são convertidos para:

- **Tabela `transacoes`**: Dados da transação (valor, status, método pagamento, nome_oferta)
- **Tabela `clientes`**: Dados do cliente (nome, email, CPF)
- **Tabela `assinaturas`**: Se for uma assinatura (opcional)

#### Subscriptions (Assinaturas)

Os dados de subscriptions da API são convertidos para:

- **Tabela `assinaturas`**: Dados da assinatura (status, valores, datas, nome_oferta)
- **Tabela `clientes`**: Dados do cliente (nome, email, CPF)
- **Tabela `transacoes`**: Transações relacionadas (se houver)

### Guru

#### Transactions (Transações)

Os dados de transactions da API são convertidos para:

- **Tabela `transacoes`**: Dados da transação (valor, status, método pagamento, produto_nome)
- **Tabela `clientes`**: Dados do cliente (nome, email, documento)
- **Tabela `assinaturas`**: Se for uma assinatura (opcional)

#### Subscriptions (Assinaturas)

Os dados de subscriptions da API são convertidos para:

- **Tabela `assinaturas`**: Dados da assinatura (status, valores, datas, produto_nome)
- **Tabela `clientes`**: Dados do cliente (nome, email, documento)
- **Tabela `transacoes`**: Transações relacionadas (se houver)

## 🔄 Mapeamento de Status

### Ticto

| Status API | Status Banco | Descrição |
|------------|--------------|-----------|
| `approved` | `approved` | Venda aprovada |
| `refused` | `refused` | Venda recusada |
| `refunded` | `refunded` | Venda reembolsada |
| `waiting_payment` | `waiting_payment` | Aguardando pagamento |
| `abandoned_cart` | `abandoned_cart` | Carrinho abandonado |

### Guru

| Status API | Status Banco | Descrição |
|------------|--------------|-----------|
| `approved` | `approved` | Venda aprovada |
| `refused` | `refused` | Venda recusada |
| `refunded` | `refunded` | Venda reembolsada |
| `waiting_payment` | `waiting_payment` | Aguardando pagamento |
| `active` | `active` | Assinatura ativa |
| `canceled` | `canceled` | Assinatura cancelada |

## 📈 Logs e Backups

Todos os scripts geram:

- **Logs detalhados** em `logs/` com timestamp
- **Backups dos dados** em `backup_logs/` com timestamp
- **Estatísticas** de processamento no final

## ⚠️ Observações Importantes

### Ticto
- Usa autenticação OAuth2 com client credentials
- Busca dados históricos completos
- Processa orders e subscriptions separadamente

### Guru
- Usa autenticação Bearer Token
- Para transações, requer parâmetros obrigatórios de data (`confirmed_at_ini` e `confirmed_at_end`)
- Processa transactions e subscriptions separadamente
- Converte timestamps Unix para formato ISO

## 🐛 Troubleshooting

### Erro de Autenticação
- Verifique se as variáveis de ambiente estão corretas
- Confirme se os tokens são válidos
- Teste a conectividade primeiro

### Erro de Rate Limiting
- Os scripts incluem delays automáticos
- Se persistir, aumente o delay no código

### Erro de Dados
- Verifique os logs para detalhes
- Use os backups para análise
- Teste com períodos menores primeiro 