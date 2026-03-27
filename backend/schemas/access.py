from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AccessLogBase(BaseModel):
    usuario_id: int
    tipo: str
    resultado: str
    metodo: str = "facial"
    confidence: Optional[float] = None
    sensor_id: str = "principal"

class AccessLogCreate(AccessLogBase):
    pass

class AccessLog(AccessLogBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
