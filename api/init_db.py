import sqlite3
import os

# --- CONSTANTES DE CONFIGURACIÓN ---

# Define la ruta base absoluta del directorio 'api'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define la ruta completa para el archivo de la base de datos
DB_PATH = os.path.join(BASE_DIR, 'data', 'conciertos.db')

# Define la ruta completa para el script de schema SQL
SCHEMA_PATH = os.path.join(BASE_DIR, 'schema.sql')

# --- FUNCIONES DE BASE DE DATOS ---

def get_db_connection():
    """
    Establece y devuelve una conexión a la base de datos SQLite.
    Asegura que el directorio 'data' exista y configura la conexión 
    para devolver filas como diccionarios (sqlite3.Row).
    """
    # Asegura que el subdirectorio 'data' exista
    os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    # Habilita el acceso a columnas por nombre (como un diccionario)
    conn.row_factory = sqlite3.Row  
    return conn

def init_db():
    """
    Inicializa la base de datos ejecutando el script schema.sql.
    Borra las tablas existentes (DROP TABLE) y crea las nuevas (CREATE TABLE).
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Lee el contenido del archivo schema.sql
        with open(SCHEMA_PATH, 'r') as f:
            sql_script = f.read()
            
        # Ejecuta el script SQL completo
        cursor.executescript(sql_script)
        
        conn.commit()
        print("✅ Base de datos inicializada y tablas creadas.")
    except sqlite3.Error as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
    finally:
        if conn:
            conn.close()

def seed_db():
    """
    Puebla (siembra) la base de datos con un conjunto inicial de datos
    de artistas y conciertos.
    Verifica si ya existen datos para evitar duplicados.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica si la tabla 'artistas' ya ha sido sembrada
        cursor.execute("SELECT COUNT(*) FROM artistas")
        if cursor.fetchone()[0] > 0:
            print("⚠️ La base de datos ya tiene datos (semilla). No se insertaron nuevos.")
            return

        print("🌱 Sembrando datos (artistas y conciertos)...")

        # --- ARTISTAS (Datos de Ejemplo) ---
        # Columnas: (nombre, genero, pais, popularidad, imagen_url, biografia)
        artistas = [
            ("Taylor Swift", "Pop", "Estados Unidos", 99, "https://i.scdn.co/image/ab6761610000e5eb859e4c68b8e8f80e1e00f1c0", "Cantautora estadounidense conocida por sus letras narrativas."),
            ("The Weeknd", "R&B", "Canadá", 95, "https://i.scdn.co/image/ab6761610000e5eb214f3cf1cbe7139c1e26ff02", "Cantante, compositor y productor canadiense."),
            ("Ariana Grande", "Pop", "Estados Unidos", 94, "https://i.scdn.co/image/ab6761610000e5eb1c9f9a566589e4c35f4b5f80", "Cantante y actriz estadounidense."),
            ("Bruno Mars", "Pop/Funk", "Estados Unidos", 92, "https://i.scdn.co/image/ab6761610000e5ebc02d43e08c4a6c83dea1b44b", "Cantante, compositor y productor estadounidense."),
            ("Beyoncé", "R&B/Pop", "Estados Unidos", 97, "https://i.scdn.co/image/ab6761610000e5eb1d36be521113b2ce40e6b8e3", "Cantante, compositora y actriz estadounidense."),
            ("Harry Styles", "Pop Rock", "Reino Unido", 93, "https://i.scdn.co/image/ab6761610000e5eb5a00b1803a6a2f77d5c58a5c", "Cantante, compositor y actor británico."),
            ("Dua Lipa", "Pop", "Reino Unido", 91, "https://i.scdn.co/image/ab6761610000e5ebe4b9a1cdf1c35c4b9c1d0bfa", "Cantante y compositora británica de origen albanés."),
            ("Ed Sheeran", "Pop", "Reino Unido", 90, "https://i.scdn.co/image/ab6761610000e5ebdc0f90c44c1b91e7e466b09c", "Cantante y compositor británico."),
            ("Billie Eilish", "Pop Alternativo", "Estados Unidos", 89, "https://i.scdn.co/image/ab6761610000e5eb5bb0b1c0c6d57f0f7079f18e", "Cantante y compositora estadounidense."),
            ("Coldplay", "Rock Alternativo", "Reino Unido", 88, "https://i.scdn.co/image/ab6761610000e5eb989ed05e1f0570cc4726c2d3", "Banda británica de rock alternativo."),
            ("Bad Bunny", "Reggaeton", "Puerto Rico", 98, "https://i.scdn.co/image/ab6761610000e5eb6be070445b53e00f169d2a4a", "Rapero y cantante puertorriqueño."),
            ("Rosalía", "Flamenco Pop", "España", 90, "https://i.scdn.co/image/ab6761610000e5ebc1b7f2ddbe432f7b800c1f28", "Cantante y compositora española."),
            ("J Balvin", "Reggaeton", "Colombia", 87, "https://i.scdn.co/image/ab6761610000e5eb23b04c861d19815b3c54098c", "Cantante colombiano de reguetón."),
            ("Karol G", "Reggaeton", "Colombia", 89, "https://i.scdn.co/image/ab6761610000e5eb0d2a8f8d3f089b706c641215", "Cantante y compositora colombiana."),
            ("Shakira", "Pop Latino", "Colombia", 91, "https://i.scdn.co/image/ab6761610000e5eb5407e324c52c6f157f1396b7", "Cantautora colombiana."),
            ("Peso Pluma", "Corridos Tumbados", "México", 85, "https://i.scdn.co/image/ab6761610000e5eb41d3b0c51f491b40283d6a6a", "Cantante mexicano de corridos tumbados."),
            ("Natanael Cano", "Corridos Tumbados", "México", 82, "https://i.scdn.co/image/ab6761610000e5eb15d9333f2d20773d2a33c1f1", "Cantante mexicano, pionero de los corridos tumbados."),
            ("Drake", "Hip Hop", "Canadá", 96, "https://i.scdn.co/image/ab6761610000e5eb4293385d324db8558179afd9", "Rapero, cantante y actor canadiense."),
            ("Travis Scott", "Hip Hop", "Estados Unidos", 90, "https://i.scdn.co/image/ab6761610000e5eb4f94353d5f1717f2b1c640e7", "Rapero y productor estadounidense."),
            ("Arctic Monkeys", "Indie Rock", "Reino Unido", 86, "https://i.scdn.co/image/ab6761610000e5ebc08ddbab5d01247b4e945c26", "Banda británica de rock.")
        ]
        
        cursor.executemany(
            "INSERT INTO artistas (nombre, genero, pais, popularidad, imagen_url, biografia) VALUES (?, ?, ?, ?, ?, ?)",
            artistas
        )
        print(f"   - {len(artistas)} artistas insertados.")

        # --- CONCIERTOS (Datos de Ejemplo) ---
        # Columnas: (artista_id, nombre_evento, venue, ciudad, pais, fecha, status, 
        #            asistencia_proyectada, asistencia_real, costos_produccion, ingresos_taquilla, 
        #            latitud, longitud)
        # Nota: 'None' en Python se traduce como 'NULL' en SQLite
        conciertos = [
            # 1. Taylor Swift (ID: 1)
            (1, "Eras Tour", "SoFi Stadium", "Los Angeles", "Estados Unidos", "2025-08-03T19:00:00Z", "Confirmado", 70000, 70200, 3000000, 5000000, 33.9535, -118.3390),
            (1, "Eras Tour", "Foro Sol", "Ciudad de México", "México", "2025-08-24T19:30:00Z", "Confirmado", 65000, 65000, 2500000, 4000000, 19.4049, -99.0917),
            (1, "Eras Tour", "Wembley Stadium", "Londres", "Reino Unido", "2025-06-21T19:00:00Z", "Confirmado", 90000, 88500, 3500000, 5500000, 51.5560, -0.2795),
            (1, "Eras Tour", "La Défense Arena", "París", "Francia", "2025-05-09T20:00:00Z", "Planeado", 40000, None, 1800000, None, 48.8925, 2.2319),
            
            # 2. The Weeknd (ID: 2)
            (2, "After Hours til Dawn Tour", "Estadio BBVA", "Monterrey", "México", "2025-09-26T20:00:00Z", "Confirmado", 53000, 51000, 1500000, 2200000, 25.6706, -100.2413),
            (2, "After Hours til Dawn Tour", "Hard Rock Stadium", "Miami", "Estados Unidos", "2025-08-30T19:00:00Z", "Confirmado", 65000, 63000, 2000000, 3000000, 25.9580, -80.2389),

            # 3. Ariana Grande (ID: 3)
            (3, "Sweetener World Tour", "Madison Square Garden", "Nueva York", "Estados Unidos", "2025-11-18T20:00:00Z", "Planeado", 20000, None, 1000000, None, 40.7505, -73.9934),
            
            # 4. Bruno Mars (ID: 4)
            (4, "24K Magic World Tour", "Tokyo Dome", "Tokio", "Japón", "2025-10-11T19:00:00Z", "Confirmado", 55000, 55000, 2500000, 4000000, 35.7056, 139.7519),

            # 5. Beyoncé (ID: 5)
            (5, "Renaissance World Tour", "MetLife Stadium", "Nueva York", "Estados Unidos", "2025-07-29T20:00:00Z", "Confirmado", 82000, 81500, 4000000, 6000000, 40.8128, -74.0742),

            # 6. Harry Styles (ID: 6)
            (6, "Love On Tour", "Foro Sol", "Ciudad de México", "México", "2025-11-25T20:00:00Z", "Confirmado", 65000, 65000, 1800000, 2800000, 19.4049, -99.0917),
            (6, "Love On Tour", "Wembley Stadium", "Londres", "Reino Unido", "2025-06-14T19:00:00Z", "Confirmado", 90000, 90000, 3000000, 4500000, 51.5560, -0.2795),

            # 7. Dua Lipa (ID: 7)
            (7, "Future Nostalgia Tour", "Palau Sant Jordi", "Barcelona", "España", "2025-06-01T21:00:00Z", "Confirmado", 18000, 17500, 700000, 1200000, 41.3641, 2.1531),
            (7, "Future Nostalgia Tour", "WiZink Center", "Madrid", "España", "2025-06-03T21:00:00Z", "Confirmado", 17000, 17000, 650000, 1100000, 40.4240, -3.6705),

            # 8. Ed Sheeran (ID: 8)
            (8, "Mathematics Tour", "Estadio Azteca", "Ciudad de México", "México", "2025-04-29T20:00:00Z", "Planeado", 87000, None, 2500000, None, 19.3029, -99.1504),

            # 9. Billie Eilish (ID: 9)
            (9, "Happier Than Ever Tour", "Foro Sol", "Ciudad de México", "México", "2025-03-29T20:30:00Z", "Confirmado", 65000, 64000, 1600000, 2500000, 19.4049, -99.0917),
            (9, "Happier Than Ever Tour", "The O2", "Londres", "Reino Unido", "2025-06-25T20:00:00Z", "Cancelado", 20000, 0, 500000, 0, 51.5033, 0.0031),

            # 10. Coldplay (ID: 10)
            (10, "Music of the Spheres", "Foro Sol", "Ciudad de México", "México", "2025-04-03T20:00:00Z", "Confirmado", 65000, 65000, 2000000, 3500000, 19.4049, -99.0917),
            (10, "Music of the Spheres", "Estadio Akron", "Guadalajara", "México", "2025-03-29T20:00:00Z", "Confirmado", 45000, 44000, 1500000, 2500000, 20.6766, -103.4491),
            (10, "Music of the Spheres", "Estadio BBVA", "Monterrey", "México", "2025-03-25T20:00:00Z", "Confirmado", 53000, 52000, 1700000, 2800000, 25.6706, -100.2413),
            (10, "Music of the Spheres", "Estadi Olímpic", "Barcelona", "España", "2025-05-24T21:00:00Z", "Confirmado", 55000, 54000, 1800000, 3000000, 41.3648, 2.1556),
            
            # 11. Bad Bunny (ID: 11)
            (11, "World's Hottest Tour", "Estadio Azteca", "Ciudad de México", "México", "2025-12-09T20:30:00Z", "Confirmado", 87000, 85000, 3000000, 5000000, 19.3029, -99.1504),
            (11, "World's Hottest Tour", "Estadio BBVA", "Monterrey", "México", "2025-12-03T20:30:00Z", "Confirmado", 53000, 53000, 2000000, 3500000, 25.6706, -100.2413),

            # 12. Rosalía (ID: 12)
            (12, "Motomami World Tour", "Palau Sant Jordi", "Barcelona", "España", "2025-07-23T21:00:00Z", "Confirmado", 18000, 18000, 500000, 900000, 41.3641, 2.1531),
            (12, "Motomami World Tour", "WiZink Center", "Madrid", "España", "2025-07-19T21:00:00Z", "Confirmado", 17000, 16500, 450000, 800000, 40.4240, -3.6705),
            (12, "Motomami World Tour", "Zócalo", "Ciudad de México", "México", "2025-04-28T20:00:00Z", "Confirmado", 160000, 160000, 1000000, 0, 19.4326, -99.1332),

            # 13. J Balvin (ID: 13)
            (13, "Jose Tour", "Arena CDMX", "Ciudad de México", "México", "2025-09-15T21:00:00Z", "Planeado", 22000, None, 600000, None, 19.4950, -99.1413),
            
            # 14. Karol G (ID: 14)
            (14, "Bichota Tour", "Estadio Azteca", "Ciudad de México", "México", "2025-02-08T20:30:00Z", "Confirmado", 87000, 86000, 1800000, 3000000, 19.3029, -99.1504),
            (14, "Bichota Tour", "Estadio Mobil Super", "Monterrey", "México", "2025-02-16T20:30:00Z", "Confirmado", 22000, 21000, 700000, 1200000, 25.7029, -100.3239),

            # 15. Shakira (ID: 15)
            (15, "Las Mujeres Ya No Lloran Tour", "Kaseya Center", "Miami", "Estados Unidos", "2025-11-02T20:00:00Z", "Planeado", 20000, None, 900000, None, 25.7814, -80.1870),

            # 16. Peso Pluma (ID: 16)
            (16, "Éxodo Tour", "Foro Sol", "Ciudad de México", "México", "2025-11-11T20:00:00Z", "Confirmado", 65000, 60000, 1200000, 2000000, 19.4049, -99.0917),
            (16, "Éxodo Tour", "Estadio Akron", "Guadalajara", "México", "2025-09-27T20:00:00Z", "Confirmado", 45000, 45000, 1000000, 1800000, 20.6766, -103.4491),

            # 17. Natanael Cano (ID: 17)
            (17, "Tumbado Tour", "Auditorio Nacional", "Ciudad de México", "México", "2025-08-30T20:30:00Z", "Confirmado", 10000, 10000, 400000, 700000, 19.4208, -99.1983),

            # 18. Drake (ID: 18)
            (18, "It's All A Blur Tour", "Scotiabank Arena", "Toronto", "Canadá", "2025-10-07T20:00:00Z", "Confirmado", 19800, 19800, 1200000, 2000000, 43.6435, -79.3791),

            # 19. Travis Scott (ID: 19)
            (19, "Utopia Tour", "SoFi Stadium", "Los Angeles", "Estados Unidos", "2025-10-05T20:00:00Z", "Confirmado", 70000, 68000, 2500000, 4000000, 33.9535, -118.3390),
            (19, "Utopia Tour", "Palau Sant Jordi", "Barcelona", "España", "2025-07-28T21:00:00Z", "Cancelado", 18000, 0, 600000, 0, 41.3641, 2.1531),

            # 20. Arctic Monkeys (ID: 20)
            (20, "The Car Tour", "Foro Sol", "Ciudad de México", "México", "2025-10-06T20:00:00Z", "Confirmado", 65000, 63000, 1500000, 2500000, 19.4049, -99.0917),
            (20, "The Car Tour", "WiZink Center", "Madrid", "España", "2025-07-10T21:00:00Z", "Confirmado", 17000, 17000, 600000, 1000000, 40.4240, -3.6705),
            (20, "The Car Tour", "The O2", "Londres", "Reino Unido", "2025-06-18T20:00:00Z", "Confirmado", 20000, 19500, 700000, 1200000, 51.5033, 0.0031)
        ]
        
        cursor.executemany(
            """INSERT INTO conciertos 
           (artista_id, nombre_evento, venue, ciudad, pais, fecha, status, 
            asistencia_proyectada, asistencia_real, costos_produccion, ingresos_taquilla, 
            latitud, longitud) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            conciertos
        )
        print(f"   - {len(conciertos)} conciertos insertados.")

        # Guarda los cambios en la base de datos
        conn.commit()
        print("✅ Base de datos sembrada exitosamente.")
        
    except sqlite3.Error as e:
        print(f"❌ Error al sembrar la base de datos: {e}")
    finally:
        # Cierra la conexión
        if conn:
            conn.close()

# --- PUNTO DE ENTRADA ---

if __name__ == "__main__":
    """
    Punto de entrada para ejecutar el script directamente desde la terminal.
    Ejecuta la inicialización (init_db) y la siembra (seed_db) en orden.
    """
    print("Iniciando proceso de DB...")
    # 1. Crea las tablas
    init_db()
    # 2. Llena las tablas con datos
    seed_db()
    print("Proceso de DB completado.")