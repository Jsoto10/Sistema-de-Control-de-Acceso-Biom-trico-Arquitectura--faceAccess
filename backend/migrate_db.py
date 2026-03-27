import psycopg2
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:182000@localhost:5433/faceaccess"

def migrate():
    print(f"🔄 Iniciando migración en {DATABASE_URL}...")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            # --- Migraciones para 'alertas' ---
            try:
                conn.execute(text("ALTER TABLE alertas ADD COLUMN video_path VARCHAR;"))
                print("✅ Columna 'video_path' añadida a 'alertas'")
            except Exception: pass

            try:
                conn.execute(text("ALTER TABLE alertas ADD COLUMN nivel_riesgo VARCHAR DEFAULT 'Bajo';"))
                print("✅ Columna 'nivel_riesgo' añadida a 'alertas'")
            except Exception: pass

            # --- Migraciones para 'usuarios' ---
            columns_to_add = [
                ("apellidos", "VARCHAR"),
                ("dni", "VARCHAR"),
                ("celular", "VARCHAR"),
                ("correo", "VARCHAR"),
                ("foto_path", "VARCHAR"),
                ("rasgos_faciales", "JSON"),
                ("activo", "BOOLEAN DEFAULT TRUE")
            ]

            for col_name, col_type in columns_to_add:
                try:
                    conn.execute(text(f"ALTER TABLE usuarios ADD COLUMN {col_name} {col_type};"))
                    print(f"✅ Columna '{col_name}' añadida a 'usuarios'")
                except Exception as e:
                    # Probablemente ya existe
                    pass
            
            conn.commit()
            print("🚀 Migración completada con éxito.")
    except Exception as e:
        print(f"❌ Error fatal en migración: {e}")

if __name__ == "__main__":
    migrate()
