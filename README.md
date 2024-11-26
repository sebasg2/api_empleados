# IT Incident Priority Checker

## Important Note

The AWS database supporting this application is currently down, which has rendered the API non-functional. All features described below depend on the operational state of the database.

---

## Database Creation and Machine Learning Integration

### Database Details

#### Tables

1. **Employees**:
   - **Purpose**: Stores employee data, including roles, login states, and activity metrics.
   - **Key Fields**:
     - `id_empleado`: Unique employee ID.
     - `nombre_empleado`: Employee's name.
     - `rol`: Role in the system.
     - `is_logged`: Current login state.
     - `last_logged_date`: Timestamp of last login.

2. **Candidates**:
   - **Purpose**: Records detailed candidate information such as academic career and CV.
   - **Key Fields**:
     - `id_candidato`: Unique candidate ID.
     - `nombre_candidato`: Candidate's name.
     - `carrera`: Academic career.
     - `nivel_ingles`: English proficiency level.
     - `nota_media`: Average grade.

3. **Applications**:
   - **Purpose**: Tracks job applications, including statuses and timestamps.
   - **Key Fields**:
     - `id_candidatura`: Unique application ID.
     - `id_candidato`: Associated candidate ID.
     - `id_empleado`: Managing employee ID.
     - `status`: Application status.

4. **Competencies**:
   - **Purpose**: Evaluates competencies related to applications and assigns scores.
   - **Key Fields**:
     - `id_competencia`: Unique competency ID.
     - `id_candidatura`: Associated application ID.
     - `nombre_competencia`: Name of the competency.
     - `nota`: Score obtained.

---

### Machine Learning Integration

#### Workflow

1. **Data Preparation**:
   - Data is loaded, cleaned, and preprocessed for training.
   - Target labels are generated based on application outcomes.

2. **Model Training**:
   - A Random Forest Classifier is optimized using hyperparameter tuning.
   - Data is split into training and testing sets to ensure robust evaluation.

3. **Evaluation**:
   - The model is evaluated using metrics such as accuracy, precision, recall, and F1 score.

4. **Deployment**:
   - The trained model is saved locally or uploaded to an S3 bucket for dynamic predictions.

---

### Key Endpoints

1. **GET /all_empleados**:
   - **Purpose**: Lists employees with filters and pagination.
   - **Details**: Retrieves employee data, supporting dynamic filtering, sorting, and pagination.

2. **DELETE /delete_empleado**:
   - **Purpose**: Deletes an employee and reassigns their applications.
   - **Details**: Updates applications to assign them to a default employee before deletion.

3. **PUT /update_empleado**:
   - **Purpose**: Updates employee details dynamically.
   - **Details**: Updates only provided fields, keeping others unchanged.

4. **GET /candidaturas_por_empleado**:
   - **Purpose**: Fetches application stats for a specific employee.
   - **Details**: Groups and counts applications by status for the specified employee.

5. **GET /predict**:
   - **Purpose**: Predicts application outcomes using machine learning.
   - **Details**: Utilizes a pre-trained model to predict if a candidate is likely to be admitted or rejected.

---

# Verificador de Prioridad de Incidentes de TI

## Nota Importante

La base de datos en AWS que soporta esta aplicación actualmente no está disponible, lo que ha dejado la API inoperativa. Todas las características descritas a continuación dependen del estado operativo de la base de datos.

---

## Creación de la Base de Datos e Integración de Machine Learning

### Detalles de la Base de Datos

#### Tablas

1. **Empleados**:
   - **Propósito**: Almacena datos de empleados, incluidos roles, estados de inicio de sesión y métricas de actividad.
   - **Campos Clave**:
     - `id_empleado`: ID único del empleado.
     - `nombre_empleado`: Nombre del empleado.
     - `rol`: Rol en el sistema.
     - `is_logged`: Estado actual de inicio de sesión.
     - `last_logged_date`: Fecha y hora del último inicio de sesión.

2. **Candidatos**:
   - **Propósito**: Registra información detallada de candidatos, como carrera académica y CV.
   - **Campos Clave**:
     - `id_candidato`: ID único del candidato.
     - `nombre_candidato`: Nombre del candidato.
     - `carrera`: Carrera académica.
     - `nivel_ingles`: Nivel de inglés.
     - `nota_media`: Nota media.

3. **Candidaturas**:
   - **Propósito**: Rastrea candidaturas laborales, incluyendo estados y marcas de tiempo.
   - **Campos Clave**:
     - `id_candidatura`: ID único de la candidatura.
     - `id_candidato`: ID del candidato asociado.
     - `id_empleado`: ID del empleado que gestionó la candidatura.
     - `status`: Estado de la candidatura.

4. **Competencias**:
   - **Propósito**: Evalúa competencias relacionadas con candidaturas y asigna calificaciones.
   - **Campos Clave**:
     - `id_competencia`: ID único de la competencia.
     - `id_candidatura`: ID de la candidatura asociada.
     - `nombre_competencia`: Nombre de la competencia.
     - `nota`: Nota obtenida.

---

### Integración de Machine Learning

#### Flujo de Trabajo

1. **Preparación de Datos**:
   - Los datos se cargan, limpian y procesan para el entrenamiento.
   - Se generan etiquetas objetivo basadas en los resultados de las candidaturas.

2. **Entrenamiento del Modelo**:
   - Se optimiza un clasificador Random Forest mediante ajuste de hiperparámetros.
   - Los datos se dividen en conjuntos de entrenamiento y prueba para garantizar una evaluación robusta.

3. **Evaluación**:
   - El modelo se evalúa utilizando métricas como precisión, recuperación y puntuación F1.

4. **Despliegue**:
   - El modelo entrenado se guarda localmente o se sube a un bucket S3 para predicciones dinámicas.

---

### Endpoints Clave

1. **GET /all_empleados**:
   - **Propósito**: Lista empleados con filtros y paginación.
   - **Detalles**: Recupera datos de empleados con soporte para filtrado, ordenación y paginación dinámicos.

2. **DELETE /delete_empleado**:
   - **Propósito**: Elimina un empleado y reasigna sus candidaturas.
   - **Detalles**: Actualiza las candidaturas para asignarlas a un empleado predeterminado antes de la eliminación.

3. **PUT /update_empleado**:
   - **Propósito**: Actualiza detalles de empleados dinámicamente.
   - **Detalles**: Solo actualiza los campos proporcionados, manteniendo los demás sin cambios.

4. **GET /candidaturas_por_empleado**:
   - **Propósito**: Obtiene estadísticas de candidaturas para un empleado específico.
   - **Detalles**: Agrupa y cuenta las candidaturas por estado para el empleado especificado.

5. **GET /predict**:
   - **Propósito**: Predice resultados de candidaturas utilizando aprendizaje automático.
   - **Detalles**: Utiliza un modelo preentrenado para predecir si un candidato será admitido o rechazado.
