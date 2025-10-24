# --- Importaciones Principales ---
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn  # Importamos uvicorn para poder correr el servidor directamente

# --- Importación de Routers ---
# Importamos los módulos que contienen nuestros APIRouters
from . import routes_artistas
from . import routes_conciertos
from . import routes_stats # ¡IMPORTANTE! Asegúrate de que esta línea esté descomentada

# --- Creación de la Aplicación FastAPI ---
app = FastAPI(
    title="API de Plataforma de Conciertos",
    description="API para gestionar artistas y conciertos para el proyecto de Desarrollo Web.",
    version="1.0.0",
)

# --- Configuración de CORS ---
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:5501",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoint de Salud (Health Check) ---
@app.get("/health", tags=["Health Check"])
def health_check():
    """
    Endpoint simple para verificar que la API está
    funcionando correctamente.
    """
    return {"status": "ok", "message": "API de Conciertos funcionando."}

# --- Conexión de Rutas (Routers) ---
# Incluimos los routers en la aplicación principal.
app.include_router(routes_artistas.router)
app.include_router(routes_conciertos.router)
app.include_router(routes_stats.router) # ¡IMPORTANTE! Asegúrate de que esta línea esté descomentada


# --- Punto de Entrada para Correr el Servidor ---
if __name__ == "__main__":
    print("Iniciando servidor FastAPI en http://127.0.0.1:8000")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)