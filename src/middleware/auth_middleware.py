"""
Middleware de autenticação para FastAPI e Dash
"""
import os
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database.connection import get_db_session
from services.auth_service import auth_service
from database.auth_models import User, UserRole

# Esquema de autenticação
security = HTTPBearer()

class AuthMiddleware:
    """Middleware de autenticação para FastAPI"""
    
    def __init__(self):
        self.auth_service = auth_service
    
    async def get_current_user(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> User:
        """Obtém usuário atual a partir do token JWT"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = self.auth_service.verify_token(credentials.credentials)
            if payload is None:
                raise credentials_exception
            
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
                
        except Exception:
            raise credentials_exception
        
        db = get_db_session()
        try:
            user = self.auth_service.get_user_by_username(db, username=username)
            if user is None:
                raise credentials_exception
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Inactive user"
                )
            
            return user
        finally:
            db.close()
    
    async def get_current_active_user(
        self, 
        current_user: User = Depends(get_current_user)
    ) -> User:
        """Obtém usuário ativo atual"""
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        return current_user
    
    def require_role(self, required_role: UserRole):
        """Decorator para verificar role específica"""
        def role_checker(current_user: User = Depends(self.get_current_active_user)) -> User:
            if not self._check_role_permission(current_user.role, required_role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
            return current_user
        return role_checker
    
    def _check_role_permission(self, user_role: UserRole, required_role: UserRole) -> bool:
        """Verifica se o usuário tem permissão baseada no role"""
        role_hierarchy = {
            UserRole.VIEWER: 1,
            UserRole.MANAGER: 2,
            UserRole.ADMIN: 3,
            UserRole.API_USER: 1
        }
        
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
    
    async def get_current_user_optional(
        self, 
        request: Request
    ) -> Optional[User]:
        """Obtém usuário atual opcionalmente (para endpoints públicos)"""
        try:
            # Tentar obter token do header Authorization
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header.split(" ")[1]
            payload = self.auth_service.verify_token(token)
            if payload is None:
                return None
            
            username: str = payload.get("sub")
            if username is None:
                return None
            
            db = get_db_session()
            try:
                user = self.auth_service.get_user_by_username(db, username=username)
                if user and user.is_active:
                    return user
            finally:
                db.close()
            
        except Exception:
            pass
        
        return None

# Instância global do middleware
auth_middleware = AuthMiddleware()

# Dependências para FastAPI
get_current_user = auth_middleware.get_current_user
get_current_active_user = auth_middleware.get_current_active_user
get_current_user_optional = auth_middleware.get_current_user_optional

# Dependências para roles específicos
require_viewer = auth_middleware.require_role(UserRole.VIEWER)
require_manager = auth_middleware.require_role(UserRole.MANAGER)
require_admin = auth_middleware.require_role(UserRole.ADMIN)
require_api_user = auth_middleware.require_role(UserRole.API_USER)

class DashAuthMiddleware:
    """Middleware de autenticação para Dash"""
    
    def __init__(self, app):
        self.app = app
        self.auth_service = auth_service
        self._setup_auth_routes()
    
    def _setup_auth_routes(self):
        """Configura rotas de autenticação no Dash"""
        
        @self.app.server.before_request
        def check_auth():
            """Verifica autenticação antes de cada requisição"""
            from flask import request, redirect, url_for, session, jsonify
            
            # Rotas que não precisam de autenticação
            public_routes = ['/login', '/static', '/_dash', '/_reload-hash']
            
            if any(request.path.startswith(route) for route in public_routes):
                return None
            
            # Verificar se usuário está logado
            if 'user_id' not in session:
                return redirect('/login')
            
            # Verificar se token ainda é válido
            token = session.get('access_token')
            if not token:
                session.clear()
                return redirect('/login')
            
            payload = self.auth_service.verify_token(token)
            if not payload:
                session.clear()
                return redirect('/login')
            
            return None
    
    def login_user(self, user: User, token: str):
        """Faz login do usuário no Dash"""
        from flask import session
        
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role.value
        session['access_token'] = token
        session.permanent = True
    
    def logout_user(self):
        """Faz logout do usuário"""
        from flask import session
        session.clear()
    
    def get_current_user(self):
        """Obtém usuário atual da sessão"""
        from flask import session
        
        if 'user_id' not in session:
            return None
        
        return {
            'id': session.get('user_id'),
            'username': session.get('username'),
            'role': session.get('role')
        }
    
    def check_permission(self, required_role: UserRole) -> bool:
        """Verifica se usuário tem permissão"""
        user = self.get_current_user()
        if not user:
            return False
        
        user_role = UserRole(user['role'])
        return self._check_role_permission(user_role, required_role)
    
    def _check_role_permission(self, user_role: UserRole, required_role: UserRole) -> bool:
        """Verifica permissão baseada no role"""
        role_hierarchy = {
            UserRole.VIEWER: 1,
            UserRole.MANAGER: 2,
            UserRole.ADMIN: 3,
            UserRole.API_USER: 1
        }
        
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)