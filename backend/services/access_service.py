from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models.access_log import AccessLog
from schemas.access import AccessLogCreate
from typing import Optional

class AccessService:
    @staticmethod
    def register_access(db: Session, usuario_id: int, resultado: str, tipo: Optional[str] = None, metodo: str = "facial", confidence: Optional[float] = None, sensor_id: str = "principal"):
        """
        Registra una entrada o salida de un usuario.
        Determina automáticamente si es entrada o salida basado en el último registro.
        """
        # Buscar el último acceso del usuario
        last_access = db.query(AccessLog).filter(
            AccessLog.usuario_id == usuario_id
        ).order_by(AccessLog.id.desc()).first()
        
        # Lógica automática: Si no hay acceso previo o el último fue 'salida', este es 'entrada'
        if not tipo:
            if not last_access or last_access.tipo == "salida":
                tipo = "entrada"
            else:
                tipo = "salida"

        db_access = AccessLog(
            usuario_id=usuario_id,
            tipo=tipo,
            resultado=resultado,
            metodo=metodo,
            confidence=confidence,
            sensor_id=sensor_id,
            timestamp=datetime.utcnow()
        )
        db.add(db_access)
        db.commit()
        db.refresh(db_access)
        return db_access
