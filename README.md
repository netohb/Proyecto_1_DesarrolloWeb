# Proyecto_1_DesarrolloWeb

Este repositorio es para trabajar en el primer proyecto integrador de la materia de Introducción al Desarrollo Web, Otoño 2025 (ITAM).

## 👥 Integrantes

* Ernesto Hernández Bernal
* Emiliano Bobadilla Franco
* Brenda Montaño Oseguera
* Axalli Lopez Chavarria

---

## 📖 Descripción del Proyecto

Este proyecto es una aplicación web *full-stack* diseñada para una plataforma de gestión de conciertos. Su objetivo es permitir a los "managers" planificar y visualizar eventos, así como analizar estadísticas clave de rentabilidad y asistencia.

La aplicación consta de un **Frontend** (HTML/CSS/JS) que consume un **Backend** (API RESTful) construido con Python.

---

## 🖥️ Backend (API)

El backend es una API RESTful construida con **FastAPI**, un framework moderno de Python que proporciona alta velocidad y generación automática de documentación.

Utiliza **SQLite3** como motor de base de datos para almacenar y gestionar de forma persistente la información de artistas y conciertos.

### Estructura de Archivos y Funcionalidad

El código del backend está organizado dentro de la carpeta `/api` siguiendo un patrón modular para separar responsabilidades:

* **`api/app.py` (El "Director")**
    * Es el punto de entrada principal de la aplicación FastAPI.
    * Define la configuración de **CORS** (Cross-Origin Resource Sharing) para permitir que el frontend se comunique con la API.
    * Crea la instancia principal de `FastAPI` e **incluye** los *routers* (mensajeros) de artistas, conciertos y estadísticas.
    * Define el endpoint de salud (`/health`).

* **`api/models.py` (El "Cerebro de la BD")**
    * Contiene **toda la lógica de negocio y las interacciones con la base de datos**.
    * Incluye la función `get_db_connection()` que habilita las `FOREIGN KEY` de SQLite.
    * Define todas las funciones CRUD (Crear, Leer, Actualizar) que ejecutan consultas SQL (ej. `get_artista_by_id_from_db`, `create_concierto_in_db`, etc.).
    * Contiene la lógica de agregación compleja para el dashboard (ej. `get_stats_from_db()`).

* **`api/routes_artistas.py` (El "mensajero" de Artistas)**
    * Define un `APIRouter` (un mini-servidor) que maneja todas las URLs que comienzan con `/api/artistas`.
    * Define los *schemas* **Pydantic** (`ArtistaBase`, `ArtistaResponse`) que validan los datos de entrada y formatean los datos de salida.
    * Maneja las peticiones HTTP (`GET`, `POST`, `PUT`), llama a las funciones correspondientes en `models.py` y maneja los errores HTTP (como 404).

* **`api/routes_conciertos.py` (El "mensajero" de Conciertos)**
    * Similar al de artistas, define el `APIRouter` para todas las URLs `/api/conciertos`.
    * Define los *schemas* Pydantic para conciertos (`ConciertoBase`, `ConciertoResponse`), incluyendo validadores personalizados (como el de la fecha ISO 8601).
    * Llama a `models.py` para la lógica de conciertos.

* **`api/routes_stats.py` (El "mensajero" de Estadísticas)**
    * Define el `APIRouter` para la URL `/api/estadisticas`.
    * Define los *schemas* Pydantic para la compleja respuesta del dashboard (ej. `KPIsFinancieros`, `EstadisticasResponse`).
    * Llama a la función `get_stats_from_db()` de `models.py`.

* **`api/schema.sql` (El "Plano")**
    * Es un script SQL que define la estructura (tablas, columnas, tipos de datos, `FOREIGN KEY`) de nuestra base de datos. No se ejecuta directamente por la API, sino por `init_db.py`.

* **`api/init_db.py` (El "Instalador")**
    * Es un script de utilidad que se corre **una sola vez** localmente.
    * Lee el `schema.sql` para crear las tablas (`init_db()`).
    * Puebla ("siembra" o *seed*) la base de datos con 20 artistas y 38 conciertos de ejemplo (`seed_db()`).

---

## 📚 Documentación de la API

La documentación técnica completa de la API, destinada al equipo de *frontend*, se encuentra en el siguiente archivo. Incluye todos los *endpoints*, parámetros, y ejemplos de JSON:

* **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)**

Para una **prueba interactiva** (Swagger UI), corre el servidor localmente (ver guía de configuración) y visita:
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 🎨 Frontend 

Interfaz web de la plataforma para la gestión de conciertos y artistas.  
Desarrollada con **HTML, CSS, JavaScript y Bootstrap 5.3**, conecta con el backend FastAPI para mostrar información dinámica, mapas y estadísticas.

---

### 🧩 Herramientas utilizadas

- ⚙️ **Bootstrap 5.3** – Diseño responsivo.
- 📊 **Chart.js** – Gráficas de popularidad y rentabilidad.
- 🗺️ **Leaflet.js** – Mapa interactivo con marcadores de conciertos.
- 💾 **LocalStorage** – Guarda la preferencia del modo oscuro.
- 🌐 **API REST (FastAPI)** – Fuente de datos para artistas y estadísticas.

---
## 🎶 Frontend · Página Principal e Interfaz de Artistas

### 🏠 **index.html**
La página principal de **PulsePass**.  
Incluye el encabezado con imagen, la barra de navegación fija y secciones de **artistas destacados**, **estadísticas interactivas**, **mapa de conciertos** y **promociones**.  
Integra el **modo claro/oscuro** persistente mediante `localStorage`, además de elementos animados y diseño *responsive* con **Bootstrap** y **Leaflet**.  
Los enlaces del **navbar** permiten navegar a otras secciones del sitio y mantienen coherencia visual con el resto de las páginas.


### 🎤 **artistas.html**
Muestra dinámicamente **todos los artistas** registrados en la API mediante `fetch`.  
Presenta una **cuadrícula de tarjetas** con imagen, biografía, país y popularidad de cada artista.  
Cada tarjeta tiene **animaciones suaves** y un diseño adaptado al **modo oscuro**.  
Mantiene el mismo estilo visual, esquema de colores y navegación coherente con la página principal de *PulsePass*.

---

## 🎵 **Frontend · Conciertos**

`conciertos.html` muestra un mapa interactivo desarrollado con **Leaflet**, conectado dinámicamente a la API de PulsePass. Permite seleccionar un artista desde un menú desplegable para visualizar sus conciertos sobre el mapa y acceder a información detallada de cada evento.  

Al seleccionar un artista, se muestra su **tarjeta informativa** (foto, biografía, país, popularidad) junto con un mapa que marca la ubicación de cada concierto. Los marcadores incluyen información del evento (nombre, ciudad, fecha y precio) y se acompañan de una lista lateral con estadísticas detalladas: asistencia proyectada y real, costos de producción, ingresos por taquilla, estado y venue.  

---


## 🎯 Frontend · Registro, Login y Términos

registro.html es el formulario de alta con validación Bootstrap, autoguardado de campos y verificación de géneros (debe haber al menos uno marcado). Incluye el enlace a términos y el enlace a login. Tiene un botón de tema claro/oscuro que persiste usando localStorage.

login.html permite autenticarse con correo y contraseña, tiene mostrar/ocultar contraseña y la casilla de recordar correo. Comparte el mismo botón de tema y el mismo almacenamiento de preferencia.

terms.html contiene las secciones de términos y condiciones. Mantiene el mismo estilo y toggle y ofrece un botón para volver al registro.

Enlaces internos añadidos: en index.html los enlaces de navbar y promociones apuntan a registro.html. En registro.html se enlaza a terms.html y a login.html.

---
### 🛡️ Validaciones, errores y eventos del formulario

El registro usa validación nativa de Bootstrap (clase was-validated) y mensajes invalid-feedback en cada campo. Se requiere aceptar términos y marcar al menos un género.  
Al enviar, se manejan respuestas 2xx, 4xx y 5xx de la API; si no hay red se guarda el intento en una cola local para reintentar.

Eventos incluidos que cubren la rúbrica:  
input para autoguardado, beforeunload para guardar al salir, online/offline para mostrar estado de red y visibilitychange para guardar cuando la pestaña vuelve a estar activa. 

---

### 📁 Estructura de archivos

frontend/
├── index.html → Página principal con secciones y componentes
├── registro.html → Formulario de registro enlazado desde navbar y promociones
├── login.html → Inicio de sesión con recordar correo
├── terms.html → Términos y condiciones con toggle de tema
├── js/
│ ├── api.js → (si ya lo usan en index)
│ ├── script.js → Lógica del registro (tema, autoguardado, fetch, cola offline)
│ └── login.js → Lógica del login (recordar correo, fetch)
└── img/ → Imágenes de artistas y recursos visuales

---

### 🖥️ Funcionalidad

- **Navbar:** navegación principal con switch para modo oscuro.  
- **Hero:** portada con imagen de fondo y llamada a la acción.  
- **Artistas destacados:** tarjetas con enlaces externos a cada artista.  
- **Dashboard:** consumo de la API para listar artistas y mostrar estadísticas.  
- **Mapa de conciertos:** creado con Leaflet, muestra ubicaciones.  
- **Promociones:** última sección con enlace al registro.

---

### 🌗 Modo oscuro

- Implementado con el atributo `data-bs-theme` de Bootstrap.  
- Se activa mediante el switch con id `modoOscuro`.  
- Guarda la preferencia en `localStorage` para mantener el modo tras recargar.  
- Adapta colores, fondos y botones.

---

### 🎛️ Persistencia en localStorage 

- `pp-theme`: preferencia de tema claro/oscuro, compartida en todas las páginas.
- `pp-register-form`: autoguardado del formulario de registro en JSON.
- `pp-pending-queue`: cola de envíos de registro cuando no hay conexión.
- `pp-remember-email`: correo recordado en el login.
- `pp-auth-token`: solo en desarrollo si el backend devuelve token.

---

### 🔌 Integración con la API

El frontend consume los siguientes endpoints del backend:

- `GET /api/artistas` → carga paginada de artistas para el selector.  
- `GET /api/estadisticas` → obtiene datos para las gráficas de popularidad y rentabilidad.  
 
---

### Endpoints usados por registro y login

Base de desarrollo: http://127.0.0.1:8000

#### Registro
POST /api/registro  
request (ejemplo para pruebas)
```js
{
  "fullName": "Ana López",
  "email": "ana@example.com",
  "password": "secreta123",
  "role": "manager",
  "company": "Pulse MX",
  "phone": "+52 55 1234 5678",
  "city": "CDMX",
  "genres": ["Pop", "Rock"],
  "terms": true
}
```
response éxito (200/201)
```js
{ "id": 123, "message": "Registro creado" }
```
response error (4xx)
```js
{ "detail": "Mensaje de error" }
```
#### Login
POST /api/login  
request
```js
{ "email": "ana@example.com", "password": "secreta123" }

response éxito (200)

{ "access_token": "<TOKEN>", "token_type": "bearer" }

response error (401/403)

{ "detail": "Credenciales inválidas" }

---

### JSON en el proyecto: qué abarca y cómo se usa

Este proyecto utiliza JSON para comunicar frontend y backend, manejar errores, cachear datos y trabajar sin conexión. A continuación se resume todo lo relacionado con JSON.

#### Requests enviados por el frontend
- Formato de envío: `Content-Type: application/json` y `body` con `JSON.stringify(...)`.

#### Responses leídas por el frontend
- Éxito (2xx):
  
- Error (4xx/5xx): FastAPI devuelve

* Fechas: se envían en ISO 8601 (terminadas en Z). Se parsean con `new Date(...)` y se formatean con `toLocaleDateString()`.

#### Paginación para listados

* Estructura esperada en `GET /api/artistas` y `GET /api/conciertos`:

  ```json
  {
    "items": [ /* ... */ ],
    "pagination": {
      "page": 1,
      "total_pages": 5,
      "has_next": true,
      "has_prev": false
    }
  }
  ```

#### JSON en localStorage

* Claves y propósito:

  * `pp-theme`: preferencia de tema.
  * `pp-register-form`: autoguardado del formulario de registro.

    ```json
    {
      "fullName": "Ana López",
      "email": "ana@example.com",
      "city": "CDMX",
      "genres": ["Pop"]
    }
    ```
  * `pp-pending-queue`: cola de envíos cuando no hay red.

    ```json
    [
      {
        "endpoint": "/api/registro",
        "method": "POST",
        "payload": { "email": "ana@example.com", "fullName": "Ana López", "terms": true },
        "createdAt": "2025-10-30T21:15:00.000Z"
      }
    ]
    ```
  * `pp-remember-email`: correo recordado en login.
  * `pp-auth-token`: solo en desarrollo si la API devuelve token.

