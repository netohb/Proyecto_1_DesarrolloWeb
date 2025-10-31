import sqlite3
import os
import math
from typing import List, Dict, Any, Optional, Tuple

# --- CONSTANTES DE CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'conciertos.db')

# --- FUNCIÓN DE CONEXIÓN (CORREGIDA) ---

def get_db_connection() -> sqlite3.Connection:
    """
    Establece y devuelve una conexión a la base de datos SQLite.
    Configura la conexión para devolver filas como diccionarios (sqlite3.Row)
    y HABILITA la coerción de llaves foráneas (FOREIGN KEY).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # --- CAMBIO IMPORTANTE ---
    # Habilita la coerción de llaves foráneas (desactivado por defecto en SQLite)
    conn.execute("PRAGMA foreign_keys = ON;")
    # -----------------------
    
    return conn
# --- MODELOS DE ARTISTAS (CRUD - CORREGIDOS) ---

def get_all_artistas_from_db(page: int, limit: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Obtiene una lista paginada de artistas desde la base de datos,
    ordenados por popularidad.
    Los errores de BD (ej. sqlite3.Error) se propagan a FastAPI.
    """
    if page < 1: page = 1
    if limit < 1 or limit > 100: limit = 10
    offset = (page - 1) * limit
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM artistas")
        total_records = cursor.fetchone()[0]
        total_pages = math.ceil(total_records / limit)
        
        query = """
            SELECT id, nombre, genero, pais, popularidad, imagen_url, biografia
            FROM artistas
            ORDER BY popularidad DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, (limit, offset))
        artistas = [dict(row) for row in cursor.fetchall()]
        
        pagination_data = {
            "page": page, "limit": limit, "total_records": total_records,
            "total_pages": total_pages, "has_next": page < total_pages, "has_prev": page > 1
        }
        return artistas, pagination_data

    # Se elimina el bloque 'except Exception as e' que silenciaba los errores.
    # Los errores de BD se propagarán a FastAPI, que devolverá un 500.
    
    finally:
        # El 'finally' asegura que la conexión se cierre sin importar qué pase.
        if conn: conn.close()

def get_artista_by_id_from_db(artista_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene un artista específico por su ID.
    Devuelve un diccionario con los datos del artista o None si no se encuentra.
    Los errores de BD se propagan a FastAPI.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query_artista = """
            SELECT id, nombre, genero, pais, popularidad, imagen_url, biografia
            FROM artistas
            WHERE id = ?
        """
        cursor.execute(query_artista, (artista_id,))
        artista_row = cursor.fetchone()
        
        # Esta lógica es correcta. Si no se encuentra, devuelve None
        # y el router (routes_artistas.py) lo convertirá en un 404.
        if artista_row is None: 
            return None
        
        query_conciertos = "SELECT COUNT(*) FROM conciertos WHERE artista_id = ?"
        cursor.execute(query_conciertos, (artista_id,))
        total_conciertos = cursor.fetchone()[0]
        
        artista_data = dict(artista_row)
        artista_data["total_conciertos"] = total_conciertos
        
        return artista_data

    # Se elimina el bloque 'except Exception as e' que silenciaba los errores.
    
    finally:
        if conn: conn.close()

def create_artista_in_db(artista_data: Dict[str, Any]) -> int:
    """
    Inserta un nuevo artista en la base de datos.
    Devuelve el ID del artista recién creado.
    Los errores de BD (ej. sqlite3.IntegrityError) se propagan a FastAPI.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO artistas (nombre, genero, pais, popularidad, imagen_url, biografia)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            artista_data['nombre'],
            artista_data['genero'],
            artista_data['pais'],
            artista_data.get('popularidad', 50),
            artista_data.get('imagen_url'),
            artista_data.get('biografia')
        ))
        
        conn.commit()
        # Si la inserción es exitosa, se devuelve el ID.
        # Si falla (ej. campo NOT NULL falta), se lanzará un error de BD.
        return cursor.lastrowid 

    # Se elimina el bloque 'except Exception as e' que silenciaba los errores.
    
    finally:
        if conn: conn.close()

def update_artista_in_db(artista_id: int, artista_data: Dict[str, Any]) -> bool:
    """
    Actualiza un artista existente en la base de datos.
    Devuelve True si fue exitoso (al menos 1 fila actualizada), False si no.
    Los errores de BD se propagan a FastAPI.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        updates = []
        values = []
        
        for field in ['nombre', 'genero', 'pais', 'popularidad', 'imagen_url', 'biografia']:
            if field in artista_data:
                updates.append(f"{field} = ?")
                values.append(artista_data[field])
        
        if not updates:
            print("No hay campos para actualizar")
            return False # Esto es lógica de negocio, no un error 500.
        
        values.append(artista_id)
        query = f"UPDATE artistas SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        
        # Devuelve True si se actualizó 1 (o más) filas
        return cursor.rowcount > 0 

    # Se elimina el bloque 'except Exception as e' que silenciaba los errores.
    
    finally:
        if conn: conn.close()

# --- MODELOS DE CONCIERTOS (CRUD - CORREGIDOS) ---

def get_all_conciertos_from_db(page: int, limit: int, artista_id: Optional[int] = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Obtiene una lista paginada de conciertos, con un filtro opcional por artista_id.
    Los errores de BD se propagan a FastAPI.
    """
    if page < 1: page = 1
    if limit < 1 or limit > 100: limit = 10
    offset = (page - 1) * limit
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        base_query = "FROM conciertos c JOIN artistas a ON c.artista_id = a.id"
        where_clause = ""
        params = []

        if artista_id:
            where_clause = " WHERE c.artista_id = ?"
            params = [artista_id]
        
        cursor.execute(f"SELECT COUNT(c.id) {base_query} {where_clause}", params)
        total_records = cursor.fetchone()[0]
        total_pages = math.ceil(total_records / limit)
        
        select_clause = "SELECT c.*, a.nombre as artista_nombre"
        query = f"{select_clause} {base_query} {where_clause} ORDER BY c.fecha DESC LIMIT ? OFFSET ?"
        
        params.extend([limit, offset])
        cursor.execute(query, params)
        
        conciertos = [dict(row) for row in cursor.fetchall()]
        
        pagination_data = {
            "page": page, "limit": limit, "total_records": total_records,
            "total_pages": total_pages, "has_next": page < total_pages, "has_prev": page > 1
        }
        return conciertos, pagination_data

    # Se elimina el bloque 'except Exception as e' que silenciaba los errores.
    
    finally:
        if conn: conn.close()

def get_concierto_by_id_from_db(concierto_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene un concierto específico por su ID.
    Devuelve None si no se encuentra.
    Los errores de BD se propagan a FastAPI.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT c.*, a.nombre as artista_nombre, a.genero as artista_genero, a.pais as artista_pais
            FROM conciertos c
            JOIN artistas a ON c.artista_id = a.id
            WHERE c.id = ?
        """
        cursor.execute(query, (concierto_id,))
        concierto_row = cursor.fetchone()
        
        if concierto_row is None:
            return None # Lógica de 404 (No Encontrado)
        
        return dict(concierto_row)

    # Se elimina el bloque 'except Exception as e' que silenciaba los errores.
    
    finally:
        if conn: conn.close()

def create_concierto_in_db(concierto_data: Dict[str, Any]) -> int:
    """
    Inserta un nuevo concierto en la base de datos.
    Devuelve el ID del concierto recién creado.
    Los errores de BD (ej. FOREIGN KEY constraint) se propagan a FastAPI.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Se elimina la verificación manual del artista_id.
        # Si el artista_id no existe, la restricción FOREIGN KEY de la BD
        # lanzará un 'sqlite3.IntegrityError' que FastAPI atrapará como 500.
        
        query = """
            INSERT INTO conciertos 
            (artista_id, nombre_evento, venue, ciudad, pais, fecha, status, 
             asistencia_proyectada, asistencia_real, costos_produccion, ingresos_taquilla, 
             latitud, longitud) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            concierto_data['artista_id'],
            concierto_data['nombre_evento'],
            concierto_data['venue'],
            concierto_data['ciudad'],
            concierto_data['pais'],
            concierto_data['fecha'],
            concierto_data.get('status', 'Planeado'),
            concierto_data.get('asistencia_proyectada'),
            concierto_data.get('asistencia_real'),
            concierto_data.get('costos_produccion'),
            concierto_data.get('ingresos_taquilla'),
            concierto_data.get('latitud'),
            concierto_data.get('longitud')
        ))
        
        conn.commit()
        return cursor.lastrowid

    # Se elimina el bloque 'except Exception as e' que silenciaba los errores.
    
    finally:
        if conn: conn.close()

def update_concierto_in_db(concierto_id: int, concierto_data: Dict[str, Any]) -> bool:
    """
    Actualiza un concierto existente en la base de datos.
    Solo actualiza los campos proporcionados en concierto_data.
    Los errores de BD se propagan a FastAPI.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        updates = []
        values = []
        
        updatable_fields = [
            'artista_id', 'nombre_evento', 'venue', 'ciudad', 'pais', 'fecha', 'status', 
            'asistencia_proyectada', 'asistencia_real', 'costos_produccion', 'ingresos_taquilla', 
            'latitud', 'longitud'
        ]
        
        for field in updatable_fields:
            if field in concierto_data:
                updates.append(f"{field} = ?")
                values.append(concierto_data[field])
        
        if not updates:
            print("No hay campos para actualizar")
            return False # Lógica de negocio (400), no un error 500
        
        values.append(concierto_id)
        query = f"UPDATE conciertos SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        
        return cursor.rowcount > 0

    # Se elimina el bloque 'except Exception as e' que silenciaba los errores.
    
    finally:
        if conn: conn.close()

# --- MODELO DE ESTADÍSTICAS (CORREGIDO) ---

def get_stats_from_db() -> Dict[str, Any]:
    """
    Obtiene un resumen de estadísticas clave para el dashboard del manager.
    Los errores de BD se propagan a FastAPI.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Top 10 artistas por popularidad
        cursor.execute("SELECT nombre, popularidad FROM artistas ORDER BY popularidad DESC LIMIT 10")
        top_artistas = [dict(row) for row in cursor.fetchall()]
        
        # 2. Total de Ganancia Neta
        cursor.execute("""
            SELECT SUM(ingresos_taquilla) as total_ingresos, SUM(costos_produccion) as total_costos
            FROM conciertos
            WHERE status = 'Confirmado'
        """)
        financiero_row = cursor.fetchone()
        total_ingresos = financiero_row['total_ingresos'] or 0
        total_costos = financiero_row['total_costos'] or 0
        ganancia_neta = total_ingresos - total_costos
        
        # 3. Comparación Asistencia
        cursor.execute("""
            SELECT SUM(asistencia_proyectada) as total_proyectado, SUM(asistencia_real) as total_real
            FROM conciertos
            WHERE status = 'Confirmado'
        """)
        asistencia_row = cursor.fetchone()
        total_proyectado = asistencia_row['total_proyectado'] or 0
        total_real = asistencia_row['total_real'] or 0
        
        # 4. Rentabilidad por Ciudad
        cursor.execute("""
            SELECT 
                ciudad, 
                SUM(ingresos_taquilla) - SUM(costos_produccion) as ganancia_neta_ciudad
            FROM conciertos
            WHERE status = 'Confirmado'
            GROUP BY ciudad
            ORDER BY ganancia_neta_ciudad DESC
            LIMIT 5
        """)
        rentabilidad_ciudad = [dict(row) for row in cursor.fetchall()]
        
        return {
            "kpis_financieros": {
                "total_ingresos": total_ingresos,
                "total_costos": total_costos,
                "ganancia_neta": ganancia_neta
            },
            "kpis_asistencia": {
                "total_asistencia_proyectada": total_proyectado,
                "total_asistencia_real": total_real,
                "tasa_cumplimiento_asistencia": (total_real / total_proyectado * 100) if total_proyectado > 0 else 0
            },
            "grafica_top_artistas": top_artistas,
            "grafica_rentabilidad_ciudad": rentabilidad_ciudad
        }

    
    finally:
        if conn: conn.close()