from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from database import Base

class Alert(Base):
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    imagen_path = Column(String)
    video_path = Column(String, nullable=True)
    descripcion = Column(String)
    tipo = Column(String) # 'desconocido', 'fallo_liveness', 'intento_denegado'
    nivel_riesgo = Column(String, default="Bajo") # 'Bajo', 'Medio', 'Alto'
    estado = Column(String, default="pendiente") # 'pendiente', 'revisado'
    metadata_json = Column(JSON, nullable=True)
