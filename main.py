"""Interfaz de consola de los agentes personales.

Al iniciar, el programa pregunta con qué agente quieres conversar.
Cada agente vive en una carpeta dentro de `agents/` y tiene su propio
perfil, conocimiento, memoria e historial.
"""

import sys

# Fuerza UTF-8 en la consola (importante en Windows para los acentos).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    from agente import Agente
    from identidades import IDENTIDADES
    from memoria import (
        borrar_memoria,
        crear_agente,
        escribir_base_archivo,
        escribir_conocimiento,
        escribir_identidad,
        escribir_identidad_custom,
        establecer_bases_agente_archivos,
        leer_bases_agente_archivos,
        listar_agentes,
        listar_bases_archivos,
    )
except ModuleNotFoundError:
    print("Faltan dependencias. Ejecuta: pip install -r requirements.txt")
    sys.exit(1)

BANNER = """
========================================
    AGENTES PERSONALES - DEEPSEEK
========================================
"""

COMANDOS = """
Escribe tu pregunta.
Comandos disponibles:

/memoria
/perfil
/conocimiento
/bases
/identidad
/cambiar_identidad
/crear_identidad
/historial
/limpiar
/cambiar
/salir
"""


def elegir_agente():
    """Pregunta con qué agente conversar. Permite crear uno nuevo."""
    while True:
        agentes = listar_agentes()
        print("Agentes disponibles:")
        if agentes:
            for indice, nombre in enumerate(agentes, 1):
                print(f"  {indice}. {nombre}")
        else:
            print("  (No hay agentes creados todavía)")
        print()
        entrada = input("¿Con quién vas a hablar? (número o nombre): ").strip()
        if not entrada:
            continue
        # Si es un número, se toma el agente de la lista.
        if entrada.isdigit():
            indice = int(entrada) - 1
            if 0 <= indice < len(agentes):
                return agentes[indice]
            print("Número inválido.\n")
            continue
        # Si el nombre existe, se conversa con él. Si no, se crea.
        if entrada in agentes:
            return entrada
        nombre = crear_agente(entrada)
        print(f"\nSe creó el agente '{nombre}'.")
        escribir_conocimiento_inicial(nombre)
        elegir_identidad_inicial(nombre)
        return nombre


def escribir_conocimiento_inicial(nombre):
    """Pide al usuario los conocimientos previos de un agente nuevo."""
    print("Escribe los conocimientos del agente (uno por línea).")
    print("Escribe FIN cuando termines:")
    lineas = []
    while True:
        linea = input("  > ").strip()
        if not linea or linea.upper() == "FIN":
            break
        lineas.append(linea)
    if lineas:
        escribir_conocimiento(nombre, "\n".join(lineas))
        print(f"Conocimiento guardado en agents/{nombre}/conocimiento.txt")
    else:
        print("Conocimiento dejado vacío por ahora.")


def elegir_identidad_inicial(nombre):
    """Pide al usuario la identidad (rol) de un agente nuevo."""
    listar_identidades()
    print("  (Enter para dejar la identidad por defecto)")
    while True:
        entrada = input("Identidad (número, 0 para personalizada): ").strip()
        if not entrada:
            print("Identidad por defecto asignada.")
            return
        if entrada == "0":
            escribir_identidad_personalizada(nombre)
            return
        if entrada.isdigit():
            indice = int(entrada) - 1
            if 0 <= indice < len(IDENTIDADES):
                escribir_identidad(nombre, list(IDENTIDADES)[indice])
                print(
                    f"Identidad '{IDENTIDADES[list(IDENTIDADES)[indice]]['name']}' asignada."
                )
                return
        print("Número inválido. Intenta de nuevo.")


def listar_identidades():
    """Muestra la lista de identidades disponibles."""
    print("\nIdentidades disponibles:")
    for indice, clave in enumerate(IDENTIDADES, 1):
        identidad = IDENTIDADES[clave]
        print(f"  {indice}. {identidad['name']}: {identidad['description']}")
    print("  0. Escribir identidad personalizada")


def escribir_identidad_personalizada(nombre):
    """Pide al usuario un prompt de rol propio y lo guarda en identidad_custom.txt."""
    print("\nEscribe el prompt de rol de la identidad (una o varias líneas).")
    print("Se guardará en identidad_custom.txt y tendrá prioridad sobre")
    print("la clave de identidad.txt. Puedes usar los marcadores:")
    print("  [____] -> se reemplaza por el nombre de la persona.")
    print("  [información del documento] -> referencia a la base de conocimiento.")
    print("Escribe FIN cuando termines:")
    lineas = []
    while True:
        linea = input("  > ")
        if linea.strip().upper() == "FIN":
            break
        lineas.append(linea)
    if not lineas:
        print("Identidad sin cambios.")
        return
    escribir_identidad_custom(nombre, "\n".join(lineas))
    print(f"Identidad personalizada guardada en agents/{nombre}/identidad_custom.txt")


def mostrar_memoria(agente):
    """Muestra la memoria almacenada del agente."""
    print("\nMEMORIA DEL AGENTE")
    print("------------------")
    memoria = agente.memoria.strip()
    print(memoria if memoria else "(La memoria está vacía)")


def mostrar_perfil(agente):
    """Muestra el perfil de la persona representada."""
    print("\nPERFIL DE LA PERSONA")
    print("--------------------")
    print(agente.perfil)


def mostrar_conocimiento(agente):
    """Muestra el conocimiento previo del agente."""
    print("\nCONOCIMIENTO DEL AGENTE")
    print("------------------------")
    conocimiento = agente.conocimiento.strip()
    print(
        conocimiento
        if conocimiento
        else "(El agente no tiene conocimientos previos)"
    )


def mostrar_identidad(agente):
    """Muestra la identidad actual del agente y su prompt de rol."""
    nombre, descripcion, prompt = agente.info_identidad()
    print("\nIDENTIDAD DEL AGENTE")
    print("--------------------")
    print(f"Nombre: {nombre}")
    print(f"Descripción: {descripcion}")
    print("\nPrompt de rol:")
    print(prompt)


def nombre_identidad(agente):
    """Nombre para mostrar de la identidad actual del agente."""
    return agente.info_identidad()[0]


def cambiar_identidad(agente):
    """Cambia la identidad del agente por una de la lista o una personalizada."""
    listar_identidades()
    print(f"\n  Identidad actual: {nombre_identidad(agente)}")
    entrada = input(
        "Nueva identidad (número, 0 para personalizada o Enter para no cambiar): "
    ).strip()
    if not entrada:
        print("Identidad sin cambios.")
        return
    if entrada == "0":
        escribir_identidad_personalizada(agente.nombre)
        agente.cargar_identidad()
        return
    if entrada.isdigit():
        indice = int(entrada) - 1
        if 0 <= indice < len(IDENTIDADES):
            agente.establecer_identidad(list(IDENTIDADES)[indice])
            print(
                f"Identidad cambiada a '{IDENTIDADES[list(IDENTIDADES)[indice]]['name']}'."
            )
            return
    print("Número inválido. Identidad sin cambios.")


def mostrar_historial(agente):
    """Muestra las últimas conversaciones guardadas en el CSV."""
    historial = agente.obtener_historial(cantidad=15)
    print("\nHISTORIAL RECIENTE")
    print("------------------")
    if not historial:
        print("(Todavía no hay conversaciones guardadas)")
        return
    for rol, mensaje in historial:
        etiqueta = "Tú" if rol == "user" else "Agente"
        print(f"{etiqueta}: {mensaje}")


def confirmar_borrado(agente):
    """Borra la memoria del agente solo después de confirmar el usuario."""
    respuesta = input(
        "\n¿Estás seguro de que deseas borrar toda la memoria? (s/n) "
    ).strip().lower()
    if respuesta in ("s", "si", "sí", "yes", "y"):
        borrar_memoria(agente.nombre)
        agente.cargar_memoria()
        print("Memoria borrada correctamente.")
    else:
        print("Operación cancelada.")


def gestionar_bases_conocimiento(agente):
    """Muestra y permite asociar bases de conocimiento al agente."""
    bases_disponibles = listar_bases_archivos()
    bases_actuales = [nom for nom, _ in leer_bases_agente_archivos(agente.nombre)]

    print("\nBASES DE CONOCIMIENTO DISPONIBLES:")
    print("-----------------------------------")
    if bases_disponibles:
        for idx, base in enumerate(bases_disponibles, 1):
            marca = "[x]" if base in bases_actuales else "[ ]"
            print(f"  {idx}. {marca} {base}")
    else:
        print("  (No hay bases creadas en bases_conocimiento/)")

    print("\nOpciones:")
    print("  - Escribe los números separados por coma para asociar (ej: 1, 3)")
    print("  - Escribe 'nueva' para crear una base nueva")
    print("  - Enter para dejar como está")

    entrada = input("\nElige una opción: ").strip()
    if not entrada:
        return

    if entrada.lower() == "nueva":
        nom = input("Nombre de la nueva base: ").strip()
        if not nom:
            print("Operación cancelada.")
            return
        print("Contenido de la base (FIN para terminar):")
        lineas = []
        while True:
            l = input("  > ")
            if l.strip().upper() == "FIN":
                break
            lineas.append(l)
        escribir_base_archivo(nom, "\n".join(lineas))
        print(f"Base '{nom}' creada.")
        asociar = input(f"¿Asociar '{nom}' a {agente.nombre}? (s/n): ").strip().lower()
        if asociar in ("s", "si", "sí", "y", "yes"):
            bases_actuales.append(nom)
            establecer_bases_agente_archivos(agente.nombre, bases_actuales)
            agente.cargar_conocimiento()
            print("Base asociada al agente.")
        return

    partes = [p.strip() for p in entrada.split(",") if p.strip().isdigit()]
    if partes:
        nuevas_bases = []
        for p in partes:
            idx = int(p) - 1
            if 0 <= idx < len(bases_disponibles):
                nuevas_bases.append(bases_disponibles[idx])
        establecer_bases_agente_archivos(agente.nombre, nuevas_bases)
        agente.cargar_conocimiento()
        print(f"Bases asociadas actualizadas: {', '.join(nuevas_bases) if nuevas_bases else '(ninguna)'}")
    else:
        print("Opción no válida.")


def procesar_comando(comando, agente):
    """Ejecuta un comando y devuelve la acción a realizar.

    Devuelve 'salir' o 'cambiar' para acciones especiales, o None.
    """
    if comando == "/salir":
        return "salir"
    if comando == "/cambiar":
        return "cambiar"
    if comando == "/memoria":
        mostrar_memoria(agente)
    elif comando == "/perfil":
        mostrar_perfil(agente)
    elif comando == "/conocimiento":
        mostrar_conocimiento(agente)
    elif comando == "/bases":
        gestionar_bases_conocimiento(agente)
    elif comando == "/identidad":
        mostrar_identidad(agente)
    elif comando == "/cambiar_identidad":
        cambiar_identidad(agente)
    elif comando == "/crear_identidad":
        escribir_identidad_personalizada(agente.nombre)
        agente.cargar_identidad()
    elif comando == "/historial":
        mostrar_historial(agente)
    elif comando == "/limpiar":
        confirmar_borrado(agente)
    else:
        print(f"Comando desconocido: {comando}")
        print(
            "Usa /memoria, /perfil, /conocimiento, /bases, /identidad, "
            "/cambiar_identidad, /crear_identidad, /historial, /limpiar, "
            "/cambiar o /salir."
        )
    return None


def mostrar_agente(agente):
    """Muestra la persona y el agente con el que se conversa."""
    print("\nPersona: " + agente.obtener_nombre())
    print("Agente: " + agente.nombre + "\n")


def main():
    print(BANNER)
    print(COMANDOS)

    try:
        nombre = elegir_agente()
        agente = Agente(nombre)
    except ValueError as error:
        print(f"\nError: {error}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nSaliendo...")
        return

    mostrar_agente(agente)

    while True:
        try:
            mensaje = input("Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo...")
            break

        if not mensaje:
            continue

        if mensaje.startswith("/"):
            accion = procesar_comando(mensaje.lower(), agente)
            if accion == "salir":
                break
            if accion == "cambiar":
                try:
                    nombre = elegir_agente()
                    agente = Agente(nombre)
                    mostrar_agente(agente)
                except ValueError as error:
                    print(f"\nError: {error}\n")
            print()
            continue

        try:
            respuesta = agente.preguntar(mensaje)
        except RuntimeError as error:
            print(f"\nError: {error}\n")
            continue
        except Exception:
            print("\nError: no se pudo obtener respuesta de DeepSeek.\n")
            continue

        print(f"\nAgente:\n{respuesta}\n")

        print("[El sistema analiza si debe guardar esta información]")
        try:
            agente.actualizar_memoria(mensaje, respuesta)
        except Exception:
            pass

    print("Hasta pronto.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSaliendo...")
    except Exception as error:
        print(f"\nError inesperado: {error}")