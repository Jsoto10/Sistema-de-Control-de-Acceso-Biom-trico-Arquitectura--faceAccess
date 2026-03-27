from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import datetime
import shutil
import json
import os

from database import engine, Base, get_db
from models.user import User as UserModel
from models.access_log import AccessLog
from models.alert import Alert
from schemas.user import UserCreate, User as UserSchema, UserLogin
from services.face_service import FaceService
from services.access_service import AccessService
import base64
import os

from fastapi.staticfiles import StaticFiles

# Crear las tablas y carpetas estáticas
Base.metadata.create_all(bind=engine)
os.makedirs("static/profiles", exist_ok=True)
os.makedirs("static/alertas", exist_ok=True)
os.makedirs("static/videos", exist_ok=True) # Carpeta para evidencia en video

app = FastAPI(title="Biometric Access API PRO")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except:
                pass

manager = ConnectionManager()

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Biometric Access API is running"}

@app.post("/api/face-recognition")
async def face_recognition_endpoint(data: dict, db: Session = Depends(get_db)):
    """
    Recibe el encoding facial del sensor y procesa el acceso.
    """
    encoding = data.get("encoding")
    confidence = data.get("confidence", 0.0)
    sensor_id = data.get("sensor_id", "principal")

    if not encoding:
        raise HTTPException(status_code=400, detail="No facial encoding provided")

    # 1. Obtener usuarios activos
    db_users = db.query(UserModel).filter(UserModel.activo == True).all()
    users_list = [
        {"id": u.id, "nombre": u.nombre, "encodings": u.encodings} 
        for u in db_users
    ]

    # 2. Buscar coincidencia usando FaceService (tolerancia ajustada para mayor precisión PRO)
    match_user, distance = FaceService.get_best_match(users_list, encoding, tolerance=0.4)

    if match_user:
        # Calcular score de confianza inversa (1.0 - distancia) si no viene del sensor
        if confidence == 0.0:
            confidence = round(1.0 - distance, 2)

        # 3. Registrar Acceso
        access = AccessService.register_access(
            db, 
            match_user["id"], 
            "exito", 
            confidence=confidence, 
            sensor_id=sensor_id
        )
        
        # 4. Notificar al Dashboard vía WebSocket PRO
        event = {
            "type": "access",
            "status": "success",
            "user_id": match_user["id"],
            "user_name": match_user["nombre"],
            "access_type": access.tipo,
            "confidence": confidence,
            "sensor_id": sensor_id,
            "timestamp": datetime.datetime.now().isoformat()
        }
        await manager.broadcast(event)
        
        return {
            "status": "success", 
            "user": match_user["nombre"], 
            "type": access.tipo,
            "confidence": confidence
        }
    else:
        # 5. Rostro desconocido -> Notificar Alerta Inmediata
        event = {
            "type": "access_denied",
            "status": "unknown",
            "message": "Intento de acceso: Rostro desconocido",
            "sensor_id": sensor_id,
            "timestamp": datetime.datetime.now().isoformat()
        }
        await manager.broadcast(event)
        
        return {"status": "denied", "message": "Unknown face"}

@app.get("/api/logs")
def get_logs(limit: int = 50, db: Session = Depends(get_db)):
    """
    Obtiene los últimos n registros de acceso con información del usuario.
    """
    return db.query(AccessLog).options(joinedload(AccessLog.usuario)).order_by(AccessLog.id.desc()).limit(limit).all()

@app.post("/api/login")
async def login(credentials: UserLogin):
    # Por ahora usaremos un admin estático para simplicidad
    # En producción esto consultaría una tabla de admins con hash de password
    if credentials.username == "admin" and credentials.password == "admin123":
        return {"status": "success", "token": "fake-jwt-token-pro", "user": "Administrador"}
    raise HTTPException(status_code=401, detail="Credenciales incorrectas")

@app.post("/api/alerts")
async def create_alert(data: dict, db: Session = Depends(get_db)):
    """
    Recibe una alerta con imagen (base64) y metadata del sensor.
    """
    imagen_b64 = data.get("imagen")
    if not imagen_b64:
        raise HTTPException(status_code=400, detail="No image provided for alert")

    descripcion = data.get("descripcion", "Persona no identificada")
    tipo = data.get("tipo", "desconocido")
    metadata = data.get("metadata", {})

    # Guardar imagen físicamente
    filename = f"alerta_{datetime.datetime.now().timestamp()}.jpg"
    filepath = os.path.join("static/alertas", filename)
    
    try:
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(imagen_b64))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando imagen: {e}")

    video_b64 = data.get("video") # Opcional: clip en base64
    video_path = None

    if video_b64:
        v_filename = f"video_{datetime.datetime.now().timestamp()}.mp4"
        v_filepath = os.path.join("static/videos", v_filename)
        try:
            with open(v_filepath, "wb") as f:
                f.write(base64.b64decode(video_b64))
            video_path = f"/static/videos/{v_filename}"
        except:
            pass

    db_alert = Alert(
        imagen_path=f"/static/alertas/{filename}",
        video_path=video_path,
        descripcion=descripcion,
        tipo=tipo,
        nivel_riesgo=data.get("nivel_riesgo", "Bajo"),
        metadata_json=metadata,
        timestamp=datetime.datetime.utcnow()
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)

    # Notificar al Dashboard
    event = {
        "type": "alert",
        "status": "new",
        "id": db_alert.id,
        "image": db_alert.imagen_path,
        "video": video_path,
        "description": descripcion,
        "risk": db_alert.nivel_riesgo,
        "metadata": metadata,
        "timestamp": db_alert.timestamp.isoformat()
    }
    await manager.broadcast(event)

    return {"status": "success", "alert_id": db_alert.id}

@app.get("/api/alerts")
def get_alerts(limit: int = 20, db: Session = Depends(get_db)):
    return db.query(Alert).order_by(Alert.id.desc()).limit(limit).all()

@app.post("/api/users/register")
async def register_user(
    nombre: str = Form(...),
    apellidos: str = Form(None),
    usuario: str = Form(None),
    dni: str = Form(None),
    celular: str = Form(None),
    correo: str = Form(None),
    foto_frente: UploadFile = File(...),
    foto_izquierda: UploadFile = File(None),
    foto_derecha: UploadFile = File(None),
    foto_arriba: UploadFile = File(None),
    foto_abajo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    # Generar usuario automático si no se provee
    if not usuario:
        base_user = (nombre.split()[0].lower() + (f"_{dni[-4:]}" if dni and len(dni) >= 4 else f"_{datetime.datetime.now().microsecond}"))
        usuario = base_user
    
    # 1. Verificar si el usuario ya existe (con reintento si el generado colisiona)
    db_user = db.query(UserModel).filter(UserModel.usuario == usuario).first()
    if db_user:
        if not usuario: # Si fue generado, añadir un suffix extra
             usuario = f"{usuario}_{datetime.datetime.now().second}"
        else:
            raise HTTPException(status_code=400, detail="El usuario ya existe")

    # 2. Procesar todos los ángulos disponibles
    fotos = {
        "frente": foto_frente,
        "izquierda": foto_izquierda,
        "derecha": foto_derecha,
        "arriba": foto_arriba,
        "abajo": foto_abajo
    }
    
    dict_encodings = {}
    main_rasgos = None
    main_file_path = f"static/profiles/{usuario}.jpg"

    for angle, foto in fotos.items():
        if not foto: continue
        
        # Leer bytes
        img_bytes = await foto.read()
        
        # Extraer biometría SOLO para la foto de frente (Optimización PRO para evitar timeouts)
        if angle == "frente":
            encs, rasgos = FaceService.extract_and_analyze(img_bytes)
            if encs:
                dict_encodings[angle] = encs
                main_rasgos = rasgos
                # Guardar foto principal
                with open(main_file_path, "wb") as buffer:
                    buffer.write(img_bytes)
            else:
                raise HTTPException(status_code=400, detail="No se detectó rostro en la foto frontal")
        else:
            # Para otros ángulos, solo guardar la imagen si es necesario (opcional)
            # Por ahora solo guardamos el encoding frontal para velocidad
            pass

    if not dict_encodings:
        raise HTTPException(status_code=400, detail="No se pudo extraer biometría de ninguna toma")

    # 3. Crear usuario en DB
    nuevo_usuario = UserModel(
        nombre=nombre,
        apellidos=apellidos,
        usuario=usuario,
        dni=dni,
        celular=celular,
        correo=correo,
        foto_path=main_file_path,
        encodings=dict_encodings,
        rasgos_faciales=main_rasgos
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return {"status": "success", "user_id": nuevo_usuario.id, "angles_registered": list(dict_encodings.keys())}

@app.get("/api/users")
def get_users(limit: int = 100, db: Session = Depends(get_db)):
    """
    Lista todos los usuarios registrados.
    """
    return db.query(UserModel).order_by(UserModel.id.desc()).limit(limit).all()

@app.delete("/api/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(db_user)
    db.commit()
    return {"status": "success", "message": "Usuario eliminado"}

@app.patch("/api/users/{user_id}/status")
def update_user_status(user_id: int, activo: bool, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db_user.activo = activo
    db.commit()
    return {"status": "success", "message": f"Usuario {'activado' if activo else 'desactivado'}"}

@app.post("/api/users")
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo usuario (Legacy).
    """
    db_user = UserModel(
        nombre=user_data.nombre,
        apellidos=user_data.apellidos,
        usuario=user_data.usuario,
        dni=user_data.dni,
        celular=user_data.celular,
        correo=user_data.correo,
        encodings={} # Cambiado a dict para consistencia
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- WebSocket para el Dashboard ---
@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Mantener conexión viva y recibir si es necesario
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
