from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os
import pymysql
from typing import Optional

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

@app.get("/all_empleados")
async def get_all_empleados():
    try:
        # Conectar a la base de datos
        db = pymysql.connect(**config)
        cursor = db.cursor()

        # Realizar una consulta para obtener todos los datos de la tabla empleados
        cursor.execute('SELECT * FROM empleados')
        empleados = cursor.fetchall()

        return {"empleados": empleados}

    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'db' in locals() and db:
            db.close()

@app.delete("/delete_empleado")
async def delete_empleado(email: str):
    try:
        # Conectar a la base de datos
        db = pymysql.connect(**config)
        cursor = db.cursor()

        # Realizar una consulta para eliminar un empleado por su email
        delete_query = "DELETE FROM empleados WHERE email_empleado = %s"
        cursor.execute(delete_query, (email,))
        db.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Employee not found")

        return {"detail": "Employee deleted successfully"}

    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'db' in locals() and db:
            db.close()

@app.put("/update_empleado")
async def update_empleado(
    email: str,
    nombre_empleado: Optional[str] = None,
    apellidos_empleado: Optional[str] = None,
    password: Optional[str] = None,
    rol: Optional[str] = None,
    is_logged: Optional[bool] = None
):
    try:
        # Conectar a la base de datos
        db = pymysql.connect(**config)
        cursor = db.cursor()

        # Preparar la consulta de actualización con COALESCE
        update_query = """
        UPDATE empleados
        SET
            nombre_empleado = COALESCE(%s, nombre_empleado),
            apellidos_empleado = COALESCE(%s, apellidos_empleado),
            password = COALESCE(%s, password),
            rol = COALESCE(%s, rol),
            is_logged = COALESCE(%s, is_logged)
        WHERE email_empleado = %s;
        """
        
        # Ejecutar la consulta de actualización
        cursor.execute(update_query, (
            nombre_empleado,
            apellidos_empleado,
            password,
            rol,
            is_logged,
            email
        ))
        db.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Employee not found")

        return {"detail": "Employee updated successfully"}

    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'db' in locals() and db:
            db.close()

# Código para ejecutar el servidor Uvicorn si el script se ejecuta directamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_empleados:app", host="0.0.0.0", port=8000)


