"""
Middlewares de segurança para autenticação de webhooks
Implementa validação de tokens, rate limiting e logs de segurança
"""

import time
import json
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from .security_config import security_config

class SecurityMiddleware:
    """Classe base para middlewares de segurança"""
    
    def __init__(self):
        self.request_counts = {}  # Para rate limiting
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], request: Request):
        """
        Registra eventos de segurança
        """
        client_ip = request.client.host if request.client else "unknown"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = {
            "timestamp": timestamp,
            "event_type": event_type,
            "client_ip": client_ip,
            "endpoint": str(request.url.path),
            "method": request.method,
            "details": details
        }
        
        print(f"[SECURITY] {json.dumps(log_entry, indent=2)}")
    
    def check_rate_limit(self, request: Request, limit_per_minute: int = 60) -> bool:
        """
        Verifica rate limiting por IP
        """
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Inicializa contador para o IP
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []
        
        # Remove requisições antigas (mais de 1 minuto)
        self.request_counts[client_ip] = [
            req_time for req_time in self.request_counts[client_ip]
            if current_time - req_time < 60
        ]
        
        # Verifica se excedeu o limite
        if len(self.request_counts[client_ip]) >= limit_per_minute:
            return False
        
        # Adiciona requisição atual
        self.request_counts[client_ip].append(current_time)
        return True

class GuruWebhookMiddleware(SecurityMiddleware):
    """
    Middleware de autenticação para webhooks da Guru
    Valida o token no campo payload.api_token
    """
    
    async def __call__(self, request: Request):
        """
        Valida webhook da Guru antes do processamento
        """
        try:
            # Verifica rate limiting
            if not self.check_rate_limit(request, security_config.RATE_LIMIT_PER_MINUTE):
                self.log_security_event("RATE_LIMIT_EXCEEDED", {
                    "client_ip": request.client.host if request.client else "unknown"
                }, request)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Too many requests."
                )
            
            # Lê o corpo da requisição
            body = await request.body()
            if not body:
                self.log_security_event("EMPTY_PAYLOAD", {}, request)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Empty payload"
                )
            
            # Parse do JSON
            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                self.log_security_event("INVALID_JSON", {}, request)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid JSON payload"
                )
            
            # Valida estrutura do payload
            if "payload" not in payload:
                self.log_security_event("INVALID_PAYLOAD_STRUCTURE", {
                    "payload_keys": list(payload.keys())
                }, request)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid payload structure. Missing 'payload' field."
                )
            
            # Extrai token do payload
            api_token = payload.get("payload", {}).get("api_token")
            if not api_token:
                self.log_security_event("MISSING_API_TOKEN", {
                    "payload_keys": list(payload.get("payload", {}).keys())
                }, request)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing API token in payload"
                )
            
            # Valida token
            if not security_config.validate_guru_token(api_token):
                self.log_security_event("INVALID_GURU_TOKEN", {
                    "provided_token": api_token[:10] + "..." if len(api_token) > 10 else api_token
                }, request)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API token"
                )
            
            # Log de sucesso
            self.log_security_event("GURU_WEBHOOK_AUTHENTICATED", {
                "token_valid": True,
                "payload_type": payload.get("webhook_type", "unknown")
            }, request)
            
            # Adiciona payload validado ao request para uso posterior
            request.state.validated_payload = payload
            return None
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Log de erro inesperado
            self.log_security_event("AUTHENTICATION_ERROR", {
                "error": str(e),
                "error_type": type(e).__name__
            }, request)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal authentication error"
            )

class TictoWebhookMiddleware(SecurityMiddleware):
    """
    Middleware de autenticação para webhooks da Ticto
    Valida o token no campo raiz 'token'
    """
    
    async def __call__(self, request: Request):
        """
        Valida webhook da Ticto antes do processamento
        """
        try:
            # Verifica rate limiting
            if not self.check_rate_limit(request, security_config.RATE_LIMIT_PER_MINUTE):
                self.log_security_event("RATE_LIMIT_EXCEEDED", {
                    "client_ip": request.client.host if request.client else "unknown"
                }, request)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Too many requests."
                )
            
            # Lê o corpo da requisição
            body = await request.body()
            if not body:
                self.log_security_event("EMPTY_PAYLOAD", {}, request)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Empty payload"
                )
            
            # Parse do JSON
            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                self.log_security_event("INVALID_JSON", {}, request)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid JSON payload"
                )
            
            # Valida estrutura do payload
            if "token" not in payload:
                self.log_security_event("INVALID_PAYLOAD_STRUCTURE", {
                    "payload_keys": list(payload.keys())
                }, request)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid payload structure. Missing 'token' field."
                )
            
            # Extrai token do payload
            webhook_token = payload.get("token")
            if not webhook_token:
                self.log_security_event("MISSING_TOKEN", {
                    "payload_keys": list(payload.keys())
                }, request)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing token in payload"
                )
            
            # Valida token
            if not security_config.validate_ticto_token(webhook_token):
                self.log_security_event("INVALID_TICTO_TOKEN", {
                    "provided_token": webhook_token[:10] + "..." if len(webhook_token) > 10 else webhook_token
                }, request)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid webhook token"
                )
            
            # Log de sucesso
            self.log_security_event("TICTO_WEBHOOK_AUTHENTICATED", {
                "token_valid": True,
                "status": payload.get("status", "unknown")
            }, request)
            
            # Adiciona payload validado ao request para uso posterior
            request.state.validated_payload = payload
            return None
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Log de erro inesperado
            self.log_security_event("AUTHENTICATION_ERROR", {
                "error": str(e),
                "error_type": type(e).__name__
            }, request)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal authentication error"
            )

# Instâncias dos middlewares
guru_webhook_middleware = GuruWebhookMiddleware()
ticto_webhook_middleware = TictoWebhookMiddleware()
