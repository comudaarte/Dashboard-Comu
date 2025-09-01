#!/usr/bin/env python3
"""
Script para exportar dados das tabelas do banco para arquivos CSV
"""

import pandas as pd
from sqlalchemy import create_engine, text
import os

# Configuração do banco
DATABASE_URL = "postgresql://metrics_user:asdfghjkl@localhost:5432/metrics_db"

def exportar_tabela(engine, nome_tabela, nome_arquivo):
    """Exporta uma tabela para CSV"""
    try:
        # Consulta todos os dados da tabela
        query = f"SELECT * FROM {nome_tabela}"
        df = pd.read_sql(query, engine)
        
        # Salva como CSV
        df.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')
        
        print(f"✅ {nome_tabela}: {len(df)} registros exportados para {nome_arquivo}")
        print(f"   Colunas: {', '.join(df.columns.tolist())}")
        
        # Mostra primeiras linhas
        if len(df) > 0:
            print(f"   Primeiros registros:")
            print(df.head(3).to_string(index=False))
        else:
            print(f"   ⚠️  Tabela vazia")
        
        print("-" * 80)
        return df
        
    except Exception as e:
        print(f"❌ Erro ao exportar {nome_tabela}: {e}")
        return None

def main():
    print("🚀 Iniciando exportação dos dados do banco...")
    print("=" * 80)
    
    try:
        # Conecta ao banco
        engine = create_engine(DATABASE_URL)
        
        # Testa conexão
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            print(f"📊 Conectado ao PostgreSQL: {result.fetchone()[0]}")
        
        # Cria pasta para os arquivos se não existir
        os.makedirs("dados_exportados", exist_ok=True)
        
        # Lista de tabelas para exportar
        tabelas = [
            ("clientes", "dados_exportados/clientes.csv"),
            ("assinaturas", "dados_exportados/assinaturas.csv"),
            ("transacoes", "dados_exportados/transacoes.csv")
        ]
        
        # Exporta cada tabela
        for nome_tabela, nome_arquivo in tabelas:
            exportar_tabela(engine, nome_tabela, nome_arquivo)
        
        # Estatísticas gerais
        print("\n📈 ESTATÍSTICAS GERAIS:")
        print("=" * 80)
        
        with engine.connect() as conn:
            # Conta registros em cada tabela
            for nome_tabela, _ in tabelas:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {nome_tabela}"))
                count = result.fetchone()[0]
                print(f"   {nome_tabela}: {count} registros")
            
            # Algumas consultas úteis
            print("\n🔍 CONSULTAS ÚTEIS:")
            
            # Assinaturas por plataforma
            result = conn.execute(text("""
                SELECT plataforma, COUNT(*) as total, 
                       COUNT(CASE WHEN status = 'active' THEN 1 END) as ativas
                FROM assinaturas 
                GROUP BY plataforma
            """))
            print("   Assinaturas por plataforma:")
            for row in result:
                print(f"     {row[0]}: {row[1]} total, {row[2]} ativas")
            
            # Transações por status
            result = conn.execute(text("""
                SELECT status, COUNT(*) as total
                FROM transacoes 
                GROUP BY status
                ORDER BY total DESC
            """))
            print("   Transações por status:")
            for row in result:
                print(f"     {row[0]}: {row[1]} transações")
        
        print(f"\n✅ Exportação concluída! Arquivos salvos na pasta 'dados_exportados/'")
        print("   Você pode abrir os arquivos .csv no Excel, Google Sheets ou qualquer editor de planilhas.")
        
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        print("   Verifique se o banco está rodando: docker ps")

if __name__ == "__main__":
    main() 