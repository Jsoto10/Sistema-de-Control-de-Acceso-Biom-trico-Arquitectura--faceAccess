from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class AccessLog(Base):
    __tablename__ = "accesos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    tipo = Column(String) # 'entrada', 'salida'
    resultado = Column(String) # 'exito', 'fallido'
    metodo = Column(String, default="facial")
    confidence = Column(Float, nullable=True)
    sensor_id = Column(String, default="principal")

    usuario = relationship("User", back_populates="accesos")
