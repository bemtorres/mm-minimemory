"""Interfaz web de los agentes personales (Flask + Tailwind CSS / HeroUI).

Aplicación que ofrece la misma funcionalidad que `main.py` pero con una
interfaz web moderna. La versión web guarda los datos en una base de
datos SQLite (`agentes.db`); la versión de consola sigue usando los
archivos de `agents/`.

Antes de la primera ejecución conviene sembrar la base de datos:

    python seed.py

Ejecutar:

    python app.py
"""

import csv
import os

from dotenv import load_dotenv
from flask import Flask, abort, jsonify, render_template, request

from basededatos import (
    AgenteDB,
    actualizar_conocimiento,
    actualizar_fuente,
    actualizar_perfil,
    borrar_memoria,
    cambiar_identidad,
    crear_agente,
    crear_fuente,
    eliminar_fuente,
    establecer_fuentes_agente,
    inicializar,
    listar_agentes,
    listar_fuentes,
    migrar_conocimientos_legacy,
    obtener_agente,
    obtener_fuente,
    obtener_fuentes_agente,
    obtener_historial,
)
from identidades import IDENTIDADES
from memoria import PERFIL_INICIAL

load_dotenv()

app = Flask(__name__)

# Máximo de mensajes del historial que se muestran en el chat.
HISTORIAL_VISIBLE = 60

inicializar()


def _tiene_api_key():
    """True si hay una API Key de DeepSeek configurada en .env."""
    clave = os.getenv("DEEPSEEK_API_KEY", "").strip()
    return bool(clave) and clave != "tu_api_key"


def _nombre_persona(nombre, perfil):
    """Extrae el nombre de la persona desde el perfil del agente."""
    lineas = perfil.splitlines()
    for indice, linea in enumerate(lineas):
        if linea.strip().startswith("NOMBRE:"):
            for siguiente in lineas[indice + 1:]:
                if siguiente.strip():
                    return siguiente.strip()
    return nombre


def _iniciales(texto):
    """Iniciales de un nombre para el avatar del agente."""
    partes = [parte for parte in texto.split() if parte]
    if not partes:
        return "A"
    if len(partes) == 1:
        return partes[0][0].upper()
    return (partes[0][0] + partes[-1][0]).upper()


def _color_avatar(nombre):
    """Color del avatar según el nombre del agente."""
    paleta = ["violet", "fuchsia", "indigo", "sky", "emerald", "rose"]
    return paleta[sum(ord(caracter) for caracter in nombre) % len(paleta)]


def _info_identidad(clave, custom):
    """Devuelve (nombre, descripcion, prompt, es_personalizada, clave)."""
    if custom.strip():
        return {
            "nombre": "Identidad personalizada",
            "descripcion": "Prompt propio guardado como identidad personalizada.",
            "prompt": custom,
            "personalizada": True,
            "clave": "",
        }
    datos = IDENTIDADES.get(clave) or IDENTIDADES["basic"]
    return {
        "nombre": datos["name"],
        "descripcion": datos["description"],
        "prompt": datos["prompt"],
        "personalizada": False,
        "clave": clave if clave in IDENTIDADES else "basic",
    }


def _cargar_agente(nombre):
    """Devuelve un dict con los datos de un agente desde la base de datos."""
    datos = obtener_agente(nombre)
    if not datos:
        return None
    persona = _nombre_persona(nombre, datos["perfil"])
    return {
        "nombre": nombre,
        "persona": persona,
        "iniciales": _iniciales(persona),
        "color": _color_avatar(nombre),
        "perfil": datos["perfil"],
        "conocimiento": datos["conocimiento"],
        "memoria": datos["memoria"],
        "creado_en": datos["creado_en"],
        "identidad": _info_identidad(
            datos["identidad_clave"], datos["identidad_custom"]
        ),
        "fuentes": obtener_fuentes_agente(nombre),
        "todas_fuentes": listar_fuentes(),
    }


def _historial(nombre, cantidad=HISTORIAL_VISIBLE):
    """Devuelve los últimos mensajes como lista de dicts."""
    return [
        {"rol": rol, "mensaje": mensaje}
        for rol, mensaje in obtener_historial(nombre, cantidad)
    ]


def _agente_o_404(nombre):
    """Devuelve el nombre si el agente existe; si no, responde 404."""
    if nombre not in listar_agentes():
        abort(404)
    return nombre


# ----------------------------------------------------------------------
# Páginas
# ----------------------------------------------------------------------


@app.get("/")
def inicio():
    agentes = [_cargar_agente(nombre) for nombre in listar_agentes()]
    fuentes = listar_fuentes()
    return render_template(
        "index.html",
        agentes=agentes,
        fuentes=fuentes,
        identidades=IDENTIDADES,
        tiene_api_key=_tiene_api_key(),
    )


@app.get("/agente/<nombre>")
def pagina_chat(nombre):
    _agente_o_404(nombre)
    return render_template(
        "chat.html",
        agente=_cargar_agente(nombre),
        identidades=IDENTIDADES,
        tiene_api_key=_tiene_api_key(),
    )


# ----------------------------------------------------------------------
# API JSON
# ----------------------------------------------------------------------


@app.get("/api/agente/<nombre>")
def api_agente(nombre):
    _agente_o_404(nombre)
    return jsonify(_cargar_agente(nombre))


@app.get("/api/agente/<nombre>/historial")
def api_historial(nombre):
    _agente_o_404(nombre)
    return jsonify({"mensajes": _historial(nombre)})


@app.post("/api/agente/<nombre>/mensaje")
def api_mensaje(nombre):
    _agente_o_404(nombre)
    datos = request.get_json(silent=True) or {}
    mensaje = (datos.get("mensaje") or "").strip()
    if not mensaje:
        return jsonify({"error": "El mensaje no puede estar vacío."}), 400
    try:
        agente = AgenteDB(nombre)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    try:
        respuesta = agente.preguntar(mensaje)
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 500
    try:
        memorias = agente.actualizar_memoria(mensaje, respuesta)
    except Exception:
        memorias = []
    return jsonify(
        {
            "respuesta": respuesta,
            "memoria_guardada": bool(memorias),
        }
    )


@app.post("/api/agentes")
def api_crear_agente():
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    if not nombre:
        return jsonify({"error": "Escribe un nombre para el agente."}), 400
    if "/" in nombre or "\\" in nombre or nombre.startswith("."):
        return jsonify({"error": "El nombre no puede contener '/' ni '\\'."}), 400
    if nombre in listar_agentes():
        return jsonify({"error": f"El agente '{nombre}' ya existe."}), 400

    perfil = (datos.get("perfil") or "").strip()
    conocimiento = (datos.get("conocimiento") or "").strip()
    clave = (datos.get("identidad") or "").strip()
    personalizada = (datos.get("identidad_custom") or "").strip()
    fuentes = datos.get("fuentes") or datos.get("fuentes_ids") or []

    ids = []
    if isinstance(fuentes, list):
        for valor in fuentes:
            try:
                ids.append(int(valor))
            except (TypeError, ValueError):
                continue

    crear_agente(
        nombre=nombre,
        perfil=perfil if perfil else PERFIL_INICIAL,
        conocimiento=conocimiento,
        identidad_clave=clave if clave in IDENTIDADES else "",
        identidad_custom=personalizada,
        fuentes_ids=ids,
    )
    migrar_conocimientos_legacy()
    return jsonify({"ok": True, "nombre": nombre}), 201


@app.post("/api/agente/<nombre>/perfil")
def api_perfil(nombre):
    _agente_o_404(nombre)
    datos = request.get_json(silent=True) or {}
    texto = (datos.get("perfil") or "").strip()
    if not texto:
        return jsonify({"error": "El perfil no puede estar vacío."}), 400
    actualizar_perfil(nombre, texto)
    return jsonify(_cargar_agente(nombre))


@app.post("/api/agente/<nombre>/conocimiento")
def api_conocimiento(nombre):
    _agente_o_404(nombre)
    datos = request.get_json(silent=True) or {}
    texto = (datos.get("conocimiento") or "").strip()
    actualizar_conocimiento(nombre, texto)
    return jsonify(_cargar_agente(nombre))


@app.post("/api/agente/<nombre>/identidad")
def api_cambiar_identidad(nombre):
    _agente_o_404(nombre)
    datos = request.get_json(silent=True) or {}
    personalizada = (datos.get("identidad_custom") or "").strip()
    clave = (datos.get("identidad") or "").strip()
    if personalizada:
        cambiar_identidad(nombre, custom=personalizada)
    elif clave in IDENTIDADES:
        cambiar_identidad(nombre, clave=clave)
    else:
        return jsonify({"error": "Identidad no válida."}), 400
    return jsonify(_cargar_agente(nombre))


@app.post("/api/agente/<nombre>/editar")
def api_editar(nombre):
    _agente_o_404(nombre)
    datos = request.get_json(silent=True) or {}
    perfil = (datos.get("perfil") or "").strip()
    conocimiento = (datos.get("conocimiento") or "").strip()
    personalizada = (datos.get("identidad_custom") or "").strip()
    clave = (datos.get("identidad") or "").strip()
    fuentes = datos.get("fuentes")

    if not perfil:
        return jsonify({"error": "El perfil no puede estar vacío."}), 400
    if not personalizada and clave not in IDENTIDADES:
        return jsonify({"error": "Identidad no válida."}), 400

    actualizar_perfil(nombre, perfil)
    actualizar_conocimiento(nombre, conocimiento)
    if isinstance(fuentes, list):
        ids = []
        for valor in fuentes:
            try:
                ids.append(int(valor))
            except (TypeError, ValueError):
                continue
        establecer_fuentes_agente(nombre, ids)
    if personalizada:
        cambiar_identidad(nombre, custom=personalizada)
    else:
        cambiar_identidad(nombre, clave=clave)
    return jsonify(_cargar_agente(nombre))


@app.get("/api/fuentes")
def api_listar_fuentes():
    return jsonify({"fuentes": listar_fuentes()})


@app.get("/api/fuentes/<int:fuente_id>")
def api_obtener_fuente(fuente_id):
    fuente = obtener_fuente(fuente_id)
    if not fuente:
        return jsonify({"error": "Base de conocimiento no encontrada."}), 404
    return jsonify(fuente)


@app.post("/api/fuentes")
def api_crear_fuente():
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    contenido = (datos.get("contenido") or "").strip()
    if not nombre:
        return jsonify({"error": "Escribe un nombre para la base de conocimiento."}), 400
    try:
        nuevo_id = crear_fuente(nombre, contenido)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return jsonify({"id": nuevo_id, "nombre": nombre, "contenido": contenido}), 201


@app.route("/api/fuentes/<int:fuente_id>", methods=["POST", "PUT"])
def api_actualizar_fuente(fuente_id):
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    contenido = (datos.get("contenido") or "").strip()
    if not nombre:
        return jsonify({"error": "El nombre de la base de conocimiento no puede estar vacío."}), 400
    try:
        actualizar_fuente(fuente_id, nombre, contenido)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return jsonify({"id": fuente_id, "nombre": nombre, "contenido": contenido})


@app.delete("/api/fuentes/<int:fuente_id>")
def api_eliminar_fuente(fuente_id):
    eliminar_fuente(fuente_id)
    return jsonify({"ok": True})


@app.post("/api/agente/<nombre>/limpiar")
def api_limpiar(nombre):
    _agente_o_404(nombre)
    borrar_memoria(nombre)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True)