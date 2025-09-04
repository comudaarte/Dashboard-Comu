# 📊 Instruções para Exportação do Banco de Dados

## 🚀 Como Usar

### 1. Execução Simples (Windows)
```bash
# Duplo clique em:
exportar_banco.bat
```

### 2. Execução Manual
```bash
python export_database.py
```

### 3. Se o banco não estiver rodando
```bash
# Primeiro inicie o banco:
iniciar_banco.bat

# Depois exporte:
exportar_banco.bat
```

### 4. Execução com Docker (se estiver usando containers)
```bash
docker exec -it dashboard-comu-app-1 python export_database.py
```

## 📋 O que o Script Faz

1. **Conecta ao banco de dados** usando as configurações do projeto
2. **Exporta 3 tabelas principais:**
   - `clientes.csv` - Informações dos clientes
   - `assinaturas.csv` - Dados das assinaturas
   - `transacoes.csv` - Histórico de transações
3. **Cria um diretório organizado** com timestamp
4. **Gera um arquivo de resumo** (README_EXPORTACAO.md)

## 📁 Estrutura de Saída

```
dados_exportados_completos_YYYYMMDD_HHMMSS/
├── clientes.csv
├── assinaturas.csv
├── transacoes.csv
└── README_EXPORTACAO.md
```

## ⚠️ Pré-requisitos

- ✅ Python 3.8+
- ✅ Dependências instaladas (`pip install -r requirements.txt`)
- ✅ Banco de dados rodando
- ✅ Variáveis de ambiente configuradas

## 🔧 Configuração das Variáveis de Ambiente

Certifique-se de que o arquivo `.env` contém:

```env
DATABASE_URL=postgresql://usuario:senha@host:porta/nome_banco
```

## 📊 Campos Exportados

### Clientes
- id, nome, email, documento, data_criacao

### Assinaturas
- id, id_assinatura_origem, plataforma, cliente_id, produto_nome, nome_oferta, status, data_inicio, data_proxima_cobranca, data_cancelamento, data_expiracao_acesso, valor_mensal, valor_anual, ultima_atualizacao

### Transações
- id, id_transacao_origem, assinatura_id, cliente_id, plataforma, status, valor, valor_liquido, valor_bruto, taxa_reembolso, metodo_pagamento, data_transacao, motivo_recusa, json_completo, tipo_recusa, produto_nome, nome_oferta

## 🚨 Solução de Problemas

### ❌ Erro: `psycopg2.OperationalError` (Conexão recusada)
**Causa:** Banco de dados não está rodando

**Soluções:**
1. **Se usando Docker:**
   ```bash
   # Execute o iniciador:
   iniciar_banco.bat
   
   # Ou manualmente:
   docker-compose up -d db
   ```

2. **Se PostgreSQL local:**
   - Inicie o serviço PostgreSQL
   - Verifique se está na porta 5432
   - Confirme usuário/senha no `.env`

### ❌ Erro: `ModuleNotFoundError`
**Causa:** Dependências não instaladas

**Solução:**
```bash
pip install -r requirements.txt
```

### ❌ Erro: `Permission denied`
**Causa:** Sem permissão de escrita

**Solução:**
- Execute como administrador
- Verifique permissões da pasta

### ❌ Erro: `No such file or directory`
**Causa:** Executando no diretório errado

**Solução:**
```bash
cd "D:\Programas Python\Dashboard Comu"
```

### 🔍 Diagnóstico Avançado
```bash
# Verificar status do banco:
python check_database.py

# Verificar containers Docker:
docker-compose ps

# Verificar logs do banco:
docker-compose logs db
```

## 📈 Exemplo de Uso

```bash
# Navegue para o diretório do projeto
cd "D:\Programas Python\Dashboard Comu"

# Execute o script
python export_database.py

# Aguarde a conclusão
# Os arquivos estarão em: dados_exportados_completos_YYYYMMDD_HHMMSS/
```

## 🔍 Logs e Monitoramento

O script gera logs detalhados mostrando:
- ✅ Status de cada tabela exportada
- 📊 Número de registros por tabela
- 🔌 Status da conexão
- 📁 Localização dos arquivos gerados

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs de erro
2. Confirme a conectividade com o banco
3. Verifique as permissões de arquivo
4. Confirme que todas as dependências estão instaladas
