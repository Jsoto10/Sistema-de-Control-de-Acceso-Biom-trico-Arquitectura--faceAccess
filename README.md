# FaceAccess Biometric System

Sistema de control de acceso biométrico basado en reconocimiento facial en tiempo real, diseñado para entornos empresariales, educativos y de seguridad.

## Características principales

* 🎥 Reconocimiento facial en tiempo real
* 🧠 Detección de vida (Liveness Detection - Anti Spoofing)
* 🔐 Control de acceso automatizado
* 🚨 Sistema de alertas para intrusos
* 📊 Dashboard web administrativo
* ⚡ Comunicación en tiempo real (WebSockets)
* 🗄️ Base de datos PostgreSQL
* 🔍 Integración con búsqueda externa (Google Lens)

## Arquitectura del sistema

El sistema está dividido en tres módulos principales:

### Backend (FastAPI)

* API REST para gestión de usuarios y accesos
* WebSockets para eventos en tiempo real
* Registro de logs y alertas
* Integración con PostgreSQL

### Sensor Biométrico (Python + OpenCV)

* Captura de video desde cámara
* Detección y reconocimiento facial
* Validación de identidad
* Detección de parpadeo (anti-spoofing)
* Envío de eventos al backend

### Dashboard (Angular)

* Panel de administración
* Visualización de accesos e intrusos
* Gestión de usuarios
* Centro de alertas
* Búsqueda de intrusos en internet

## Flujo del sistema

1. El sensor captura video en tiempo real
2. Detecta y analiza rostros
3. Valida identidad contra la base de datos
4. Si es válido → acceso permitido
5. Si no es válido → se genera alerta
6. El backend notifica al dashboard en tiempo real

## Tecnologías utilizadas

* Backend: FastAPI, SQLAlchemy
* Frontend: Angular
* Base de datos: PostgreSQL
* Computer Vision: OpenCV, face_recognition
* Comunicación en tiempo real: WebSockets

## Instalación

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Sensor

```bash
cd app
python sensor.py
```

### Frontend

```bash
cd dashboard
npm install
ng serve -o
```


## Configuración

Configura la conexión a la base de datos en:

```bash
backend/database.py
```

Ejemplo:

```python
postgresql://usuario:password@localhost:agrega el puerto/faceaccess
```

##  Seguridad

* Validación biométrica
* Detección de vida (blink detection)
* Autenticación con JWT
* Registro de auditoría

##  Aertas de seguridad

Cuando el sistema detecta un rostro no autorizado:

* Se captura una imagen automáticamente
* Se registra en la base de datos
* Se envía una alerta en tiempo real al dashboard
* Se permite investigar mediante Google Lens

## Casos de uso

* Control de acceso en empresas
* Registro de asistencia
* Seguridad en instituciones educativas
* Monitoreo en entornos sensibles
  
## Autor
Desarrollado por Jose Soto celis

## Licencia
Este proyecto es de uso educativo y demostrativo.
