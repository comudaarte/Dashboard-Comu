# Database connection 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Base para modelos SQLAlchemy
Base = declarative_base()

# Busca a URL do banco de dados das variáveis de ambiente ou usa o padrão do docker-compose
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://metrics_user:asdfghjkl@db:5432/metrics_db")

# Cria o engine do SQLAlchemy
engine = create_engine(DATABASE_URL)

# Cria a fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    """
    Retorna uma nova sessão do banco de dados.
    """
    return SessionLocal()


def get_db_session():
    """
    Retorna uma nova sessão do banco de dados (alias para get_session).
    """
    return SessionLocal()

def get_db():
    """
    Dependency para FastAPI que retorna uma sessão do banco de dados.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 