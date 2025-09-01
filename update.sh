#!/bin/bash

# =============================================================================
# SCRIPT DE ATUALIZAÇÃO RÁPIDA - DASHBOARD COMU
# =============================================================================
# 
# Este script faz atualizações rápidas do código sem rebuild completo.
# Ideal para pequenas correções e ajustes.
#
# O que ele faz:
# 1. Puxa o código mais recente do GitHub
# 2. Reinicia apenas os containers necessários
# 3. Testa se está funcionando
# 4. Não reconstrói imagens (mais rápido)
#
# Como usar:
# ./update.sh
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

# =============================================================================
# CONFIGURAÇÕES
# =============================================================================

# ⚠️ IMPORTANTE: Altere estas variáveis para sua VPS
VPS_HOST="seu-servidor.com"
VPS_USER="root"
VPS_PORT="22"
PROJECT_DIR="/opt/dashboard-comu"

# =============================================================================
# VALIDAÇÕES
# =============================================================================

print_status "🔄 Iniciando atualização rápida..."
print_status "📅 Data: $(date)"
print_status "🖥️  VPS: $VPS_USER@$VPS_HOST:$VPS_PORT"

# Verificar se as configurações foram alteradas
if [ "$VPS_HOST" = "seu-servidor.com" ]; then
    print_error "❌ Configure as variáveis VPS_HOST, VPS_USER, etc. no início do script!"
    exit 1
fi

# =============================================================================
# ATUALIZAÇÃO DO CÓDIGO
# =============================================================================

print_status "📥 Atualizando código do GitHub..."

ssh -p $VPS_PORT $VPS_USER@$VPS_HOST "
    cd $PROJECT_DIR
    
    print_status '🔄 Puxando código mais recente...'
    git fetch origin
    git reset --hard origin/main
    
    if [ \$? -eq 0 ]; then
        echo '✅ Código atualizado com sucesso'
    else
        echo '❌ Erro ao atualizar código'
        exit 1
    fi
"

# =============================================================================
# REINICIALIZAÇÃO DOS CONTAINERS
# =============================================================================

print_status "🔄 Reiniciando containers..."

ssh -p $VPS_PORT $VPS_USER@$VPS_HOST "
    cd $PROJECT_DIR
    
    print_status '🔄 Reiniciando container da API...'
    docker-compose -f docker-compose.prod.yml restart api
    
    print_status '⏳ Aguardando API iniciar...'
    sleep 10
    
    print_status '🔍 Verificando status...'
    docker-compose -f docker-compose.prod.yml ps
"

# =============================================================================
# TESTES RÁPIDOS
# =============================================================================

print_status "🧪 Testando funcionamento..."

# Testar API
print_status "🔗 Testando API..."
ssh -p $VPS_PORT $VPS_USER@$VPS_HOST "
    cd $PROJECT_DIR
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

print_success "🎉 Atualização rápida concluída!"
print_status "📊 Dashboard: http://$VPS_HOST:8052"
print_status "🔗 API: http://$VPS_HOST:8000"
print_status "💚 Health Check: http://$VPS_HOST:8000/api/health"

print_status "📋 Próximos passos:"
print_status "   1. Teste o dashboard no navegador"
print_status "   2. Teste os webhooks"
print_status "   3. Verifique os logs se necessário"

print_success "✅ Sistema atualizado e funcionando!"
