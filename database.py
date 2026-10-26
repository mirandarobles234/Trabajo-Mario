"""Conexión, esquema y datos de ejemplo de SQLite para Brick Vault."""
from contextlib import contextmanager
from pathlib import Path
import os
import sqlite3

BASE_DIR = Path(__file__).resolve().parent

# En Vercel el proyecto es de solo lectura: el único lugar donde se puede
# escribir es /tmp. En la computadora la base queda junto al código.
if os.environ.get("VERCEL"):
    DB_PATH = Path("/tmp/brick_vault.db")
else:
    DB_PATH = BASE_DIR / "brick_vault.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS tema (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL,
  descripcion TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS set_lego (
  numero TEXT PRIMARY KEY,
  nombre TEXT NOT NULL,
  tema INTEGER NOT NULL,
  estado TEXT NOT NULL,
  piezas INTEGER NOT NULL CHECK(piezas > 0),
  anno INTEGER NOT NULL CHECK(anno > 0),
  precio REAL NOT NULL CHECK(precio >= 0),
  piezas_faltantes INTEGER NOT NULL DEFAULT 0 CHECK(piezas_faltantes >= 0),
  FOREIGN KEY (tema) REFERENCES tema(id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS minifigura (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL,
  set_lego TEXT NOT NULL,
  cantidad INTEGER NOT NULL CHECK(cantidad > 0),
  FOREIGN KEY (set_lego) REFERENCES set_lego(numero) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS pieza_faltante (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  set_lego TEXT NOT NULL,
  descripcion TEXT NOT NULL,
  color TEXT NOT NULL,
  cantidad INTEGER NOT NULL CHECK(cantidad > 0),
  FOREIGN KEY (set_lego) REFERENCES set_lego(numero) ON DELETE CASCADE
);
"""

# Datos de ejemplo: solo se insertan la primera vez, cuando la base está vacía.
SEED = """
INSERT INTO tema (nombre, descripcion) VALUES
  ('Star Wars', 'Naves, escenas y personajes de la saga.'),
  ('City', 'Vehículos y edificios de la vida en la ciudad.'),
  ('Technic', 'Modelos con engranajes, ejes y mecanismos.'),
  ('Ideas', 'Sets propuestos por fanáticos.');
INSERT INTO set_lego (numero, nombre, tema, estado, piezas, anno, precio, piezas_faltantes) VALUES
  ('75301', 'X-Wing de Luke Skywalker', 1, 'En exhibición', 474, 2021, 32000, 2),
  ('60316', 'Estación de policía', 2, 'Armado', 668, 2022, 41000, 0),
  ('42151', 'Bugatti Bolide', 3, 'Armado', 905, 2023, 30000, 1),
  ('21335', 'Faro motorizado', 4, 'En caja', 2065, 2022, 165000, 0);
INSERT INTO minifigura (nombre, set_lego, cantidad) VALUES
  ('Luke Skywalker', '75301', 1), ('Princesa Leia', '75301', 1), ('R2-D2', '75301', 1),
  ('Oficial de policía', '60316', 3), ('Ladrón', '60316', 2);
INSERT INTO pieza_faltante (set_lego, descripcion, color, cantidad) VALUES
  ('75301', 'Placa 1x2', 'Gris claro', 2),
  ('42151', 'Pin con fricción', 'Azul', 1);
"""


@contextmanager
def get_connection():
    """Abre una conexión, guarda los cambios si todo sale bien y siempre la cierra."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row            # permite leer las filas como diccionarios
    conn.execute("PRAGMA foreign_keys = ON")  # SQLite no revisa llaves foráneas si no se activa
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_database():
    """Crea las tablas si no existen y carga los datos de ejemplo una sola vez."""
    with get_connection() as conn:
        conn.executescript(SCHEMA)
        vacia = conn.execute("SELECT COUNT(*) FROM tema").fetchone()[0] == 0
        if vacia:
            conn.executescript(SEED)
