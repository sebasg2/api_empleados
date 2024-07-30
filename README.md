## Creación de la Base de Datos

### Conexión a la Base de Datos

Se estableció una conexión a un servidor MySQL utilizando credenciales específicas, como el nombre de usuario, la contraseña, el host y el puerto. Esto permitió interactuar con la base de datos y ejecutar consultas SQL para crear la estructura necesaria.

### Creación de la Base de Datos y Tablas

Primero, se creó una base de datos llamada `exe_db` si no existía previamente. Luego, se definieron y crearon las siguientes tablas:

1. **Tabla de Empleados:**
   - **Campos:**
     - `id_empleado` (BIGINT, NOT NULL): Identificador único del empleado.
     - `nombre_empleado` (VARCHAR(255), NOT NULL): Nombre del empleado.
     - `apellidos_empleado` (VARCHAR(255), NOT NULL): Apellidos del empleado.
     - `email_empleado` (VARCHAR(255), NOT NULL): Correo electrónico del empleado.
     - `password` (VARCHAR(255), NOT NULL): Contraseña del empleado.
     - `rol` (VARCHAR(255), NOT NULL): Rol del empleado en el sistema.
     - `is_logged` (BOOLEAN, NOT NULL): Indica si el empleado está actualmente conectado.
     - `last_logged_date` (TIMESTAMP, NOT NULL): Fecha y hora del último inicio de sesión.
     - `num_candidaturas` (INTEGER, NOT NULL): Número total de candidaturas gestionadas por el empleado.
   - **Propósito:** Almacenar la información de los empleados que gestionan el sistema.

2. **Tabla de Candidatos:**
   - **Campos:**
     - `id_candidato` (BIGINT, NOT NULL): Identificador único del candidato.
     - `nombre_candidato` (VARCHAR(255), NOT NULL): Nombre del candidato.
     - `apellidos_candidato` (VARCHAR(255), NOT NULL): Apellidos del candidato.
     - `email_candidato` (VARCHAR(255), NOT NULL): Correo electrónico del candidato.
     - `telefono_candidato` (VARCHAR(255), NOT NULL): Número de teléfono del candidato.
     - `edad` (INTEGER, NOT NULL): Edad del candidato.
     - `carrera` (VARCHAR(255), NOT NULL): Carrera académica del candidato.
     - `nota_media` (FLOAT, NOT NULL): Nota media del candidato.
     - `nivel_ingles` (VARCHAR(50), NOT NULL): Nivel de inglés del candidato.
     - `cv` (TEXT, NOT NULL): Curriculum vitae del candidato.
     - `sexo` (VARCHAR(10), NOT NULL): Sexo del candidato.
   - **Propósito:** Registrar los datos completos de los candidatos que postulan a las posiciones.

3. **Tabla de Candidaturas:**
   - **Campos:**
     - `id_candidatura` (BIGINT, NOT NULL): Identificador único de la candidatura.
     - `id_candidato` (BIGINT, NOT NULL): Identificador del candidato que realiza la candidatura.
     - `id_empleado` (BIGINT, NOT NULL): Identificador del empleado que gestionó la candidatura.
     - `status` (VARCHAR(255), NOT NULL): Estado de la candidatura (e.g., pendiente, aceptada, rechazada).
     - `fecha_registro` (TIMESTAMP, NOT NULL): Fecha y hora en que se registró la candidatura.
   - **Relaciones:**
     - Referencia a la tabla `candidatos` para obtener detalles del candidato.
     - Referencia a la tabla `empleados` para identificar al empleado que gestionó la candidatura.
   - **Propósito:** Seguir el estado y los detalles de cada candidatura.

4. **Tabla de Competencias:**
   - **Campos:**
     - `id_competencia` (BIGINT, NOT NULL): Identificador único de la competencia.
     - `id_candidatura` (BIGINT, NOT NULL): Identificador de la candidatura asociada.
     - `nombre_competencia` (VARCHAR(255), NOT NULL): Nombre de la competencia evaluada.
     - `nota` (INTEGER, NOT NULL): Nota obtenida en la competencia.
   - **Relación:** Referencia a la tabla `candidaturas` para vincular las competencias con la candidatura.
   - **Propósito:** Almacenar las competencias evaluadas y las notas correspondientes.



## Entrenamiento del Modelo

### Preparación de Datos

Se cargaron los datos desde un archivo CSV y se prepararon para el entrenamiento del modelo. Primero, se creó una variable objetivo basada en si el candidato fue admitido o no. Luego, se eliminaron las columnas no necesarias para el análisis y se separaron las características y la variable objetivo en conjuntos de datos distintos.

### Dividir los Datos

Los datos se dividieron en conjuntos de entrenamiento y prueba para evaluar el rendimiento del modelo. El conjunto de entrenamiento se utilizó para ajustar el modelo, mientras que el conjunto de prueba se empleó para verificar la capacidad predictiva del modelo en datos no vistos anteriormente.

### Configuración y Entrenamiento del Modelo

Se configuró un pipeline que incluye un escalador de características y un clasificador de bosque aleatorio. Se realizaron pruebas exhaustivas para encontrar los mejores parámetros del modelo utilizando una búsqueda de hiperparámetros. Esta búsqueda ajustó el número de árboles, la profundidad máxima, el número mínimo de muestras para dividir un nodo y el número mínimo de muestras en una hoja para optimizar el rendimiento del modelo.

### Evaluación y Guardado del Modelo

Después de entrenar el modelo con los mejores parámetros, se evaluó su precisión utilizando el conjunto de prueba. Se calculó el porcentaje de aciertos y se generó un informe de clasificación que detalla el rendimiento del modelo en términos de precisión, recuperación y puntuación F1. Finalmente, el modelo entrenado se guardó en un archivo para su uso futuro.

## Endpoints

### 1. GET /all_empleados

Recupera una lista de empleados con opciones de filtrado, ordenación y paginación.

**Parámetros:**
- `limit` (obligatorio): Número máximo de resultados a devolver (máximo 50)
- `offset` (obligatorio): Número de resultados a omitir para la paginación
- `search` (opcional): Término de búsqueda para filtrar resultados
- `sort_by` (opcional): Campo para ordenar ('num_candidaturas', 'nombre_empleado', 'rol')
- `sort_order` (opcional): Orden de clasificación ('asc' o 'desc')

**Respuesta:** Lista de objetos de empleados

**Detalles:** Este endpoint consulta la tabla 'empleados' en la base de datos RDS. Permite búsqueda flexible en varios campos y ordenación dinámica.

### 2. DELETE /delete_empleado

Elimina un empleado y reasigna sus candidaturas.

**Parámetros:**
- `id_empleado` (obligatorio): ID del empleado a eliminar

**Respuesta:** Mensaje de confirmación

**Detalles:** Primero verifica la existencia del empleado, luego actualiza las candidaturas asociadas asignándolas al empleado con ID 1 (probablemente un empleado por defecto) y finalmente elimina el registro del empleado.

### 3. PUT /update_empleado

Actualiza la información de un empleado.

**Cuerpo:**
- `id_empleado` (obligatorio): ID del empleado a actualizar
- `nombre_empleado` (opcional): Nuevo nombre
- `apellidos_empleado` (opcional): Nuevos apellidos
- `password` (opcional): Nueva contraseña
- `rol` (opcional): Nuevo rol
- `is_logged` (opcional): Nuevo estado de inicio de sesión

**Respuesta:** Mensaje de confirmación

**Detalles:** Utiliza la función COALESCE en la consulta SQL para actualizar solo los campos proporcionados, manteniendo los valores existentes para los campos no especificados.

### 4. GET /candidaturas_por_empleado

Recupera estadísticas de candidaturas para un empleado específico.

**Parámetros:**
- `id_empleado` (obligatorio): ID del empleado

**Respuesta:** Recuento de candidaturas por estado

**Detalles:** Consulta la tabla 'candidaturas' en RDS y agrupa los resultados por estado para el empleado especificado.

### 5. GET /candidaturas_status

Recupera estadísticas generales de candidaturas.

**Respuesta:** Recuento de candidaturas por estado para todos los empleados

**Detalles:** Similar al endpoint anterior, pero para todas las candidaturas en la base de datos.

### 6. GET /estadisticas/carrera

Recupera estadísticas sobre la distribución de carreras de los candidatos.

**Respuesta:** Porcentaje de candidatos por carrera

**Detalles:** Calcula los porcentajes basados en el total de candidatos en la tabla 'candidatos'.

### 7. GET /estadisticas/notas

Recupera las notas promedio por carrera.

**Respuesta:** Nota media para cada carrera

**Detalles:** Calcula el promedio de la columna 'nota_media' agrupando por carrera.

### 8. GET /estadisticas/ingles

Recupera estadísticas sobre la distribución del nivel de inglés de los candidatos.

**Respuesta:** Porcentaje de candidatos por nivel de inglés

**Detalles:** Similar al endpoint de estadísticas de carrera, pero para la columna 'nivel_ingles'.

### 9. GET /estadisticas/edad

Recupera la distribución de edad de los candidatos.

**Respuesta:** Porcentaje de candidatos por rango de edad

**Detalles:** Agrupa las edades en rangos predefinidos y calcula los porcentajes.

### 10. GET /predict

Realiza una predicción de admisión para una candidatura utilizando un modelo de aprendizaje automático optimizado.

**Parámetros:**
- `id_candidatura` (obligatorio): ID de la candidatura a predecir

**Respuesta:** Resultado de la predicción ("Admitido" o "Rechazado")

**Detalles:**
- Este endpoint utiliza un modelo de machine learning entrenado y optimizado, que se basa en datos que han demostrado una alta correlación con los resultados de admisión.
- Recupera las competencias de la candidatura especificada desde la base de datos RDS.
- Preprocesa los datos de la candidatura para que coincidan con el formato esperado por el modelo optimizado.
- Carga el modelo optimizado desde un archivo local ('models/model_web.pkl').
- Utiliza el modelo para realizar la predicción basada en las competencias del candidato.
- Este modelo optimizado puede no reflejar los datos más recientes de la base de datos, pero está diseñado para ofrecer predicciones más precisas basadas en patrones históricos probados.


### 11. POST /retrain

Reentrena el modelo de aprendizaje automático con los datos actuales y lo actualiza en S3.

**Respuesta:** Mensaje de confirmación

**Detalles:** Recopila datos actualizados de las tablas 'competencias' y 'candidaturas', entrena un nuevo modelo Random Forest, lo guarda localmente y luego lo sube a un bucket de S3.

### 12. GET /predict_bucket

Realiza una predicción de admisión para una candidatura utilizando el modelo más reciente entrenado con datos actuales de la base de datos y almacenado en Amazon S3.

**Parámetros:**
- `id_candidatura` (obligatorio): ID de la candidatura a predecir

**Respuesta:** Resultado de la predicción ("Admitido" o "Rechazado")

**Detalles:**
- Este endpoint utiliza un modelo que se actualiza regularmente con los datos más recientes de la base de datos RDS.
- Recupera las competencias de la candidatura especificada desde la base de datos RDS.
- Descarga el modelo más reciente desde el bucket especificado en Amazon S3 ('model_web1.pkl').
- Carga el modelo descargado en memoria.
- Preprocesa los datos de la candidatura para que coincidan con el formato esperado por el modelo.
- Utiliza el modelo cargado para realizar la predicción.
- Este enfoque asegura que las predicciones se basen en los datos más actuales disponibles en la base de datos, reflejando cualquier tendencia o cambio reciente en los patrones de admisión.
- Sin embargo, al usar datos más recientes y potencialmente menos probados, las predicciones podrían ser más sensibles a fluctuaciones a corto plazo en los datos.

**Nota:** La elección entre usar /predict o /predict_bucket dependerá de si se prefiere un modelo más estable y probado (/predict) o uno que refleje los datos y tendencias más recientes (/predict_bucket).
