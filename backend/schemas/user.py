from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    nombre: str
    apellidos: Optional[str] = None
    usuario: str
    dni: Optional[str] = None
    celular: Optional[str] = None
    correo: Optional[EmailStr] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    foto_path: Optional[str] = None
    encodings: Optional[dict] = None # Lista de vectores/dict
    rasgos_faciales: Optional[dict] = None
    fecha_registro: datetime
    activo: bool

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    status: str
    user_id: Optional[int] = None
    message: Optional[str] = None
