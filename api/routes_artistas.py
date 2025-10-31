# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException, Query, Body, status
from typing import List, Optional, Dict, Any
from . import models  # Importa el módulo models.py que contiene la lógica de base de datos
from pydantic import BaseModel, Field # Importa utilidades de Pydantic para validación y definición de schemas

# --- Router ---
# Se crea una instancia de APIRouter para agrupar las rutas relacionadas con artistas.
# Esto permite organizar la API de forma modular.
router = APIRouter(
    prefix="/api/artistas",  # Define el prefijo base para todas las rutas en este archivo. Ej: "/" se convierte en "/api/artistas/".
    tags=["Artistas"],       # Agrupa estas rutas bajo la etiqueta "Artistas" en la documentación interactiva (Swagger UI / ReDoc).
    responses={404: {"description": "Recurso no encontrado"}} # Define una respuesta estándar para errores 404 en todas las rutas de este router.
)

# --- Schemas Pydantic (Modelos de Datos y Validación) ---
# Los schemas Pydantic definen la estructura esperada de los datos de entrada (request)
# y salida (response), proporcionando validación automática y documentación.

# Schema para la estructura de la respuesta de paginación.
class Pagination(BaseModel):
    page: int = Field(..., description="Número de la página actual")
    limit: int = Field(..., description="Número de registros por página")
    total_records: int = Field(..., description="Número total de registros disponibles")
    total_pages: int = Field(..., description="Número total de páginas")
    has_next: bool = Field(..., description="Indica si existe una página siguiente")
    has_prev: bool = Field(..., description="Indica si existe una página anterior")

# Schema base para definir los datos esperados al crear o actualizar un artista.
# Utiliza Field para añadir metadatos y validaciones (ej. longitud mínima/máxima).
class ArtistaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre completo del artista")
    genero: str = Field(..., max_length=50, description="Género musical principal del artista")
    pais: str = Field(..., max_length=50, description="País de origen del artista")
    popularidad: Optional[int] = Field(None, ge=0, le=100, description="Nivel de popularidad estimado (0-100), opcional")
    imagen_url: Optional[str] = Field(None, max_length=500, description="URL de una imagen representativa del artista, opcional")
    biografia: Optional[str] = Field(None, description="Texto descriptivo o biografía breve del artista, opcional")

    # Configuración de Pydantic para añadir un ejemplo en la documentación de la API (Swagger UI).
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nombre": "Nuevo Artista Ejemplo",
                    "genero": "Rock Alternativo",
                    "pais": "México",
                    "popularidad": 80,
                    "imagen_url": "http://ejemplo.com/imagen_artista.jpg",
                    "biografia": "Descripción detallada del nuevo artista y su trayectoria."
                }
            ]
        }
    }

# Schema para la respuesta al solicitar los datos de un artista específico.
# Hereda de ArtistaBase y añade campos adicionales (id, total_conciertos) que no se envían al crear/actualizar.
class ArtistaResponse(ArtistaBase):
    id: int = Field(..., description="Identificador único del artista")
    total_conciertos: Optional[int] = Field(None, description="Número total de conciertos asociados a este artista")

# Schema para la respuesta al solicitar la lista completa de artistas (GET /).
# Define la estructura que incluye una lista de artistas ('data') y los metadatos de paginación ('pagination').
class ArtistaListResponse(BaseModel):
    success: bool = Field(True, description="Indica si la solicitud fue exitosa")
    data: List[ArtistaResponse] = Field(..., description="Lista de artistas encontrados")
    pagination: Pagination = Field(..., description="Metadatos de la paginación")

# Schema para la respuesta exitosa al crear un nuevo artista (POST /).
class ArtistaCreateResponse(BaseModel):
    success: bool = Field(True, description="Indica si la creación fue exitosa")
    message: str = Field("Artista creado exitosamente", description="Mensaje de confirmación")
    data: Dict[str, int] = Field(..., description="Diccionario que contiene el ID del nuevo artista creado, ej: {'id': 123}")

# Schema para la respuesta exitosa al actualizar un artista (PUT /{artista_id}).
class ArtistaUpdateResponse(BaseModel):
    success: bool = Field(True, description="Indica si la actualización fue exitosa")
    message: str = Field("Artista actualizado exitosamente", description="Mensaje de confirmación")


# --- Endpoints (Definiciones de Rutas API) ---
# Cada función decorada con @router define un endpoint de la API.

@router.get("/", 
            response_model=ArtistaListResponse, 
            summary="Obtener lista paginada de artistas",
            description="Recupera una lista de artistas con paginación, ordenados por popularidad descendente.")
def get_artistas(
    page: int = Query(1, ge=1, description="Número de página a solicitar (mínimo 1)"),
    limit: int = Query(10, ge=1, le=100, description="Número de artistas por página (entre 1 y 100)")
):
    """
    Endpoint para obtener una lista paginada de todos los artistas.
    Utiliza los parámetros 'page' y 'limit' especificados en la URL (query parameters)
    para controlar la paginación de los resultados.
    """
    # Llama a la función correspondiente en 'models.py' para interactuar con la base de datos.
    artistas, pagination_data = models.get_all_artistas_from_db(page, limit)

    # FastAPI utiliza 'response_model' para validar y formatear la respuesta saliente.
    # Se devuelve un diccionario que coincide con la estructura de 'ArtistaListResponse'.
    return {"data": artistas, "pagination": pagination_data}

@router.get("/{artista_id}", 
            response_model=ArtistaResponse, 
            summary="Obtener un artista por ID",
            description="Recupera los detalles de un artista específico mediante su ID numérico único.")
def get_artista(artista_id: int):
    """
    Endpoint para obtener los detalles de un artista específico.
    El ID del artista se extrae de la ruta URL (path parameter).
    Incluye información adicional como el número total de conciertos asociados.
    """
    # Llama a la función en 'models.py' para buscar el artista en la base de datos.
    artista = models.get_artista_by_id_from_db(artista_id)
    if artista is None:
        # Si la función de 'models' devuelve None, significa que el artista no fue encontrado.
        # Se lanza una excepción HTTPException que FastAPI convierte en una respuesta HTTP 404.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Artista con ID {artista_id} no encontrado")
    
    # Si se encuentra, FastAPI usa 'response_model' para devolver los datos del artista.
    return artista

@router.post("/", 
             status_code=status.HTTP_201_CREATED, 
             response_model=ArtistaCreateResponse, 
             summary="Crear un nuevo artista",
             description="Registra un nuevo artista en la base de datos.")
def create_artista(artista: ArtistaBase = Body(..., description="Datos del nuevo artista a crear según el schema ArtistaBase")):
    """
    Endpoint para crear un nuevo artista.
    Recibe los datos del artista en el cuerpo (body) de la solicitud HTTP POST.
    FastAPI valida automáticamente los datos recibidos contra el schema 'ArtistaBase'.
    Si la validación falla, FastAPI devuelve un error 422 automáticamente.
    """
    # Convierte el modelo Pydantic 'artista' recibido a un diccionario estándar de Python.
    # Este diccionario se pasará a la función de base de datos.
    artista_data = artista.model_dump()
    
    # Llama a la función en 'models.py' para insertar el nuevo artista en la base de datos.
    # Si 'models.py' (corregido) lanza un error de BD, FastAPI lo atrapará 
    # y devolverá una respuesta 500 automáticamente.
    nuevo_id = models.create_artista_in_db(artista_data)
    
    # Se elimina el bloque 'if nuevo_id is None: raise HTTPException(500)'
    # para seguir la recomendación del profesor de no lanzar errores 500 manualmente.
                            
    # Si la creación es exitosa, se devuelve la respuesta definida en 'ArtistaCreateResponse'.
    return {"data": {"id": nuevo_id}}

@router.put("/{artista_id}", 
            response_model=ArtistaUpdateResponse, 
            summary="Actualizar un artista existente",
            description="Actualiza la información de un artista existente identificado por su ID.")
def update_artista(artista_id: int, artista: ArtistaBase = Body(..., description="Nuevos datos para actualizar el artista")):
    """
    Endpoint para actualizar un artista existente.
    Recibe el ID del artista en la ruta URL y los nuevos datos en el cuerpo (body) de la solicitud PUT.
    Solo los campos presentes en el body serán actualizados en la base de datos.
    Los datos del body son validados automáticamente por FastAPI usando el schema 'ArtistaBase'.
    """
    # Paso 1: Verificar si el artista que se intenta actualizar existe.
    artista_existente = models.get_artista_by_id_from_db(artista_id)
    if artista_existente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Artista con ID {artista_id} no encontrado para actualizar")

    # Paso 2: Convertir el modelo Pydantic a diccionario.
    # 'exclude_unset=True' asegura que solo se incluyan los campos que el cliente envió explícitamente.
    # Esto permite actualizaciones parciales (PATCH-like behavior con PUT).
    artista_data = artista.model_dump(exclude_unset=True) 

    if not artista_data:
         # Si el cliente envió un body vacío o sin campos actualizables, se devuelve un error 400.
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se proporcionaron campos válidos para actualizar")

    # Paso 3: Llamar a la función en 'models.py' para ejecutar la actualización en la BD.
    # Si 'models.py' (corregido) lanza un error de BD, 
    # FastAPI lo atrapará y devolverá un 500 automáticamente.
    models.update_artista_in_db(artista_id, artista_data)
    
    # Se elimina el bloque 'if not success: raise HTTPException(500)'
    # para seguir la recomendación del profesor de no lanzar errores 500 manualmente.
                            
    # Si la actualización es exitosa, se devuelve la respuesta definida en 'ArtistaUpdateResponse'.
    return {"message": "Artista actualizado exitosamente"}