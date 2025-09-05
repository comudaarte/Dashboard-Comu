# 🚀 Guia de Deploy para Produção - Dashboard Comu

## 📋 **PRÉ-REQUISITOS**

### **1. VPS/Servidor**
- **Sistema Operacional**: Ubuntu 20.04+ ou CentOS 8+
- **RAM**: Mínimo 2GB (Recomendado: 4GB+)
- **CPU**: Mínimo 2 cores
- **Disco**: Mínimo 20GB (Recomendado: 50GB+)
- **Docker**: Instalado e configurado
- **Docker Compose**: Instalado

### **2. Domínio**
- **Domínio**: `dashboard.comunidadedaarte.com`
- **DNS**: Configurado para apontar para o IP da VPS
- **SSL**: Certificado SSL (Let's Encrypt recomendado)

## 🔧 **CONFIGURAÇÃO INICIAL**

### **1. Conectar na VPS**
```bash
ssh root@SEU_IP_DA_VPS
```

### **2. Instalar Docker (se não estiver instalado)**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### **3. Criar diretório do projeto**
```bash
mkdir -p /opt/dashboard-comu
cd /opt/dashboard-comu
```

## 📁 **UPLOAD DOS ARQUIVOS**

### **1. Upload via SCP**
```bash
# Do seu computador local
scp -r . root@SEU_IP_DA_VPS:/opt/dashboard-comu/
```

### **2. Ou via Git**
```bash
# Na VPS
git clone https://github.com/SEU_USUARIO/dashboard-comu.git .
```

## ⚙️ **CONFIGURAÇÃO DE PRODUÇÃO**

### **1. Configurar arquivo .env**
```bash
# Copiar arquivo de produção
cp .env.production .env

# Editar configurações
nano .env
```

### **2. Configurações importantes no .env**
```bash
# Banco de dados
POSTGRES_PASSWORD=SUA_SENHA_SUPER_SEGURA_AQUI

# Segurança
SECRET_KEY=SUA_CHAVE_SECRETA_MUITO_LONGA_E_SEGURA_AQUI

# Domínio
ALLOWED_HOSTS=dashboard.comunidadedaarte.com,www.dashboard.comunidadedaarte.com

# Webhooks
GURU_ACCOUNT_TOKEN=seu_token_guru_real
TICTO_CLIENT_ID=seu_client_id_ticto_real
```

## 🚀 **EXECUTAR DEPLOY**

### **1. Executar script de deploy**
```bash
chmod +x deploy-production.sh
./deploy-production.sh
```

### **2. Ou manualmente**
```bash
# Parar containers existentes
docker-compose -f docker-compose.prod.yml down

# Construir imagens
docker-compose -f docker-compose.prod.yml build --no-cache

# Iniciar containers
docker-compose -f docker-compose.prod.yml up -d

# Verificar status
docker-compose -f docker-compose.prod.yml ps
```

## 🔒 **CONFIGURAÇÃO DE SSL**

### **1. Instalar Certbot**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

### **2. Obter certificado SSL**
```bash
sudo certbot --nginx -d dashboard.comunidadedaarte.com -d www.dashboard.comunidadedaarte.com
```

### **3. Configurar renovação automática**
```bash
sudo crontab -e
# Adicionar linha:
0 12 * * * /usr/bin/certbot renew --quiet
```

## 🌐 **CONFIGURAÇÃO DO NGINX**

### **1. Configurar Nginx**
```bash
sudo nano /etc/nginx/sites-available/dashboard-comu
```

### **2. Configuração do site**
```nginx
server {
    listen 80;
    server_name dashboard.comunidadedaarte.com www.dashboard.comunidadedaarte.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name dashboard.comunidadedaarte.com www.dashboard.comunidadedaarte.com;

    ssl_certificate /etc/letsencrypt/live/dashboard.comunidadedaarte.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dashboard.comunidadedaarte.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8052;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **3. Ativar site**
```bash
sudo ln -s /etc/nginx/sites-available/dashboard-comu /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📊 **MONITORAMENTO**

### **1. Verificar logs**
```bash
# Logs em tempo real
docker-compose -f docker-compose.prod.yml logs -f

# Logs específicos
docker-compose -f docker-compose.prod.yml logs api
docker-compose -f docker-compose.prod.yml logs db
```

### **2. Verificar status**
```bash
# Status dos containers
docker-compose -f docker-compose.prod.yml ps

# Uso de recursos
docker stats
```

### **3. Backup automático**
```bash
# Configurar cron para backup
crontab -e
# Adicionar linha:
0 2 * * * /opt/dashboard-comu/scripts/backup.sh
```

## 🔧 **MANUTENÇÃO**

### **1. Atualizar aplicação**
```bash
# Parar containers
docker-compose -f docker-compose.prod.yml down

# Atualizar código
git pull origin main

# Reconstruir e iniciar
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### **2. Backup do banco**
```bash
# Backup manual
docker-compose -f docker-compose.prod.yml exec db pg_dump -U metrics_user metrics_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### **3. Restaurar backup**
```bash
# Restaurar backup
docker-compose -f docker-compose.prod.yml exec -T db psql -U metrics_user metrics_db < backup_20250101_120000.sql
```

## 🚨 **SOLUÇÃO DE PROBLEMAS**

### **1. Container não inicia**
```bash
# Verificar logs
docker-compose -f docker-compose.prod.yml logs api

# Verificar configurações
docker-compose -f docker-compose.prod.yml config
```

### **2. Erro de conexão com banco**
```bash
# Verificar se o banco está rodando
docker-compose -f docker-compose.prod.yml ps db

# Verificar logs do banco
docker-compose -f docker-compose.prod.yml logs db
```

### **3. Erro de permissão**
```bash
# Corrigir permissões
sudo chown -R $USER:$USER /opt/dashboard-comu
chmod +x deploy-production.sh
```

## 📞 **SUPORTE**

### **Comandos úteis**
```bash
# Reiniciar todos os containers
docker-compose -f docker-compose.prod.yml restart

# Parar todos os containers
docker-compose -f docker-compose.prod.yml down

# Ver logs em tempo real
docker-compose -f docker-compose.prod.yml logs -f

# Acessar container
docker-compose -f docker-compose.prod.yml exec api bash
```

### **URLs importantes**
- **Dashboard**: https://dashboard.comunidadedaarte.com
- **API**: https://dashboard.comunidadedaarte.com/api
- **Health Check**: https://dashboard.comunidadedaarte.com/api/health

---

## ✅ **CHECKLIST DE DEPLOY**

- [ ] VPS configurada com Docker
- [ ] Domínio configurado no DNS
- [ ] Arquivo .env.production configurado
- [ ] SSL configurado
- [ ] Nginx configurado
- [ ] Containers rodando
- [ ] Dashboard acessível
- [ ] API funcionando
- [ ] Backup configurado
- [ ] Monitoramento ativo

**🎉 Parabéns! Seu Dashboard Comu está em produção!**
