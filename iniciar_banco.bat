@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    INICIADOR DO BANCO DE DADOS
echo ========================================
echo.

echo 🐳 Iniciando banco de dados via Docker...
echo.

REM Verifica se o Docker está instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker não encontrado! Instale o Docker Desktop primeiro.
    echo.
    pause
    exit /b 1
)

REM Verifica se está no diretório correto
if not exist "docker-compose.yml" (
    echo ❌ Execute este script no diretório raiz do projeto!
    echo.
    pause
    exit /b 1
)

echo ✅ Docker encontrado
echo ✅ Arquivo docker-compose.yml encontrado
echo.

echo 🔄 Parando containers existentes...
docker-compose down >nul 2>&1

echo 🚀 Iniciando banco de dados...
docker-compose up -d db

echo.
echo ⏳ Aguardando banco inicializar...
timeout /t 10 /nobreak >nul

echo.
echo 🔍 Verificando status do banco...
docker-compose ps

echo.
echo ✅ Banco de dados iniciado!
echo.
echo 💡 Agora você pode executar:
echo    python export_database.py
echo    ou
echo    exportar_banco.bat
echo.

echo Pressione qualquer tecla para sair...
pause >nul
