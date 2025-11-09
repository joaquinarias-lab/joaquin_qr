# app/schemas.py
# VERSIÓN 3 (A prueba de balas para la 'ñ')
# Esta es la versión que necesitas.

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional # <-- Importante

# 1. ESTE ARCHIVO NO DEBE IMPORTAR 'app.crud' NI 'app.database'
# (Esto arregla la importación circular)

class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    rol: str
    activo: bool = True

class UsuarioCreate(UsuarioBase):
    contrasena: str = Field(..., alias="contraseña")
    class Config:
        populate_by_name = True

# --- INICIO DE LA MODIFICACIÓN CLAVE PARA EL LOGIN ---

class UsuarioLogin(BaseModel):
    email: EmailStr
    
    # Campo con alias (acepta 'contraseña' con ñ)
    contrasena: Optional[str] = Field(None, alias="contraseña") 
    # Campo sin alias (acepta 'contrasena' sin ñ)
    contraseña: Optional[str] = None 

    class Config:
        populate_by_name = True 
        from_attributes = True # Reemplaza a orm_mode
# --- FIN DE LA MODIFICACIÓN CLAVE ---

class Usuario(UsuarioBase):
    id: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user_role: str
    user_name: str
    user_id: int

class SessionCreate(BaseModel):
    session_id: str
    valid_from: datetime
    valid_until: datetime
    lat: float
    lng: float
    radius_meters: float

class AttendanceCreate(BaseModel):
    session_id: str
    timestamp: datetime
    lat: float
    lng: float

class ClaseCreate(BaseModel):
    nombre: str
    profesor_id: int
    fecha: date
    hora_inicio: str
    hora_fin: str
    ubicacion: str | None = None

class Clase(ClaseCreate):
    id: int
    class Config:
        from_attributes = True

class QrCodeCreate(BaseModel):
    clase_id: int
    qr_hash: str
    fecha_creacion: datetime
    fecha_expiracion: datetime
    ubicacion_permitida: str | None = None

class QrCode(QrCodeCreate):
    id: int
    class Config:
        from_attributes = True

class AsistenciaCreate(BaseModel):
    clase_id: int
    alumno_id: int
    timestamp: datetime
    estado: str
    token_qr: str

class Asistencia(AsistenciaCreate):
    id: int
    class Config:
        from_attributes = True

class AsistenciaToken(BaseModel):
    qr_token: str

