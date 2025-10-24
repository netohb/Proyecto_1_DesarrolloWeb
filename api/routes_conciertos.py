# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException, Query, Body, status
from typing import List, Optional, Dict, Any
from . import models  # Importa el módulo models.py que contiene la lógica de base de datos
from pydantic import BaseModel, Field, validator # Importa utilidades de Pydantic
import datetime # Para validación de fechas

# --- Router ---
# Se crea una instancia de APIRouter para agrupar las rutas relacionadas con conciertos.
router = APIRouter(
    prefix="/api/conciertos", # Define el prefijo base para todas las rutas en este archivo.
    tags=["Conciertos"],     # Agrupa estas rutas bajo la etiqueta "Conciertos" en la documentación.
    responses={404: {"description": "Recurso no encontrado"}} # Respuesta estándar para 404.
)

# --- Schemas Pydantic (Modelos de Datos y Validación) ---

# Schema importado de routes_artistas para la paginación.
class Pagination(BaseModel):
    page: int
    limit: int
    total_records: int
    total_pages: int
    has_next: bool
    has_prev: bool

# Schema base para definir los datos esperados al crear o actualizar un concierto.
class ConciertoBase(BaseModel):
    artista_id: int = Field(..., description="ID del artista asociado al concierto")
    nombre_evento: str = Field(..., max_length=150, description="Nombre del evento o gira")
    venue: str = Field(..., max_length=100, description="Lugar (recinto) donde se realiza el concierto")
    ciudad: str = Field(..., max_length=100, description="Ciudad donde se realiza el concierto")
    pais: str = Field(..., max_length=100, description="País donde se realiza el concierto")
    fecha: str = Field(..., description="Fecha y hora del concierto en formato ISO 8601 (ej: '2025-11-20T20:00:00Z')")
    status: Optional[str] = Field("Planeado", max_length=50, description="Estado actual del concierto (ej: 'Planeado', 'Confirmado', 'Cancelado')")
    asistencia_proyectada: Optional[int] = Field(None, ge=0, description="Estimación de asistentes (meta)")
    asistencia_real: Optional[int] = Field(None, ge=0, description="Número real de asistentes (resultado)")
    costos_produccion: Optional[int] = Field(None, ge=0, description="Costos totales asociados a la producción del evento")
    ingresos_taquilla: Optional[int] = Field(None, ge=0, description="Ingresos totales generados por la venta de entradas")
    latitud: Optional[float] = Field(None, description="Coordenada de latitud del venue")
    longitud: Optional[float] = Field(None, description="Coordenada de longitud del venue")

    # Validador personalizado para asegurar que el formato de fecha sea correcto (ISO 8601).
    @validator('fecha')
    def validate_fecha_format(cls, v):
        try:
            # Intenta parsear la fecha/hora. Si falla, el formato es incorrecto.
            datetime.datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError("El formato de fecha debe ser ISO 8601 (ej: '2025-11-20T20:00:00Z')")

    # Configuración de Pydantic para añadir un ejemplo en la documentación de la API.
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "artista_id": 1,
                    "nombre_evento": "Gira Mundial 2026",
                    "venue": "Arena Principal",
                    "ciudad": "Ciudad Ejemplo",
                    "pais": "País Ejemplo",
                    "fecha": "2026-05-10T21:00:00Z",
                    "status": "Planeado",
                    "asistencia_proyectada": 15000,
                    "costos_produccion": 500000,
                    "latitud": 19.4326,
                    "longitud": -99.1332
                }
            ]
        }
    }

# Schema para la respuesta al solicitar los datos de un concierto específico.
# Hereda de ConciertoBase y añade campos calculados o de solo lectura (id, detalles del artista).
class ConciertoResponse(ConciertoBase):
    id: int = Field(..., description="Identificador único del concierto")
    # Campos adicionales obtenidos del JOIN en models.py
    artista_nombre: Optional[str] = Field(None, description="Nombre del artista asociado")
    artista_genero: Optional[str] = Field(None, description="Género del artista asociado")
    artista_pais: Optional[str] = Field(None, description="País del artista asociado")

# Schema para la respuesta al solicitar la lista completa de conciertos (GET /).
class ConciertoListResponse(BaseModel):
    success: bool = Field(True, description="Indica si la solicitud fue exitosa")
    data: List[ConciertoResponse] = Field(..., description="Lista de conciertos encontrados")
    pagination: Pagination = Field(..., description="Metadatos de la paginación")

# Schema para la respuesta exitosa al crear un nuevo concierto (POST /).
class ConciertoCreateResponse(BaseModel):
    success: bool = Field(True, description="Indica si la creación fue exitosa")
    message: str = Field("Concierto creado exitosamente", description="Mensaje de confirmación")
    data: Dict[str, int] = Field(..., description="Diccionario que contiene el ID del nuevo concierto creado, ej: {'id': 101}")

# Schema para la respuesta exitosa al actualizar un concierto (PUT /{concierto_id}).
class ConciertoUpdateResponse(BaseModel):
    success: bool = Field(True, description="Indica si la actualización fue exitosa")
    message: str = Field("Concierto actualizado exitosamente", description="Mensaje de confirmación")


# --- Endpoints (Definiciones de Rutas API) ---

@router.get("/",
            response_model=ConciertoListResponse,
            summary="Obtener lista paginada de conciertos",
            description="Recupera una lista de conciertos con paginación, opcionalmente filtrada por artista, ordenada por fecha descendente.")
def get_conciertos(
    page: int = Query(1, ge=1, description="Número de página a solicitar (mínimo 1)"),
    limit: int = Query(10, ge=1, le=100, description="Número de conciertos por página (entre 1 y 100)"),
    artista_id: Optional[int] = Query(None, description="ID opcional del artista para filtrar los conciertos")
):
    """
    Endpoint para obtener una lista paginada de conciertos.
    Permite filtrar los resultados por el ID de un artista ('artista_id').
    """
    # Llama a la función en 'models.py', pasando los parámetros de paginación y el filtro opcional.
    conciertos, pagination_data = models.get_all_conciertos_from_db(page, limit, artista_id)

    # Devuelve los datos formateados según 'ConciertoListResponse'.
    return {"data": conciertos, "pagination": pagination_data}

@router.get("/{concierto_id}",
            response_model=ConciertoResponse,
            summary="Obtener un concierto por ID",
            description="Recupera los detalles de un concierto específico mediante su ID numérico único, incluyendo información básica del artista asociado.")
def get_concierto(concierto_id: int):
    """
    Endpoint para obtener los detalles de un concierto específico.
    El ID del concierto se extrae de la ruta URL.
    """
    # Llama a la función en 'models.py' para buscar el concierto.
    concierto = models.get_concierto_by_id_from_db(concierto_id)
    if concierto is None:
        # Si no se encuentra, lanza un error 404.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Concierto con ID {concierto_id} no encontrado")

    # Devuelve los datos del concierto.
    return concierto

@router.post("/",
             status_code=status.HTTP_201_CREATED,
             response_model=ConciertoCreateResponse,
             summary="Crear un nuevo concierto",
             description="Registra un nuevo concierto en la base de datos.")
def create_concierto(concierto: ConciertoBase = Body(..., description="Datos del nuevo concierto a crear según el schema ConciertoBase")):
    """
    Endpoint para crear un nuevo concierto.
    Recibe los datos en el cuerpo de la solicitud POST y los valida contra 'ConciertoBase'.
    Verifica que el 'artista_id' proporcionado exista antes de intentar la inserción.
    """
    # Convierte el modelo Pydantic a diccionario.
    concierto_data = concierto.model_dump()
    
    # Intenta crear el concierto en la base de datos llamando a 'models.py'.
    nuevo_id = models.create_concierto_in_db(concierto_data)
    
    if nuevo_id is None:
        # Si 'models.py' devuelve None, hubo un error (posiblemente el artista_id no existía o error de BD).
        # Aunque 'models.py' imprime el error específico, aquí devolvemos un error genérico 500.
        # Podríamos añadir lógica para devolver 404 si el error fue por artista_id no encontrado.
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error interno del servidor al intentar crear el concierto")
                            
    # Devuelve la respuesta de éxito con el ID del nuevo concierto.
    return {"data": {"id": nuevo_id}}

@router.put("/{concierto_id}",
            response_model=ConciertoUpdateResponse,
            summary="Actualizar un concierto existente",
            description="Actualiza la información de un concierto existente identificado por su ID.")
def update_concierto(concierto_id: int, concierto: ConciertoBase = Body(..., description="Nuevos datos para actualizar el concierto")):
    """
    Endpoint para actualizar un concierto existente.
    Recibe el ID en la ruta URL y los nuevos datos en el cuerpo de la solicitud PUT.
    Valida los datos del cuerpo contra 'ConciertoBase'.
    Solo los campos presentes en el body serán actualizados.
    """
    # Paso 1: Verificar si el concierto existe.
    concierto_existente = models.get_concierto_by_id_from_db(concierto_id)
    if concierto_existente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Concierto con ID {concierto_id} no encontrado para actualizar")

    # Paso 2: Convertir datos Pydantic a diccionario, excluyendo valores no enviados.
    concierto_data = concierto.model_dump(exclude_unset=True) 

    if not concierto_data:
         # Si el body está vacío o no contiene campos actualizables, error 400.
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se proporcionaron campos válidos para actualizar")

    # Paso 3: Llamar a 'models.py' para ejecutar la actualización.
    success = models.update_concierto_in_db(concierto_id, concierto_data)
    
    if not success:
        # Si la actualización falla, error 500.
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="Error interno del servidor al intentar actualizar el concierto")
                            
    # Devuelve la respuesta de éxito.
    return {"message": "Concierto actualizado exitosamente"}