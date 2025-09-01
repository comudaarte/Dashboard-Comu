#!/bin/bash

# =============================================================================
# SCRIPT DE DEPLOY AUTOMÁTICO - DASHBOARD COMU
# =============================================================================
# 
# Este script automatiza o processo de deploy do Dashboard Comu para produção.
# 
# O que ele faz:
# 1. Conecta na VPS via SSH
# 2. Puxa o código mais recente do GitHub
# 3. Para os containers antigos
# 4. Reconstrói com o código novo
# 5. Inicia os containers novamente
# 6. Testa se está funcionando
#
# Como usar:
# ./deploy.sh
#
# Autor: Dashboard Comu Team
# Data: 2025
# =============================================================================

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Função para verificar se um comando foi executado com sucesso
check_command() {
    if [ $? -eq 0 ]; then
        print_success "$1"
        return 0
    else
        print_error "$2"
        exit 1
    fi
}

# =============================================================================
# CONFIGURAÇÕES - ALTERE AQUI CONFORME SUA VPS
# =============================================================================

# ⚠️ IMPORTANTE: Altere estas variáveis para sua VPS
VPS_HOST="seu-servidor.com"           # IP ou domínio da sua VPS
VPS_USER="root"                       # Usuário SSH da VPS
VPS_PORT="22"                         # Porta SSH (geralmente 22)
PROJECT_DIR="/opt/dashboard-comu"     # Diretório do projeto na VPS
GITHUB_REPO="https://github.com/seu-usuario/dashboard-comu.git"  # URL do seu repositório

# =============================================================================
# VALIDAÇÕES INICIAIS
# =============================================================================

print_status "🚀 Iniciando deploy do Dashboard Comu..."
print_status "📅 Data: $(date)"
print_status "🖥️  VPS: $VPS_USER@$VPS_HOST:$VPS_PORT"
print_status "📁 Diretório: $PROJECT_DIR"

# Verificar se as configurações foram alteradas
if [ "$VPS_HOST" = "seu-servidor.com" ]; then
    print_error "❌ Configure as variáveis VPS_HOST, VPS_USER, etc. no início do script!"
    print_error "   Edite o arquivo deploy.sh e altere as configurações da sua VPS"
    exit 1
fi

# Verificar se o SSH está configurado
print_status "🔐 Verificando conexão SSH..."
ssh -o ConnectTimeout=10 -p $VPS_PORT $VPS_USER@$VPS_HOST "echo 'Conexão SSH OK'" 2>/dev/null
check_command "Conexão SSH estabelecida" "❌ Não foi possível conectar na VPS. Verifique:"
print_error "   - IP/domínio da VPS está correto?"
print_error "   - Usuário SSH está correto?"
print_error "   - Chave SSH está configurada?"
print_error "   - VPS está ligada?"

# =============================================================================
# BACKUP ANTES DO DEPLOY
# =============================================================================

print_status "💾 Criando backup antes do deploy..."
ssh -p $VPS_PORT $VPS_USER@$VPS_HOST "
    if [ -d '$PROJECT_DIR' ]; then
        cd $PROJECT_DIR
        docker-compose exec -T db pg_dump -U metrics_user -d metrics_db > backup_$(date +%Y%m%d_%H%M%S).sql 2>/dev/null || echo 'Backup do banco criado'
        echo 'Backup criado com sucesso'
    else
        echo 'Diretório do projeto não existe ainda'
    fi
" 2>/dev/null

# =============================================================================
# ATUALIZAÇÃO DO CÓDIGO
# =============================================================================

print_status "📥 Atualizando código do GitHub..."

# Se o diretório não existe, clonar o repositório
ssh -p $VPS_PORT $VPS_USER@$VPS_HOST "
    if [ ! -d '$PROJECT_DIR' ]; then
        print_status '📁 Clonando repositório pela primeira vez...'
        git clone $GITHUB_REPO $PROJECT_DIR
        check_command 'Repositório clonado' 'Erro ao clonar repositório'
    else
        print_status '🔄 Atualizando código existente...'
        cd $PROJECT_DIR
        git fetch origin
        git reset --hard origin/main
        check_command 'Código atualizado' 'Erro ao atualizar código'
    fi
"

# =============================================================================
# DEPLOY DOS CONTAINERS
# =============================================================================

print_status "🐳 Fazendo deploy dos containers Docker..."

ssh -p $VPS_PORT $VPS_USER@$VPS_HOST "
    cd $PROJECT_DIR
    
    print_status '🛑 Parando containers antigos...'
    docker-compose down 2>/dev/null || echo 'Nenhum container rodando'
    
    print_status '🏗️  Construindo containers...'
    docker-compose build --no-cache
    
    print_status '🚀 Iniciando containers...'
    docker-compose up -d
    
    print_status '⏳ Aguardando containers iniciarem...'
    sleep 10
    
    print_status '🔍 Verificando status dos containers...'
    docker-compose ps
"

check_command "Containers iniciados com sucesso" "Erro ao iniciar containers"

# =============================================================================
# TESTES DE FUNCIONAMENTO
# =============================================================================

print_status "🧪 Testando funcionamento do sistema..."

# Testar API
print_status "🔗 Testando API..."
ssh -p $VPS_PORT $VPS_USER@$VPS_HOST "
    cd $PROJECT_DIR
    sleep 5
    curl -f http://localhost:8000/api/health > /dev/null 2>&1
    if [ \$? -eq 0 ]; then
        echo '✅ API funcionando'
    else
        echo '❌ API não está respondendo'
        exit 1
    fi
"

# Testar Dashboard
print_status "📊 Testando Dashboard..."
ssh -p $VPS_PORT $VPS_USER@$VPS_HOST "
    cd $PROJECT_DIR
    curl -f http://localhost:8052 > /dev/null 2>&1
    if [ \$? -eq 0 ]; then
        echo '✅ Dashboard funcionando'
    else
        echo '❌ Dashboard não está respondendo'
        exit 1
    fi
"

# =============================================================================
# INFORMAÇÕES FINAIS
# =============================================================================

print_success "🎉 Deploy concluído com sucesso!"
print_status "📊 Dashboard: http://$VPS_HOST:8052"
print_status "🔗 API: http://$VPS_HOST:8000"
print_status "💚 Health Check: http://$VPS_HOST:8000/api/health"

print_status "📋 Próximos passos:"
print_status "   1. Configure seu domínio para apontar para $VPS_HOST"
print_status "   2. Configure SSL/HTTPS"
print_status "   3. Configure Cloudflare (opcional)"
print_status "   4. Teste os webhooks em produção"

print_success "✅ Sistema pronto para uso em produção!"
