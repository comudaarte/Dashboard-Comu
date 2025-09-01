"""
Script para verificar a estrutura da tabela assinaturas
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import get_session
from sqlalchemy import text

def check_table_structure():
    db = get_session()
    try:
        # Verifica colunas da tabela assinaturas
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'assinaturas' 
            ORDER BY ordinal_position
        """))
        
        print("Colunas da tabela 'assinaturas':")
        for row in result:
            print(f"  {row[0]} ({row[1]}) - nullable: {row[2]}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_table_structure()
