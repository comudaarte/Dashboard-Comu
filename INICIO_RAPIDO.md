# 🚀 Dashboard Comu - Início Rápido

## ⚡ Execução Rápida

### 🐳 Docker (Recomendado)
```bash
# 1. Iniciar todos os serviços (API + Dashboard automático)
docker-compose up -d

# 2. Acessar serviços
# API: http://localhost:8000
# Dashboard: http://localhost:8052
```

### 💻 Local
```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar dashboard
python simple_dashboard.py

# 3. Acessar dashboard
http://localhost:8050
```

## 📊 Scripts Disponíveis

| Script | Descrição | Uso |
|--------|-----------|-----|
| `src/main.py` | Aplicação principal (Docker) | `docker-compose up -d` |
| `simple_dashboard.py` | Execução local simples | `python simple_dashboard.py` |
| `run_dashboard.py` | Execução configurável | `python run_dashboard.py --external --debug` |
| `test_integration.py` | Teste de integração | `python test_integration.py` |

## 🔧 Opções do Dashboard Configurável

```bash
python run_dashboard.py --help

# Exemplos:
python run_dashboard.py --port 8080
python run_dashboard.py --external --debug
python run_dashboard.py --host 0.0.0.0 --port 9000
```

## 🐛 Resolução de Problemas

### Dashboard não carrega
```bash
# Verificar containers
docker ps

# Ver logs da aplicação principal
docker-compose logs api

# Reiniciar tudo
docker-compose restart
```

### Erro de porta em uso
```bash
# Parar Docker completamente
docker-compose down

# Verificar portas locais
netstat -ano | findstr :8050
netstat -ano | findstr :8052
```

## 📚 Documentação Completa

- **README.md** - Documentação completa
- **docs/implementacao_dashboard_visual.md** - Detalhes do dashboard
- **docs/documentacao_metricas.md** - Sistema de métricas
