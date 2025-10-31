# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any, Optional
from . import models # Importa el módulo models.py
from pydantic import BaseModel, Field # Para definir el schema de respuesta

# --- Router ---
# Se crea una instancia de APIRouter para la ruta de estadísticas.
router = APIRouter(
    prefix="/api/estadisticas", # Define el prefijo base para esta ruta.
    tags=["Estadísticas"],     # Agrupa esta ruta bajo la etiqueta "Estadísticas" en la documentación.
    responses={500: {"description": "Error interno del servidor"}} # Respuesta estándar para 500.
)

# --- Schemas Pydantic (Modelos de Datos para la Respuesta) ---

# Define la estructura esperada para un elemento en la lista de top artistas.
class TopArtistaStat(BaseModel):
    nombre: str = Field(..., description="Nombre del artista")
    popularidad: int = Field(..., description="Nivel de popularidad del artista")

# Define la estructura esperada para un elemento en la lista de rentabilidad por ciudad.
class RentabilidadCiudadStat(BaseModel):
    ciudad: str = Field(..., description="Nombre de la ciudad")
    ganancia_neta_ciudad: float = Field(..., description="Ganancia neta generada en esa ciudad (ingresos - costos)")

# Define la estructura de los KPIs financieros.
class KPIsFinancieros(BaseModel):
    total_ingresos: float = Field(..., description="Suma de ingresos_taquilla de conciertos confirmados")
    total_costos: float = Field(..., description="Suma de costos_produccion de conciertos confirmados")
    ganancia_neta: float = Field(..., description="Diferencia entre ingresos y costos totales")

# Define la estructura de los KPIs de asistencia.
class KPIsAsistencia(BaseModel):
    total_asistencia_proyectada: int = Field(..., description="Suma de asistencia_proyectada de conciertos confirmados")
    total_asistencia_real: int = Field(..., description="Suma de asistencia_real de conciertos confirmados")
    tasa_cumplimiento_asistencia: float = Field(..., description="Porcentaje de asistencia real sobre la proyectada")

# Define la estructura completa de la respuesta del endpoint de estadísticas.
class EstadisticasResponse(BaseModel):
    success: bool = Field(True, description="Indica si la solicitud fue exitosa")
    data: Dict[str, Any] = Field(..., description="Diccionario que contiene todas las estadísticas calculadas")
    # Ejemplo de la estructura del diccionario 'data':
    # data: {
    #     "kpis_financieros": KPIsFinancieros,
    #     "kpis_asistencia": KPIsAsistencia,
    #     "grafica_top_artistas": List[TopArtistaStat],
    #     "grafica_rentabilidad_ciudad": List[RentabilidadCiudadStat]
    # }


# --- Endpoint (Definición de Ruta API) ---

@router.get("/",
            response_model=EstadisticasResponse,
            summary="Obtener estadísticas consolidadas",
            description="Recupera un conjunto de KPIs y datos agregados para el dashboard del manager.")
def get_estadisticas():
    """
    Endpoint para obtener las estadísticas consolidadas.
    Llama a la función 'get_stats_from_db' en 'models.py' que realiza
    múltiples consultas de agregación a la base de datos.
    """
    # Llama a la función en 'models.py' para obtener todas las estadísticas.
    # Si 'models.py' (corregido) lanza un error de BD, 
    # FastAPI lo atrapará y devolverá un 500 automáticamente.
    estadisticas_data = models.get_stats_from_db()

    # Se elimina el bloque 'if not estadisticas_data: raise HTTPException(500)'
    # para seguir la recomendación del profesor de no lanzar errores 500 manualmente.

    # Devuelve los datos formateados según 'EstadisticasResponse'.
    return {"data": estadisticas_data}