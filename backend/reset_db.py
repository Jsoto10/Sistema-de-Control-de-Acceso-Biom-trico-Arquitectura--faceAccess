import psycopg2
DATABASE_URL = "postgresql://postgres:182000@localhost:5433/faceaccess"

def reset_db():
    print(f"⚠️ REINICIANDO TABLAS en {DATABASE_URL}...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Eliminar tablas (CUIDADO: Borra los datos)
        cur.execute("DROP TABLE IF EXISTS access_logs CASCADE;")
        cur.execute("DROP TABLE IF EXISTS alertas CASCADE;")
        cur.execute("DROP TABLE IF EXISTS usuarios CASCADE;")
        
        print("✅ Tablas eliminadas con éxito.")
        cur.close()
        conn.close()
        
        # Recrear usando SQLAlchemy (como hace main.py)
        print("🔄 Recreando tablas con SQLAlchemy...")
        from database import engine, Base
        from models.user import User
        from models.access_log import AccessLog
        from models.alert import Alert
        
        Base.metadata.create_all(bind=engine)
        print("🚀 Tablas recreadas con el esquema CORRECTO.")
        
    except Exception as e:
        print(f"❌ Error al reiniciar DB: {e}")

if __name__ == "__main__":
    reset_db()
