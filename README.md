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

# 🎨 Frontend 

Interfaz web de la plataforma para la gestión de conciertos y artistas.  
Desarrollada con **HTML, CSS, JavaScript y Bootstrap 5.3**, conecta con el backend FastAPI para mostrar información dinámica, mapas y estadísticas.

---

## 🧩 Herramientas utilizadas

- ⚙️ **Bootstrap 5.3** – Diseño responsivo.
- 📊 **Chart.js** – Gráficas de popularidad y rentabilidad.
- 🗺️ **Leaflet.js** – Mapa interactivo con marcadores de conciertos.
- 💾 **LocalStorage** – Guarda la preferencia del modo oscuro.
- 🌐 **API REST (FastAPI)** – Fuente de datos para artistas y estadísticas.

---

## 📁 Estructura de archivos

frontend/
├── index.html → Página principal con secciones y componentes
├── js/api.js → Conexión con API, modo oscuro y render dinámico
├── img/ → Imágenes de artistas y recursos visuales
└── registro.html → Formulario de registro enlazado desde promociones

---

## 🖥️ Funcionalidad

- **Navbar:** navegación principal con switch para modo oscuro.  
- **Hero:** portada con imagen de fondo y llamada a la acción.  
- **Artistas destacados:** tarjetas con enlaces externos a cada artista.  
- **Dashboard:** consumo de la API para listar artistas y mostrar estadísticas.  
- **Mapa de conciertos:** creado con Leaflet, muestra ubicaciones.  
- **Promociones:** última sección con enlace al registro.

---

## 🌗 Modo oscuro

- Implementado con el atributo `data-bs-theme` de Bootstrap.  
- Se activa mediante el switch con id `modoOscuro`.  
- Guarda la preferencia en `localStorage` para mantener el modo tras recargar.  
- Adapta colores, fondos y botones.

---

## 🔌 Integración con la API

El frontend consume los siguientes endpoints del backend:

- `GET /api/artistas` → carga paginada de artistas para el selector.  
- `GET /api/estadisticas` → obtiene datos para las gráficas de popularidad y rentabilidad.  
 
---
