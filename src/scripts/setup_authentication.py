"""
Script de setup inicial para o sistema de autenticação
"""
import os
import sys
import sys
sys.path.append('/app/src')
from sqlalchemy.orm import Session
from database.connection import get_db_session, engine, Base
from database.auth_models import User, UserRole
from services.auth_service import auth_service

def create_tables():
    """Cria todas as tabelas de autenticação"""
    print("🔧 Criando tabelas de autenticação...")
    
    try:
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def create_admin_user():
    """Cria usuário administrador inicial"""
    print("👤 Criando usuário administrador...")
    
    try:
        db = get_db_session()
        
        # Verificar se já existe admin
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if existing_admin:
            print("ℹ️  Usuário administrador já existe!")
            return True
        
        # Criar admin
        admin_user = auth_service.create_user(
            db=db,
            username="admin",
            email="admin@dashboard.comu",
            password="admin123",  # Senha padrão - deve ser alterada
            full_name="Administrador do Sistema",
            role=UserRole.ADMIN
        )
        
        print(f"✅ Usuário administrador criado!")
        print(f"   Username: admin")
        print(f"   Email: admin@dashboard.comu")
        print(f"   Senha: admin123")
        print(f"   ⚠️  ALTERE A SENHA APÓS O PRIMEIRO LOGIN!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário administrador: {e}")
        return False
    finally:
        db.close()

def create_test_users():
    """Cria usuários de teste"""
    print("🧪 Criando usuários de teste...")
    
    try:
        db = get_db_session()
        
        # Usuário viewer
        viewer_user = auth_service.create_user(
            db=db,
            username="viewer",
            email="viewer@dashboard.comu",
            password="viewer123",
            full_name="Usuário Visualizador",
            role=UserRole.VIEWER
        )
        
        # Usuário manager
        manager_user = auth_service.create_user(
            db=db,
            username="manager",
            email="manager@dashboard.comu",
            password="manager123",
            full_name="Usuário Gerente",
            role=UserRole.MANAGER
        )
        
        print("✅ Usuários de teste criados!")
        print("   Viewer: viewer / viewer123")
        print("   Manager: manager / manager123")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar usuários de teste: {e}")
        return False
    finally:
        db.close()

def main():
    """Função principal do setup"""
    print("🚀 Setup do Sistema de Autenticação - Dashboard Comu")
    print("=" * 60)
    
    # Verificar variáveis de ambiente
    if not os.getenv("SECRET_KEY"):
        print("⚠️  SECRET_KEY não definida. Usando valor padrão.")
        print("   Configure SECRET_KEY no arquivo .env para produção!")
    
    # Criar tabelas
    if not create_tables():
        print("❌ Falha ao criar tabelas. Abortando setup.")
        return False
    
    # Criar usuário admin
    if not create_admin_user():
        print("❌ Falha ao criar usuário administrador. Abortando setup.")
        return False
    
    # Criar usuários de teste (opcional)
    create_test = input("Deseja criar usuários de teste? (s/n): ").lower().strip()
    if create_test in ['s', 'sim', 'y', 'yes']:
        create_test_users()
    
    print("\n" + "=" * 60)
    print("✅ Setup de autenticação concluído com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Acesse o dashboard em http://localhost:8052")
    print("2. Faça login com: admin / admin123")
    print("3. ALTERE A SENHA DO ADMINISTRADOR!")
    print("4. Configure usuários adicionais conforme necessário")
    print("\n🔐 Credenciais padrão:")
    print("   Admin: admin / admin123")
    print("   Viewer: viewer / viewer123")
    print("   Manager: manager / manager123")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
