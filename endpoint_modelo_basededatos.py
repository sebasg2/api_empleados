
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
    allow_origins=[
        "http://localhost:5173",
        "https://dt-empieza-por-educar-docker.onrender.com",
        "https://empieza-por-educar.onrender.com"
    ], # Allow only the specific origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

#Conectar con S3

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)
s3_bucket_name = 'modelosexe'
s3_model_key = 'model_web.pkl'


@app.get("/predict_bucket")
async def predict_bucket(id_candidatura: int):
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

        # Descargar y cargar el modelo desde S3
        model_path = 'models/model_web1.pkl'  # Ruta temporal en el sistema de archivos local
        s3_client.download_file(s3_bucket_name, 'model_web1.pkl', model_path)

        with open(model_path, 'rb') as f:
            model = joblib.load(f)

        # Realizar la predicción
        prediction = model.predict(input_data)
        result = 'Admitido' if prediction == 1 else 'Rechazado'

        return {"prediction": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

    finally:
        cursor.close()
        db.close()




# Código para ejecutar el servidor Uvicorn si el script se ejecuta directamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_empleados:app", host="0.0.0.0", port=8000)