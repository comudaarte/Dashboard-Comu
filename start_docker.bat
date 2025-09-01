@echo off
echo ========================================
echo    Dashboard Comu - Docker Setup
echo ========================================
echo.

echo Verificando se o Docker esta instalado...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ Docker nao encontrado!
    echo.
    echo Por favor, instale o Docker Desktop:
    echo 1. Vá para: https://www.docker.com/products/docker-desktop/
    echo 2. Baixe e instale o Docker Desktop
    echo 3. Reinicie o computador
    echo 4. Execute este script novamente
    echo.
    pause
    exit /b 1
)

echo ✅ Docker encontrado!
echo.

echo Verificando se o Docker esta rodando...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ Docker nao esta rodando!
    echo.
    echo Por favor:
    echo 1. Abra o Docker Desktop
    echo 2. Aguarde ele inicializar completamente
    echo 3. Execute este script novamente
    echo.
    pause
    exit /b 1
)

echo ✅ Docker esta rodando!
echo.

echo Iniciando o projeto...
echo.
echo 📊 Dashboard: http://localhost:8050
echo 🔌 API: http://localhost:8000
echo 🗄️  Banco: localhost:5432
echo.

docker-compose up --build

pause 