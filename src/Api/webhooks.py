# Webhooks endpoints com autenticação e segurança

from fastapi import FastAPI, Request, Depends
from src.services.webhook_handler import processar_guru_assinatura, processar_guru_transacao, processar_ticto
from src.utils.security_middleware import guru_webhook_middleware, ticto_webhook_middleware
from src.utils.security_config import security_config

app = FastAPI(
    title="Dashboard Comu - Webhooks API",
    description="API para recebimento de webhooks das plataformas Guru e Ticto",
    version="1.0.0"
)

@app.get("/health")
def health():
    """
    Endpoint de saúde da aplicação
    """
    return {
        "status": "ok",
        "security_configured": security_config.is_configured(),
        "guru_token_configured": bool(security_config.GURU_ACCOUNT_TOKEN),
        "ticto_tokens_configured": len(security_config.get_ticto_tokens()) > 0
    }

@app.post("/webhook/guru")
async def webhook_guru(request: Request):
    """
    Endpoint para webhooks da plataforma Guru
    Requer autenticação via api_token no payload
    """
    # Middleware de segurança já validou o token e payload
    # Usa o payload validado do request.state
    payload = request.state.validated_payload
    
    # Extrai payload real se vier aninhado
    if "payload" in payload:
        payload = payload["payload"]
    
    webhook_type = payload.get("webhook_type", "transaction")
    
    if webhook_type == "subscription":
        resultado = processar_guru_assinatura(payload)
    else:
        resultado = processar_guru_transacao(payload)
    
    return {
        "received": True, 
        "platform": "guru", 
        "webhook_type": webhook_type,
        "result": resultado
    }

@app.post("/webhook/ticto")
async def webhook_ticto(request: Request):
    """
    Endpoint para webhooks da plataforma Ticto
    Requer autenticação via token no nível raiz
    """
    # Middleware de segurança já validou o token e payload
    # Usa o payload validado do request.state
    payload = request.state.validated_payload
    
    resultado = processar_ticto(payload)
    
    return {
        "received": True, 
        "platform": "ticto", 
        "status": payload.get("status", "unknown"),
        "result": resultado
    }

# Middleware de segurança para Guru
@app.middleware("http")
async def guru_security_middleware(request: Request, call_next):
    if request.url.path == "/webhook/guru":
        await guru_webhook_middleware(request)
    return await call_next(request)

# Middleware de segurança para Ticto
@app.middleware("http")
async def ticto_security_middleware(request: Request, call_next):
    if request.url.path == "/webhook/ticto":
        await ticto_webhook_middleware(request)
    return await call_next(request)