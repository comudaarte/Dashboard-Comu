"""
Configurações de segurança para webhooks e autenticação
Centraliza todas as configurações de segurança da aplicação
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class SecurityConfig:
    """Configurações de segurança centralizadas"""
    
    # Tokens de autenticação
    GURU_ACCOUNT_TOKEN = os.getenv("GURU_ACCOUNT_TOKEN")
    TICTO_WEBHOOK_TOKENS = os.getenv("TICTO_WEBHOOK_TOKENS", "")
    
    # Chave secreta da aplicação
    SECRET_KEY = os.getenv("SECRET_KEY")
    
    # Configurações de rate limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    
    # Configurações de segurança
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")
    
    @classmethod
    def get_ticto_tokens(cls) -> List[str]:
        """
        Retorna lista de tokens válidos da Ticto
        Formato esperado: token1,token2,token3
        """
        if not cls.TICTO_WEBHOOK_TOKENS:
            return []
        
        # Remove espaços e divide por vírgula
        tokens = [token.strip() for token in cls.TICTO_WEBHOOK_TOKENS.split(",")]
        # Remove tokens vazios
        tokens = [token for token in tokens if token and token != "your_webhook_token"]
        return tokens
    
    @classmethod
    def validate_guru_token(cls, token: str) -> bool:
        """
        Valida token da Guru
        """
        if not cls.GURU_ACCOUNT_TOKEN:
            print("[SECURITY] ⚠️ GURU_ACCOUNT_TOKEN não configurado")
            return False
        
        return token == cls.GURU_ACCOUNT_TOKEN
    
    @classmethod
    def validate_ticto_token(cls, token: str) -> bool:
        """
        Valida token da Ticto
        """
        valid_tokens = cls.get_ticto_tokens()
        
        if not valid_tokens:
            print("[SECURITY] ⚠️ Nenhum token Ticto configurado")
            return False
        
        return token in valid_tokens
    
    @classmethod
    def is_configured(cls) -> bool:
        """
        Verifica se todas as configurações de segurança estão configuradas
        """
        required_configs = [
            cls.GURU_ACCOUNT_TOKEN,
            cls.SECRET_KEY,
            cls.get_ticto_tokens()
        ]
        
        # Verifica se pelo menos um token Ticto está configurado
        ticto_configured = len(cls.get_ticto_tokens()) > 0
        
        return all([
            cls.GURU_ACCOUNT_TOKEN,
            cls.SECRET_KEY,
            ticto_configured
        ])

# Instância global da configuração
security_config = SecurityConfig()
