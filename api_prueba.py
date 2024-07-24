from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os
import pymysql
import uvicorn

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

app = FastAPI()

@app.get("/tables")
async def get_tables():
    try:
        # Conectar a la base de datos
        db = pymysql.connect(**config)
        cursor = db.cursor()

        # Realizar una consulta para obtener las tablas
        cursor.execute('SHOW TABLES')
        tables = cursor.fetchall()
        
        # Extraer los nombres de las tablas
        table_names = [table[f'Tables_in_{database}'] for table in tables]

        return {"tables": table_names}

    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'db' in locals() and db:
            db.close()

# Código para ejecutar el servidor Uvicorn si el script se ejecuta directamente
if __name__ == "__main__":
    uvicorn.run("api_prueba:app", host="0.0.0.0", port=8000)

