# 🚀 Guía de Configuración del Entorno de Backend

Esta guía detalla los pasos necesarios para configurar el entorno de desarrollo del backend (API con FastAPI) en tu máquina local.

## FASE 1: Montar el Entorno Virtual 📦

```bash
# 1. Crear la carpeta 'venv' (usando Python 3.8 o superior)
python -m venv venv

# 2. Activar el entorno:

#    En Windows (PowerShell):
.\venv\Scripts\Activate.ps1

#    En Windows (CMD):
.\venv\Scripts\activate.bat

#    En Windows (Git Bash):
source venv/Scripts/activate

#    En macOS / Linux:
source venv/bin/activate
```
Con el entorno (venv) activo, instala todas las librerías necesarias:

```bash
# 1. Actualiza pip (el instalador) a la última versión
python -m pip install --upgrade pip

# 2. Instala todas las librerías del proyecto desde el archivo
pip install -r requirements.txt

# verificacion
pip list

# para apagar el entorno usa:
deactivate

#Deberías ver fastapi, uvicorn, pydantic, etc., en la lista.
```

## FASE 2: Montar la API y la Base de Datos ⚙️
Ejecuta el siguiente comando (asegúrate de que tu venv esté activo)
```bash
python api/init_db.py
```
Este comando ejecuta un script que crea el archivo de base de datos (api/data/conciertos.db) y lo llena con datos de ejemplo (artistas y conciertos). Solo necesitas correrlo una vez (o si quieres reiniciar la BD).

Ahora ejecuta para encender el servidor FastAPI usando Uvicorn:
```bash
uvicorn api.app:app --reload
```
El siguiente mensaje debería aparecer:
INFO:     Uvicorn running on [http://127.0.0.1:8000](http://127.0.0.1:8000) (Press CTRL+C to quit)
INFO:     Application startup complete.

Con el servidor corriendo, abre tu navegador web y ve a:
<http://127.0.0.1:8000/docs>

Verás la documentación interactiva (Swagger UI).

Puedes expandir las secciones (Artistas, Conciertos, Estadísticas), hacer clic en "Try it out" y "Execute" para probar cada endpoint directamente desde el navegador.

Cuando quieras apagar la API, simplemente regresa a la terminal donde está corriendo uvicorn y presiona CTRL + C.

## ¿Cómo usar la API?
La forma más fácil de probar la API es usando la documentación automática que genera FastAPI. Con el servidor corriendo localmente, visita:
<http://127.0.0.1:8000/docs>

---

## 🏥 Health Check

Este endpoint sirve para verificar rápidamente si la API está en línea y operativa.

### GET /health

* **Descripción:** Devuelve un mensaje simple indicando que la API está funcionando.
* **Método:** `GET`
* **Path:** `/health`
* **Query Parameters:** Ninguno
* **Request Body:** Ninguno

**Respuesta Exitosa (Código 200 OK):**
```json
{
  "status": "ok",
  "message": "API de Conciertos funcionando."
}
```

# 📡 Documentación de la API - Plataforma de Conciertos (FastAPI)

Esta documentación describe los endpoints disponibles en la API del backend, construida con FastAPI y SQLite.

## URL Base (Local)
```
http://127.0.0.1:8000
```

*(Nota: Usamos el puerto 8000 por defecto de Uvicorn)*

## 📚 Documentación Interactiva (Swagger UI)

Para probar la API de forma interactiva, corre el servidor localmente y visita:
```
http://127.0.0.1:8000/docs
```

---

## 🏥 Health Check

### GET /health

Verifica que la API esté funcionando correctamente.

**Respuesta Exitosa (200 OK):**
```json
{
  "status": "ok",
  "message": "API de Conciertos funcionando."
}
```

---

## 🎤 Endpoints de Artistas (`/api/artistas`)

### GET /api/artistas

Obtiene una lista paginada de artistas, ordenados por popularidad descendente.

**Query Parameters:**

- `page` (int, opcional, default: 1): Número de página a solicitar (mínimo 1).
- `limit` (int, opcional, default: 10): Número de artistas por página (entre 1 y 100).

**Ejemplo:** `GET /api/artistas?page=2&limit=5`

**Respuesta Exitosa (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "nombre": "Artista Ejemplo 1",
      "genero": "Pop",
      "pais": "México",
      "popularidad": 85,
      "imagen_url": "https://...",
      "biografia": "...",
      "id": 11,
      "total_conciertos": 2 
    } 
  ],
  "pagination": {
    "page": 2,
    "limit": 5,
    "total_records": 20,
    "total_pages": 4,
    "has_next": true,
    "has_prev": true
  }
}
```

---

### GET /api/artistas/{artista_id}

Obtiene los detalles de un artista específico por su ID numérico.

**Ejemplo:** `GET /api/artistas/1`

**Respuesta Exitosa (200 OK):**
```json
{
  "nombre": "Taylor Swift",
  "genero": "Pop",
  "pais": "Estados Unidos",
  "popularidad": 99,
  "imagen_url": "https://...",
  "biografia": "...",
  "id": 1,
  "total_conciertos": 4
}
```

**Respuesta de Error (404 Not Found):**
```json
{
  "detail": "Artista con ID 99 no encontrado"
}
```

---

### POST /api/artistas

Crea un nuevo artista en la base de datos.

**Request Body (JSON):** (Campos requeridos: `nombre`, `genero`, `pais`)
```json
{
  "nombre": "Nuevo Artista",
  "genero": "Indie Rock",
  "pais": "Argentina",
  "popularidad": 60,
  "imagen_url": "https://...",
  "biografia": "Biografía opcional..."
}
```

**Respuesta Exitosa (201 Created):**
```json
{
  "success": true,
  "message": "Artista creado exitosamente",
  "data": {
    "id": 21
  }
}
```

**Respuesta de Error (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "nombre"],
      "msg": "Field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

### PUT /api/artistas/{artista_id}

Actualiza la información de un artista existente. Solo actualiza los campos enviados en el body.

**Ejemplo:** `PUT /api/artistas/21`

**Request Body (JSON):** (Envía solo los campos a modificar)
```json
{
  "popularidad": 65,
  "biografia": "Biografía actualizada."
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "success": true,
  "message": "Artista actualizado exitosamente"
}
```

**Respuesta de Error (404 Not Found):**
```json
{
  "detail": "Artista con ID 21 no encontrado para actualizar"
}
```

**Respuesta de Error (400 Bad Request):**
```json
{
  "detail": "No se proporcionaron campos válidos para actualizar"
}
```

---

## 🎸 Endpoints de Conciertos (`/api/conciertos`)

### GET /api/conciertos

Obtiene una lista paginada de conciertos, ordenada por fecha descendente. Permite filtrar por `artista_id`.

**Query Parameters:**

- `page` (int, opcional, default: 1): Número de página.
- `limit` (int, opcional, default: 10): Conciertos por página.
- `artista_id` (int, opcional): ID del artista para filtrar.

**Ejemplo:** `GET /api/conciertos?page=1&limit=5&artista_id=1`

**Respuesta Exitosa (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "artista_id": 1,
      "nombre_evento": "Eras Tour",
      "venue": "Foro Sol",
      "ciudad": "Ciudad de México",
      "pais": "México",
      "fecha": "2025-08-24T19:30:00Z",
      "status": "Confirmado",
      "asistencia_proyectada": 65000,
      "asistencia_real": 65000,
      "costos_produccion": 2500000,
      "ingresos_taquilla": 4000000,
      "latitud": 19.4049,
      "longitud": -99.0917,
      "id": 2,
      "artista_nombre": "Taylor Swift"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 5,
    "total_records": 4,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

---

### GET /api/conciertos/{concierto_id}

Obtiene los detalles de un concierto específico por su ID.

**Ejemplo:** `GET /api/conciertos/1`

**Respuesta Exitosa (200 OK):**
```json
{
  "artista_id": 1,
  "nombre_evento": "Most Wanted Tour",
  "venue": "Foro Sol",
  "ciudad": "Ciudad de México",
  "pais": "México",
  "fecha": "2025-11-15T20:00:00Z",
  "status": "Confirmado",
  "asistencia_proyectada": 65000,
  "asistencia_real": 62000,
  "costos_produccion": 1000000,
  "ingresos_taquilla": 1500000,
  "latitud": 19.4326,
  "longitud": -99.1332,
  "id": 1,
  "artista_nombre": "Bad Bunny",
  "artista_genero": "Reggaeton",
  "artista_pais": "Puerto Rico"
}
```

**Respuesta de Error (404 Not Found):**
```json
{
  "detail": "Concierto con ID 999 no encontrado"
}
```

---

### POST /api/conciertos

Crea un nuevo concierto en la base de datos.

**Request Body (JSON):** (Campos requeridos: `artista_id`, `nombre_evento`, `venue`, `ciudad`, `pais`, `fecha`)
```json
{
  "artista_id": 2,
  "nombre_evento": "Eras Tour - Fecha Extra",
  "venue": "Estadio Azteca",
  "ciudad": "Ciudad de México",
  "pais": "México",
  "fecha": "2025-08-27T19:30:00Z",
  "status": "Planeado",
  "asistencia_proyectada": 87000,
  "costos_produccion": 3000000,
  "latitud": 19.3029,
  "longitud": -99.1504
}
```

**Respuesta Exitosa (201 Created):**
```json
{
  "success": true,
  "message": "Concierto creado exitosamente",
  "data": {
    "id": 41
  }
}
```

**Respuesta de Error (422 Unprocessable Entity):**
```json
{
  "detail": []
}
```

**Respuesta de Error (500 Internal Server Error):**
```json
{
  "detail": "Error interno del servidor al intentar crear el concierto"
}
```

---

### PUT /api/conciertos/{concierto_id}

Actualiza la información de un concierto existente. Solo actualiza los campos enviados en el body.

**Ejemplo:** `PUT /api/conciertos/4`

**Request Body (JSON):** (Actualizamos el status y los resultados reales)
```json
{
  "status": "Confirmado",
  "asistencia_real": 82000,
  "ingresos_taquilla": 4500000
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "success": true,
  "message": "Concierto actualizado exitosamente"
}
```

**Respuesta de Error (404 Not Found):**
```json
{
  "detail": "Concierto con ID 999 no encontrado para actualizar"
}
```

---

## 📊 Endpoint de Estadísticas (`/api/estadisticas`)

### GET /api/estadisticas

Obtiene un conjunto consolidado de KPIs y datos agregados para el dashboard del manager.

**Respuesta Exitosa (200 OK):**
```json
{
  "success": true,
  "data": {
    "kpis_financieros": {
      "total_ingresos": 28350000.0,
      "total_costos": 18250000.0,
      "ganancia_neta": 10100000.0
    },
    "kpis_asistencia": {
      "total_asistencia_proyectada": 855000,
      "total_asistencia_real": 841500,
      "tasa_cumplimiento_asistencia": 98.42
    },
    "grafica_top_artistas": [
      { "nombre": "Taylor Swift", "popularidad": 99 },
      { "nombre": "Bad Bunny", "popularidad": 98 }
    ],
    "grafica_rentabilidad_ciudad": [
      { "ciudad": "Los Angeles", "ganancia_neta_ciudad": 3500000.0 },
      { "ciudad": "Nueva York", "ganancia_neta_ciudad": 1800000.0 }
    ]
  }
}
```

**Respuesta de Error (500 Internal Server Error):**
```json
{
  "detail": "Error interno del servidor al calcular las estadísticas"
}
```

---

## 💡 Notas para el Equipo Frontend

1. **URL Base:** Recuerden usar `http://127.0.0.1:8000` para las llamadas `fetch` mientras desarrollan localmente.
2. **Documentación Interactiva:** Usen `http://127.0.0.1:8000/docs` para probar los endpoints y ver los schemas exactos.
3. **Paginación:** Los endpoints `GET /api/artistas` y `GET /api/conciertos` devuelven un objeto `pagination`. Usen `page`, `total_pages`, `has_next`, `has_prev` para construir los controles de paginación.
4. **Fechas:** Las fechas se devuelven en formato **ISO 8601 UTC** (`...Z`). Usen `new Date("...")` en JavaScript para parsearlas correctamente y luego `toLocaleDateString()` o librerías como `date-fns` para formatearlas como quieran.
5. **Errores:** Fíjense que las respuestas de error de FastAPI tienen el formato `{"detail": "Mensaje de error"}`. Manejen los códigos `404`, `422`, `400` y `500`.
6. **CORS:** La API está configurada para aceptar peticiones desde `localhost` y `127.0.0.1` en puertos comunes (5500, 5501, 8080). Si usan otro puerto para el frontend, avisen para agregarlo a la lista `origins` en `api/app.py`.
7. **Cache con localStorage:** Consideren guardar las respuestas de `GET /api/artistas` y `GET /api/conciertos` en `localStorage` para mejorar el rendimiento y reducir llamadas innecesarias.

---

## 🔧 Ejemplos de Uso con Fetch (JavaScript)

### Obtener artistas (página 1)
```javascript
async function getArtistas(page = 1) {
  try {
    const response = await fetch(`http://127.0.0.1:8000/api/artistas?page=${page}&limit=10`);
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Error HTTP ${response.status}`);
    }
    const data = await response.json();

    console.log('Artistas:', data.data); 
    console.log('Paginación:', data.pagination); 
    return data;

  } catch (error) {
    console.error('Error al obtener artistas:', error);
    return null;
  }
}
```

### Crear un nuevo concierto
```javascript
async function crearConcierto(conciertoData) {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/conciertos', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(conciertoData)
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || `Error HTTP ${response.status}`);
    }
    
    console.log('Concierto creado con ID:', data.data.id);
    return data;

  } catch (error) {
    console.error('Error al crear concierto:', error);
    return null;
  }
}

// Ejemplo de uso:
const nuevoConcierto = {
  artista_id: 3, 
  nombre_evento: "Sweetener Session",
  venue: "Foro Pegaso",
  ciudad: "Toluca",
  pais: "México",
  fecha: "2026-03-15T20:00:00Z",
  asistencia_proyectada: 30000,
  costos_produccion: 800000
};
// crearConcierto(nuevoConcierto);
```