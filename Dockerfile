FROM python:3.10

# Diretório de trabalho
WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código-fonte e as migrações
COPY src/ ./src/
COPY src/database/migrations/ ./database/migrations/
COPY src/alembic.ini ./src/

# Variáveis de ambiente padrão
ENV PYTHONUNBUFFERED=1

# Portas da aplicação
EXPOSE 8000 8052

# Comando padrão - executa API + Dashboard
CMD ["python", "-m", "src.main"] 