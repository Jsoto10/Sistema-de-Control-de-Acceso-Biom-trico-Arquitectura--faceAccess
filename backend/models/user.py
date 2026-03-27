from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    apellidos = Column(String, nullable=True)
    usuario = Column(String, unique=True, index=True)
    dni = Column(String, unique=True, index=True, nullable=True)
    celular = Column(String, nullable=True)
    correo = Column(String, nullable=True)
    foto_path = Column(String, nullable=True)
    encodings = Column(JSON) # Lista de listas (vectores faciales)
    rasgos_faciales = Column(JSON, nullable=True) # Metadata extra PRO
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    activo = Column(Boolean, default=True)

    accesos = relationship("AccessLog", back_populates="usuario", cascade="all, delete-orphan")
