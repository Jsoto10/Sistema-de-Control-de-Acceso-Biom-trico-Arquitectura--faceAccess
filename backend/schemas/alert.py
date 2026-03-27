from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AlertBase(BaseModel):
    imagen_path: str
    video_path: Optional[str] = None
    descripcion: str
    tipo: str
    nivel_riesgo: str = "Bajo"
    metadata_json: Optional[dict] = None

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    id: int
    timestamp: datetime
    estado: str

    class Config:
        from_attributes = True
