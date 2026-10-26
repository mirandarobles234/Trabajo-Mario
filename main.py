"""Brick Vault: API REST con FastAPI + SQLite. Control de una colección de sets LEGO."""
from pathlib import Path
import os
import sqlite3
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from database import get_connection, initialize_database

# Crea las tablas (y los datos de ejemplo) antes de atender la primera petición.
initialize_database()

app = FastAPI(title="Brick Vault", description="Control de una colección de sets LEGO.", version="1.0.0")


# ==================== Modelos: validan los datos que llegan a la API ====================

class Tema(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    descripcion: str = Field(min_length=1, max_length=500)


class SetLego(BaseModel):
    numero: str = Field(min_length=1, max_length=40)
    nombre: str = Field(min_length=1, max_length=120)
    tema: int
    estado: Literal["En caja", "Armado", "En exhibición", "Desarmado"]
    piezas: int = Field(gt=0)
    anno: int = Field(gt=0)
    precio: float = Field(ge=0)


class Minifigura(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    set_lego: str = Field(min_length=1)
    cantidad: int = Field(gt=0)


class PiezaFaltante(BaseModel):
    set_lego: str = Field(min_length=1)
    descripcion: str = Field(min_length=1, max_length=120)
    color: str = Field(min_length=1, max_length=120)
    cantidad: int = Field(gt=0)


# ==================== Reglas de negocio ====================
def regla_faltantes(conn, nuevo, anterior):
    """Regla de negocio: mantiene al día el contador de piezas faltantes de cada set.

    Se ejecuta después de crear, modificar o eliminar una pieza faltante.
    Si la pieza cambió de set, se recalculan los dos sets.
    """
    numeros = {fila["set_lego"] for fila in (nuevo, anterior) if fila}
    for numero in numeros:
        conn.execute(
            """UPDATE set_lego SET piezas_faltantes =
                 (SELECT COALESCE(SUM(cantidad), 0) FROM pieza_faltante WHERE set_lego = ?)
               WHERE numero = ?""", (numero, numero))


# ==================== Temas ====================
# Consulta base: trae cada fila de tema.
CONSULTA_TEMA = """
SELECT t.*
FROM tema t
"""


@app.get("/api/temas")
def listar_temas():
    with get_connection() as conn:
        return [dict(fila) for fila in conn.execute(CONSULTA_TEMA + " ORDER BY t.nombre")]


@app.get("/api/temas/{id}")
def obtener_tema(id: int):
    with get_connection() as conn:
        fila = conn.execute(CONSULTA_TEMA + " WHERE t.id = ?", (id,)).fetchone()
    if not fila:
        raise HTTPException(404, "No se encontró el tema.")
    return dict(fila)


@app.post("/api/temas", status_code=201)
def crear_tema(datos: Tema):
    nuevo = datos.model_dump(mode="json")
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO tema (nombre, descripcion) VALUES (:nombre, :descripcion)", nuevo)
            nuevo["id"] = cursor.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(409, "No se pudo guardar: revise los datos.")
    return nuevo


@app.put("/api/temas/{id}")
def actualizar_tema(id: int, datos: Tema):
    nuevo = datos.model_dump(mode="json")
    try:
        with get_connection() as conn:
            anterior = conn.execute("SELECT * FROM tema WHERE id = ?", (id,)).fetchone()
            if not anterior:
                raise HTTPException(404, "No se encontró el tema.")
            conn.execute("UPDATE tema SET nombre = :nombre, descripcion = :descripcion WHERE id = :pk_url", {**nuevo, "pk_url": id})
    except sqlite3.IntegrityError:
        raise HTTPException(409, "No se pudo guardar: revise los datos.")
    return {"id": id, **nuevo}


@app.delete("/api/temas/{id}", status_code=204)
def eliminar_tema(id: int):
    try:
        with get_connection() as conn:
            anterior = conn.execute("SELECT * FROM tema WHERE id = ?", (id,)).fetchone()
            if not anterior:
                raise HTTPException(404, "No se encontró el tema.")
            conn.execute("DELETE FROM tema WHERE id = ?", (id,))
    except sqlite3.IntegrityError:
        raise HTTPException(409, "No se puede eliminar el tema: hay sets que dependen de este registro.")


# ==================== Sets de la colección ====================
# Consulta base: trae cada fila de set_lego con el nombre de sus datos relacionados.
CONSULTA_SET_LEGO = """
SELECT t.*,
       (SELECT nombre FROM tema WHERE id = t.tema) AS tema_nombre
FROM set_lego t
"""


@app.get("/api/sets")
def listar_sets():
    with get_connection() as conn:
        return [dict(fila) for fila in conn.execute(CONSULTA_SET_LEGO + " ORDER BY t.numero")]


@app.get("/api/sets/{numero}")
def obtener_set_lego(numero: str):
    with get_connection() as conn:
        fila = conn.execute(CONSULTA_SET_LEGO + " WHERE t.numero = ?", (numero,)).fetchone()
    if not fila:
        raise HTTPException(404, "No se encontró el set.")
    return dict(fila)


@app.post("/api/sets", status_code=201)
def crear_set_lego(datos: SetLego):
    nuevo = datos.model_dump(mode="json")
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO set_lego (numero, nombre, tema, estado, piezas, anno, precio) VALUES (:numero, :nombre, :tema, :estado, :piezas, :anno, :precio)", nuevo)
    except sqlite3.IntegrityError:
        raise HTTPException(409, "Revise los datos: alguno de los registros relacionados no existe, o ya existe otro registro con ese número de set.")
    return nuevo


@app.put("/api/sets/{numero}")
def actualizar_set_lego(numero: str, datos: SetLego):
    if datos.numero != numero:
        raise HTTPException(400, "El número de set no se puede cambiar.")
    nuevo = datos.model_dump(mode="json")
    try:
        with get_connection() as conn:
            anterior = conn.execute("SELECT * FROM set_lego WHERE numero = ?", (numero,)).fetchone()
            if not anterior:
                raise HTTPException(404, "No se encontró el set.")
            conn.execute("UPDATE set_lego SET nombre = :nombre, tema = :tema, estado = :estado, piezas = :piezas, anno = :anno, precio = :precio WHERE numero = :pk_url", {**nuevo, "pk_url": numero})
    except sqlite3.IntegrityError:
        raise HTTPException(409, "Revise los datos: alguno de los registros relacionados no existe, o ya existe otro registro con ese número de set.")
    return {"numero": numero, **nuevo}


@app.delete("/api/sets/{numero}", status_code=204)
def eliminar_set_lego(numero: str):
    try:
        with get_connection() as conn:
            anterior = conn.execute("SELECT * FROM set_lego WHERE numero = ?", (numero,)).fetchone()
            if not anterior:
                raise HTTPException(404, "No se encontró el set.")
            conn.execute("DELETE FROM set_lego WHERE numero = ?", (numero,))
    except sqlite3.IntegrityError:
        raise HTTPException(409, "No se puede eliminar el set.")


# ==================== Minifiguras ====================
# Consulta base: trae cada fila de minifigura con el nombre de sus datos relacionados.
CONSULTA_MINIFIGURA = """
SELECT t.*,
       (SELECT nombre FROM set_lego WHERE numero = t.set_lego) AS set_lego_nombre
FROM minifigura t
"""


@app.get("/api/minifiguras")
def listar_minifiguras():
    with get_connection() as conn:
        return [dict(fila) for fila in conn.execute(CONSULTA_MINIFIGURA + " ORDER BY t.nombre")]


@app.get("/api/minifiguras/{id}")
def obtener_minifigura(id: int):
    with get_connection() as conn:
        fila = conn.execute(CONSULTA_MINIFIGURA + " WHERE t.id = ?", (id,)).fetchone()
    if not fila:
        raise HTTPException(404, "No se encontró la minifigura.")
    return dict(fila)


@app.post("/api/minifiguras", status_code=201)
def crear_minifigura(datos: Minifigura):
    nuevo = datos.model_dump(mode="json")
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO minifigura (nombre, set_lego, cantidad) VALUES (:nombre, :set_lego, :cantidad)", nuevo)
            nuevo["id"] = cursor.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(409, "Revise los datos: alguno de los registros relacionados no existe.")
    return nuevo


@app.put("/api/minifiguras/{id}")
def actualizar_minifigura(id: int, datos: Minifigura):
    nuevo = datos.model_dump(mode="json")
    try:
        with get_connection() as conn:
            anterior = conn.execute("SELECT * FROM minifigura WHERE id = ?", (id,)).fetchone()
            if not anterior:
                raise HTTPException(404, "No se encontró la minifigura.")
            conn.execute("UPDATE minifigura SET nombre = :nombre, set_lego = :set_lego, cantidad = :cantidad WHERE id = :pk_url", {**nuevo, "pk_url": id})
    except sqlite3.IntegrityError:
        raise HTTPException(409, "Revise los datos: alguno de los registros relacionados no existe.")
    return {"id": id, **nuevo}


@app.delete("/api/minifiguras/{id}", status_code=204)
def eliminar_minifigura(id: int):
    try:
        with get_connection() as conn:
            anterior = conn.execute("SELECT * FROM minifigura WHERE id = ?", (id,)).fetchone()
            if not anterior:
                raise HTTPException(404, "No se encontró la minifigura.")
            conn.execute("DELETE FROM minifigura WHERE id = ?", (id,))
    except sqlite3.IntegrityError:
        raise HTTPException(409, "No se puede eliminar la minifigura.")


# ==================== Piezas faltantes ====================
# Consulta base: trae cada fila de pieza_faltante con el nombre de sus datos relacionados.
CONSULTA_PIEZA_FALTANTE = """
SELECT t.*,
       (SELECT nombre FROM set_lego WHERE numero = t.set_lego) AS set_lego_nombre
FROM pieza_faltante t
"""


@app.get("/api/faltantes")
def listar_faltantes():
    with get_connection() as conn:
        return [dict(fila) for fila in conn.execute(CONSULTA_PIEZA_FALTANTE + " ORDER BY t.id DESC")]


@app.get("/api/faltantes/{id}")
def obtener_pieza_faltante(id: int):
    with get_connection() as conn:
        fila = conn.execute(CONSULTA_PIEZA_FALTANTE + " WHERE t.id = ?", (id,)).fetchone()
    if not fila:
        raise HTTPException(404, "No se encontró la pieza.")
    return dict(fila)


@app.post("/api/faltantes", status_code=201)
def crear_pieza_faltante(datos: PiezaFaltante):
    nuevo = datos.model_dump(mode="json")
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO pieza_faltante (set_lego, descripcion, color, cantidad) VALUES (:set_lego, :descripcion, :color, :cantidad)", nuevo)
            nuevo["id"] = cursor.lastrowid
            regla_faltantes(conn, nuevo, None)
    except sqlite3.IntegrityError:
        raise HTTPException(409, "Revise los datos: alguno de los registros relacionados no existe.")
    return nuevo


@app.put("/api/faltantes/{id}")
def actualizar_pieza_faltante(id: int, datos: PiezaFaltante):
    nuevo = datos.model_dump(mode="json")
    try:
        with get_connection() as conn:
            anterior = conn.execute("SELECT * FROM pieza_faltante WHERE id = ?", (id,)).fetchone()
            if not anterior:
                raise HTTPException(404, "No se encontró la pieza.")
            conn.execute("UPDATE pieza_faltante SET set_lego = :set_lego, descripcion = :descripcion, color = :color, cantidad = :cantidad WHERE id = :pk_url", {**nuevo, "pk_url": id})
            regla_faltantes(conn, nuevo, anterior)
    except sqlite3.IntegrityError:
        raise HTTPException(409, "Revise los datos: alguno de los registros relacionados no existe.")
    return {"id": id, **nuevo}


@app.delete("/api/faltantes/{id}", status_code=204)
def eliminar_pieza_faltante(id: int):
    try:
        with get_connection() as conn:
            anterior = conn.execute("SELECT * FROM pieza_faltante WHERE id = ?", (id,)).fetchone()
            if not anterior:
                raise HTTPException(404, "No se encontró la pieza.")
            conn.execute("DELETE FROM pieza_faltante WHERE id = ?", (id,))
            regla_faltantes(conn, None, anterior)
    except sqlite3.IntegrityError:
        raise HTTPException(409, "No se puede eliminar la pieza.")


# ==================== Resumen ====================
@app.get("/api/resumen")
def resumen():
    """Calcula estadísticas con consultas SQL para la pantalla de resumen."""
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*), COALESCE(SUM(piezas), 0), COALESCE(SUM(precio), 0) FROM set_lego").fetchone()
        minifiguras = conn.execute("SELECT COALESCE(SUM(cantidad), 0) FROM minifigura").fetchone()[0]
        incompletos = conn.execute("SELECT nombre, piezas_faltantes FROM set_lego WHERE piezas_faltantes > 0 ORDER BY nombre").fetchall()
        favorito = conn.execute(
            """SELECT t.nombre, COUNT(*) AS sets FROM set_lego s JOIN tema t ON t.id = s.tema
               GROUP BY t.id ORDER BY sets DESC LIMIT 1""").fetchone()
    return [
        {"dato": "Sets en la colección", "valor": str(total[0])},
        {"dato": "Piezas en total", "valor": f"{total[1]:,}".replace(",", " ")},
        {"dato": "Minifiguras", "valor": str(minifiguras)},
        {"dato": "Valor de la colección", "valor": f"₡{total[2]:,.0f}".replace(",", " ")},
        {"dato": "Tema con más sets", "valor": f"{favorito['nombre']} ({favorito['sets']})" if favorito else "Aún no hay sets"},
        {"dato": "Sets incompletos",
         "valor": ", ".join(f"{s['nombre']} (faltan {s['piezas_faltantes']})" for s in incompletos) or "Ninguno"},
    ]


# El frontend vive en public/. Vercel publica esa carpeta por su cuenta,
# así que solo se monta desde FastAPI cuando el proyecto corre en la computadora.
# Va al final para que las rutas /api y /docs tengan prioridad.
if not os.environ.get("VERCEL"):
    app.mount("/", StaticFiles(directory=Path(__file__).parent / "public", html=True), name="frontend")
