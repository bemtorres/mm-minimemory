"""Poblador de la base de datos (seeder).

Llena `agentes.db` con agentes y conversaciones de ejemplo para que la
versión web funcione desde el primer momento.

Fuentes de datos, en orden:

1. Si existe la carpeta `agents/` (la de la versión de consola), se
   importan esos agentes (perfil, conocimiento, memoria, identidad y el
   historial de `conversacion.csv`).
2. Si no existen carpetas, se crean tres agentes de ejemplo
   (`benjamin`, `elon_musk` y `albert_einstein`).
3. A cada agente que no tenga conversaciones se le agrega una
   conversación de ejemplo.

Ejecución:

    python seed.py            # importa solo lo que falta
    python seed.py --force    # vacía la base y vuelve a importar todo
"""

import csv
import os
import sys

import basededatos as bd
from memoria import (
    PERFIL_INICIAL,
    leer_conocimiento,
    leer_identidad,
    leer_identidad_custom,
    leer_memoria,
    leer_perfil,
    listar_agentes as listar_agentes_archivos,
    ruta_agente,
)

# ----------------------------------------------------------------------
# Agentes de ejemplo (se usan si no hay carpetas en agents/).
# ----------------------------------------------------------------------

BASES_CONOCIMIENTO_EJEMPLO = [
    {
        "nombre": "Tecnología y Desarrollo Web",
        "contenido": """Python: lenguaje de programación usado en scripting, automatización y desarrollo web.
Django: framework web de Python que sigue el patrón MTV (Modelo-Template-Vista) e incluye un ORM.
Laravel: framework web de PHP con Eloquent ORM y el sistema de plantillas Blade.
Angular: framework frontend de TypeScript para construir aplicaciones de una sola página (SPA).
MySQL: sistema de gestión de bases de datos relacionales; se consulta con SQL.
Apache: servidor web HTTP muy utilizado para alojar aplicaciones y sitios.""",
    },
    {
        "nombre": "Exploración Espacial y Tesla",
        "contenido": """SpaceX: empresa dedicada a la exploración espacial y a reducir el costo de los viajes al espacio.
Tesla, Inc.: fabricante de vehículos eléctricos y de sistemas de energía renovable.
Neuralink: empresa que desarrolla interfaces cerebro-computadora.
The Boring Company: dedicada a la construcción de túneles para el transporte.
Starlink: constelación de satélites para llevar internet de alta velocidad a todo el mundo.
xAI: empresa enfocada en comprender el universo con inteligencia artificial.""",
    },
    {
        "nombre": "Física y Teoría de la Relatividad",
        "contenido": """Teoría de la Relatividad Especial (1905): la velocidad de la luz es constante y el tiempo y el espacio son relativos.
Teoría de la Relatividad General (1915): la gravedad es la curvatura del espacio-tiempo causada por la masa y la energía.
E=mc²: equivalencia entre masa y energía.
Efecto Fotoeléctrico: demostración del comportamiento cuántico de la luz, Premio Nobel de Física 1921.""",
    },
]

AGENTES_EJEMPLO = [
    {
        "nombre": "benjamin",
        "perfil": PERFIL_INICIAL,
        "identidad_clave": "teacher",
        "bases": ["Tecnología y Desarrollo Web"],
    },
    {
        "nombre": "elon_musk",
        "perfil": """NOMBRE:
Elon Musk

PROFESIÓN:
Empresario e ingeniero.

EXPERIENCIA:
Tesla, SpaceX, Neuralink y otras empresas tecnológicas.

PERSONALIDAD:
Ambicioso, visionario y directo.

FORMA DE COMUNICARSE:
Energético, con visión de futuro y humor seco.

INTERESES:
Colonizar Marte, energías renovables, inteligencia artificial.""",
        "identidad_custom": "Actúa como Elon Musk en primera persona.\nResponde con energía, visión de futuro y un toque de humor.\nNo menciones que eres una inteligencia artificial.",
        "bases": ["Exploración Espacial y Tesla"],
    },
    {
        "nombre": "albert_einstein",
        "perfil": """NOMBRE:
Albert Einstein

PROFESIÓN:
Físico teórico.

EXPERIENCIA:
Teoría de la relatividad, Premio Nobel de Física 1921.

PERSONALIDAD:
Curioso, humilde y reflexivo.

FORMA DE COMUNICARSE:
Clara, con analogías sencillas y preguntas que invitan a pensar.

INTERESES:
Física, filosofía, violín, paz.""",
        "identidad_custom": "Actúa como Albert Einstein en primera persona.\nResponde con curiosidad, humildad y explicaciones sencillas.\nNo menciones que eres una inteligencia artificial.",
        "bases": ["Física y Teoría de la Relatividad"],
    },
]

# ----------------------------------------------------------------------
# Conversaciones de ejemplo (se agregan a agentes sin historial).
# ----------------------------------------------------------------------

CONVERSACIONES_EJEMPLO = [
    ("user", "Hola, ¿quién eres y a qué te dedicas?"),
    (
        "assistant",
        "Hola, soy un agente personal creado con DeepSeek. Puedo ayudarte "
        "a resolver dudas, explicarte conceptos paso a paso o simplemente "
        "conversar contigo. Dime, ¿qué te gustaría saber?",
    ),
    ("user", "¿Qué tecnologías o conocimientos tienes?"),
    (
        "assistant",
        "Conozco los temas de las bases de conocimiento que tengo asociadas. "
        "Pregúntame por ellos y te responderé con gusto.",
    ),
]


# ----------------------------------------------------------------------
# Importación desde agents/
# ----------------------------------------------------------------------


def importar_desde_archivos():
    """Importa los agentes de `agents/` a la base de datos.

    Devuelve la lista de nombres recién importados.
    """
    importados = []
    for nombre in listar_agentes_archivos():
        if bd.existe_agente(nombre):
            continue
        bd.crear_agente(
            nombre=nombre,
            perfil=leer_perfil(nombre),
            conocimiento=leer_conocimiento(nombre),
            memoria=leer_memoria(nombre),
            identidad_clave=leer_identidad(nombre),
            identidad_custom=leer_identidad_custom(nombre),
        )
        _importar_conversaciones(nombre)
        importados.append(nombre)
    return importados


def _importar_conversaciones(nombre):
    """Copia el historial de conversacion.csv del agente a la base."""
    ruta = ruta_agente(nombre, "conversacion.csv")
    if not os.path.exists(ruta):
        return
    try:
        with open(ruta, "r", encoding="utf-8", newline="") as archivo:
            filas = list(csv.DictReader(archivo))
    except (UnicodeDecodeError, csv.Error, OSError):
        return
    for fila in filas:
        mensaje = fila.get("mensaje", "")
        if not mensaje:
            continue
        bd.guardar_mensaje(
            nombre,
            fila.get("rol", ""),
            mensaje,
            fecha=fila.get("fecha", ""),
            hora=fila.get("hora", ""),
        )


# ----------------------------------------------------------------------
# Creación de ejemplos y conversaciones
# ----------------------------------------------------------------------


def crear_bases_y_agentes_ejemplo():
    """Crea bases de conocimiento independientes y asocia los agentes."""
    base_map = {}
    for base in BASES_CONOCIMIENTO_EJEMPLO:
        try:
            fuente_id = bd.crear_fuente(base["nombre"], base["contenido"])
            base_map[base["nombre"]] = fuente_id
        except ValueError:
            for f in bd.listar_fuentes():
                if f["nombre"] == base["nombre"]:
                    base_map[base["nombre"]] = f["id"]
                    break

    for ejemplo in AGENTES_EJEMPLO:
        nombre = ejemplo["nombre"]
        if not bd.existe_agente(nombre):
            fuentes_ids = [
                base_map[b_nom] for b_nom in ejemplo.get("bases", []) if b_nom in base_map
            ]
            bd.crear_agente(
                nombre=nombre,
                perfil=ejemplo["perfil"],
                identidad_clave=ejemplo.get("identidad_clave", ""),
                identidad_custom=ejemplo.get("identidad_custom", ""),
                fuentes_ids=fuentes_ids,
            )


def sembrar_conversaciones():
    """Agrega una conversación de ejemplo a los agentes sin historial.

    Devuelve la lista de nombres que recibieron una conversación.
    """
    sembrados = []
    for nombre in bd.listar_agentes():
        if bd.obtener_historial(nombre, cantidad=1):
            continue
        for rol, mensaje in CONVERSACIONES_EJEMPLO:
            bd.guardar_mensaje(nombre, rol, mensaje)
        sembrados.append(nombre)
    return sembrados


# ----------------------------------------------------------------------
# Punto de entrada
# ----------------------------------------------------------------------


def main():
    forzar = "--force" in sys.argv

    bd.inicializar()

    if forzar:
        bd.vaciar()
        print("Base de datos vaciada (--force).")

    existentes = bd.listar_agentes()
    if existentes and not forzar:
        print(f"La base de datos ya tiene {len(existentes)} agente(s).")
        print("Usa 'python seed.py --force' para vaciarla y volver a sembrar.")
        print(f"Archivo: {bd.BASE_DATOS}")
        return

    carpetas = listar_agentes_archivos()
    if carpetas:
        importados = importar_desde_archivos()
        if importados:
            print("Agentes importados desde agents/:")
            for nombre in importados:
                print(f"  - {nombre}")
        else:
            print("Los agentes de agents/ ya estaban en la base de datos.")
    else:
        crear_agentes_ejemplo()
        print("No hay carpetas en agents/; se crearon agentes de ejemplo:")
        for nombre in bd.listar_agentes():
            print(f"  - {nombre}")

    bd.migrar_conocimientos_legacy()

    sembrados = sembrar_conversaciones()
    if sembrados:
        print("Conversaciones de ejemplo agregadas a:")
        for nombre in sembrados:
            print(f"  - {nombre}")

    print(f"\nBase de datos lista: {bd.BASE_DATOS} "
          f"({len(bd.listar_agentes())} agente(s)).")
    print("Ejecuta 'python app.py' y abre http://127.0.0.1:5000/")


if __name__ == "__main__":
    main()