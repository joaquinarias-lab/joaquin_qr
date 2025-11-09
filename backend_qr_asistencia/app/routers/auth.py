# app/routers/auth.py
# VERSIÓN 3 (A prueba de balas para la 'ñ')
# Esta versión SÍ es compatible con app/schemas.py (Versión 3)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import database, schemas, auth_utils, crud

router = APIRouter(
    tags=["Autenticación"]
)

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    login_data: schemas.UsuarioLogin, # Correcto, sin Depends
    db: Session = Depends(database.get_db)
):
    """
    Inicia sesión de un usuario y devuelve un access token y un refresh token.
    """
    
    # --- LÓGICA MEJORADA PARA OBTENER LA CONTRASEÑA ---
    # Verificamos cuál de los dos campos (con o sin ñ) nos envió el frontend
    password = login_data.contraseña or login_data.contrasena
    
    if not password:
         raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No se proporcionó contraseña",
         )
    # --- FIN DE LA LÓGICA MEJORADA ---

    usuario = auth_utils.authenticate_user(
        db, 
        email=login_data.email,
        password=password # <-- Usamos la contraseña que encontramos
    )
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear tokens
    access_token_data = {"sub": usuario.email}
    access_token = auth_utils.create_access_token(data=access_token_data)
    
    refresh_token_data = {"sub": usuario.email}
    refresh_token = auth_utils.create_refresh_token(data=refresh_token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_role": usuario.rol,
        "user_name": usuario.nombre,
        "user_id": usuario.id
    }

@router.post("/token/refresh", response_model=schemas.Token)
async def refresh_access_token(
    db: Session = Depends(database.get_db),
    refresh_token: str = Depends(auth_utils.oauth2_scheme_refresh) 
):
    """
    Refresca un access token usando un refresh token válido.
    """
    usuario = auth_utils.verify_refresh_token(db, refresh_token)
    
    access_token_data = {"sub": usuario.email}
    access_token = auth_utils.create_access_token(data=access_token_data)

    new_refresh_token_data = {"sub": usuario.email}
    new_refresh_token = auth_utils.create_refresh_token(data=new_refresh_token_data)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user_role": usuario.rol,
        "user_name": usuario.nombre,
        "user_id": usuario.id
    }
