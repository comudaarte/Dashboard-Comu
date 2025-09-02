# 🚀 GUIA COMPLETO DE OPERAÇÃO - Dashboard Comu

## 🎯 Visão Geral da Operação

Este guia documenta todas as operações necessárias para manter o Dashboard Comu funcionando em produção, incluindo deploy, backup, monitoramento, troubleshooting e manutenção do sistema.

---

## 🚀 DEPLOY E PRODUÇÃO

### **Pré-requisitos para Produção**

#### **VPS (Servidor)**
- **Sistema**: Ubuntu 20.04+ ou CentOS 8+
- **RAM**: Mínimo 2GB (recomendado 4GB+)
- **CPU**: Mínimo 1 core (recomendado 2+ cores)
- **Disco**: Mínimo 20GB (recomendado 50GB+)
- **Rede**: IP público e portas 80/443 abertas

#### **Software Necessário**
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.30+
- **Nginx**: 1.18+ (opcional, pode usar container)

#### **Contas e Serviços**
- **GitHub**: Para repositório e CI/CD
- **Domínio**: Para acesso público
- **Certificado SSL**: Let's Encrypt ou comercial
- **Cloudflare**: (opcional) Para CDN e segurança

---

### **Configuração Inicial da VPS**

#### **1. Preparar a VPS**
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Instalar Git
sudo apt install git -y

# Reiniciar para aplicar mudanças
sudo reboot
```

#### **2. Configurar SSH**
```bash
# Gerar chave SSH (no seu PC)
ssh-keygen -t rsa -b 4096 -C "seu-email@exemplo.com"

# Copiar chave pública para VPS
ssh-copy-id -i ~/.ssh/id_rsa.pub root@SEU_IP_VPS

# Testar conexão
ssh root@SEU_IP_VPS
```

#### **3. Configurar Firewall**
```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Ou iptables (CentOS)
sudo firewall-cmd --permanent --add-port=22/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

---

### **Deploy Manual**

#### **1. Configurar Variáveis de Ambiente**
```bash
# Copiar arquivo de exemplo
cp .env.production .env

# Editar configurações
nano .env
```

**Altere as seguintes variáveis:**
```bash
# Banco de dados
POSTGRES_PASSWORD=SUA_SENHA_SUPER_SEGURA_AQUI_123!@#

# Domínio
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com,IP_DA_VPS

# Webhooks
GURU_ACCOUNT_TOKEN=seu_token_guru_aqui
TICTO_CLIENT_ID=seu_client_id_ticto_aqui
TICTO_CLIENT_SECRET=seu_client_secret_ticto_aqui

# URLs dos webhooks
GURU_WEBHOOK_URL=https://seu-dominio.com/api/webhook/guru
TICTO_WEBHOOK_URL=https://seu-dominio.com/api/webhook/ticto
```

#### **2. Executar Deploy**
```bash
# Tornar script executável
chmod +x deploy.sh

# Executar deploy
./deploy.sh
```

#### **3. Verificar Funcionamento**
```bash
# Verificar containers
docker-compose -f docker-compose.prod.yml ps

# Verificar logs
docker-compose -f docker-compose.prod.yml logs -f

# Testar API
curl http://localhost:8000/api/health

# Testar Dashboard
curl http://localhost:8052
```

---

### **Deploy Automático (GitHub Actions)**

#### **1. Configurar Repositório GitHub**
```bash
# Inicializar Git (se não existir)
git init

# Adicionar arquivos
git add .

# Primeiro commit
git commit -m "Initial commit"

# Adicionar repositório remoto
git remote add origin https://github.com/SEU_USUARIO/dashboard-comu.git

# Push inicial
git push -u origin main
```

#### **2. Configurar Secrets no GitHub**
Vá em **Settings > Secrets and variables > Actions** e adicione:
```
VPS_HOST=seu-servidor.com
VPS_USER=root
VPS_PORT=22
PROJECT_DIR=/opt/dashboard-comu
SSH_PRIVATE_KEY=conteudo_da_sua_chave_privada_ssh
```

#### **3. Configurar Deploy Automático**
O arquivo `.github/workflows/deploy.yml` já está configurado. Ele executará automaticamente quando você fizer push para a branch `main`.

---

### **Configuração de Domínio e SSL**

#### **1. Configurar DNS**
No seu provedor de domínio, configure:
```
A    @           IP_DA_VPS
A    www         IP_DA_VPS
A    api         IP_DA_VPS
```

#### **2. Instalar Certificado SSL**
```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obter certificado
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com

# Testar renovação automática
sudo certbot renew --dry-run
```

#### **3. Configurar Nginx**
```bash
# Copiar certificados para o projeto
sudo cp /etc/letsencrypt/live/seu-dominio.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/seu-dominio.com/privkey.pem nginx/ssl/key.pem

# Reiniciar containers
docker-compose -f docker-compose.prod.yml restart nginx
```

---

## 🔧 OPERAÇÃO E MANUTENÇÃO

### **Monitoramento e Logs**

#### **1. Verificar Logs**
```bash
# Logs da aplicação
docker-compose -f docker-compose.prod.yml logs -f api

# Logs do banco
docker-compose -f docker-compose.prod.yml logs -f db

# Logs do Nginx
docker-compose -f docker-compose.prod.yml logs -f nginx
```

#### **2. Monitorar Recursos**
```bash
# Uso de CPU e memória
docker stats

# Espaço em disco
df -h

# Uso de rede
netstat -tulpn
```

#### **3. Health Checks**
```bash
# API Health
curl https://seu-dominio.com/api/health

# Dashboard
curl https://seu-dominio.com/

# Nginx Health
curl https://seu-dominio.com/health
```

---

### **Backup e Recuperação**

#### **1. Backup Automático**
O sistema já está configurado para fazer backup automático diário às 2h da manhã.

```bash
# Executar backup manual
docker-compose -f docker-compose.prod.yml run --rm backup

# Verificar backups
ls -la backup_logs/
```

#### **2. Restaurar Backup**
```bash
# Parar aplicação
docker-compose -f docker-compose.prod.yml down

# Restaurar banco
docker-compose -f docker-compose.prod.yml up -d db
sleep 10
docker-compose -f docker-compose.prod.yml exec db psql -U metrics_user -d metrics_db -f /backup/backup_YYYYMMDD_HHMMSS.sql

# Reiniciar aplicação
docker-compose -f docker-compose.prod.yml up -d
```

---

### **Atualizações e Manutenção**

#### **1. Atualizar Código**
```bash
# Atualizar código
git pull origin main

# Reconstruir containers
docker-compose -f docker-compose.prod.yml build --no-cache

# Reiniciar
docker-compose -f docker-compose.prod.yml up -d
```

#### **2. Limpeza**
```bash
# Limpar logs antigos
find logs/ -name "*.log" -mtime +30 -delete

# Limpar backups antigos
find backup_logs/ -name "*.sql.gz" -mtime +30 -delete

# Limpar imagens Docker antigas
docker image prune -f
```

#### **3. Monitoramento**
```bash
# Verificar status
docker-compose -f docker-compose.prod.yml ps

# Verificar recursos
docker stats --no-stream

# Verificar logs de erro
docker-compose -f docker-compose.prod.yml logs --tail=100 | grep ERROR
```

---

## 🚨 TROUBLESHOOTING

### **Problemas Comuns**

#### **1. Container não inicia**
```bash
# Verificar logs
docker-compose -f docker-compose.prod.yml logs api

# Verificar configurações
docker-compose -f docker-compose.prod.yml config

# Reconstruir containers
docker-compose -f docker-compose.prod.yml build --no-cache
```

#### **2. Banco não conecta**
```bash
# Verificar se o banco está rodando
docker-compose -f docker-compose.prod.yml ps db

# Testar conexão
docker-compose -f docker-compose.prod.yml exec db psql -U metrics_user -d metrics_db -c "SELECT 1;"

# Verificar variáveis de ambiente
docker-compose -f docker-compose.prod.yml exec api env | grep DATABASE
```

#### **3. Nginx não funciona**
```bash
# Verificar configuração
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Verificar logs
docker-compose -f docker-compose.prod.yml logs nginx

# Testar conectividade
curl -I http://localhost
```

#### **4. Webhooks não chegam**
```bash
# Verificar logs da API
docker-compose -f docker-compose.prod.yml logs -f api

# Testar endpoint
curl -X POST https://seu-dominio.com/api/webhook/guru -H "Content-Type: application/json" -d '{"test": "data"}'

# Verificar firewall
sudo ufw status
```

---

### **Comandos Úteis**

```bash
# Reiniciar todos os containers
docker-compose -f docker-compose.prod.yml restart

# Parar tudo
docker-compose -f docker-compose.prod.yml down

# Limpar containers antigos
docker system prune -f

# Ver uso de recursos
docker stats --no-stream

# Backup manual
./scripts/backup.sh
```

---

## 📊 COMANDOS DE BANCO DE DADOS

### **Acessar Banco de Dados**
```bash
# Acessar PostgreSQL
docker-compose exec db psql -U metrics_user -d metrics_db

# Ou localmente
psql -h localhost -U metrics_user -d metrics_db
```

### **Consultas Úteis**
```sql
-- Ver estrutura das tabelas
SELECT * FROM clientes LIMIT 5;
SELECT * FROM assinaturas LIMIT 5;
SELECT * FROM transacoes LIMIT 5;

-- Ver estatísticas
SELECT COUNT(*) as total_clientes FROM clientes;
SELECT COUNT(*) as total_assinaturas FROM assinaturas;
SELECT COUNT(*) as total_transacoes FROM transacoes;

-- Ver assinaturas ativas
SELECT COUNT(*) as assinaturas_ativas 
FROM assinaturas 
WHERE data_expiracao_acesso >= NOW();

-- Ver transações por status
SELECT status, COUNT(*) as total 
FROM transacoes 
GROUP BY status 
ORDER BY total DESC;
```

### **Manutenção do Banco**
```sql
-- Excluir todos os dados de uma tabela
DELETE FROM transacoes;
DELETE FROM assinaturas;
DELETE FROM clientes;

-- Resetar contadores de ID
TRUNCATE TABLE transacoes RESTART IDENTITY CASCADE;
TRUNCATE TABLE assinaturas RESTART IDENTITY CASCADE;
TRUNCATE TABLE clientes RESTART IDENTITY CASCADE;

-- Excluir dados de um cliente específico
DELETE FROM transacoes WHERE cliente_id = (SELECT id FROM clientes WHERE email = 'email@cliente.com');
DELETE FROM assinaturas WHERE cliente_id = (SELECT id FROM clientes WHERE email = 'email@cliente.com');
DELETE FROM clientes WHERE email = 'email@cliente.com';
```

---

## 🔄 MIGRAÇÕES E SCHEMA

### **Executar Migrações**
```bash
# Acessar container da API
docker-compose exec api bash

# Navegar para src
cd src

# Executar migrações
alembic upgrade head

# Ver status das migrações
alembic current

# Ver histórico de migrações
alembic history
```

### **Criar Nova Migração**
```bash
# Acessar container da API
docker-compose exec api bash

# Navegar para src
cd src

# Criar nova migração
alembic revision --autogenerate -m "Descrição da mudança"

# Aplicar migração
alembic upgrade head
```

---

## 📈 MONITORAMENTO AVANÇADO

### **Métricas de Sistema**
```bash
# Monitorar uso de recursos em tempo real
docker stats

# Ver logs de erro
docker-compose logs --tail=100 | grep ERROR

# Verificar espaço em disco
df -h

# Verificar uso de memória
free -h

# Verificar processos
ps aux | grep python
```

### **Alertas e Notificações**
```bash
# Verificar se serviços estão rodando
docker-compose ps

# Verificar health checks
curl -f http://localhost:8000/api/health || echo "API down"
curl -f http://localhost:8052 || echo "Dashboard down"

# Verificar conectividade do banco
docker-compose exec db pg_isready -U metrics_user -d metrics_db
```

---

## 🔮 PRÓXIMOS PASSOS DE OPERAÇÃO

### **Melhorias de Produção**
1. **Monitoramento**: Prometheus + Grafana para métricas de sistema
2. **Logs**: ELK Stack para centralização e análise de logs
3. **Alertas**: Sistema de notificações para problemas críticos
4. **Backup**: Backup automático para cloud (AWS S3, Google Cloud Storage)
5. **CI/CD**: Pipeline completo com testes automatizados

### **Escalabilidade**
1. **Load Balancer**: Distribuição de carga entre múltiplas instâncias
2. **Cache**: Redis para métricas frequentemente acessadas
3. **CDN**: Cloudflare para arquivos estáticos
4. **Microserviços**: Separação de responsabilidades

---

## 📚 DOCUMENTAÇÃO RELACIONADA

- **`README.md`** - Visão geral e status do projeto
- **`GUIA_IMPLEMENTACAO.md`** - Implementação das métricas
- **`GUIA_TECNICO.md`** - Arquitetura e APIs

---

## 🆘 SUPORTE E CONTATO

### **Em Caso de Problemas**
1. **Verifique os logs** primeiro
2. **Consulte este documento** para soluções comuns
3. **Teste localmente** antes de fazer mudanças
4. **Faça backup** antes de operações críticas

### **Canais de Suporte**
- **GitHub Issues**: Para bugs e problemas técnicos
- **Documentação**: Este guia e arquivos relacionados
- **Logs**: Sistema de logging estruturado
- **Monitoramento**: Health checks e métricas de sistema

---

**🚀 OPERAÇÃO COMPLETA - SISTEMA ESTÁVEL E MONITORADO!**

**Status**: ✅ **OPERACIONAL**  
**Última atualização**: 28/08/2025  
**Autor**: Dashboard Comu Team
