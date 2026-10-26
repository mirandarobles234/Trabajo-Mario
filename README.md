# Brick Vault

Aplicación web para llevar el control de una colección de sets LEGO: temas, sets, minifiguras y piezas faltantes.

## Descripción

Quien colecciona sets LEGO llega a tener decenas de cajas, minifiguras y piezas sueltas. Sin un registro es fácil olvidar qué sets se tienen, comprar uno repetido o no saber cuáles están incompletos. Brick Vault permite registrar toda la colección y calcula automáticamente cuántas piezas le faltan a cada set, el valor total de la colección y otros datos de resumen.

**Funcionalidades principales**

- Registrar, consultar, modificar y eliminar temas, sets, minifiguras y piezas faltantes (CRUD completo).
- Relacionar cada set con un tema, y cada minifigura o pieza faltante con un set.
- Actualizar automáticamente el contador de piezas faltantes de cada set.
- Mostrar un resumen con el total de sets, piezas, minifiguras, valor de la colección y sets incompletos.
- Impedir que se elimine un tema que todavía tiene sets asociados.

El análisis completo (problema, objetivo, usuarios y diseño de la base de datos) está en [`docs/analisis.md`](docs/analisis.md) y el diagrama entidad-relación en [`docs/diagrama_er.png`](docs/diagrama_er.png).

## Tecnologías utilizadas

| Parte | Tecnología |
|---|---|
| Backend | Python 3 y FastAPI |
| Base de datos | SQLite |
| Frontend | HTML, CSS y JavaScript |
| Servidor local | Uvicorn |
| Control de versiones | Git y GitHub |
| Publicación | Vercel |

## Instalación

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/USUARIO/brick-vault.git
   cd brick-vault
   ```

2. Crear y activar un entorno virtual:

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. Instalar las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

## Ejecución

```bash
uvicorn main:app --reload
```

Luego abrir en el navegador:

- Aplicación: http://127.0.0.1:8000
- Documentación de la API: http://127.0.0.1:8000/docs

La primera vez que se ejecuta, el sistema crea las tablas de `brick_vault.db` y carga unos datos de ejemplo.

## Estructura del sistema

```
brick-vault/
├── main.py            # API con FastAPI: modelos, endpoints CRUD y reglas de negocio
├── database.py        # Conexión a SQLite, creación de tablas y datos de ejemplo
├── brick_vault.db     # Base de datos SQLite
├── requirements.txt   # Dependencias de Python
├── public/            # Frontend
│   ├── index.html
│   ├── styles.css
│   └── app.js         # Consume la API con fetch()
└── docs/
    ├── analisis.md    # Análisis y diseño
    └── diagrama_er.png
```

**Flujo:** Frontend (`public/`) → API FastAPI (`main.py`) → SQLite (`database.py` / `brick_vault.db`)

### Endpoints de la API

| Recurso | Endpoints |
|---|---|
| Temas | `GET /api/temas` · `GET /api/temas/{id}` · `POST /api/temas` · `PUT /api/temas/{id}` · `DELETE /api/temas/{id}` |
| Sets | `GET /api/sets` · `GET /api/sets/{numero}` · `POST /api/sets` · `PUT /api/sets/{numero}` · `DELETE /api/sets/{numero}` |
| Minifiguras | `GET /api/minifiguras` · `GET /api/minifiguras/{id}` · `POST /api/minifiguras` · `PUT /api/minifiguras/{id}` · `DELETE /api/minifiguras/{id}` |
| Piezas faltantes | `GET /api/faltantes` · `GET /api/faltantes/{id}` · `POST /api/faltantes` · `PUT /api/faltantes/{id}` · `DELETE /api/faltantes/{id}` |
| Resumen | `GET /api/resumen` |

## Publicación

- Aplicación en Vercel: https://ENLACE-DE-VERCEL.vercel.app
- Repositorio: https://github.com/USUARIO/brick-vault

> En Vercel, el sistema de archivos es de solo lectura, por lo que la base SQLite se crea en `/tmp`. Los cambios funcionan mientras el servidor está activo, pero pueden reiniciarse a los datos de ejemplo cuando Vercel apaga la instancia. En la ejecución local los datos quedan guardados de forma permanente en `brick_vault.db`.
