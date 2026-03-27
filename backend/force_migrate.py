import psycopg2
DATABASE_URL = "postgresql://postgres:182000@localhost:5433/faceaccess"

def force_migrate():
    print(f"🔄 Forzando migración directa en {DATABASE_URL}...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
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
                cur.execute(f"ALTER TABLE usuarios ADD COLUMN {col_name} {col_type};")
                print(f"✅ Columna '{col_name}' añadida a 'usuarios'")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"ℹ️ Columna '{col_name}' ya existe.")
                else:
                    print(f"❌ Error añadiendo '{col_name}': {e}")
        
        # --- Migraciones para 'alertas' ---
        alerts_cols = [
            ("video_path", "VARCHAR"),
            ("nivel_riesgo", "VARCHAR DEFAULT 'Bajo'")
        ]
        for col_name, col_type in alerts_cols:
            try:
                cur.execute(f"ALTER TABLE alertas ADD COLUMN {col_name} {col_type};")
                print(f"✅ Columna '{col_name}' añadida a 'alertas'")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"ℹ️ Columna '{col_name}' ya existe.")
                else:
                    print(f"❌ Error añadiendo '{col_name}' a 'alertas': {e}")

        cur.close()
        conn.close()
        print("🚀 Migración FORZADA completada con éxito.")
    except Exception as e:
        print(f"❌ Error fatal en migración forzada: {e}")

if __name__ == "__main__":
    force_migrate()
