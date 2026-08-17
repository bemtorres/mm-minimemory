"""Gestión del conocimiento, perfil y memoria de cada agente.

Cada agente vive en su propia carpeta dentro de `agents/`. Una carpeta
con un nombre único equivale a un agente. Dentro de cada carpeta se
guardan los archivos:

- perfil.txt          -> datos de la persona representada.
- conocimiento.txt    -> conocimientos previos en los que se basan las respuestas.
- memoria.txt         -> información aprendida durante las conversaciones.
- conversacion.csv    -> historial completo de la conversación.

Este módulo solo trabaja con los archivos; la clase Agente (agente.py)
es quien conversa con DeepSeek.
"""

import os
import re

# Carpeta raíz donde vive cada agente.
DIRECTORIO_AGENTES = "agents"

# Identidad por defecto de un agente nuevo.
IDENTIDAD_DEFECTO = "basic"

# Plantilla de perfil que se asigna a un agente nuevo.
PERFIL_INICIAL = """NOMBRE:
Benjamín Mora

PROFESIÓN:
Docente y desarrollador de software.

EXPERIENCIA:
Experiencia en docencia, desarrollo de aplicaciones web,
modelamiento de soluciones informáticas y tecnología educativa.

CONOCIMIENTOS:
Python
Django
Laravel
Angular
MySQL
Apache
UML
BPMN

PERSONALIDAD:
Práctico
Directo
Analítico
Orientado a soluciones

FORMA DE COMUNICARSE:
Utiliza un lenguaje claro, directo y profesional.
Prefiere explicaciones prácticas y ejemplos.

INTERESES:
Tecnología
Educación
Desarrollo de software

OBJETIVOS:
Crear soluciones tecnológicas.
Mejorar procesos educativos.
Enseñar tecnología de manera práctica.
"""

# Cabecera del historial de conversación.
CABECERA_CSV = "fecha,hora,rol,mensaje\n"


def ruta_agente(nombre, archivo):
    """Devuelve la ruta de un archivo dentro de la carpeta del agente."""
    return os.path.join(DIRECTORIO_AGENTES, nombre, archivo)


def listar_agentes():
    """Devuelve los nombres de los agentes existentes (sus carpetas)."""
    if not os.path.isdir(DIRECTORIO_AGENTES):
        return []
    return sorted(
        nombre
        for nombre in os.listdir(DIRECTORIO_AGENTES)
        if os.path.isdir(os.path.join(DIRECTORIO_AGENTES, nombre))
        and not nombre.startswith(".")
    )


def crear_agente(nombre):
    """Crea la carpeta y los archivos iniciales de un agente nuevo.

    No se crean archivos de identidad: el agente empieza con la
    identidad 'basic'. identidad.txt o identidad_custom.txt se crean
    solo cuando se eligen, y son mutuamente excluyentes.

    Devuelve el nombre normalizado del agente.
    """
    nombre = nombre.strip()
    os.makedirs(os.path.join(DIRECTORIO_AGENTES, nombre), exist_ok=True)
    iniciales = {
        "perfil.txt": PERFIL_INICIAL,
        "conocimiento.txt": "",
        "memoria.txt": "",
        "conversacion.csv": CABECERA_CSV,
    }
    for archivo, contenido in iniciales.items():
        ruta = ruta_agente(nombre, archivo)
        if not os.path.exists(ruta):
            with open(ruta, "w", encoding="utf-8") as archivo_datos:
                archivo_datos.write(contenido)
    return nombre


def _leer_archivo(nombre, archivo, contenido_inicial=""):
    """Lee un archivo del agente. Si no existe, lo crea con contenido inicial."""
    ruta = ruta_agente(nombre, archivo)
    if os.path.exists(ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as archivo_datos:
                return archivo_datos.read().strip()
        except (UnicodeDecodeError, OSError):
            return contenido_inicial.strip()
    crear_agente(nombre)
    with open(ruta, "w", encoding="utf-8") as archivo_datos:
        archivo_datos.write(contenido_inicial)
    return contenido_inicial.strip()


def leer_perfil(nombre):
    """Devuelve el perfil del agente como texto."""
    return _leer_archivo(nombre, "perfil.txt", PERFIL_INICIAL)


def leer_conocimiento(nombre):
    """Devuelve el conocimiento previo del agente como texto."""
    return _leer_archivo(nombre, "conocimiento.txt", "")


def leer_memoria(nombre):
    """Devuelve la memoria del agente como texto."""
    return _leer_archivo(nombre, "memoria.txt", "")


def escribir_conocimiento(nombre, texto):
    """Sobrescribe el archivo de conocimiento del agente."""
    os.makedirs(os.path.join(DIRECTORIO_AGENTES, nombre), exist_ok=True)
    with open(ruta_agente(nombre, "conocimiento.txt"), "w", encoding="utf-8") as archivo:
        archivo.write(texto.strip() + "\n")


def _borrar_archivo(ruta):
    """Elimina un archivo si existe, sin lanzar errores."""
    try:
        os.remove(ruta)
    except OSError:
        pass


def _leer_si_existe(nombre, archivo):
    """Lee un archivo del agente si existe; si no, devuelve ''."""
    ruta = ruta_agente(nombre, archivo)
    if os.path.exists(ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as archivo_datos:
                return archivo_datos.read().strip()
        except (UnicodeDecodeError, OSError):
            return ""
    return ""


def leer_identidad(nombre):
    """Devuelve la clave predefinida de identidad.txt, o '' si no existe.

    Los agentes con identidad personalizada no tienen identidad.txt
    (escribir_identidad_custom lo elimina).
    """
    return _leer_si_existe(nombre, "identidad.txt")


def escribir_identidad(nombre, contenido):
    """Usa una identidad predefinida.

    Guarda la clave en identidad.txt y elimina identidad_custom.txt,
    porque las dos identidades son mutuamente excluyentes.
    """
    contenido = contenido.strip() or IDENTIDAD_DEFECTO
    _borrar_archivo(ruta_agente(nombre, "identidad_custom.txt"))
    os.makedirs(os.path.join(DIRECTORIO_AGENTES, nombre), exist_ok=True)
    with open(ruta_agente(nombre, "identidad.txt"), "w", encoding="utf-8") as archivo:
        archivo.write(contenido)
    return contenido


def leer_identidad_custom(nombre):
    """Devuelve el prompt personalizado de identidad_custom.txt, o ''."""
    return _leer_si_existe(nombre, "identidad_custom.txt")


def escribir_identidad_custom(nombre, contenido):
    """Usa una identidad personalizada.

    Guarda el prompt en identidad_custom.txt y elimina identidad.txt,
    porque la identidad personalizada reemplaza a la predefinida.
    """
    contenido = contenido.strip()
    _borrar_archivo(ruta_agente(nombre, "identidad.txt"))
    os.makedirs(os.path.join(DIRECTORIO_AGENTES, nombre), exist_ok=True)
    with open(ruta_agente(nombre, "identidad_custom.txt"), "w", encoding="utf-8") as archivo:
        archivo.write(contenido + "\n")
    return contenido


def borrar_identidad_custom(nombre):
    """Elimina identidad_custom.txt (vuelve a valer identidad.txt)."""
    _borrar_archivo(ruta_agente(nombre, "identidad_custom.txt"))
    return ""


def borrar_memoria(nombre):
    """Borra la memoria del agente. El perfil y el conocimiento no cambian."""
    os.makedirs(os.path.join(DIRECTORIO_AGENTES, nombre), exist_ok=True)
    with open(ruta_agente(nombre, "memoria.txt"), "w", encoding="utf-8") as archivo:
        archivo.write("")
    return leer_memoria(nombre)


def _normalizar(texto):
    """Reduce un texto a una forma comparable (sin espacios ni mayúsculas)."""
    return " ".join(texto.lower().split())


def _dividir_memorias(texto):
    """Divide la respuesta del modelo en memorias individuales."""
    memorias = []
    for bloque in re.split(r"\n\s*\n", texto.strip()):
        lineas = [linea.strip() for linea in bloque.splitlines() if linea.strip()]
        if not lineas:
            continue
        # Si todas las líneas empiezan con una viñeta o número,
        # cada una es una memoria independiente.
        es_lista = all(re.match(r"^[-*•\d.]+\)?\s*", linea) for linea in lineas)
        if es_lista:
            for linea in lineas:
                limpia = re.sub(r"^[-*•\d.]+\)?\s*", "", linea)
                if limpia:
                    memorias.append(limpia)
        else:
            memorias.append(" ".join(lineas))
    return memorias


def agregar_memorias(nombre, texto_nuevo):
    """Agrega memorias nuevas al agente evitando duplicados.

    La comparación es básica (texto normalizado) y suficiente para
    esta primera versión del proyecto.
    """
    existentes = _normalizar(leer_memoria(nombre))
    agregadas = []
    for memoria in _dividir_memorias(texto_nuevo):
        normalizada = _normalizar(memoria)
        if not normalizada:
            continue
        # Evita duplicados contra la memoria ya almacenada.
        if normalizada in existentes:
            continue
        # Evita duplicados dentro de la misma tanda de nuevas memorias.
        if any(
            normalizada in _normalizar(agregada)
            or _normalizar(agregada) in normalizada
            for agregada in agregadas
        ):
            continue
        agregadas.append(memoria)

    if agregadas:
        os.makedirs(os.path.join(DIRECTORIO_AGENTES, nombre), exist_ok=True)
        with open(ruta_agente(nombre, "memoria.txt"), "a", encoding="utf-8") as archivo:
            for memoria in agregadas:
                archivo.write(memoria + "\n\n")
    return agregadas
