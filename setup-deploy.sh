#!/bin/bash

# =============================================================================
# SCRIPT DE CONFIGURAÇÃO INICIAL - DASHBOARD COMU
# =============================================================================
# 
# Este script configura automaticamente o ambiente de deploy.
# 
# O que ele faz:
# 1. Verifica se o Git está configurado
# 2. Configura o repositório GitHub
# 3. Cria arquivos de configuração
# 4. Configura permissões
# 5. Testa a configuração
#
# Como usar:
# ./setup-deploy.sh
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
# CONFIGURAÇÃO INICIAL
# =============================================================================

print_status "🚀 Configurando ambiente de deploy do Dashboard Comu..."
print_status "📅 Data: $(date)"

# =============================================================================
# VERIFICAÇÕES INICIAIS
# =============================================================================

print_status "🔍 Verificando pré-requisitos..."

# Verificar se o Git está instalado
if ! command -v git &> /dev/null; then
    print_error "❌ Git não está instalado. Instale o Git primeiro."
    exit 1
fi

print_success "✅ Git está instalado"

# Verificar se estamos em um repositório Git
if [ ! -d ".git" ]; then
    print_status "📁 Inicializando repositório Git..."
    git init
    print_success "✅ Repositório Git inicializado"
else
    print_success "✅ Repositório Git já existe"
fi

# =============================================================================
# CONFIGURAÇÃO DO GIT
# =============================================================================

print_status "⚙️ Configurando Git..."

# Verificar se o usuário Git está configurado
if [ -z "$(git config user.name)" ]; then
    print_warning "⚠️ Nome do usuário Git não configurado"
    read -p "Digite seu nome: " GIT_NAME
    git config user.name "$GIT_NAME"
fi

if [ -z "$(git config user.email)" ]; then
    print_warning "⚠️ Email do usuário Git não configurado"
    read -p "Digite seu email: " GIT_EMAIL
    git config user.email "$GIT_EMAIL"
fi

print_success "✅ Git configurado"

# =============================================================================
# CONFIGURAÇÃO DO REPOSITÓRIO
# =============================================================================

print_status "📦 Configurando repositório..."

# Verificar se há um repositório remoto
if [ -z "$(git remote -v)" ]; then
    print_warning "⚠️ Nenhum repositório remoto configurado"
    read -p "Digite a URL do seu repositório GitHub: " GITHUB_URL
    
    if [ -n "$GITHUB_URL" ]; then
        git remote add origin "$GITHUB_URL"
        print_success "✅ Repositório remoto configurado"
    else
        print_warning "⚠️ Repositório remoto não configurado. Configure manualmente depois."
    fi
else
    print_success "✅ Repositório remoto já configurado"
fi

# =============================================================================
# CONFIGURAÇÃO DOS ARQUIVOS
# =============================================================================

print_status "📝 Configurando arquivos de deploy..."

# Copiar .gitignore.production para .gitignore se não existir
if [ ! -f ".gitignore" ]; then
    cp .gitignore.production .gitignore
    print_success "✅ .gitignore criado"
else
    print_success "✅ .gitignore já existe"
fi

# Criar diretório nginx/ssl se não existir
if [ ! -d "nginx/ssl" ]; then
    mkdir -p nginx/ssl
    print_success "✅ Diretório nginx/ssl criado"
fi

# =============================================================================
# CONFIGURAÇÃO DAS VARIÁVEIS
# =============================================================================

print_status "⚙️ Configurando variáveis de ambiente..."

# Verificar se .env.production existe
if [ -f ".env.production" ]; then
    print_warning "⚠️ Arquivo .env.production já existe"
    print_warning "   Lembre-se de alterar as senhas e tokens antes de usar!"
else
    print_success "✅ Arquivo .env.production criado"
fi

# =============================================================================
# CONFIGURAÇÃO DOS SCRIPTS
# =============================================================================

print_status "🔧 Configurando scripts..."

# Verificar se os scripts existem
if [ -f "deploy.sh" ]; then
    print_success "✅ Script deploy.sh encontrado"
else
    print_error "❌ Script deploy.sh não encontrado"
fi

if [ -f "update.sh" ]; then
    print_success "✅ Script update.sh encontrado"
else
    print_error "❌ Script update.sh não encontrado"
fi

if [ -f "scripts/backup.sh" ]; then
    print_success "✅ Script backup.sh encontrado"
else
    print_error "❌ Script backup.sh não encontrado"
fi

# =============================================================================
# CONFIGURAÇÃO DO GITHUB ACTIONS
# =============================================================================

print_status "🤖 Configurando GitHub Actions..."

if [ -f ".github/workflows/deploy.yml" ]; then
    print_success "✅ Workflow de deploy encontrado"
else
    print_error "❌ Workflow de deploy não encontrado"
fi

# =============================================================================
# TESTE DE CONFIGURAÇÃO
# =============================================================================

print_status "🧪 Testando configuração..."

# Verificar se o Docker está funcionando
if command -v docker &> /dev/null; then
    if docker --version &> /dev/null; then
        print_success "✅ Docker está funcionando"
    else
        print_warning "⚠️ Docker não está funcionando"
    fi
else
    print_warning "⚠️ Docker não está instalado"
fi

# Verificar se o Docker Compose está funcionando
if command -v docker-compose &> /dev/null; then
    if docker-compose --version &> /dev/null; then
        print_success "✅ Docker Compose está funcionando"
    else
        print_warning "⚠️ Docker Compose não está funcionando"
    fi
else
    print_warning "⚠️ Docker Compose não está instalado"
fi

# =============================================================================
# INFORMAÇÕES FINAIS
# =============================================================================

print_success "🎉 Configuração inicial concluída!"
print_status "📋 Próximos passos:"
print_status "   1. Configure as variáveis no arquivo .env.production"
print_status "   2. Configure as variáveis nos scripts deploy.sh e update.sh"
print_status "   3. Configure os secrets no GitHub (se usando GitHub Actions)"
print_status "   4. Teste o deploy localmente primeiro"
print_status "   5. Execute o deploy na VPS"

print_status "📚 Documentação:"
print_status "   - Leia o arquivo DEPLOY.md para instruções detalhadas"
print_status "   - Configure seu domínio e SSL"
print_status "   - Teste os webhooks em produção"

print_warning "⚠️ IMPORTANTE:"
print_warning "   - Altere TODAS as senhas e tokens antes de usar"
print_warning "   - Configure o firewall da VPS"
print_warning "   - Configure o domínio e SSL"
print_warning "   - Teste tudo em ambiente de desenvolvimento primeiro"

print_success "✅ Ambiente de deploy configurado com sucesso!"
