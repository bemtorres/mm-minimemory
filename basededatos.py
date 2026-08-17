"""Base de datos SQLite para la versión web de los agentes.

Sustituye a los archivos de texto (`agents/`) en la versión web: los datos
de cada agente (perfil, conocimiento, memoria, identidad) y las
conversaciones se guardan en `agentes.db`.

La versión de consola (`main.py`) sigue usando los archivos de `agents/`.
Para llenar la base de datos con los agentes existentes, ejecuta:

    python seed.py
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime

from agente import Agente, HISTORIAL_RECIENTE, SIN_MEMORIA
from memoria import _dividir_memorias, _normalizar
from prompt import construir_prompt_memoria

# Archivo de la base de datos (se crea automáticamente al usarla).
BASE_DATOS = "agentes.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS agentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    perfil TEXT NOT NULL DEFAULT '',
    conocimiento TEXT NOT NULL DEFAULT '',
    memoria TEXT NOT NULL DEFAULT '',
    identidad_clave TEXT NOT NULL DEFAULT '',
    identidad_custom TEXT NOT NULL DEFAULT '',
    creado_en TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS conversaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agente_id INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    hora TEXT NOT NULL,
    rol TEXT NOT NULL,
    mensaje TEXT NOT NULL,
    FOREIGN KEY (agente_id) REFERENCES agentes(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_conversaciones_agente
ON conversaciones(agente_id);

CREATE TABLE IF NOT EXISTS fuentes_conocimiento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    contenido TEXT NOT NULL DEFAULT '',
    creado_en TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS agente_fuentes (
    agente_id INTEGER NOT NULL,
    fuente_id INTEGER NOT NULL,
    PRIMARY KEY (agente_id, fuente_id),
    FOREIGN KEY (agente_id) REFERENCES agentes(id) ON DELETE CASCADE,
    FOREIGN KEY (fuente_id) REFERENCES fuentes_conocimiento(id) ON DELETE CASCADE
);
"""


@contextmanager
def _conexion():
    """Abre una conexión a SQLite: confirma al terminar y cierra siempre."""
    conexion = sqlite3.connect(BASE_DATOS)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    try:
        yield conexion
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def inicializar():
    """Crea las tablas de la base de datos si no existen."""
    with _conexion() as conexion:
        conexion.executescript(SCHEMA)
    migrar_conocimientos_legacy()


def vaciar():
    """Borra todos los agentes, conversaciones y fuentes (re-sembrar)."""
    with _conexion() as conexion:
        conexion.execute("DELETE FROM agente_fuentes")
        conexion.execute("DELETE FROM conversaciones")
        conexion.execute("DELETE FROM agentes")
        conexion.execute("DELETE FROM fuentes_conocimiento")


def listar_agentes():
    """Devuelve los nombres de los agentes de la base de datos."""
    with _conexion() as conexion:
        filas = conexion.execute(
            "SELECT nombre FROM agentes ORDER BY nombre"
        ).fetchall()
    return [fila["nombre"] for fila in filas]


def existe_agente(nombre):
    """True si el agente existe en la base de datos."""
    with _conexion() as conexion:
        fila = conexion.execute(
            "SELECT 1 FROM agentes WHERE nombre = ?", (nombre,)
        ).fetchone()
    return fila is not None


def crear_agente(
    nombre,
    perfil="",
    conocimiento="",
    identidad_clave="",
    identidad_custom="",
    memoria="",
    fuentes_ids=None,
):
    """Crea un agente nuevo en la base de datos y asocia sus fuentes si se pasan."""
    with _conexion() as conexion:
        conexion.execute(
            """INSERT INTO agentes
               (nombre, perfil, conocimiento, memoria,
                identidad_clave, identidad_custom)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                nombre,
                perfil,
                conocimiento,
                memoria,
                identidad_clave,
                identidad_custom,
            ),
        )
    if fuentes_ids:
        establecer_fuentes_agente(nombre, fuentes_ids)



def obtener_agente(nombre):
    """Devuelve un dict con los datos del agente, o None si no existe."""
    with _conexion() as conexion:
        fila = conexion.execute(
            "SELECT * FROM agentes WHERE nombre = ?", (nombre,)
        ).fetchone()
    return dict(fila) if fila else None


def leer_memoria(nombre):
    """Devuelve la memoria del agente como texto."""
    datos = obtener_agente(nombre)
    return datos["memoria"] if datos else ""


def guardar_mensaje(nombre, rol, mensaje, fecha=None, hora=None):
    """Guarda un mensaje en la conversación del agente.

    Si no se pasan fecha/hora, se usan la fecha y hora actuales.
    """
    ahora = datetime.now()
    fecha = fecha or ahora.strftime("%Y-%m-%d")
    hora = hora or ahora.strftime("%H:%M")
    mensaje = " ".join(str(mensaje).split())
    with _conexion() as conexion:
        fila = conexion.execute(
            "SELECT id FROM agentes WHERE nombre = ?", (nombre,)
        ).fetchone()
        if not fila:
            return
        conexion.execute(
            """INSERT INTO conversaciones (agente_id, fecha, hora, rol, mensaje)
               VALUES (?, ?, ?, ?, ?)""",
            (fila["id"], fecha, hora, rol, mensaje),
        )


def obtener_historial(nombre, cantidad=HISTORIAL_RECIENTE):
    """Devuelve los últimos mensajes como lista de tuplas (rol, mensaje)."""
    with _conexion() as conexion:
        fila = conexion.execute(
            "SELECT id FROM agentes WHERE nombre = ?", (nombre,)
        ).fetchone()
        if not fila:
            return []
        filas = conexion.execute(
            """SELECT rol, mensaje FROM conversaciones
               WHERE agente_id = ? ORDER BY id DESC LIMIT ?""",
            (fila["id"], cantidad),
        ).fetchall()
    return [(fila["rol"], fila["mensaje"]) for fila in reversed(filas)]


def actualizar_conocimiento(nombre, texto):
    """Sobrescribe el conocimiento del agente."""
    with _conexion() as conexion:
        conexion.execute(
            "UPDATE agentes SET conocimiento = ? WHERE nombre = ?",
            (texto.strip(), nombre),
        )


# ----------------------------------------------------------------------
# Fuentes de conocimiento (base de datos compartida)
# ----------------------------------------------------------------------


def listar_fuentes():
    """Devuelve todas las fuentes de conocimiento con el número de agentes asociados."""
    with _conexion() as conexion:
        filas = conexion.execute(
            """SELECT f.id, f.nombre, f.contenido, f.creado_en,
                      COUNT(af.agente_id) AS total_agentes
               FROM fuentes_conocimiento f
               LEFT JOIN agente_fuentes af ON af.fuente_id = f.id
               GROUP BY f.id
               ORDER BY f.nombre"""
        ).fetchall()
    return [dict(fila) for fila in filas]


def obtener_fuente(fuente_id):
    """Devuelve los datos de una fuente por su ID, o None si no existe."""
    with _conexion() as conexion:
        fila = conexion.execute(
            """SELECT f.id, f.nombre, f.contenido, f.creado_en,
                      COUNT(af.agente_id) AS total_agentes
               FROM fuentes_conocimiento f
               LEFT JOIN agente_fuentes af ON af.fuente_id = f.id
               WHERE f.id = ?
               GROUP BY f.id""",
            (fuente_id,),
        ).fetchone()
    return dict(fila) if fila else None


def crear_fuente(nombre, contenido=""):
    """Crea una fuente de conocimiento nueva y devuelve su id.

    Lanza ValueError si el nombre está vacío o ya existe.
    """
    nombre = nombre.strip()
    contenido = contenido.strip()
    if not nombre:
        raise ValueError("El nombre de la base de conocimiento no puede estar vacío.")
    with _conexion() as conexion:
        existe = conexion.execute(
            "SELECT 1 FROM fuentes_conocimiento WHERE nombre = ?", (nombre,)
        ).fetchone()
        if existe:
            raise ValueError(f"La base de conocimiento '{nombre}' ya existe.")
        cursor = conexion.execute(
            "INSERT INTO fuentes_conocimiento (nombre, contenido) VALUES (?, ?)",
            (nombre, contenido),
        )
        return cursor.lastrowid


def actualizar_fuente(fuente_id, nombre, contenido=""):
    """Actualiza el nombre y contenido de una fuente de conocimiento existente."""
    nombre = nombre.strip()
    contenido = contenido.strip()
    if not nombre:
        raise ValueError("El nombre de la base de conocimiento no puede estar vacío.")
    with _conexion() as conexion:
        duplicado = conexion.execute(
            "SELECT 1 FROM fuentes_conocimiento WHERE nombre = ? AND id != ?",
            (nombre, fuente_id),
        ).fetchone()
        if duplicado:
            raise ValueError(f"Ya existe otra base de conocimiento con el nombre '{nombre}'.")
        conexion.execute(
            "UPDATE fuentes_conocimiento SET nombre = ?, contenido = ? WHERE id = ?",
            (nombre, contenido, fuente_id),
        )


def eliminar_fuente(fuente_id):
    """Elimina una fuente y quita su selección de todos los agentes."""
    with _conexion() as conexion:
        conexion.execute(
            "DELETE FROM agente_fuentes WHERE fuente_id = ?", (fuente_id,)
        )
        conexion.execute(
            "DELETE FROM fuentes_conocimiento WHERE id = ?", (fuente_id,)
        )


def obtener_fuentes_agente(nombre):
    """Devuelve las fuentes de conocimiento seleccionadas por un agente."""
    with _conexion() as conexion:
        agente = conexion.execute(
            "SELECT id FROM agentes WHERE nombre = ?", (nombre,)
        ).fetchone()
        if not agente:
            return []
        filas = conexion.execute(
            """SELECT f.id, f.nombre, f.contenido
               FROM fuentes_conocimiento f
               JOIN agente_fuentes af ON af.fuente_id = f.id
               WHERE af.agente_id = ?
               ORDER BY f.nombre""",
            (agente["id"],),
        ).fetchall()
    return [dict(fila) for fila in filas]


def establecer_fuentes_agente(nombre, ids):
    """Reemplaza la selección de fuentes de un agente por la lista dada."""
    ids = [int(i) for i in ids if str(i).strip().lstrip("-").isdigit()]
    with _conexion() as conexion:
        agente = conexion.execute(
            "SELECT id FROM agentes WHERE nombre = ?", (nombre,)
        ).fetchone()
        if not agente:
            return
        agente_id = agente["id"]
        conexion.execute(
            "DELETE FROM agente_fuentes WHERE agente_id = ?", (agente_id,)
        )
        if not ids:
            return
        marcadores = ",".join("?" for _ in ids)
        filas = conexion.execute(
            f"SELECT id FROM fuentes_conocimiento WHERE id IN ({marcadores})",
            tuple(ids),
        ).fetchall()
        for fila in filas:
            conexion.execute(
                "INSERT INTO agente_fuentes (agente_id, fuente_id) VALUES (?, ?)",
                (agente_id, fila["id"]),
            )


def migrar_conocimientos_legacy():
    """Convierte el conocimiento manual de agentes antiguos en fuentes.

    Por cada agente con `conocimiento` propio y sin fuentes seleccionadas
    se crea una fuente con su nombre, se selecciona y se limpia la columna
    antigua. Así el conocimiento sigue funcionando con el nuevo modelo.
    """
    with _conexion() as conexion:
        filas = conexion.execute(
            "SELECT id, nombre, conocimiento FROM agentes WHERE conocimiento != ''"
        ).fetchall()
        for agente in filas:
            ya_tiene = conexion.execute(
                "SELECT 1 FROM agente_fuentes WHERE agente_id = ? LIMIT 1",
                (agente["id"],),
            ).fetchone()
            if ya_tiene:
                continue
            fuente = conexion.execute(
                "SELECT id FROM fuentes_conocimiento WHERE nombre = ?",
                (agente["nombre"],),
            ).fetchone()
            if fuente:
                fuente_id = fuente["id"]
            else:
                cursor = conexion.execute(
                    "INSERT INTO fuentes_conocimiento (nombre, contenido) VALUES (?, ?)",
                    (agente["nombre"], agente["conocimiento"]),
                )
                fuente_id = cursor.lastrowid
            conexion.execute(
                "INSERT INTO agente_fuentes (agente_id, fuente_id) VALUES (?, ?)",
                (agente["id"], fuente_id),
            )
            conexion.execute(
                "UPDATE agentes SET conocimiento = '' WHERE id = ?",
                (agente["id"],),
            )


def actualizar_perfil(nombre, texto):
    """Sobrescribe el perfil (información de la persona) del agente."""
    with _conexion() as conexion:
        conexion.execute(
            "UPDATE agentes SET perfil = ? WHERE nombre = ?",
            (texto.strip(), nombre),
        )


def borrar_memoria(nombre):
    """Borra la memoria del agente (perfil y conocimiento no cambian)."""
    with _conexion() as conexion:
        conexion.execute(
            "UPDATE agentes SET memoria = '' WHERE nombre = ?", (nombre,)
        )


def cambiar_identidad(nombre, clave="", custom=""):
    """Cambia la identidad del agente (clave predefinida o personalizada)."""
    with _conexion() as conexion:
        conexion.execute(
            """UPDATE agentes
               SET identidad_clave = ?, identidad_custom = ?
               WHERE nombre = ?""",
            (clave.strip(), custom.strip(), nombre),
        )


def agregar_memorias(nombre, texto_nuevo):
    """Agrega memorias nuevas al agente en la base de datos, evitando duplicados."""
    actual = leer_memoria(nombre)
    existentes = _normalizar(actual)
    agregadas = []
    for memoria in _dividir_memorias(texto_nuevo):
        normalizada = _normalizar(memoria)
        if not normalizada or normalizada in existentes:
            continue
        if any(
            normalizada in _normalizar(agregada)
            or _normalizar(agregada) in normalizada
            for agregada in agregadas
        ):
            continue
        agregadas.append(memoria)
    if agregadas:
        texto = actual.strip()
        if texto:
            texto += "\n\n" + "\n\n".join(agregadas)
        else:
            texto = "\n\n".join(agregadas)
        with _conexion() as conexion:
            conexion.execute(
                "UPDATE agentes SET memoria = ? WHERE nombre = ?",
                (texto, nombre),
            )
    return agregadas


class AgenteDB(Agente):
    """Agente que guarda sus datos en SQLite en lugar de archivos.

    Hereda toda la lógica de conversación de `Agente` (construcción del
    prompt, llamadas a DeepSeek y memoria automática) y solo cambia la
    forma de persistir los datos: en lugar de archivos en `agents/`,
    usa la base de datos `agentes.db`.
    """

    def cargar_perfil(self):
        datos = obtener_agente(self.nombre)
        self.perfil = datos["perfil"] if datos else ""

    def cargar_conocimiento(self):
        """Construye el conocimiento desde las bases de conocimiento asociadas.

        Se compila el contenido de las bases activas. Si quedara
        conocimiento manual antiguo (columna `conocimiento`), se agrega
        como respaldo.
        """
        datos = obtener_agente(self.nombre)
        fuentes = obtener_fuentes_agente(self.nombre)
        partes = []
        for fuente in fuentes:
            texto = (fuente.get("contenido") or "").strip()
            if texto:
                nombre_fuente = fuente.get("nombre", "").strip()
                if nombre_fuente:
                    partes.append(f"[{nombre_fuente}]\n{texto}")
                else:
                    partes.append(texto)
        manual = (datos["conocimiento"] if datos else "").strip()
        if manual:
            partes.append(manual)
        self.conocimiento = "\n\n".join(partes)

    def cargar_identidad(self):
        datos = obtener_agente(self.nombre)
        self.identidad = datos["identidad_clave"] if datos else ""
        self.identidad_custom = datos["identidad_custom"] if datos else ""

    def cargar_memoria(self):
        datos = obtener_agente(self.nombre)
        self.memoria = datos["memoria"] if datos else ""

    def guardar_conversacion(self, rol, mensaje):
        guardar_mensaje(self.nombre, rol, mensaje)

    def obtener_historial(self, cantidad=HISTORIAL_RECIENTE):
        return obtener_historial(self.nombre, cantidad)

    def actualizar_memoria(self, mensaje_usuario, respuesta):
        conversacion = f"Usuario: {mensaje_usuario}\nAgente: {respuesta}"
        prompt = construir_prompt_memoria(self.memoria, conversacion)
        try:
            contenido = self._enviar([{"role": "user", "content": prompt}])
        except RuntimeError:
            return []
        if not contenido or SIN_MEMORIA in contenido.upper():
            return []
        agregadas = agregar_memorias(self.nombre, contenido)
        if agregadas:
            self.cargar_memoria()
        return agregadas