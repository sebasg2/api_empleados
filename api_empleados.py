from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import pymysql
import pandas as pd
from typing import Optional
import re 
import joblib
from sklearn.ensemble import RandomForestClassifier
import boto3




# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener las credenciales desde las variables de entorno
username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
database = os.getenv('DB_DATABASE')

config = {
    'user': username,
    'password': password,
    'host': host,
    'port': 3306,  # Asegúrate de incluir el puerto si es necesario
    'database': database,
    'cursorclass': pymysql.cursors.DictCursor
}

app = FastAPI()

# Configuración del middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow only the specific origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Cargar el modelo
model_path = 'models/model_web.pkl'  # Actualiza el nombre del archivo del modelo
with open(model_path, 'rb') as f:
    model = joblib.load(f)

#Conectar con S3

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)
s3_bucket_name = 'modelosexe'
s3_model_key = 'model_web.pkl'


@app.get("/all_empleados")
async def get_all_empleados(
    limit: int = Query(..., le=50),  # Límite máximo es 50
    offset: int = Query(...),
    search: Optional[str] = None,
    sort_by: Optional[str] = Query('num_candidaturas', enum=['num_candidaturas', 'nombre_empleado', 'rol']),
    sort_order: Optional[str] = Query('desc', enum=['asc', 'desc'])  # Agregar parámetro opcional para ordenar
):
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

@app.delete("/delete_empleado")
async def delete_empleado(id_empleado: int):
    try:
        # Conectar a la base de datos
        db = pymysql.connect(**config)
        cursor = db.cursor()

        # Verificar si el empleado existe
        select_query = "SELECT id_empleado FROM empleados WHERE id_empleado = %s"
        cursor.execute(select_query, (id_empleado,))
        empleado = cursor.fetchone()

        if not empleado:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")

        # Actualizar las candidaturas para que el id_empleado sea 1
        update_query = "UPDATE candidaturas SET id_empleado = 1 WHERE id_empleado = %s"
        cursor.execute(update_query, (id_empleado,))
        db.commit()

        # Eliminar el empleado
        delete_query = "DELETE FROM empleados WHERE id_empleado = %s"
        cursor.execute(delete_query, (id_empleado,))
        db.commit()

        return {"detail": "Empleado eliminado exitosamente"}

    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'db' in locals() and db:
            db.close()

@app.put("/update_empleado")
async def update_empleado(request: Request):
    try:
        body = await request.json()
        id_empleado = body.get("id_empleado")
        nombre_empleado = body.get("nombre_empleado")
        apellidos_empleado = body.get("apellidos_empleado")
        password = body.get("password")
        rol = body.get("rol")
        is_logged = body.get("is_logged")
        
        if not id_empleado:
            raise HTTPException(status_code=400, detail="El campo 'id_empleado' es requerido.")

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
        WHERE id_empleado = %s;
        """
        
        # Ejecutar la consulta de actualización
        cursor.execute(update_query, (
            nombre_empleado,
            apellidos_empleado,
            password,
            rol,
            is_logged,
            id_empleado
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

@app.get("/candidaturas_por_empleado")
async def get_candidaturas_por_empleado(id_empleado: int = Query(..., description="ID del empleado para filtrar candidaturas")):
    try:
        # Conectar a la base de datos
        db = pymysql.connect(**config)
        cursor = db.cursor(pymysql.cursors.DictCursor)  # Use DictCursor to get results as dictionaries

        # Obtener los datos de la tabla de candidaturas para el empleado específico
        query = """
        SELECT status, COUNT(*) as count 
        FROM candidaturas 
        WHERE id_empleado = %s
        GROUP BY status
        """
        cursor.execute(query, (id_empleado,))
        data = cursor.fetchall()
        
        # Convertir los datos a un DataFrame de pandas
        df = pd.DataFrame(data)

        # Cerrar la conexión
        cursor.close()
        db.close()

        # Verificar si se obtuvieron datos
        if df.empty:
            return {"message": "No se encontraron candidaturas para el empleado especificado."}

        # Convertir el DataFrame a un diccionario
        result = df.set_index('status')['count'].to_dict()

        # Retornar el diccionario como respuesta JSON
        return result

    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")

    except Exception as e:
   
 
        raise HTTPException(status_code=500, detail=f"Error al generar la respuesta: {e}")
    


@app.get("/candidaturas_status")
async def get_candidaturas_status():
    try:
        # Conectar a la base de datos
        db = pymysql.connect(**config)
        cursor = db.cursor(pymysql.cursors.DictCursor)

        # Obtener los datos de la tabla de candidaturas
        query = "SELECT status FROM candidaturas"
        cursor.execute(query)
        data = cursor.fetchall()

        # Convertir los datos a un DataFrame de pandas
        df = pd.DataFrame(data)

        # Contar candidatos en cada estado
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']

        # Convertir el DataFrame a un diccionario
        result = status_counts.set_index('status')['count'].to_dict()

        # Cerrar la conexión
        cursor.close()
        db.close()

        # Retornar el diccionario como respuesta JSON
        return result

    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.get("/estadisticas/carrera")
async def get_career_count():
    try:
        # Conectar a la base de datos
        db = pymysql.connect(**config)
        cursor = db.cursor()

        # Obtener el total de candidatos
        cursor.execute('SELECT COUNT(*) as total FROM candidatos')
        total_count = cursor.fetchone()['total']

        # Obtener el conteo de cada carrera
        cursor.execute('SELECT carrera, COUNT(*) as count FROM candidatos GROUP BY carrera')
        data = cursor.fetchall()

        # Calcular el porcentaje para cada carrera
        if total_count == 0:
            return {"message": "No hay datos disponibles"}

        career_count = {
            re.sub(r'\s+', '_', row['carrera']).lower(): round((row['count'] / total_count) * 100, 2)
            for row in data
        }

        return career_count

    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")

    finally:
        cursor.close()
        db.close()


@app.get("/estadisticas/notas")
async def get_average_grades():
    try:
        # Conectar a la base de datos
        db = pymysql.connect(**config)
        cursor = db.cursor()

        # Ejecutar la consulta para obtener el promedio de notas por carrera
        cursor.execute('SELECT carrera, AVG(nota_media) as average FROM candidatos GROUP BY carrera')
        
        # Obtener los resultados
        average_grades = {}
        for row in cursor.fetchall():
            carrera = row['carrera']
            average = row['average']
            
            # Formatear el nombre de la carrera
            formatted_carrera = re.sub(r'\s+', '_', carrera).lower()
            
            # Redondear la nota media a 2 decimales si no es None
            average_grades[formatted_carrera] = round(average, 2) if average is not None else None
        
        return average_grades

    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")

    finally:
        cursor.close()
        db.close()



@app.get("/estadisticas/ingles")
async def get_english_level_count():
    try:
        # Conectar a la base de datos
        db = pymysql.connect(**config)
        cursor = db.cursor()

        # Obtener el total de candidatos
        cursor.execute('SELECT COUNT(*) as total FROM candidatos')
        total_count = cursor.fetchone()['total']

        # Obtener el conteo de cada nivel de inglés
        cursor.execute('SELECT nivel_ingles, COUNT(*) as count FROM candidatos GROUP BY nivel_ingles')
        data = cursor.fetchall()

        # Calcular el porcentaje para cada nivel de inglés
        if total_count == 0:
            return {"message": "No hay datos disponibles"}

        english_level_count = {
            row['nivel_ingles']: round((row['count'] / total_count) * 100, 2)
            for row in data
        }
        return english_level_count

    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")

    finally:
        cursor.close()
        db.close()




@app.get("/estadisticas/edad")
async def get_age_distribution():
    try:
        # Conectar a la base de datos
        db = pymysql.connect(**config)
        cursor = db.cursor(pymysql.cursors.DictCursor)

        # Obtener el total de candidatos
        cursor.execute('SELECT COUNT(*) as total FROM candidatos')
        total_count = cursor.fetchone()['total']

        # Consulta SQL para agrupar edades en rangos de 5 años y ordenarlos
        query = """
        SELECT 
            CONCAT(FLOOR(edad / 5) * 5, '-', FLOOR(edad / 5) * 5 + 4) AS age_range,
            COUNT(*) as count 
        FROM 
            candidatos 
        GROUP BY 
            age_range
        ORDER BY
            FLOOR(edad / 5) * 5
        """
        cursor.execute(query)
        data = cursor.fetchall()

        # Calcular el porcentaje para cada rango de edad
        if total_count == 0:
            return {"message": "No hay datos disponibles"}

        df = pd.DataFrame(data)
        df['percentage'] = (df['count'] / total_count) * 100
        df['percentage'] = df['percentage'].round(2)  # Round percentages to 2 decimal places

        # Convertir el DataFrame a un diccionario
        result = df.set_index('age_range')['percentage'].to_dict()

        # Cerrar la conexión
        cursor.close()
        db.close()

        return result

    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")




@app.get("/predict")
async def predict(id_candidatura: int):
    # Conectar a la base de datos
    db = pymysql.connect(**config)
    cursor = db.cursor()
    
    try:
        # Obtener las notas de competencias de la candidatura
        cursor.execute("""
            SELECT nombre_competencia, nota
            FROM competencias
            WHERE id_candidatura = %s
        """, (id_candidatura,))
        
        competencias = cursor.fetchall()

        if not competencias:
            raise HTTPException(status_code=404, detail="No se encontraron competencias para la candidatura proporcionada.")

        # Crear un diccionario para las competencias
        competencias_dict = {comp['nombre_competencia']: comp['nota'] for comp in competencias}

        # Verificar que todas las competencias necesarias están presentes
        required_competencies = ['Profesionalidad', 'Dominio', 'Resiliencia', 'HabilidadesSociales', 'Liderazgo', 'Colaboracion', 'Compromiso', 'Iniciativa']
        for comp in required_competencies:
            if comp not in competencias_dict:
                competencias_dict[comp] = 0  # Asignar 0 si la competencia no está presente

        # Crear un DataFrame con las competencias en el orden correcto
        input_data = pd.DataFrame([[
            competencias_dict['Profesionalidad'],
            competencias_dict['Dominio'],
            competencias_dict['Resiliencia'],
            competencias_dict['HabilidadesSociales'],
            competencias_dict['Liderazgo'],
            competencias_dict['Colaboracion'],
            competencias_dict['Compromiso'],
            competencias_dict['Iniciativa']
        ]], columns=[
            'Profesionalidad', 'Dominio', 'Resiliencia', 'HabilidadesSociales', 'Liderazgo', 'Colaboracion', 'Compromiso', 'Iniciativa'
        ])

        # Realizar la predicción
        prediction = model.predict(input_data)
        result = 'Admitido' if prediction == 1 else 'Rechazado'

        return {"prediction": result}

    finally:
        cursor.close()
        db.close()


@app.post("/retrain")
def retrain():
    try:
        # Conectar a la base de datos
        db = pymysql.connect(**config)
        cursor = db.cursor()

        # Obtener todas las competencias y candidaturas
        cursor.execute("SELECT * FROM competencias")
        competencias = cursor.fetchall()

        cursor.execute("""
            SELECT * FROM candidaturas
            WHERE status IN ('Entrevista2', 'Ofertado', 'Entrevista1', 'CentroEvaluación', 'Descartado')
        """)
        candidaturas = cursor.fetchall()

        if not competencias or not candidaturas:
            raise HTTPException(status_code=404, detail="No se encontraron suficientes datos para reentrenar el modelo.")

        # Crear un diccionario para las competencias por candidatura
        competencias_dict = {}
        for comp in competencias:
            if comp['id_candidatura'] not in competencias_dict:
                competencias_dict[comp['id_candidatura']] = {}
            competencias_dict[comp['id_candidatura']][comp['nombre_competencia']] = comp['nota']

        # Crear listas para los datos de entrada (X) y las etiquetas (y)
        X = []
        y = []

        required_competencies = ['Profesionalidad', 'Dominio', 'Resiliencia', 'HabilidadesSociales', 'Liderazgo', 'Colaboracion', 'Compromiso', 'Iniciativa']
        for cand in candidaturas:
            if cand['id_candidatura'] in competencias_dict:
                comp_dict = competencias_dict[cand['id_candidatura']]
                # Verificar que todas las competencias necesarias están presentes
                if all(comp in comp_dict for comp in required_competencies):
                    X.append([comp_dict[comp] for comp in required_competencies])
                    y.append(1 if cand['status'] in ["Entrevista2", "Ofertado", "Entrevista1", "CentroEvaluación"] else 0)

        if not X or not y:
            raise HTTPException(status_code=400, detail="No se encontraron suficientes datos válidos para reentrenar el modelo.")

        # Convertir a DataFrame
        X = pd.DataFrame(X, columns=required_competencies)
        y = pd.Series(y)

        # Entrenar el modelo
        new_model = RandomForestClassifier()
        new_model.fit(X, y)

        # Guardar el nuevo modelo localmente
        local_model_path = 'models/model_web.pkl'
        joblib.dump(new_model, local_model_path)

        # Subir el modelo al bucket S3
        try:
            s3_client.upload_file(local_model_path, s3_bucket_name, s3_model_key)
            return {
                "detail": "Modelo reentrenado y actualizado con los datos actuales.",
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al subir el modelo a S3: {e}")

    finally:
        # Asegurarse de cerrar el cursor y la conexión a la base de datos
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'db' in locals() and db:
            db.close()



# Código para ejecutar el servidor Uvicorn si el script se ejecuta directamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_empleados:app", host="0.0.0.0", port=8000)




