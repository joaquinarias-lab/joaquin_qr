# app/auth_utils.py
# VERSIÓN FINAL Y COMPLETA
# Este archivo define las *herramientas* para la autenticación.

from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app import crud, database
from app.schemas import Usuario

# 1. Definimos el Contexto de Contraseña
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# 2. Definimos los "schemes" de seguridad de FastAPI
# FastAPI usará esto para buscar el token en el "Header"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False) 
oauth2_scheme_refresh = OAuth2PasswordBearer(tokenUrl="token/refresh", auto_error=False)

# 3. Función para verificar la contraseña
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 4. Función para autenticar (buscar en DB y verificar contraseña)
def authenticate_user(db: Session, email: str, password: str):
    usuario = crud.get_usuario_por_email(db, email)
    if not usuario or not verify_password(password, usuario.contrasena_hash):
        return None
    return usuario

# --- Lógica de Access Token ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# 5. ESTA ES LA FUNCIÓN QUE FALTABA (Arregla el ImportError)
def get_current_user(db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
    if token is None:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proveyó token de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            raise credentials_exception
        
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    usuario = crud.get_usuario_por_email(db, email)
    if usuario is None:
        raise credentials_exception
    return usuario

# --- Lógica de Refresh Token ---
def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_refresh_token(db: Session, token: str) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token inválido o expirado"
    )
    try:
        payload = jwt.decode(token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise credentials_exception
        
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    usuario = crud.get_usuario_por_email(db, email)
    if usuario is None:
        raise credentials_exception
    return usuario

# 6. ESTA ES LA OTRA FUNCIÓN QUE FALTABA
def get_current_user_with_roles(required_roles: List[str]):
    def role_dependency(current_user: Usuario = Depends(get_current_user)):
        if current_user.rol not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, # 403 Forbidden
                detail=f"Se requiere uno de estos roles: {', '.join(required_roles)}"
            )
        return current_user
    return role_dependency

