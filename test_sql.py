import pyodbc

SERVER = "192.168.68.22,1433"
DATABASE = "LAB"
USER = "admin"
PASSWORD = "Opentext1"
DRIVER = "SQL Server"  

conn_str = (
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"UID={USER};"
    f"PWD={PASSWORD};"
)

try:
    print(f"Conectando a SQL Server / DB: {DATABASE} ...")
    conn = pyodbc.connect(conn_str, timeout=10)
    cursor = conn.cursor()

    # En tu script plano, reemplaza la query por esta:
    query = """
    SELECT name FROM sys.tables WHERE name LIKE 'KUAF%';
    """
    cursor.execute(query)

    columns = [c[0] for c in cursor.description]
    rows = cursor.fetchall()

    print(f"Filas obtenidas: {len(rows)}")
    print("Columnas:", columns)

    for row in rows[:20]:
        print(tuple(row))

    cursor.close()
    conn.close()

except pyodbc.Error as e:
    print("Error al ejecutar la consulta")
    print(e)