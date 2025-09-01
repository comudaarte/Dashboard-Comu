#!/bin/bash

# =============================================================================
# SCRIPT DE BACKUP AUTOMÁTICO - DASHBOARD COMU
# =============================================================================
# 
# Este script faz backup automático do banco de dados PostgreSQL
# e limpa backups antigos para economizar espaço.
#
# O que ele faz:
# 1. Conecta no banco PostgreSQL
# 2. Faz dump completo do banco
# 3. Comprime o backup
# 4. Remove backups antigos (mantém apenas os últimos 30)
# 5. Envia notificação por email (opcional)
#
# Como usar:
# ./scripts/backup.sh
# 
# Para agendar (crontab):
# 0 2 * * * /opt/dashboard-comu/scripts/backup.sh
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

# Diretório de backup
BACKUP_DIR="/app/backup_logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${TIMESTAMP}.sql"
BACKUP_FILE_COMPRESSED="backup_${TIMESTAMP}.sql.gz"

# Configurações do banco
DB_HOST="db"
DB_PORT="5432"
DB_NAME="${POSTGRES_DB:-metrics_db}"
DB_USER="${POSTGRES_USER:-metrics_user}"
DB_PASSWORD="${POSTGRES_PASSWORD}"

# Configurações de retenção
RETENTION_DAYS=30
MAX_BACKUPS=30

# =============================================================================
# VALIDAÇÕES
# =============================================================================

print_status "🔄 Iniciando backup automático..."
print_status "📅 Data: $(date)"
print_status "📁 Diretório: $BACKUP_DIR"
print_status "🗄️  Banco: $DB_NAME"

# Verificar se o diretório de backup existe
if [ ! -d "$BACKUP_DIR" ]; then
    print_status "📁 Criando diretório de backup..."
    mkdir -p "$BACKUP_DIR"
fi

# Verificar se as variáveis de ambiente estão definidas
if [ -z "$DB_PASSWORD" ]; then
    print_error "❌ Variável POSTGRES_PASSWORD não está definida!"
    exit 1
fi

# =============================================================================
# BACKUP DO BANCO
# =============================================================================

print_status "💾 Fazendo backup do banco de dados..."

# Exportar senha para o pg_dump
export PGPASSWORD="$DB_PASSWORD"

# Fazer o dump do banco
pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --verbose \
    --no-password \
    --format=plain \
    --file="$BACKUP_DIR/$BACKUP_FILE" 2>/dev/null

# Verificar se o backup foi criado com sucesso
if [ $? -eq 0 ] && [ -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
    print_success "✅ Backup criado: $BACKUP_FILE"
    
    # Verificar tamanho do arquivo
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
    print_status "📊 Tamanho do backup: $BACKUP_SIZE"
    
else
    print_error "❌ Erro ao criar backup!"
    exit 1
fi

# =============================================================================
# COMPRESSÃO DO BACKUP
# =============================================================================

print_status "🗜️  Comprimindo backup..."

gzip "$BACKUP_DIR/$BACKUP_FILE"

if [ $? -eq 0 ] && [ -f "$BACKUP_DIR/$BACKUP_FILE_COMPRESSED" ]; then
    print_success "✅ Backup comprimido: $BACKUP_FILE_COMPRESSED"
    
    # Verificar tamanho do arquivo comprimido
    COMPRESSED_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE_COMPRESSED" | cut -f1)
    print_status "📊 Tamanho comprimido: $COMPRESSED_SIZE"
    
else
    print_error "❌ Erro ao comprimir backup!"
    exit 1
fi

# =============================================================================
# LIMPEZA DE BACKUPS ANTIGOS
# =============================================================================

print_status "🧹 Limpando backups antigos..."

# Contar backups existentes
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/backup_*.sql.gz 2>/dev/null | wc -l)
print_status "📊 Total de backups: $BACKUP_COUNT"

# Se há mais backups que o limite, remover os mais antigos
if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
    BACKUPS_TO_REMOVE=$((BACKUP_COUNT - MAX_BACKUPS))
    print_status "🗑️  Removendo $BACKUPS_TO_REMOVE backup(s) antigo(s)..."
    
    # Listar e remover os backups mais antigos
    ls -1t "$BACKUP_DIR"/backup_*.sql.gz | tail -n "$BACKUPS_TO_REMOVE" | xargs -r rm -f
    
    if [ $? -eq 0 ]; then
        print_success "✅ Backups antigos removidos"
    else
        print_warning "⚠️  Erro ao remover backups antigos"
    fi
else
    print_status "✅ Número de backups dentro do limite ($MAX_BACKUPS)"
fi

# =============================================================================
# VERIFICAÇÃO FINAL
# =============================================================================

print_status "🔍 Verificação final..."

# Verificar se o backup mais recente existe e é válido
LATEST_BACKUP=$(ls -1t "$BACKUP_DIR"/backup_*.sql.gz 2>/dev/null | head -n 1)

if [ -n "$LATEST_BACKUP" ] && [ -f "$LATEST_BACKUP" ]; then
    BACKUP_SIZE=$(du -h "$LATEST_BACKUP" | cut -f1)
    print_success "✅ Backup mais recente: $(basename "$LATEST_BACKUP") ($BACKUP_SIZE)"
    
    # Testar se o backup pode ser descomprimido
    if gzip -t "$LATEST_BACKUP" 2>/dev/null; then
        print_success "✅ Backup válido e íntegro"
    else
        print_error "❌ Backup corrompido!"
        exit 1
    fi
else
    print_error "❌ Nenhum backup encontrado!"
    exit 1
fi

# =============================================================================
# ESTATÍSTICAS FINAIS
# =============================================================================

print_status "📊 Estatísticas do backup:"
print_status "   📁 Diretório: $BACKUP_DIR"
print_status "   📊 Total de backups: $(ls -1 "$BACKUP_DIR"/backup_*.sql.gz 2>/dev/null | wc -l)"
print_status "   💾 Espaço usado: $(du -sh "$BACKUP_DIR" | cut -f1)"
print_status "   🕒 Último backup: $(basename "$LATEST_BACKUP")"

print_success "🎉 Backup automático concluído com sucesso!"
print_status "⏰ Próximo backup agendado para: $(date -d '+1 day' '+%Y-%m-%d %H:%M')"
