import pymysql
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener las credenciales desde las variables de entorno
username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
database = os.getenv('DB_DATABASE')

# Configuración de la conexión
config = {
    'user': username,
    'password': password,
    'host': host,
    'database': database,
    'cursorclass': pymysql.cursors.DictCursor
}

# Conectar a la base de datos
try:
    db = pymysql.connect(**config)
    cursor = db.cursor()
    # Realizar una consulta (ejemplo: mostrar tablas)
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    print('Tablas en la base de datos:', tables)


finally:
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'db' in locals() and db:
        db.close()