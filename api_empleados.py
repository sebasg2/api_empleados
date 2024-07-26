from fastapi import FastAPI, HTTPException, Request,Query
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

# Configuración de la conexión a la base de datos


#ordenar el search por numero de candidaturas, orden alfabetico de nombre_empleado y orden alfabetico de rol

config = {
    'user': username,
    'password': password,
    'host': host,
    'database': database,
    'cursorclass': pymysql.cursors.DictCursor
}

app = FastAPI()

@app.get("/all_empleados")
async def get_all_empleados(
    limit: int = Query(10, le=100),  # Límite por defecto es 10, máximo es 100
    offset: int = 0,
    search: Optional[str] = None,
    sort_by: Optional[str] = Query('num_candidaturas', enum=['num_candidaturas', 'nombre_empleado', 'rol']),
    sort_order: Optional[str] = Query('desc', enum=['asc', 'desc'])  # Agregar parámetro opcional para ordenar
):
    if limit > 50:
        limit = 50  # Establece el límite a 100 para no devolver resultados si excede 50

    try:
        # Conectar a la base de datos
        db = pymysql.connect(**config)
        cursor = db.cursor()

        # Construir la consulta base
        query = """
        SELECT * FROM empleados
        WHERE TRUE
        """
        parameters = []

        # Agregar filtro de búsqueda si se proporciona
        if search:
            query += ' AND (nombre_empleado LIKE %s OR apellidos_empleado LIKE %s OR rol LIKE %s)'
            parameters.extend([f'%{search}%', f'%{search}%', f'%{search}%'])

        # Construir la cláusula ORDER BY dinámicamente basada en el parámetro sort_by y sort_order
        valid_sort_columns = ['num_candidaturas', 'nombre_empleado', 'rol']
        if sort_by not in valid_sort_columns:
            sort_by = 'num_candidaturas'  # Valor por defecto

        if sort_order not in ['asc', 'desc']:
            sort_order = 'desc'  # Valor por defecto

        query += f' ORDER BY {sort_by} {sort_order.upper()} LIMIT %s OFFSET %s'
        parameters.extend([limit, offset])

        # Ejecutar la consulta
        cursor.execute(query, parameters)
        empleados = cursor.fetchall()

        return {"empleados": empleados}

    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")

    finally:
        # Asegurarse de cerrar el cursor y la conexión a la base de datos
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'db' in locals() and db:
            db.close()




#hacer que el delete pongan todas las candidaturas de ese empleado a que sean a id  1 que seria el administrador y luego se elimina el empleado
@app.delete("/delete_empleado")
async def delete_empleado(email_empleado: str):
    try:
        # Conectar a la base de datos
        db = pymysql.connect(**config)
        cursor = db.cursor()

        # Obtener el empleado_id del empleado a eliminar
        select_query = "SELECT id_empleado FROM empleados WHERE email_empleado = %s"
        cursor.execute(select_query, (email_empleado,))
        empleado = cursor.fetchone()

        if not empleado:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")

        empleado_id = empleado['id_empleado']

        # Actualizar las candidaturas para que el empleado_id sea 1
        update_query = "UPDATE candidaturas SET id_empleado = 1 WHERE id_empleado = %s"
        cursor.execute(update_query, (empleado_id,))
        db.commit()

        # Eliminar el empleado
        delete_query = "DELETE FROM empleados WHERE email_empleado = %s"
        cursor.execute(delete_query, (email_empleado,))
        db.commit()

        return {"detail": "Empleado eliminado exitosamente"}

    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'db' in locals() and db:
            db.close()

# Endpoint para actualizar un empleado
@app.put("/update_empleado")
async def update_empleado(request: Request):
    try:
        body = await request.json()
        email_empleado = body.get("email_empleado")
        nombre_empleado = body.get("nombre_empleado")
        apellidos_empleado = body.get("apellidos_empleado")
        password = body.get("password")
        rol = body.get("rol")
        is_logged = body.get("is_logged")
        
        if not email_empleado:
            raise HTTPException(status_code=400, detail="El campo 'email_empleado' es requerido.")

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
            email_empleado
        ))
        db.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")

        return {"detail": "Empleado actualizado exitosamente"}

    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'db' in locals() and db:
            db.close()

    
# Código para ejecutar el servidor Uvicorn si el script se ejecuta directamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_empleados:app", host="0.0.0.0", port=8000)



