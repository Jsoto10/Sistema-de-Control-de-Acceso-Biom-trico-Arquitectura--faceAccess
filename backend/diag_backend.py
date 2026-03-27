import sys
import os

# Asegurar que el directorio actual está en el path
sys.path.append(os.getcwd())

import traceback

print("--- Diagnóstico del Backend PRO ---")

# Verificar variables de entorno
db_env = os.getenv("DATABASE_URL")
if db_env:
    print(f"(!) Detectada variable de entorno DATABASE_URL: {db_env}")
else:
    print("(-) No se detectó variable de entorno DATABASE_URL (usando default).")

try:
    print("1. Probando imports de Base y engine...")
    from database import Base, engine, get_db, SQLALCHEMY_DATABASE_URL
    print(f"   URL de conexión actual: {SQLALCHEMY_DATABASE_URL}")
    print("   [OK] Imports de database exitosos.")
except Exception:
    print("   [ERROR] Fallo en imports de database.")
    traceback.print_exc()
    sys.exit(1)

try:
    print("2. Probando conexión a la base de datos...")
    # Intento 1: SQLAlchemy
    with engine.connect() as connection:
        print("   [OK] Conexión establecida con SQLAlchemy.")
except Exception:
    print("\n[!] Falló SQLAlchemy. Probando conexión directa con psycopg2...")
    try:
        import psycopg2
        print("\n[!] Listando bases de datos disponibles en localhost:5433...")
        # Conectar a la base por defecto 'postgres' para listar las demás
        conn = psycopg2.connect("host=localhost port=5433 user=postgres password=182000 dbname=postgres")
        cur = conn.cursor()
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        dbs = [row[0] for row in cur.fetchall()]
        print(f"   Bases de datos encontradas: {dbs}")
        
        if "FaceAccess" in dbs:
            print("   [OK] La base 'FaceAccess' SI EXISTE. El problema podría ser otro.")
        elif "faceaccess" in dbs:
            print("   [AVISO] Encontré 'faceaccess' (todo minúsculas). Cambia el nombre en database.py.")
        else:
            print("   [ERROR] 'FaceAccess' NO ESTÁ en la lista. Por favor, créala en pgAdmin.")
        
        cur.close()
        conn.close()
    except Exception as e2:
        print("\n[ERROR CRÍTICO] FALLO AL CONECTAR CON POSTGRES")
        print(f"   MENSAJE DIRECTO: {e2}")
        sys.exit(1)

try:
    print("3. Probando imports de modelos...")
    from models.user import User
    from models.access_log import AccessLog
    from models.alert import Alert
    print("   [OK] Modelos cargados.")
except Exception as e:
    print(f"   [ERROR] Fallo al cargar modelos: {e}")
    sys.exit(1)

try:
    print("4. Probando imports de servicios...")
    from services.face_service import FaceService
    from services.access_service import AccessService
    print("   [OK] Servicios cargados.")
except Exception as e:
    print(f"   [ERROR] Fallo al cargar servicios: {e}")
    sys.exit(1)

print("\n--- Diagnóstico Completado ---")
print("Si todo salió OK, puedes iniciar el servidor con:")
print("uvicorn main:app --reload")
