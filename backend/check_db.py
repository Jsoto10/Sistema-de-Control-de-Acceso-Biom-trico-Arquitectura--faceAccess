import psycopg2
try:
    conn = psycopg2.connect("postgresql://postgres:182000@localhost:5433/faceaccess")
    cur = conn.cursor()
    cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'usuarios';")
    columns = cur.fetchall()
    print("Columns in 'usuarios' table:")
    for col in columns:
        print(f" - {col[0]} ({col[1]})")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
