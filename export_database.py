#!/usr/bin/env python3
"""
Script para exportar todo o banco de dados em planilhas CSV
Exporta as tabelas: clientes, assinaturas e transacoes
"""

import os
import sys
import pandas as pd
from datetime import datetime
from sqlalchemy import text, create_engine
from sqlalchemy.exc import OperationalError
import logging

# Adiciona o diretório src ao path para importar os módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import get_session
from database.models import Cliente, Assinatura, Transacao

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_database_connection():
    """
    Testa diferentes configurações de conexão com o banco
    """
    logger.info("🔍 Testando conexões com o banco de dados...")
    
    # Lista de URLs de conexão para testar
    connection_urls = [
        # URL do .env
        os.getenv("DATABASE_URL", "postgresql://metrics_user:asdfghjkl@localhost:5432/metrics_db"),
        # URL para Docker
        "postgresql://metrics_user:asdfghjkl@db:5432/metrics_db",
        # URL alternativa local
        "postgresql://metrics_user:asdfghjkl@127.0.0.1:5432/metrics_db",
    ]
    
    for i, url in enumerate(connection_urls, 1):
        try:
            logger.info(f"   Teste {i}: {url.split('@')[1] if '@' in url else url}")
            engine = create_engine(url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"   ✅ Conexão {i} bem-sucedida!")
            return url
        except Exception as e:
            logger.info(f"   ❌ Conexão {i} falhou: {str(e)[:100]}...")
    
    logger.error("❌ Nenhuma conexão funcionou!")
    return None

def get_working_session():
    """
    Obtém uma sessão funcional do banco de dados
    """
    # Primeiro tenta a conexão padrão
    try:
        session = get_session()
        # Testa a conexão
        session.execute(text("SELECT 1"))
        logger.info("✅ Usando conexão padrão do projeto")
        return session
    except Exception as e:
        logger.warning(f"⚠️ Conexão padrão falhou: {str(e)[:100]}...")
        
        # Testa outras conexões
        working_url = test_database_connection()
        if working_url:
            try:
                engine = create_engine(working_url)
                from sqlalchemy.orm import sessionmaker
                SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
                session = SessionLocal()
                logger.info("✅ Usando conexão alternativa")
                return session
            except Exception as e:
                logger.error(f"❌ Erro ao criar sessão alternativa: {str(e)}")
        
        raise Exception("Não foi possível conectar ao banco de dados. Verifique se o PostgreSQL está rodando.")

def export_table_to_csv(session, model_class, output_dir, filename):
    """
    Exporta uma tabela específica para CSV
    
    Args:
        session: Sessão do banco de dados
        model_class: Classe do modelo SQLAlchemy
        output_dir: Diretório de saída
        filename: Nome do arquivo CSV
    """
    try:
        # Busca todos os dados da tabela
        query = session.query(model_class)
        df = pd.read_sql(query.statement, session.bind)
        
        # Cria o diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Caminho completo do arquivo
        filepath = os.path.join(output_dir, filename)
        
        # Exporta para CSV
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        logger.info(f"✅ Tabela {model_class.__tablename__} exportada: {filepath}")
        logger.info(f"   📊 Registros exportados: {len(df)}")
        
        return len(df)
        
    except Exception as e:
        logger.error(f"❌ Erro ao exportar {model_class.__tablename__}: {str(e)}")
        return 0

def export_database_complete():
    """
    Exporta todo o banco de dados em planilhas CSV
    """
    logger.info("🚀 Iniciando exportação completa do banco de dados...")
    
    # Cria diretório de saída com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"dados_exportados_completos_{timestamp}"
    
    # Configurações das tabelas para exportar
    tables_config = [
        {
            'model': Cliente,
            'filename': 'clientes.csv',
            'description': 'Tabela de clientes'
        },
        {
            'model': Assinatura,
            'filename': 'assinaturas.csv',
            'description': 'Tabela de assinaturas'
        },
        {
            'model': Transacao,
            'filename': 'transacoes.csv',
            'description': 'Tabela de transações'
        }
    ]
    
    total_records = 0
    session = None
    
    try:
        # Obtém sessão do banco
        session = get_working_session()
        logger.info("🔌 Conectado ao banco de dados")
        
        # Exporta cada tabela
        for table_config in tables_config:
            logger.info(f"📋 Exportando {table_config['description']}...")
            
            records_count = export_table_to_csv(
                session=session,
                model_class=table_config['model'],
                output_dir=output_dir,
                filename=table_config['filename']
            )
            
            total_records += records_count
        
        # Cria arquivo de resumo
        create_summary_file(output_dir, total_records, timestamp)
        
        logger.info(f"🎉 Exportação concluída com sucesso!")
        logger.info(f"📁 Arquivos salvos em: {output_dir}")
        logger.info(f"📊 Total de registros exportados: {total_records}")
        
    except Exception as e:
        logger.error(f"❌ Erro durante a exportação: {str(e)}")
        raise
        
    finally:
        if session:
            session.close()
            logger.info("🔌 Conexão com banco fechada")

def create_summary_file(output_dir, total_records, timestamp):
    """
    Cria um arquivo de resumo da exportação
    """
    try:
        summary_content = f"""# Resumo da Exportação do Banco de Dados

**Data/Hora da Exportação:** {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
**Timestamp:** {timestamp}
**Total de Registros Exportados:** {total_records:,}

## Tabelas Exportadas:

### 1. Clientes (clientes.csv)
- Informações básicas dos clientes
- Campos: id, nome, email, documento, data_criacao

### 2. Assinaturas (assinaturas.csv)
- Dados das assinaturas dos clientes
- Campos: id, id_assinatura_origem, plataforma, cliente_id, produto_nome, nome_oferta, status, data_inicio, data_proxima_cobranca, data_cancelamento, data_expiracao_acesso, valor_mensal, valor_anual, ultima_atualizacao

### 3. Transações (transacoes.csv)
- Histórico de transações financeiras
- Campos: id, id_transacao_origem, assinatura_id, cliente_id, plataforma, status, valor, valor_liquido, valor_bruto, taxa_reembolso, metodo_pagamento, data_transacao, motivo_recusa, json_completo, tipo_recusa, produto_nome, nome_oferta

## Observações:
- Todos os arquivos estão em formato CSV com encoding UTF-8
- O campo 'json_completo' da tabela transações contém dados adicionais em formato JSON
- Os relacionamentos entre tabelas são mantidos através dos campos de ID
"""
        
        summary_file = os.path.join(output_dir, "README_EXPORTACAO.md")
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
            
        logger.info(f"📝 Arquivo de resumo criado: {summary_file}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar arquivo de resumo: {str(e)}")

def check_docker_status():
    """
    Verifica se o Docker está rodando e sugere comandos
    """
    logger.info("🐳 Verificando status do Docker...")
    
    # Verifica se docker-compose.yml existe
    if os.path.exists("docker-compose.yml"):
        logger.info("📄 Arquivo docker-compose.yml encontrado")
        logger.info("💡 Para iniciar o banco via Docker, execute:")
        logger.info("   docker-compose up -d db")
        logger.info("   ou")
        logger.info("   docker-compose up -d")
    else:
        logger.info("📄 Arquivo docker-compose.yml não encontrado")

def main():
    """
    Função principal
    """
    try:
        export_database_complete()
        print("\n" + "="*60)
        print("✅ EXPORTAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERRO NA EXPORTAÇÃO: {str(e)}")
        print("\n" + "="*60)
        print("🔧 SOLUÇÕES POSSÍVEIS:")
        print("="*60)
        print("1. 🐳 Se usando Docker:")
        print("   docker-compose up -d db")
        print("   docker-compose up -d")
        print()
        print("2. 🖥️  Se PostgreSQL local:")
        print("   - Verifique se o PostgreSQL está rodando")
        print("   - Confirme usuário/senha no arquivo .env")
        print()
        print("3. 🔍 Para diagnóstico:")
        print("   python check_database.py")
        print()
        check_docker_status()
        sys.exit(1)

if __name__ == "__main__":
    main()
