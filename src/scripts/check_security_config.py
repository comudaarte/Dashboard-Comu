#!/usr/bin/env python3
"""
Script de verificação rápida das configurações de segurança
Verifica se todas as variáveis necessárias estão configuradas
"""

import sys
import os

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def check_security_config():
    """
    Verifica configurações de segurança
    """
    print("🔒 Verificando configurações de segurança...")
    print("=" * 50)
    
    try:
        from utils.security_config import security_config
        
        # Verifica configuração geral
        is_configured = security_config.is_configured()
        print(f"✅ Configuração completa: {is_configured}")
        
        # Verifica SECRET_KEY
        secret_key = security_config.SECRET_KEY
        if secret_key and secret_key != "your-secret-key-here-generate-with-openssl":
            print(f"✅ SECRET_KEY: Configurada ({secret_key[:10]}...)")
        else:
            print("❌ SECRET_KEY: Não configurada ou inválida")
        
        # Verifica token Guru
        guru_token = security_config.GURU_ACCOUNT_TOKEN
        if guru_token:
            print(f"✅ GURU_ACCOUNT_TOKEN: Configurado ({guru_token[:10]}...)")
        else:
            print("❌ GURU_ACCOUNT_TOKEN: Não configurado")
        
        # Verifica tokens Ticto
        ticto_tokens = security_config.get_ticto_tokens()
        if ticto_tokens:
            print(f"✅ TICTO_WEBHOOK_TOKENS: {len(ticto_tokens)} token(s) configurado(s)")
            for i, token in enumerate(ticto_tokens, 1):
                print(f"   Token {i}: {token[:10]}...")
        else:
            print("❌ TICTO_WEBHOOK_TOKENS: Nenhum token configurado")
        
        # Verifica configurações de rate limiting
        rate_limit_min = security_config.RATE_LIMIT_PER_MINUTE
        rate_limit_hour = security_config.RATE_LIMIT_PER_HOUR
        print(f"✅ Rate Limiting: {rate_limit_min}/min, {rate_limit_hour}/hora")
        
        # Verifica hosts permitidos
        allowed_hosts = security_config.ALLOWED_HOSTS
        print(f"✅ ALLOWED_HOSTS: {', '.join(allowed_hosts)}")
        
        print("\n" + "=" * 50)
        
        if is_configured:
            print("🎉 Todas as configurações de segurança estão corretas!")
            print("💡 Execute 'python src/scripts/test_security.py' para testes completos")
        else:
            print("⚠️ Algumas configurações estão faltando ou incorretas")
            print("💡 Verifique o arquivo .env e execute novamente")
        
        return is_configured
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("💡 Verifique se está executando do diretório correto")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    success = check_security_config()
    sys.exit(0 if success else 1)
