"""
Rotas de autenticação para o Dashboard Comu
"""
from datetime import timedelta
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database.connection import get_db_session
from services.auth_service import auth_service
from middleware.auth_middleware import get_current_user, require_admin
from database.auth_models import User, UserRole

# Router para autenticação
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# Modelos Pydantic
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.VIEWER

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: str
    last_login: str = None

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class LoginRequest(BaseModel):
    username: str
    password: str

class APIKeyCreate(BaseModel):
    key_name: str

class APIKeyResponse(BaseModel):
    api_key: str
    key_name: str
    expires_at: str

@auth_router.post("/login", response_model=Token)
async def login(
    request: Request,
    login_data: LoginRequest
):
    """Endpoint de login"""
    # Obter IP do cliente
    client_ip = request.client.host
    if "x-forwarded-for" in request.headers:
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
    
    # Autenticar usuário
    db = get_db_session()
    try:
        user = auth_service.authenticate_user(
            db, 
            login_data.username, 
            login_data.password, 
            client_ip
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Criar token de acesso
        access_token_expires = timedelta(minutes=auth_service.access_token_expire_minutes)
        access_token = auth_service.create_access_token(
            data={"sub": user.username}, 
            expires_delta=access_token_expires
        )
        
        # Log de auditoria
        auth_service.log_audit(
            db, 
            user.id, 
            "LOGIN", 
            "AUTH", 
            f"User {user.username} logged in",
            client_ip,
            request.headers.get("user-agent")
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": auth_service.access_token_expire_minutes * 60
        }
    finally:
        db.close()

@auth_router.post("/register", response_model=UserResponse)
async def register(
    request: Request,
    user_data: UserCreate,
    current_user: User = Depends(require_admin)
):
    """Endpoint de registro de usuário (apenas admin)"""
    db = get_db_session()
    try:
        # Verificar se username já existe
        existing_user = auth_service.get_user_by_username(db, user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Criar usuário
        user = auth_service.create_user(
            db,
            user_data.username,
            user_data.email,
            user_data.password,
            user_data.full_name,
            user_data.role
        )
        
        # Log de auditoria
        auth_service.log_audit(
            db,
            current_user.id,
            "CREATE_USER",
            "USER",
            f"Created user {user.username} with role {user.role.value}",
            request.client.host,
            request.headers.get("user-agent")
        )
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None
        )
    finally:
        db.close()

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Obtém informações do usuário atual"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at.isoformat(),
        last_login=current_user.last_login.isoformat() if current_user.last_login else None
    )

@auth_router.post("/api-key", response_model=APIKeyResponse)
async def create_api_key(
    request: Request,
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user)
):
    """Cria nova chave de API"""
    db = get_db_session()
    try:
        api_key = auth_service.create_api_key(
            db,
            current_user.id,
            key_data.key_name
        )
        
        # Log de auditoria
        auth_service.log_audit(
            db,
            current_user.id,
            "CREATE_API_KEY",
            "API_KEY",
            f"Created API key: {key_data.key_name}",
            request.client.host,
            request.headers.get("user-agent")
        )
        
        return APIKeyResponse(
            api_key=api_key,
            key_name=key_data.key_name,
            expires_at="1 year"
        )
    finally:
        db.close()

@auth_router.get("/users", response_model=list[UserResponse])
async def list_users(
    current_user: User = Depends(require_admin)
):
    """Lista todos os usuários (apenas admin)"""
    db = get_db_session()
    try:
        users = db.query(User).all()
        
        return [
            UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at.isoformat(),
                last_login=user.last_login.isoformat() if user.last_login else None
            )
            for user in users
        ]
    finally:
        db.close()

@auth_router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    new_role: UserRole,
    current_user: User = Depends(require_admin)
):
    """Atualiza role do usuário (apenas admin)"""
    db = get_db_session()
    try:
        success = auth_service.update_user_role(db, user_id, new_role)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "User role updated successfully"}
    finally:
        db.close()

@auth_router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_admin)
):
    """Desativa usuário (apenas admin)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate yourself"
        )
    
    db = get_db_session()
    try:
        success = auth_service.deactivate_user(db, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "User deactivated successfully"}
    finally:
        db.close()

@auth_router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Endpoint de logout"""
    db = get_db_session()
    try:
        # Log de auditoria
        auth_service.log_audit(
            db,
            current_user.id,
            "LOGOUT",
            "AUTH",
            f"User {current_user.username} logged out",
            request.client.host,
            request.headers.get("user-agent")
        )
        
        return {"message": "Successfully logged out"}
    finally:
        db.close()

@auth_router.get("/health")
async def auth_health():
    """Health check para autenticação"""
    return {"status": "healthy", "service": "authentication"}