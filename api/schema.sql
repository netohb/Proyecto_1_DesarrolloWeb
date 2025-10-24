-- Borra las tablas si ya existen (para poder reiniciar la BD fácilmente)
DROP TABLE IF EXISTS artistas;
DROP TABLE IF EXISTS conciertos;

-- 1. Tabla de Artistas
CREATE TABLE artistas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    genero TEXT NOT NULL,
    pais TEXT NOT NULL,
    popularidad INTEGER DEFAULT 50,
    imagen_url TEXT,
    biografia TEXT
);

-- 2. Tabla de Conciertos
CREATE TABLE conciertos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artista_id INTEGER NOT NULL,
    
    -- Info del Evento
    nombre_evento TEXT NOT NULL,
    venue TEXT NOT NULL,
    ciudad TEXT NOT NULL,
    pais TEXT NOT NULL,
    fecha TEXT NOT NULL,              -- Formato ISO 8601: "2025-11-20T20:00:00Z"
    status TEXT NOT NULL DEFAULT 'Planeado', 

    -- Métricas de Asistencia (para el Manager)
    asistencia_proyectada INTEGER,
    asistencia_real INTEGER,          

    -- Métricas Financieras (para el Manager)
    costos_produccion INTEGER,
    ingresos_taquilla INTEGER,

    -- Info de Mapa (para el Frontend)
    latitud REAL,
    longitud REAL,

    -- Conexión
    FOREIGN KEY (artista_id) REFERENCES artistas (id)
);