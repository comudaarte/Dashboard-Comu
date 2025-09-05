"""
Serviço de autenticação para o Dashboard Comu
"""
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from database.auth_models import User, APIKey, AuditLog, LoginAttempt, UserRole
from database.connection import get_db_session

# Configurações de segurança
SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta-muito-longa-e-segura-aqui")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
API_KEY_EXPIRE_DAYS = 365

# Contexto de hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Serviço principal de autenticação"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha está correta"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Gera hash da senha"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Cria token JWT de acesso"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifica e decodifica token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    def authenticate_user(self, db: Session, username: str, password: str, ip_address: str = None) -> Optional[User]:
        """Autentica usuário com username e senha"""
        user = db.query(User).filter(
            or_(User.username == username, User.email == username)
        ).first()
        
        if not user:
            self._log_login_attempt(db, username, ip_address, False, "User not found")
            return None
        
        if not user.is_active:
            self._log_login_attempt(db, username, ip_address, False, "User inactive")
            return None
        
        if not self.verify_password(password, user.hashed_password):
            self._log_login_attempt(db, username, ip_address, False, "Invalid password")
            return None
        
        # Login bem-sucedido
        user.last_login = datetime.utcnow()
        db.commit()
        self._log_login_attempt(db, username, ip_address, True, "Success")
        
        return user
    
    def create_user(self, db: Session, username: str, email: str, password: str, 
                   full_name: str, role: UserRole = UserRole.VIEWER) -> User:
        """Cria novo usuário"""
        hashed_password = self.get_password_hash(password)
        
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            is_active=True,
            is_verified=True  # Auto-verificar para simplificar
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    def create_api_key(self, db: Session, user_id: int, key_name: str) -> str:
        """Cria nova chave de API"""
        # Gerar chave aleatória
        api_key = f"dash_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Data de expiração (1 ano)
        expires_at = datetime.utcnow() + timedelta(days=API_KEY_EXPIRE_DAYS)
        
        db_key = APIKey(
            user_id=user_id,
            key_name=key_name,
            key_hash=key_hash,
            expires_at=expires_at
        )
        
        db.add(db_key)
        db.commit()
        
        return api_key
    
    def verify_api_key(self, db: Session, api_key: str) -> Optional[User]:
        """Verifica chave de API"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        db_key = db.query(APIKey).filter(
            and_(
                APIKey.key_hash == key_hash,
                APIKey.is_active == True,
                or_(
                    APIKey.expires_at.is_(None),
                    APIKey.expires_at > datetime.utcnow()
                )
            )
        ).first()
        
        if not db_key:
            return None
        
        # Atualizar último uso
        db_key.last_used = datetime.utcnow()
        db.commit()
        
        return db_key.user
    
    def log_audit(self, db: Session, user_id: int, action: str, resource: str, 
                  details: str = None, ip_address: str = None, user_agent: str = None):
        """Registra log de auditoria"""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(audit_log)
        db.commit()
    
    def _log_login_attempt(self, db: Session, username: str, ip_address: str, 
                          success: bool, reason: str = None):
        """Registra tentativa de login"""
        attempt = LoginAttempt(
            username=username,
            ip_address=ip_address,
            success=success,
            failure_reason=reason
        )
        
        db.add(attempt)
        db.commit()
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Busca usuário por ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """Busca usuário por username"""
        return db.query(User).filter(User.username == username).first()
    
    def update_user_role(self, db: Session, user_id: int, new_role: UserRole) -> bool:
        """Atualiza role do usuário"""
        user = self.get_user_by_id(db, user_id)
        if not user:
            return False
        
        user.role = new_role
        db.commit()
        return True
    
    def deactivate_user(self, db: Session, user_id: int) -> bool:
        """Desativa usuário"""
        user = self.get_user_by_id(db, user_id)
        if not user:
            return False
        
        user.is_active = False
        db.commit()
        return True

# Instância global do serviço
auth_service = AuthService()
