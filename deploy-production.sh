#!/bin/bash

# =============================================================================
# SCRIPT DE DEPLOY PARA PRODUÇÃO - DASHBOARD COMU
# =============================================================================
# 
# Este script automatiza o deploy do Dashboard Comu para produção.
# 
# Como usar:
# 1. Configure o arquivo .env.production
# 2. Execute: ./deploy-production.sh
#
# Autor: Dashboard Comu Team
# Data: 2025
# =============================================================================

set -e  # Parar em caso de erro

echo "🚀 Iniciando deploy do Dashboard Comu para produção..."
echo "============================================================"

# Verificar se o arquivo .env.production existe
if [ ! -f ".env.production" ]; then
    echo "❌ Erro: Arquivo .env.production não encontrado!"
    echo "📝 Crie o arquivo .env.production com as configurações de produção."
    exit 1
fi

# Verificar se o arquivo .env.production tem configurações padrão
if grep -q "SUA_SENHA_SUPER_SEGURA_AQUI" .env.production; then
    echo "⚠️  AVISO: Você ainda está usando senhas padrão no .env.production!"
    echo "🔒 Altere todas as senhas e tokens antes de continuar."
    read -p "Deseja continuar mesmo assim? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deploy cancelado. Configure o .env.production primeiro."
        exit 1
    fi
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose -f docker-compose.prod.yml down || true

# Remover imagens antigas (opcional)
echo "🧹 Limpando imagens antigas..."
docker system prune -f || true

# Construir novas imagens
echo "🏗️  Construindo imagens para produção..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Iniciar containers
echo "🚀 Iniciando containers de produção..."
docker-compose -f docker-compose.prod.yml up -d

# Aguardar containers iniciarem
echo "⏳ Aguardando containers iniciarem..."
sleep 30

# Verificar status dos containers
echo "🔍 Verificando status dos containers..."
docker-compose -f docker-compose.prod.yml ps

# Testar API
echo "🧪 Testando API..."
if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ API funcionando corretamente!"
else
    echo "❌ Erro: API não está respondendo!"
    echo "📋 Logs da API:"
    docker-compose -f docker-compose.prod.yml logs api --tail=20
    exit 1
fi

# Testar Dashboard
echo "📊 Testando Dashboard..."
if curl -f http://localhost:8052 > /dev/null 2>&1; then
    echo "✅ Dashboard funcionando corretamente!"
else
    echo "❌ Erro: Dashboard não está respondendo!"
    echo "📋 Logs do Dashboard:"
    docker-compose -f docker-compose.prod.yml logs api --tail=20
    exit 1
fi

# Verificar logs de erro
echo "📋 Verificando logs de erro..."
ERROR_COUNT=$(docker-compose -f docker-compose.prod.yml logs --tail=100 | grep -i error | wc -l)
if [ $ERROR_COUNT -gt 0 ]; then
    echo "⚠️  Encontrados $ERROR_COUNT erros nos logs:"
    docker-compose -f docker-compose.prod.yml logs --tail=100 | grep -i error
else
    echo "✅ Nenhum erro encontrado nos logs!"
fi

echo ""
echo "🎉 Deploy concluído com sucesso!"
echo "============================================================"
echo "📊 Dashboard: http://localhost:8052"
echo "🔗 API: http://localhost:8000"
echo "📋 Logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "🛑 Parar: docker-compose -f docker-compose.prod.yml down"
echo ""
echo "🔒 Lembre-se de:"
echo "   - Configurar SSL/HTTPS"
echo "   - Configurar domínio"
echo "   - Configurar backup automático"
echo "   - Monitorar logs regularmente"
echo "============================================================"
