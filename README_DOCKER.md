# 🐳 Dashboard Comu - Instruções Docker

## 📋 Pré-requisitos

### 1. Instalar Docker Desktop
- **Windows 10/11 Pro/Enterprise/Education:**
  - Baixe: https://www.docker.com/products/docker-desktop/
  - Instale e reinicie o computador

- **Windows Home:**
  - Use Docker Toolbox: https://github.com/docker-archive/toolbox/releases

### 2. Verificar Instalação
```bash
docker --version
docker-compose --version
```

## 🚀 Como Executar

### Opção 1: Script Automático (Recomendado)
```bash
# No Windows, execute:
start_docker.bat
```

### Opção 2: Comandos Manuais
```bash
# 1. Construir e iniciar todos os serviços
docker-compose up --build

# 2. Para rodar em background
docker-compose up -d

# 3. Para parar
docker-compose down
```

## 📊 Acessos

Após iniciar, você pode acessar:

- **Dashboard:** http://localhost:8050
- **API:** http://localhost:8000
- **Banco de Dados:** localhost:5432
  - Usuário: `metrics_user`
  - Senha: `asdfghjkl`
  - Banco: `metrics_db`

## 🔧 Comandos Úteis

### Gerenciar Containers
```bash
# Ver containers rodando
docker ps

# Ver logs
docker-compose logs api
docker-compose logs db

# Parar tudo
docker-compose down

# Remover volumes (cuidado: apaga dados)
docker-compose down -v
```

### Banco de Dados
```bash
# Acessar PostgreSQL
docker-compose exec db psql -U metrics_user -d metrics_db

# Executar migrações
docker-compose exec api alembic upgrade head

# Ver dados
docker-compose exec db psql -U metrics_user -d metrics_db -c "SELECT * FROM clientes;"
```

### Desenvolvimento
```bash
# Reconstruir após mudanças
docker-compose up --build

# Ver logs em tempo real
docker-compose logs -f api
```

## 🐛 Solução de Problemas

### Docker não encontrado
```bash
# Verificar se está instalado
docker --version

# Se não funcionar, reinstale o Docker Desktop
```

### Porta já em uso
```bash
# Verificar o que está usando a porta
netstat -ano | findstr :8000

# Parar o processo ou mudar porta no docker-compose.yml
```

### Erro de permissão
```bash
# No Windows, execute PowerShell como Administrador
# Ou adicione seu usuário ao grupo docker-users
```

### Container não inicia
```bash
# Ver logs detalhados
docker-compose logs api

# Reconstruir sem cache
docker-compose build --no-cache
```

## 📁 Estrutura do Projeto

```
Dashboard Comu/
├── docker-compose.yml    # Configuração dos serviços
├── Dockerfile           # Imagem da API
├── requirements.txt     # Dependências Python
├── start_docker.bat    # Script de inicialização
└── src/
    ├── Api/            # Endpoints FastAPI
    ├── dashboard/      # Dashboard Dash
    ├── database/       # Modelos e conexão
    ├── services/       # Lógica de negócio
    └── utils/          # Utilitários
```

## 🔄 Fluxo de Desenvolvimento

1. **Instalar Docker Desktop**
2. **Executar `start_docker.bat`**
3. **Acessar http://localhost:8050**
4. **Fazer mudanças no código**
5. **Reconstruir: `docker-compose up --build`**

## 📞 Suporte

Se encontrar problemas:
1. Verifique se o Docker está rodando
2. Execute `docker-compose logs` para ver erros
3. Tente `docker-compose down && docker-compose up --build` 