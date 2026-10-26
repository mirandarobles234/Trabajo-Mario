# Análisis y diseño: Brick Vault

## Nombre del proyecto

Brick Vault: control de una colección de sets LEGO.

## Descripción del problema

Una persona que colecciona sets LEGO llega a tener decenas de cajas, minifiguras y piezas sueltas. Sin un registro es fácil olvidar qué sets tiene, comprar uno repetido, no saber cuáles están incompletos ni qué piezas hay que reponer, y desconocer cuánto vale la colección.

## Objetivo general

Desarrollar una aplicación web que permita registrar los sets de una colección LEGO con sus temas, minifiguras y piezas faltantes, y que indique automáticamente qué sets están incompletos.

## Principales funcionalidades

- Registrar, consultar, modificar y eliminar temas, sets, minifiguras y piezas faltantes.
- Asociar cada set a un tema y cada minifigura o pieza faltante a un set.
- Actualizar automáticamente el contador de piezas faltantes de cada set.
- Mostrar un resumen con el total de sets, de piezas, el valor de la colección y los sets incompletos.
- Impedir que se elimine un tema que todavía tiene sets.

## Usuarios del sistema

- **Coleccionista:** registra sus sets, minifiguras y las piezas que le faltan.
- **Familiar o amigo:** consulta la colección para no regalar un set repetido.

## Diseño de la base de datos

El diagrama entidad-relación está en `docs/diagrama_er.png`.

### Descripción de las tablas

| Tabla | Qué guarda | Llave primaria | Llaves foráneas |
|---|---|---|---|
| `tema` | Líneas o temas de LEGO | `id` (autoincremental) | Ninguna |
| `set_lego` | Sets de la colección | `numero` | `tema` → `tema.id` |
| `minifigura` | Minifiguras incluidas en los sets | `id` (autoincremental) | `set_lego` → `set_lego.numero` |
| `pieza_faltante` | Piezas que le faltan a un set | `id` (autoincremental) | `set_lego` → `set_lego.numero` |

### Relaciones

| Relación | Tipo | Explicación |
|---|---|---|
| tema – set_lego | 1 a N | Cada fila de `set_lego` guarda en `tema` a cuál fila de `tema` pertenece |
| set_lego – minifigura | 1 a N | Cada fila de `minifigura` guarda en `set_lego` a cuál fila de `set_lego` pertenece |
| set_lego – pieza_faltante | 1 a N | Cada fila de `pieza_faltante` guarda en `set_lego` a cuál fila de `set_lego` pertenece |

### Reglas de integridad

- Se activan las llaves foráneas de SQLite con `PRAGMA foreign_keys = ON` en cada conexión.
- `ON DELETE RESTRICT` en `set_lego.tema`: no se puede eliminar un registro que otro todavía usa.
- `ON DELETE CASCADE` en `minifigura.set_lego`, `pieza_faltante.set_lego`: al eliminar el registro principal se eliminan sus detalles.
- Restricciones `CHECK`: las cantidades y los montos no pueden ser negativos.

### Regla de negocio

`set_lego.piezas_faltantes` = suma de `cantidad` de todas las filas de `pieza_faltante` de ese set. El backend la recalcula cada vez que se agrega, modifica o elimina una pieza faltante.
