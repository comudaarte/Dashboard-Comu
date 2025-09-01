#!/usr/bin/env python3
"""
Script para gerar relatórios detalhados em Excel com múltiplas abas
"""

import pandas as pd
from sqlalchemy import create_engine, text
import os
from datetime import datetime

# Configuração do banco
DATABASE_URL = "postgresql://metrics_user:asdfghjkl@localhost:5432/metrics_db"

def gerar_relatorio_excel():
    """Gera relatório completo em Excel"""
    
    print("📊 Gerando relatório Excel detalhado...")
    
    try:
        # Conecta ao banco
        engine = create_engine(DATABASE_URL)
        
        # Cria pasta se não existir
        os.makedirs("relatorios", exist_ok=True)
        
        # Nome do arquivo com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorios/relatorio_dashboard_{timestamp}.xlsx"
        
        # Cria o writer do Excel
        with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
            
            # 1. ABA: Dados Brutos - Clientes
            print("   📋 Exportando dados de clientes...")
            df_clientes = pd.read_sql("SELECT * FROM clientes ORDER BY data_criacao DESC", engine)
            df_clientes.to_excel(writer, sheet_name='Clientes', index=False)
            
            # 2. ABA: Dados Brutos - Assinaturas
            print("   📋 Exportando dados de assinaturas...")
            df_assinaturas = pd.read_sql("SELECT * FROM assinaturas ORDER BY ultima_atualizacao DESC", engine)
            df_assinaturas.to_excel(writer, sheet_name='Assinaturas', index=False)
            
            # 3. ABA: Dados Brutos - Transações
            print("   📋 Exportando dados de transações...")
            df_transacoes = pd.read_sql("SELECT * FROM transacoes ORDER BY data_transacao DESC", engine)
            df_transacoes.to_excel(writer, sheet_name='Transações', index=False)
            
            # 4. ABA: Resumo Executivo
            print("   📋 Gerando resumo executivo...")
            resumo_data = []
            
            # Estatísticas gerais
            with engine.connect() as conn:
                # Total de clientes
                result = conn.execute(text("SELECT COUNT(*) FROM clientes"))
                total_clientes = result.fetchone()[0]
                resumo_data.append(["Total de Clientes", total_clientes])
                
                # Total de assinaturas
                result = conn.execute(text("SELECT COUNT(*) FROM assinaturas"))
                total_assinaturas = result.fetchone()[0]
                resumo_data.append(["Total de Assinaturas", total_assinaturas])
                
                # Assinaturas ativas
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM assinaturas 
                    WHERE data_expiracao_acesso >= CURRENT_DATE
                """))
                assinaturas_ativas = result.fetchone()[0]
                resumo_data.append(["Assinaturas Ativas", assinaturas_ativas])
                
                # Total de transações
                result = conn.execute(text("SELECT COUNT(*) FROM transacoes"))
                total_transacoes = result.fetchone()[0]
                resumo_data.append(["Total de Transações", total_transacoes])
                
                # MRR (Receita Recorrente Mensal)
                result = conn.execute(text("""
                    SELECT COALESCE(SUM(valor_mensal), 0) 
                    FROM assinaturas 
                    WHERE data_expiracao_acesso >= CURRENT_DATE
                """))
                mrr = result.fetchone()[0]
                resumo_data.append(["MRR (R$)", f"R$ {mrr:.2f}"])
                
                # ARR (Receita Anual Recorrente)
                arr = mrr * 12
                resumo_data.append(["ARR (R$)", f"R$ {arr:.2f}"])
                
                # Assinaturas por plataforma
                result = conn.execute(text("""
                    SELECT plataforma, COUNT(*) as total,
                           COUNT(CASE WHEN status = 'active' THEN 1 END) as ativas
                    FROM assinaturas 
                    GROUP BY plataforma
                """))
                for row in result:
                    resumo_data.append([f"Assinaturas {row[0].upper()}", f"{row[1]} total, {row[2]} ativas"])
                
                # Transações por status
                result = conn.execute(text("""
                    SELECT status, COUNT(*) as total
                    FROM transacoes 
                    GROUP BY status
                    ORDER BY total DESC
                """))
                for row in result:
                    resumo_data.append([f"Transações {row[0].upper()}", row[1]])
            
            df_resumo = pd.DataFrame(resumo_data, columns=["Métrica", "Valor"])
            df_resumo.to_excel(writer, sheet_name='Resumo Executivo', index=False)
            
            # 5. ABA: Análise por Plataforma
            print("   📋 Gerando análise por plataforma...")
            with engine.connect() as conn:
                # Assinaturas detalhadas por plataforma
                result = conn.execute(text("""
                    SELECT 
                        plataforma,
                        status,
                        COUNT(*) as quantidade,
                        AVG(valor_mensal) as valor_medio_mensal,
                        SUM(valor_mensal) as valor_total_mensal
                    FROM assinaturas 
                    GROUP BY plataforma, status
                    ORDER BY plataforma, status
                """))
                
                dados_plataforma = []
                for row in result:
                    dados_plataforma.append([
                        row[0], row[1], row[2], 
                        f"R$ {row[3]:.2f}" if row[3] else "R$ 0,00",
                        f"R$ {row[4]:.2f}" if row[4] else "R$ 0,00"
                    ])
                
                df_plataforma = pd.DataFrame(
                    dados_plataforma, 
                    columns=["Plataforma", "Status", "Quantidade", "Valor Médio Mensal", "Valor Total Mensal"]
                )
                df_plataforma.to_excel(writer, sheet_name='Análise por Plataforma', index=False)
            
            # 6. ABA: Últimas Transações
            print("   📋 Gerando últimas transações...")
            df_ultimas = pd.read_sql("""
                SELECT 
                    t.id_transacao_origem,
                    t.status,
                    t.valor,
                    t.metodo_pagamento,
                    t.data_transacao,
                    c.nome as cliente_nome,
                    c.email as cliente_email,
                    a.produto_nome,
                    a.plataforma
                FROM transacoes t
                JOIN clientes c ON t.cliente_id = c.id
                JOIN assinaturas a ON t.assinatura_id = a.id
                ORDER BY t.data_transacao DESC
                LIMIT 50
            """, engine)
            df_ultimas.to_excel(writer, sheet_name='Últimas Transações', index=False)
            
            # 7. ABA: Clientes com Assinaturas
            print("   📋 Gerando clientes com assinaturas...")
            df_clientes_assinaturas = pd.read_sql("""
                SELECT 
                    c.id,
                    c.nome,
                    c.email,
                    c.documento,
                    c.data_criacao,
                    a.id_assinatura_origem,
                    a.plataforma,
                    a.produto_nome,
                    a.status,
                    a.data_inicio,
                    a.data_expiracao_acesso,
                    a.valor_mensal,
                    a.ultima_atualizacao
                FROM clientes c
                LEFT JOIN assinaturas a ON c.id = a.cliente_id
                ORDER BY c.data_criacao DESC
            """, engine)
            df_clientes_assinaturas.to_excel(writer, sheet_name='Clientes e Assinaturas', index=False)
        
        print(f"✅ Relatório Excel gerado com sucesso: {nome_arquivo}")
        print(f"   📁 Localização: {os.path.abspath(nome_arquivo)}")
        print(f"   📊 Abas incluídas:")
        print(f"      - Resumo Executivo")
        print(f"      - Clientes")
        print(f"      - Assinaturas") 
        print(f"      - Transações")
        print(f"      - Análise por Plataforma")
        print(f"      - Últimas Transações")
        print(f"      - Clientes e Assinaturas")
        
        return nome_arquivo
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
        return None

if __name__ == "__main__":
    gerar_relatorio_excel() 