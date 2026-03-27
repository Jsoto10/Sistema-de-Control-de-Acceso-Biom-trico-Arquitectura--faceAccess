import psycopg2
try:
    conn = psycopg2.connect("postgresql://postgres:182000@localhost:5433/faceaccess")
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'usuarios';")
    columns = cur.fetchall()
    print("FIELDS_IN_USUARIOS:")
    for col in columns:
        print(f"COL:{col[0]}")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
