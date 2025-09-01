"""
Utilitários comuns para scripts de backfill
"""
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
import os
import json
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def setup_logging(script_name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Configura logging robusto para o script com múltiplos handlers
    """
    logger = logging.getLogger(script_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove handlers existentes para evitar duplicação
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Formato detalhado para arquivo
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s'
    )
    
    # Formato simplificado para console
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Handler para arquivo detalhado
    try:
        os.makedirs('logs', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_handler = logging.FileHandler(f'logs/{script_name}_{timestamp}.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
        # Handler para arquivo de erros separado
        error_handler = logging.FileHandler(f'logs/{script_name}_errors_{timestamp}.log', encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_handler)
        
        logger.info(f"📝 Sistema de logging configurado - Arquivos: {script_name}_{timestamp}.log e {script_name}_errors_{timestamp}.log")
        
    except Exception as e:
        logger.warning(f"⚠️ Não foi possível configurar logging para arquivo: {e}")
    
    return logger

def setup_backfill_logging(script_name: str, start_date: str = None, end_date: str = None) -> tuple:
    """
    Configura logging específico para backfill com arquivos organizados
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Cria diretórios
    os.makedirs('logs', exist_ok=True)
    os.makedirs('backup_logs', exist_ok=True)
    
    # Nome base dos arquivos
    base_name = f"{script_name}_{timestamp}"
    
    # Logger principal
    logger = setup_logging(script_name, "DEBUG")
    
    # Arquivo de log principal
    main_log_file = f'logs/{base_name}.log'
    
    # Arquivo de log de transações
    transactions_log_file = f'logs/{base_name}_transactions.log'
    
    # Arquivo de log de assinaturas
    subscriptions_log_file = f'logs/{base_name}_subscriptions.log'
    
    # Arquivo de log de erros
    errors_log_file = f'logs/{base_name}_errors.log'
    
    # Arquivo de log de API calls
    api_log_file = f'logs/{base_name}_api_calls.log'
    
    # Arquivo de log de estatísticas
    stats_log_file = f'logs/{base_name}_statistics.log'
    
    # Configura handlers específicos
    setup_specialized_handlers(logger, {
        'transactions': transactions_log_file,
        'subscriptions': subscriptions_log_file,
        'errors': errors_log_file,
        'api_calls': api_log_file,
        'statistics': stats_log_file
    })
    
    # Log inicial com informações do backfill
    logger.info("=" * 80)
    logger.info("🚀 INICIANDO BACKFILL COMPLETO")
    logger.info("=" * 80)
    logger.info(f"📅 Script: {script_name}")
    logger.info(f"🕐 Timestamp: {timestamp}")
    logger.info(f"📊 Data Início: {start_date or 'TODOS OS DADOS'}")
    logger.info(f"📊 Data Fim: {end_date or 'TODOS OS DADOS'}")
    logger.info(f"📁 Arquivos de Log:")
    logger.info(f"   📝 Principal: {main_log_file}")
    logger.info(f"   💰 Transações: {transactions_log_file}")
    logger.info(f"   📋 Assinaturas: {subscriptions_log_file}")
    logger.info(f"   ❌ Erros: {errors_log_file}")
    logger.info(f"   🌐 API Calls: {api_log_file}")
    logger.info(f"   📊 Estatísticas: {stats_log_file}")
    logger.info("=" * 80)
    
    return logger, base_name

def setup_specialized_handlers(logger: logging.Logger, log_files: Dict[str, str]):
    """
    Configura handlers especializados para diferentes tipos de log
    """
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s'
    )
    
    for log_type, file_path in log_files.items():
        try:
            handler = logging.FileHandler(file_path, encoding='utf-8')
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(detailed_formatter)
            
            # Filtro para mensagens específicas
            if log_type == 'transactions':
                handler.addFilter(lambda record: 'transação' in record.getMessage().lower() or 'transaction' in record.getMessage().lower())
            elif log_type == 'subscriptions':
                handler.addFilter(lambda record: 'assinatura' in record.getMessage().lower() or 'subscription' in record.getMessage().lower())
            elif log_type == 'errors':
                handler.addFilter(lambda record: record.levelno >= logging.ERROR)
            elif log_type == 'api_calls':
                handler.addFilter(lambda record: 'api call' in record.getMessage().lower() or 'request' in record.getMessage().lower())
            elif log_type == 'statistics':
                handler.addFilter(lambda record: 'estatística' in record.getMessage().lower() or 'stat' in record.getMessage().lower())
            
            logger.addHandler(handler)
            
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível configurar handler para {log_type}: {e}")

def log_transaction_details(logger: logging.Logger, transaction_data: Dict[str, Any], action: str, result: Dict[str, Any] = None):
    """
    Log detalhado de transações
    """
    transaction_id = transaction_data.get('id', 'unknown')
    
    logger.info(f"💰 PROCESSANDO TRANSAÇÃO: {transaction_id}")
    logger.info(f"   📊 Ação: {action}")
    logger.info(f"   📅 Data: {transaction_data.get('dates', {}).get('created_at', 'N/A')}")
    logger.info(f"   💵 Valor: {transaction_data.get('payment', {}).get('total', 'N/A')}")
    logger.info(f"   🏷️ Status: {transaction_data.get('status', 'N/A')}")
    logger.info(f"   👤 Cliente: {transaction_data.get('contact', {}).get('email', 'N/A')}")
    logger.info(f"   📦 Produto: {transaction_data.get('product', {}).get('name', 'N/A')}")
    
    if result:
        logger.info(f"   ✅ Resultado: {result.get('status', 'N/A')}")
        if result.get('motivo'):
            logger.info(f"   📝 Motivo: {result.get('motivo')}")
    
    logger.info(f"   {'='*50}")

def log_subscription_details(logger: logging.Logger, subscription_data: Dict[str, Any], action: str, enriched_data: Dict[str, Any] = None):
    """
    Log detalhado de assinaturas
    """
    subscription_id = subscription_data.get('id', 'unknown')
    
    logger.info(f"📋 PROCESSANDO ASSINATURA: {subscription_id}")
    logger.info(f"   📊 Ação: {action}")
    logger.info(f"   📅 Data Início: {subscription_data.get('started_at', 'N/A')}")
    logger.info(f"   🏷️ Status: {subscription_data.get('status', 'N/A')}")
    logger.info(f"   👤 Cliente: {subscription_data.get('contact', {}).get('email', 'N/A')}")
    logger.info(f"   📦 Produto: {subscription_data.get('product', {}).get('name', 'N/A')}")
    
    if enriched_data:
        logger.info(f"   🔍 Dados Enriquecidos:")
        logger.info(f"      💰 Valor Mensal: {enriched_data.get('valor_mensal', 'N/A')}")
        logger.info(f"      💰 Valor Anual: {enriched_data.get('valor_anual', 'N/A')}")
        logger.info(f"      📅 Data Cancelamento: {enriched_data.get('data_cancelamento', 'N/A')}")
        logger.info(f"      🏷️ Nome Oferta: {enriched_data.get('nome_oferta', 'N/A')}")
    
    logger.info(f"   {'='*50}")

def log_api_call(logger: logging.Logger, method: str, url: str, params: Dict = None, response_status: int = None, response_data: Dict = None):
    """
    Log detalhado de chamadas para API
    """
    logger.info(f"🌐 API CALL: {method} {url}")
    if params:
        logger.info(f"   📋 Parâmetros: {json.dumps(params, indent=2, default=str)}")
    if response_status:
        logger.info(f"   📊 Status: {response_status}")
    if response_data:
        logger.info(f"   📄 Resposta: {json.dumps(response_data, indent=2, default=str)[:500]}...")
    logger.info(f"   {'='*50}")

def log_statistics(logger: logging.Logger, stats: Dict[str, Any], phase: str = "GERAL"):
    """
    Log de estatísticas do backfill
    """
    logger.info(f"📊 ESTATÍSTICAS - {phase}")
    logger.info(f"   💰 Transações Processadas: {stats.get('transactions_processed', 0)}")
    logger.info(f"   💰 Transações Criadas: {stats.get('transactions_created', 0)}")
    logger.info(f"   💰 Transações Atualizadas: {stats.get('transactions_updated', 0)}")
    logger.info(f"   📋 Assinaturas Processadas: {stats.get('subscriptions_processed', 0)}")
    logger.info(f"   📋 Assinaturas Criadas: {stats.get('subscriptions_created', 0)}")
    logger.info(f"   📋 Assinaturas Atualizadas: {stats.get('subscriptions_updated', 0)}")
    logger.info(f"   ❌ Erros: {stats.get('errors', 0)}")
    logger.info(f"   {'='*50}")

def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator para retry em caso de erro
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    print(f"Tentativa {attempt + 1} falhou: {e}. Tentando novamente em {delay}s...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

def get_env_var(var_name: str, required: bool = True) -> Optional[str]:
    """
    Obtém variável de ambiente
    """
    value = os.getenv(var_name)
    if required and not value:
        raise ValueError(f"Variável de ambiente {var_name} é obrigatória")
    return value

def validate_response(response: Dict[str, Any], expected_keys: list) -> bool:
    """
    Valida se a resposta da API contém as chaves esperadas
    """
    for key in expected_keys:
        if key not in response:
            print(f"Chave esperada '{key}' não encontrada na resposta")
            return False
    return True

def format_progress(current: int, total: int, description: str = "") -> str:
    """
    Formata string de progresso
    """
    percentage = (current / total * 100) if total > 0 else 0
    return f"{description} - {current}/{total} ({percentage:.1f}%)"

def create_backup_log(data: Dict[str, Any], filename: str, logger: logging.Logger = None):
    """
    Cria log de backup dos dados processados com logging detalhado
    """
    try:
        os.makedirs('backup_logs', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f'backup_logs/{filename}_{timestamp}.json'
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
        
        if logger:
            logger.info(f"✅ Backup criado: {backup_file}")
            logger.info(f"📊 Conteúdo do backup:")
            logger.info(f"   💰 Transações: {data.get('transactions', {}).get('total', 0)}")
            logger.info(f"   📋 Assinaturas: {data.get('subscriptions', {}).get('total', 0)}")
            logger.info(f"   ❌ Erros: {data.get('errors', 0)}")
        else:
            print(f"✅ Backup criado: {backup_file}")
            
        return backup_file
        
    except Exception as e:
        error_msg = f"⚠️ Não foi possível criar backup: {e}"
        if logger:
            logger.error(error_msg)
        else:
            print(error_msg)
        
        # Salva no console como fallback
        print(f"📄 Dados do backup ({filename}):")
        print(json.dumps(data, indent=2, default=str, ensure_ascii=False)[:1000] + "..." if len(json.dumps(data, default=str)) > 1000 else "")
        return None

def finalize_backfill_logging(logger: logging.Logger, base_name: str, final_stats: Dict[str, Any], duration: float):
    """
    Finaliza o logging do backfill com resumo completo
    """
    logger.info("=" * 80)
    logger.info("🏁 BACKFILL FINALIZADO")
    logger.info("=" * 80)
    logger.info(f"⏱️ Duração Total: {duration:.2f} segundos")
    logger.info(f"📊 Estatísticas Finais:")
    log_statistics(logger, final_stats, "FINAL")
    logger.info(f"📁 Arquivos de Log Gerados:")
    logger.info(f"   📝 Principal: logs/{base_name}.log")
    logger.info(f"   💰 Transações: logs/{base_name}_transactions.log")
    logger.info(f"   📋 Assinaturas: logs/{base_name}_subscriptions.log")
    logger.info(f"   ❌ Erros: logs/{base_name}_errors.log")
    logger.info(f"   🌐 API Calls: logs/{base_name}_api_calls.log")
    logger.info(f"   📊 Estatísticas: logs/{base_name}_statistics.log")
    logger.info("=" * 80)
