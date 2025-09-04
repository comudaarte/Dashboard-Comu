@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    EXPORTADOR DE BANCO DE DADOS
echo ========================================
echo.

echo 🚀 Iniciando exportação do banco de dados...
echo.

REM Verifica se o Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado! Instale o Python primeiro.
    echo.
    pause
    exit /b 1
)

REM Verifica se está no diretório correto
if not exist "src\database\models.py" (
    echo ❌ Execute este script no diretório raiz do projeto!
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo ✅ Diretório do projeto correto
echo.

REM Instala dependências se necessário
echo 📦 Verificando dependências...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Aviso: Erro ao instalar dependências. Tentando continuar...
)

echo.
echo 🔌 Conectando ao banco de dados...
echo 📊 Exportando tabelas...
echo.

REM Executa o script de exportação
python export_database.py

echo.
if errorlevel 1 (
    echo ❌ Erro na exportação!
    echo.
    echo 💡 Dicas para resolver:
    echo    - Verifique se o banco está rodando
    echo    - Confirme as configurações no arquivo .env
    echo    - Verifique se todas as dependências estão instaladas
    echo.
) else (
    echo ✅ Exportação concluída com sucesso!
    echo.
    echo 📁 Os arquivos CSV estão em uma pasta com timestamp
    echo 📖 Consulte INSTRUCOES_EXPORTACAO.md para mais detalhes
    echo.
)

echo Pressione qualquer tecla para sair...
pause >nul
