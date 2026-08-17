"""Definición de los prompts utilizados por el agente.

Aquí viven las plantillas de texto que se envían a DeepSeek.
La identidad, el perfil, el conocimiento y la memoria se inyectan de
forma dinámica: nunca están escritos directamente dentro de este archivo.
"""

# Plantilla del prompt de memoria: decide si una conversación aporta
# información nueva que valga la pena recordar.
PLANTILLA_MEMORIA = """Analiza la conversación.

Determina si apareció información NUEVA y RELEVANTE
que debería recordarse para futuras conversaciones.

Solo devuelve información que sea:
- útil
- persistente
- relevante para el usuario
- diferente de lo que ya existe en la memoria

Si no existe información nueva, responde:

NO_MEMORIA

Si existe información nueva, devuelve únicamente
los recuerdos que deberían almacenarse.

MEMORIA ACTUAL:
{memoria}

CONVERSACIÓN:
{conversacion}"""

# Marcadores dentro de los prompts de identidad.
MARCA_NOMBRE = "[____]"
MARCA_DOCUMENTO = "[información del documento]"


def procesar_identidad(prompt_identidad, nombre_persona):
    """Reemplaza los marcadores del prompt de identidad.

    - [____] -> nombre de la persona representada.
    - [información del documento] -> referencia a la base de conocimiento.
    """
    nombre = nombre_persona.strip() or "el tema de conversación"
    prompt = prompt_identidad.replace(MARCA_NOMBRE, nombre)
    prompt = prompt.replace(
        MARCA_DOCUMENTO, "la información disponible en la base de conocimiento"
    )
    return prompt


def construir_system_prompt(rol, perfil, conocimiento, memoria):
    """Construye el System Prompt final.

    `rol` es el prompt de identidad ya procesado (ver procesar_identidad).
    Luego se agregan las secciones de perfil, conocimiento y memoria.
    """
    return f"""{rol}

PERFIL:
{perfil.strip()}

BASE DE CONOCIMIENTO:
{conocimiento.strip() if conocimiento.strip() else "(sin conocimientos previos)"}

MEMORIA:
{memoria.strip() if memoria.strip() else "(sin memorias almacenadas)"}"""


def construir_prompt_memoria(memoria, conversacion):
    """Construye el prompt que decide qué información recordar."""
    return PLANTILLA_MEMORIA.format(
        memoria=memoria.strip() if memoria.strip() else "(sin memorias almacenadas)",
        conversacion=conversacion.strip(),
    )
