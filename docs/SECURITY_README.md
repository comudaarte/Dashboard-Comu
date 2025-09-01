# Sistema de Segurança - Dashboard Comu

## 🛡️ Visão Geral

Este documento descreve o sistema de segurança implementado para os webhooks das plataformas **Guru** e **Ticto**. O sistema implementa autenticação por token, validação de payload, rate limiting e logs de segurança.

## 🔐 Componentes de Segurança

### 1. **Autenticação por Token**
- **Guru:** Valida `payload.api_token` contra `GURU_ACCOUNT_TOKEN`
- **Ticto:** Valida `token` (nível raiz) contra lista de tokens válidos
- **Formato:** Tokens únicos por plataforma/account

### 2. **Validação de Payload**
- **Estrutura JSON:** Validação de campos obrigatórios
- **Tipos de dados:** Verificação de tipos corretos
- **Campos obrigatórios:** Validação específica por plataforma

### 3. **Rate Limiting**
- **Limite por minuto:** Configurável via variáveis de ambiente
- **Limite por hora:** Proteção contra spam
- **Por IP:** Controle individual por endereço IP

### 4. **Logs de Segurança**
- **Eventos de autenticação:** Sucesso/falha de validação
- **Tentativas de acesso:** IPs e timestamps
- **Rate limiting:** Logs de excedentes
- **Erros de validação:** Detalhes de falhas

## ⚙️ Configuração

### **Variáveis de Ambiente (.env)**

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

### **Geração de SECRET_KEY**

```bash
# Gerar chave secreta segura
openssl rand -hex 32
```

### **Configuração de Tokens Ticto**

Para cada webhook criado na Ticto, adicione o token à variável `TICTO_WEBHOOK_TOKENS`:

```env
# Exemplo com 3 webhooks
TICTO_WEBHOOK_TOKENS=token_webhook1,token_webhook2,token_webhook3
```

## 🏗️ Arquitetura

### **Fluxo de Segurança**

```
Webhook Recebido → Middleware de Segurança → Validação → Processamento
       ↓
1. Rate Limiting Check
2. Parse JSON
3. Validação de Estrutura
4. Validação de Token
5. Log de Segurança
6. Processamento do Webhook
```

### **Estrutura de Arquivos**

```
src/utils/
├── security_config.py      # Configurações de segurança
├── security_middleware.py  # Middlewares de autenticação
└── ...

src/Api/
└── webhooks.py            # Endpoints com segurança integrada

src/scripts/
└── test_security.py       # Script de teste de segurança
```

## 🧪 Testes

### **Executar Testes de Segurança**

```bash
# 1. Iniciar a API
uvicorn src.Api.webhooks:app --reload

# 2. Em outro terminal, executar testes
python src/scripts/test_security.py
```

### **Testes Incluídos**

- ✅ **Configuração:** Verifica se todas as variáveis estão configuradas
- ✅ **Autenticação Guru:** Testa tokens válidos, inválidos e ausentes
- ✅ **Autenticação Ticto:** Testa múltiplos tokens válidos
- ✅ **Rate Limiting:** Verifica proteção contra spam
- ✅ **Endpoint de Saúde:** Valida informações de segurança

### **Exemplo de Teste Manual**

```bash
# Teste de webhook Guru válido
curl -X POST http://localhost:8000/webhook/guru \
  -H "Content-Type: application/json" \
  -d '{
    "webhook_type": "transaction",
    "payload": {
      "api_token": "SEU_TOKEN_GURU",
      "id": "test-123",
      "status": "approved"
    }
  }'

# Teste de webhook Ticto válido
curl -X POST http://localhost:8000/webhook/ticto \
  -H "Content-Type: application/json" \
  -d '{
    "token": "SEU_TOKEN_TICTO",
    "status": "authorized",
    "order": {
      "transaction_hash": "test-hash",
      "paid_amount": 1000
    }
  }'
```

## 📊 Monitoramento

### **Logs de Segurança**

O sistema gera logs estruturados para todos os eventos de segurança:

```json
{
  "timestamp": "2025-01-14 15:30:45",
  "event_type": "GURU_WEBHOOK_AUTHENTICATED",
  "client_ip": "192.168.1.100",
  "endpoint": "/webhook/guru",
  "method": "POST",
  "details": {
    "token_valid": true,
    "payload_type": "transaction"
  }
}
```

### **Tipos de Eventos**

- `GURU_WEBHOOK_AUTHENTICATED` - Webhook Guru autenticado com sucesso
- `TICTO_WEBHOOK_AUTHENTICATED` - Webhook Ticto autenticado com sucesso
- `INVALID_GURU_TOKEN` - Token Guru inválido
- `INVALID_TICTO_TOKEN` - Token Ticto inválido
- `RATE_LIMIT_EXCEEDED` - Rate limit excedido
- `INVALID_PAYLOAD_STRUCTURE` - Estrutura de payload inválida
- `MISSING_API_TOKEN` - Token Guru ausente
- `MISSING_TOKEN` - Token Ticto ausente

### **Endpoint de Saúde**

```bash
GET /health
```

Resposta:
```json
{
  "status": "ok",
  "security_configured": true,
  "guru_token_configured": true,
  "ticto_tokens_configured": true
}
```

## 🚀 Deploy para Produção

### **Checklist de Produção**

- [ ] **SECRET_KEY** configurada e segura
- [ ] **GURU_ACCOUNT_TOKEN** configurado
- [ ] **TICTO_WEBHOOK_TOKENS** configurados
- [ ] **Rate limiting** ajustado para produção
- [ ] **Logs** configurados para arquivo/centralizado
- [ ] **HTTPS** configurado
- [ ] **Firewall** configurado para portas necessárias

### **Configurações de Produção**

```env
# Ambiente de Produção
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# Rate Limiting mais restritivo
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_PER_HOUR=500

# Hosts permitidos
ALLOWED_HOSTS=dashboard.suaempresa.com.br,www.suaempresa.com.br
```

### **Monitoramento de Produção**

- **Logs de segurança** em arquivo separado
- **Alertas** para múltiplas falhas consecutivas
- **Métricas** de taxa de sucesso de autenticação
- **Monitoramento** de rate limiting

## 🔧 Troubleshooting

### **Problemas Comuns**

#### 1. **Token Guru Inválido**
```
❌ INVALID_GURU_TOKEN
```
**Solução:** Verificar se `GURU_ACCOUNT_TOKEN` está correto no `.env`

#### 2. **Token Ticto Inválido**
```
❌ INVALID_TICTO_TOKEN
```
**Solução:** Verificar se o token está na lista `TICTO_WEBHOOK_TOKENS`

#### 3. **Rate Limit Excedido**
```
❌ RATE_LIMIT_EXCEEDED
```
**Solução:** Ajustar `RATE_LIMIT_PER_MINUTE` ou implementar delay entre requisições

#### 4. **Payload Inválido**
```
❌ INVALID_PAYLOAD_STRUCTURE
```
**Solução:** Verificar estrutura do JSON enviado pela plataforma

### **Logs de Debug**

Para debug detalhado, ajuste o nível de log:

```env
LOG_LEVEL=DEBUG
```

### **Verificação de Configuração**

```bash
# Verificar se todas as configurações estão corretas
python -c "
from src.utils.security_config import security_config
print(f'Security configured: {security_config.is_configured()}')
print(f'Guru token: {bool(security_config.GURU_ACCOUNT_TOKEN)}')
print(f'Ticto tokens: {len(security_config.get_ticto_tokens())}')
print(f'Secret key: {bool(security_config.SECRET_KEY)}')
"
```

## 📚 Referências

### **Documentação das Plataformas**

- **Guru:** [Configuração de Webhook](https://docs.digitalmanager.guru/configuracoes-gerais/configuracao-de-webhook)
- **Ticto:** Interface de configuração de webhooks

### **Arquivos de Exemplo**

- **Guru:** `Jsons (exemplos)/Guru/`
- **Ticto:** `Jsons (exemplos)/Ticto/`

### **Código Fonte**

- **Configuração:** `src/utils/security_config.py`
- **Middlewares:** `src/utils/security_middleware.py`
- **Endpoints:** `src/Api/webhooks.py`
- **Testes:** `src/scripts/test_security.py`

## 🎯 Próximos Passos

### **Melhorias Futuras**

1. **Validação de IP:** Whitelist de IPs das plataformas
2. **Assinatura Digital:** Verificação de assinatura dos webhooks
3. **Auditoria Avançada:** Logs estruturados para análise
4. **Alertas Automáticos:** Notificações para eventos suspeitos
5. **Métricas de Segurança:** Dashboard de segurança

### **Integração com Monitoramento**

- **Sentry:** Rastreamento de erros
- **Prometheus:** Métricas de segurança
- **Grafana:** Dashboards de monitoramento
- **ELK Stack:** Análise de logs

---

**Sistema de Segurança implementado para a Semana 3 do projeto Dashboard Comu** 🚀
