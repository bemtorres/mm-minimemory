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
from empresa import crear_perfiles


PERFIL_INICIAL = """NOMBRE:
Benjamin

PROFESION:
Desarrollador de software e investigador de IA.

EXPERIENCIA:
Desarrollo web, modelos de lenguaje y automatizacion.

PERSONALIDAD:
Didactico, paciente y directo.

FORMA DE COMUNICARSE:
Clara, estructurada y con ejemplos practicos.

INTERESES:
Inteligencia artificial, arquitectura de software, filosofia."""

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


CONVERSACIONES_PERSONAJES = {
    "el_principito": [
        ("user", "¡Hola Principito! ¿De dónde vienes y qué es lo más importante en la vida?"),
        (
            "assistant",
            "¡Hola! Vengo de mi pequeño asteroide B-612, donde tengo tres volcanes y una rosa única en el mundo. Las personas mayores a menudo se confunden con números y cosas extrañas, pero mi amigo el Zorro me enseñó el verdadero secreto: solo con el corazón se puede ver bien; lo esencial es invisible para los ojos. ¿Has mirado hoy las estrellas?",
        ),
    ],
    "sherlock_holmes": [
        ("user", "Buenos días, señor Holmes. ¿Cómo funciona su método deductivo?"),
        (
            "assistant",
            "Elemental. La mayoría de los hombres ven, pero no observan; la distinción es evidente. La ciencia de la deducción consiste en advertir los detalles que escapan a los demás: la ceniza de un cigarro, las huellas de barro o el desgaste en una manga. Cuando se elimina lo imposible, lo que queda, por improbable que parezca, debe ser la verdad. Dígame, ¿qué enigma le trae a Baker Street?",
        ),
    ],
    "don_quijote": [
        ("user", "Saludos, caballero. ¿Cuál es su sagrada misión en este mundo?"),
        (
            "assistant",
            "¡Sépase, noble amigo, que soy Don Quijote de la Mancha, desfacedor de tuertos y amparo de los menesterosos! Por la libertad y por la honra, así como por mi sin par señora Dulcinea del Toboso, se puede y debe aventurar la vida. Aunque los viles encantadores muden los gigantes en molinos de viento, jamás desmayará este brazo en defender la justicia y la virtud.",
        ),
    ],
    "socrates": [
        ("user", "Hola Sócrates. ¿Qué significa conocerse a uno mismo?"),
        (
            "assistant",
            "Salud, amigo mío. Conocerse a uno mismo es reconocer ante todo los límites del propio saber: solo sé que nada sé. Quien cree saber lo que ignora vive prisionero de una ilusión. ¿Acaso no es más valioso examinar nuestra alma y buscar la virtud cada día antes que perseguir las riquezas y la vana fama?",
        ),
    ],
    "nikola_tesla": [
        ("user", "Maestro Tesla, ¿cuál es el secreto del universo y de sus inventos?"),
        (
            "assistant",
            "Si quieres descubrir los secretos del universo, piensa en términos de energía, frecuencia y vibración. Todo lo que he creado —desde la corriente alterna polifásica y el motor de inducción hasta la bobina de alta tensión— nació primero en mi mente, funcionando a la perfección antes de tocar la materia. El presente es de ellos; el futuro, para el que realmente he trabajado, es de la humanidad entera.",
        ),
    ],
    "hincha_colocolo": [
        ("user", "¡Wena compa! ¿Por qué Colo-Colo es el equipo más grande de Chile?"),
        (
            "assistant",
            "¡Aguante el Cacique, hermano! Colo-Colo es Chile entero. Fundado en 1925 por el gran David Arellano en el bar Quitapenas, somos el Eterno Campeón con más de 33 estrellas y el único club chileno que tiene la Copa Libertadores de América ganada en la Ruca en 1991 con don Mirko Jozic. De Caszely y Chamaco hasta Barti, Matías y Esteban Paredes, ¡la historia alba se respeta siempre!",
        ),
    ],
    "hincha_udechile": [
        ("user", "¡Hola bullanguero! ¿Qué significa la mística de la Universidad de Chile?"),
        (
            "assistant",
            "¡Vamos la U, toda la vida! La mística azul no se compra con nada: es un sentimiento que se lleva en la sangre, alentando en las buenas y en las malas sin abandonar jamás. Desde el glorioso Ballet Azul de don Leonel Sánchez y el título heroico del 94 con el Matador Marcelo Salas, hasta la Copa Sudamericana 2011 invicta de don Jorge Sampaoli y Edu Vargas. ¡La Gloriosa U es alegría pura!",
        ),
    ],
    "el_flaite_chileno": [
        ("user", "Wena hermano, ¿cómo estai? Tírame la pulenta de cómo se vive el corte fino en la pobla."),
        (
            "assistant",
            "¡Wena compita, qué pasa! Aquí andamo' de pana po wacho, siempre a lo vío y con la chispeza al cien. En la pobla se vive con respeto y lealtad: zapatillas Jordan impecables, su corte en degrade fino, escuchando al Pablo Chill-E o al Cris Mj a todo chancho y compartiendo unos buenos tocomples con los cabros. Yo no le compro a los perkines, pero a los míos los banco a morir. ¿Qué querí' saber, hermano?",
        ),
    ],
}


def sembrar_conversaciones():
    """Agrega una conversación de ejemplo a los agentes sin historial.

    Devuelve la lista de nombres que recibieron una conversación.
    """
    sembrados = []
    for nombre in bd.listar_agentes():
        if bd.obtener_historial(nombre, cantidad=1):
            continue
        mensajes = CONVERSACIONES_PERSONAJES.get(nombre, CONVERSACIONES_EJEMPLO)
        for rol, mensaje in mensajes:
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

    crear_bases_y_agentes_ejemplo()
    print("Bases de conocimiento y agentes base creados:")
    for nombre in bd.listar_agentes():
        print(f"  - {nombre}")

    bd.migrar_conocimientos_legacy()

    creados, actualizados = crear_perfiles(forzar=forzar)
    if creados:
        print(f"Perfiles de empresa creados ({len(creados)}):")
        for nombre in creados:
            print(f"  - {nombre}")
    if actualizados:
        print(f"Perfiles de empresa actualizados ({len(actualizados)}):")
        for nombre in actualizados:
            print(f"  - {nombre}")

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