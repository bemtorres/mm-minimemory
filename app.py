"""Interfaz web de los agentes personales (Flask + Tailwind CSS / HeroUI).

Incluye:
- Chat interactivo con DeepSeek y múltiples hilos de conversación.
- Gestión de agentes, identidades y memoria.
- Bases de conocimiento independientes asociadas a los agentes.
- Sistema de autenticación (Login/Logout).
- Dashboard administrativo para gestionar agentes, bases y métricas.
"""

import os
import uuid
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

from basededatos import (
    AgenteDB,
    actualizar_avatar,
    actualizar_conocimiento,
    actualizar_fuente,
    actualizar_perfil,
    actualizar_rol,
    actualizar_usuario,
    borrar_memoria,
    cambiar_identidad,
    crear_agente,
    crear_fuente,
    crear_rol,
    crear_sesion_chat,
    crear_usuario,
    eliminar_agente,
    eliminar_fuente,
    eliminar_rol,
    eliminar_sesion_chat,
    eliminar_usuario,
    establecer_fuentes_agente,
    inicializar,
    listar_agentes,
    listar_fuentes,
    listar_roles,
    listar_sesiones_agente,
    listar_todas_las_sesiones,
    listar_usuarios,
    migrar_conocimientos_legacy,
    obtener_agente,
    obtener_estadisticas_dashboard,
    obtener_fuente,
    obtener_fuentes_agente,
    obtener_historial,
    obtener_o_crear_sesion_activa,
    obtener_rol,
    obtener_rol_por_clave,
    obtener_sesion_chat,
    obtener_todos_mensajes_sesion,
    obtener_usuario,
    obtener_usuario_por_nombre,
    renombrar_sesion_chat,
    verificar_usuario,
)
from identidades import IDENTIDADES

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "minimind-secret-key-agentes-2026-auth")

CARPETA_AVATARES = os.path.join(app.static_folder, "uploads", "avatars")
os.makedirs(CARPETA_AVATARES, exist_ok=True)
EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "gif", "webp", "svg"}

# Máximo de mensajes del historial que se muestran en el chat.
HISTORIAL_VISIBLE = 60

inicializar()


def login_requerido(f):
    """Decorador para proteger rutas que requieren inicio de sesión."""
    @wraps(f)
    def decorada(*args, **kwargs):
        if not session.get("usuario"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "No autorizado. Inicia sesión primero."}), 401
            return redirect(url_for("pagina_login", next=request.path))
        return f(*args, **kwargs)
    return decorada


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
    """Devuelve (nombre, descripcion, prompt, es_personalizada, clave) consultando la base de datos."""
    if custom.strip():
        return {
            "nombre": "Identidad personalizada",
            "descripcion": "Prompt propio guardado como identidad personalizada.",
            "prompt": custom,
            "personalizada": True,
            "clave": "",
        }
    if clave:
        rol = obtener_rol_por_clave(clave)
        if rol:
            return {
                "nombre": rol["nombre"],
                "descripcion": rol["descripcion"],
                "prompt": rol["prompt"],
                "personalizada": False,
                "clave": rol["clave"],
            }
    rol_defecto = obtener_rol_por_clave("basic")
    if rol_defecto:
        return {
            "nombre": rol_defecto["nombre"],
            "descripcion": rol_defecto["descripcion"],
            "prompt": rol_defecto["prompt"],
            "personalizada": False,
            "clave": "basic",
        }
    return {
        "nombre": "Básico",
        "descripcion": "Agente experto en la base de conocimiento.",
        "prompt": "Eres un modelo de inteligencia artificial experto...",
        "personalizada": False,
        "clave": "basic",
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
        "avatar_url": datos.get("avatar_url", "") or "",
        "perfil": datos["perfil"],
        "conocimiento": datos["conocimiento"],
        "memoria": datos["memoria"],
        "creado_en": datos["creado_en"],
        "identidad": _info_identidad(
            datos["identidad_clave"], datos["identidad_custom"]
        ),
        "fuentes": obtener_fuentes_agente(nombre),
        "todas_fuentes": listar_fuentes(),
        "sesiones": listar_sesiones_agente(nombre),
        "roles": listar_roles(),
    }


def _agente_o_404(nombre):
    """Devuelve el nombre si el agente existe; si no, responde 404."""
    if nombre not in listar_agentes():
        abort(404)
    return nombre


# ----------------------------------------------------------------------
# Páginas Públicas y de Chat
# ----------------------------------------------------------------------


@app.get("/")
def inicio():
    agentes = [_cargar_agente(nombre) for nombre in listar_agentes()]
    fuentes = listar_fuentes()
    roles = listar_roles()
    return render_template(
        "index.html",
        agentes=agentes,
        fuentes=fuentes,
        roles=roles,
        identidades=IDENTIDADES,
        tiene_api_key=_tiene_api_key(),
        usuario_actual=session.get("usuario"),
    )


@app.get("/agente/<nombre>")
@login_requerido
def pagina_chat(nombre):
    _agente_o_404(nombre)
    agente = _cargar_agente(nombre)
    sesion_activa = obtener_o_crear_sesion_activa(nombre)
    roles = listar_roles()
    todos_los_agentes = listar_agentes()
    return render_template(
        "chat.html",
        agente=agente,
        sesion_activa=sesion_activa,
        sesiones=listar_sesiones_agente(nombre),
        roles=roles,
        todos_los_agentes=todos_los_agentes,
        identidades=IDENTIDADES,
        tiene_api_key=_tiene_api_key(),
        usuario_actual=session.get("usuario"),
    )


# ----------------------------------------------------------------------
# Autenticación (Login / Logout)
# ----------------------------------------------------------------------


@app.get("/login")
def pagina_login():
    if session.get("usuario"):
        siguiente = request.args.get("next") or url_for("pagina_dashboard")
        return redirect(siguiente)
    return render_template("login.html", next=request.args.get("next", ""))


@app.post("/login")
def procesar_login():
    datos = request.get_json(silent=True) or request.form
    usuario = (datos.get("usuario") or "").strip()
    password = (datos.get("password") or "").strip()
    siguiente = request.args.get("next") or (datos.get("next") if isinstance(datos, dict) else "") or url_for("pagina_dashboard")

    resultado = verificar_usuario(usuario, password)
    if not resultado:
        if request.is_json:
            return jsonify({"error": "Usuario o contraseña incorrectos."}), 401
        return render_template("login.html", error="Usuario o contraseña incorrectos.", usuario=usuario, next=siguiente), 401

    session["usuario"] = resultado["usuario"]
    session["rol"] = resultado["rol"]

    if request.is_json:
        return jsonify({"ok": True, "redirect": siguiente})
    return redirect(siguiente)


@app.get("/logout")
def cerrar_sesion():
    session.clear()
    return redirect(url_for("inicio"))


# ----------------------------------------------------------------------
# Dashboard Administrativo
# ----------------------------------------------------------------------


@app.get("/dashboard")
@app.get("/admin")
@login_requerido
def pagina_dashboard():
    stats = obtener_estadisticas_dashboard()
    fuentes = listar_fuentes()
    roles = listar_roles()
    usuarios = listar_usuarios()
    return render_template(
        "dashboard.html",
        stats=stats,
        fuentes=fuentes,
        roles=roles,
        usuarios=usuarios,
        identidades=IDENTIDADES,
        usuario_actual=session.get("usuario"),
        tiene_api_key=_tiene_api_key(),
    )


@app.get("/api/dashboard/stats")
@login_requerido
def api_dashboard_stats():
    return jsonify(obtener_estadisticas_dashboard())


# ----------------------------------------------------------------------
# API JSON: Agentes
# ----------------------------------------------------------------------


@app.get("/api/agente/<nombre>")
def api_agente(nombre):
    _agente_o_404(nombre)
    return jsonify(_cargar_agente(nombre))


@app.post("/api/upload/avatar")
@login_requerido
def api_upload_avatar():
    if "avatar" not in request.files and "file" not in request.files:
        return jsonify({"error": "No se envió ningún archivo de imagen."}), 400
    archivo = request.files.get("avatar") or request.files.get("file")
    if not archivo or not archivo.filename:
        return jsonify({"error": "Nombre de archivo inválido."}), 400

    partes = archivo.filename.rsplit(".", 1)
    if len(partes) < 2 or partes[1].lower() not in EXTENSIONES_PERMITIDAS:
        return jsonify({"error": "Formato no permitido. Usa PNG, JPG, JPEG, WEBP, GIF o SVG."}), 400

    ext = partes[1].lower()
    nombre_archivo = f"{uuid.uuid4().hex[:12]}_{secure_filename(partes[0])}.{ext}"
    ruta_destino = os.path.join(CARPETA_AVATARES, nombre_archivo)
    archivo.save(ruta_destino)
    url_relativa = f"/static/uploads/avatars/{nombre_archivo}"
    return jsonify({"ok": True, "url": url_relativa})


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
    avatar_url = (datos.get("avatar_url") or "").strip()
    fuentes = datos.get("fuentes") or datos.get("fuentes_ids") or []

    ids = []
    if isinstance(fuentes, list):
        for valor in fuentes:
            try:
                ids.append(int(valor))
            except (TypeError, ValueError):
                continue

    rol_valido = bool(obtener_rol_por_clave(clave)) or clave in IDENTIDADES
    crear_agente(
        nombre=nombre,
        perfil=perfil if perfil else PERFIL_INICIAL,
        conocimiento=conocimiento,
        identidad_clave=clave if rol_valido else "",
        identidad_custom=personalizada,
        avatar_url=avatar_url,
        fuentes_ids=ids,
    )
    migrar_conocimientos_legacy()
    return jsonify({"ok": True, "nombre": nombre}), 201


@app.delete("/api/agente/<nombre>")
@login_requerido
def api_eliminar_agente(nombre):
    _agente_o_404(nombre)
    exito = eliminar_agente(nombre)
    if not exito:
        return jsonify({"error": "No se pudo eliminar el agente."}), 500
    return jsonify({"ok": True, "mensaje": f"Agente '{nombre}' eliminado correctamente."})


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
    rol_valido = bool(obtener_rol_por_clave(clave)) or clave in IDENTIDADES
    if personalizada:
        cambiar_identidad(nombre, custom=personalizada)
    elif rol_valido:
        cambiar_identidad(nombre, clave=clave)
    else:
        return jsonify({"error": "Identidad o rol no válido."}), 400
    return jsonify(_cargar_agente(nombre))


@app.post("/api/agente/<nombre>/editar")
def api_editar(nombre):
    _agente_o_404(nombre)
    datos = request.get_json(silent=True) or {}
    perfil = (datos.get("perfil") or "").strip()
    conocimiento = (datos.get("conocimiento") or "").strip()
    personalizada = (datos.get("identidad_custom") or "").strip()
    clave = (datos.get("identidad") or "").strip()
    avatar_url = datos.get("avatar_url")
    fuentes = datos.get("fuentes") or datos.get("fuentes_ids")
    rol_valido = bool(obtener_rol_por_clave(clave)) or clave in IDENTIDADES

    if not perfil:
        return jsonify({"error": "El perfil no puede estar vacío."}), 400
    if not personalizada and not rol_valido and clave:
        return jsonify({"error": "Identidad o rol no válido."}), 400

    actualizar_perfil(nombre, perfil)
    actualizar_conocimiento(nombre, conocimiento)
    if avatar_url is not None:
        actualizar_avatar(nombre, str(avatar_url).strip())

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


@app.post("/api/agente/<nombre>/limpiar")
def api_limpiar(nombre):
    _agente_o_404(nombre)
    borrar_memoria(nombre)
    return jsonify({"ok": True})


# ----------------------------------------------------------------------
# API JSON: Roles e Identidades
# ----------------------------------------------------------------------


@app.get("/api/roles")
@login_requerido
def api_listar_roles():
    return jsonify({"roles": listar_roles()})


@app.get("/api/roles/<int:rol_id>")
@login_requerido
def api_obtener_rol(rol_id):
    rol = obtener_rol(rol_id)
    if not rol:
        return jsonify({"error": "Rol no encontrado."}), 404
    return jsonify(rol)


@app.post("/api/roles")
@login_requerido
def api_crear_rol():
    datos = request.get_json(silent=True) or {}
    clave = (datos.get("clave") or "").strip().lower()
    nombre = (datos.get("nombre") or "").strip()
    descripcion = (datos.get("descripcion") or "").strip()
    prompt = (datos.get("prompt") or "").strip()

    if not clave or not nombre or not prompt:
        return jsonify({"error": "La clave, el nombre y el prompt son obligatorios."}), 400

    try:
        nuevo_id = crear_rol(clave, nombre, descripcion, prompt)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify({"id": nuevo_id, "clave": clave, "nombre": nombre, "descripcion": descripcion, "prompt": prompt}), 201


@app.route("/api/roles/<int:rol_id>", methods=["POST", "PUT"])
@login_requerido
def api_actualizar_rol(rol_id):
    datos = request.get_json(silent=True) or {}
    clave = (datos.get("clave") or "").strip().lower()
    nombre = (datos.get("nombre") or "").strip()
    descripcion = (datos.get("descripcion") or "").strip()
    prompt = (datos.get("prompt") or "").strip()

    if not clave or not nombre or not prompt:
        return jsonify({"error": "La clave, el nombre y el prompt son obligatorios."}), 400

    try:
        actualizar_rol(rol_id, clave, nombre, descripcion, prompt)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify({"id": rol_id, "clave": clave, "nombre": nombre, "descripcion": descripcion, "prompt": prompt})


@app.delete("/api/roles/<int:rol_id>")
@login_requerido
def api_eliminar_rol(rol_id):
    exito = eliminar_rol(rol_id)
    if not exito:
        return jsonify({"error": "No se pudo eliminar el rol."}), 404
    return jsonify({"ok": True})


# ----------------------------------------------------------------------
# API JSON: Usuarios y Perfil Administrativo (Show, Edit, Update, Delete)
# ----------------------------------------------------------------------


@app.get("/api/usuarios")
@login_requerido
def api_listar_usuarios():
    return jsonify({"usuarios": listar_usuarios()})


@app.get("/api/usuario/<int:usuario_id>")
@login_requerido
def api_obtener_usuario(usuario_id):
    """Show: Detalle del usuario."""
    usuario = obtener_usuario(usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado."}), 404
    return jsonify(usuario)


@app.post("/api/usuarios")
@login_requerido
def api_crear_usuario():
    """Crear nuevo usuario."""
    datos = request.get_json(silent=True) or {}
    usuario = (datos.get("usuario") or "").strip()
    password = (datos.get("password") or "").strip()
    rol = (datos.get("rol") or "usuario").strip()

    if not usuario or not password:
        return jsonify({"error": "El nombre de usuario y la contraseña son obligatorios."}), 400

    try:
        crear_usuario(usuario, password, rol)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    usuario_creado = obtener_usuario_por_nombre(usuario)
    return jsonify(usuario_creado), 201


@app.route("/api/usuario/<int:usuario_id>", methods=["POST", "PUT"])
@login_requerido
def api_actualizar_usuario(usuario_id):
    """Edit & Update: Actualizar datos y/o contraseña del usuario."""
    datos = request.get_json(silent=True) or {}
    usuario = (datos.get("usuario") or "").strip()
    rol = (datos.get("rol") or "usuario").strip()
    password = (datos.get("password") or "").strip()

    if not usuario:
        return jsonify({"error": "El nombre de usuario no puede estar vacío."}), 400

    try:
        actualizar_usuario(usuario_id, usuario, rol, nuevo_password=password if password else None)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    # Si se actualizó el propio usuario activo, sincronizar sesión
    usuario_actual = session.get("usuario")
    usuario_db = obtener_usuario(usuario_id)
    if usuario_actual and usuario_db:
        usuario_sesion_info = obtener_usuario_por_nombre(usuario_actual)
        if usuario_sesion_info and usuario_sesion_info["id"] == usuario_id:
            session["usuario"] = usuario_db["usuario"]
            session["rol"] = usuario_db["rol"]

    return jsonify(usuario_db)


@app.delete("/api/usuario/<int:usuario_id>")
@login_requerido
def api_eliminar_usuario(usuario_id):
    """Delete: Eliminar usuario."""
    usuario_actual = session.get("usuario")
    try:
        exito = eliminar_usuario(usuario_id, usuario_actual_nombre=usuario_actual)
        if not exito:
            return jsonify({"error": "Usuario no encontrado."}), 404
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify({"ok": True})


@app.get("/api/perfil")
@login_requerido
def api_obtener_perfil():
    """Show: Detalle del perfil del usuario actualmente autenticado."""
    usuario_nombre = session.get("usuario")
    if not usuario_nombre:
        return jsonify({"error": "No autenticado."}), 401
    usuario = obtener_usuario_por_nombre(usuario_nombre)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado."}), 404
    return jsonify(usuario)


@app.post("/api/perfil")
@login_requerido
def api_actualizar_perfil():
    """Update: Actualizar perfil y/o contraseña propia."""
    usuario_nombre = session.get("usuario")
    usuario_info = obtener_usuario_por_nombre(usuario_nombre)
    if not usuario_info:
        return jsonify({"error": "Usuario no encontrado."}), 404

    datos = request.get_json(silent=True) or {}
    nuevo_nombre = (datos.get("usuario") or usuario_nombre).strip()
    nuevo_password = (datos.get("password") or "").strip()

    try:
        actualizar_usuario(
            usuario_info["id"],
            nuevo_nombre,
            nuevo_rol=usuario_info["rol"],
            nuevo_password=nuevo_password if nuevo_password else None,
        )
        session["usuario"] = nuevo_nombre
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify(obtener_usuario(usuario_info["id"]))


# ----------------------------------------------------------------------
# API JSON: Sesiones de Chat (Multi-Conversación)
# ----------------------------------------------------------------------


@app.get("/api/sesiones")
@login_requerido
def api_todas_las_sesiones():
    agente = request.args.get("agente")
    return jsonify({"sesiones": listar_todas_las_sesiones(agente if agente else None)})


@app.get("/api/agente/<nombre>/sesiones")
@login_requerido
def api_listar_sesiones(nombre):
    _agente_o_404(nombre)
    return jsonify({"sesiones": listar_sesiones_agente(nombre)})


@app.post("/api/agente/<nombre>/sesiones")
@login_requerido
def api_crear_sesion(nombre):
    _agente_o_404(nombre)
    datos = request.get_json(silent=True) or {}
    titulo = (datos.get("titulo") or "").strip()
    nueva_sesion = crear_sesion_chat(nombre, titulo=titulo if titulo else None)
    return jsonify(nueva_sesion), 201


@app.get("/api/sesion/<int:sesion_id>")
@login_requerido
def api_obtener_sesion(sesion_id):
    sesion = obtener_sesion_chat(sesion_id)
    if not sesion:
        return jsonify({"error": "Conversación no encontrada."}), 404
    mensajes = obtener_todos_mensajes_sesion(sesion_id)
    sesion["mensajes"] = mensajes
    return jsonify(sesion)


@app.put("/api/sesion/<int:sesion_id>")
@login_requerido
def api_renombrar_sesion(sesion_id):
    sesion = obtener_sesion_chat(sesion_id)
    if not sesion:
        return jsonify({"error": "Conversación no encontrada."}), 404
    datos = request.get_json(silent=True) or {}
    titulo = (datos.get("titulo") or "").strip()
    if not titulo:
        return jsonify({"error": "El título no puede estar vacío."}), 400
    renombrar_sesion_chat(sesion_id, titulo)
    return jsonify({"ok": True, "id": sesion_id, "titulo": titulo})


@app.delete("/api/sesion/<int:sesion_id>")
@login_requerido
def api_eliminar_sesion(sesion_id):
    sesion = obtener_sesion_chat(sesion_id)
    if not sesion:
        return jsonify({"error": "Conversación no encontrada."}), 404
    eliminar_sesion_chat(sesion_id)
    return jsonify({"ok": True})


@app.post("/api/sesion/<int:sesion_id>/mensaje")
@login_requerido
def api_mensaje_sesion(sesion_id):
    sesion = obtener_sesion_chat(sesion_id)
    if not sesion:
        return jsonify({"error": "Conversación no encontrada."}), 404

    nombre = sesion["agente_nombre"]
    datos = request.get_json(silent=True) or {}
    mensaje = (datos.get("mensaje") or "").strip()
    if not mensaje:
        return jsonify({"error": "El mensaje no puede estar vacío."}), 400

    try:
        agente = AgenteDB(nombre)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    try:
        respuesta = agente.preguntar(mensaje, sesion_id=sesion_id)
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 500

    try:
        memorias = agente.actualizar_memoria(mensaje, respuesta)
    except Exception:
        memorias = []

    # Recargar datos actualizados de la sesión
    sesion_actualizada = obtener_sesion_chat(sesion_id)

    return jsonify(
        {
            "respuesta": respuesta,
            "memoria_guardada": bool(memorias),
            "sesion": sesion_actualizada,
        }
    )


# Compatibilidad retroactiva para endpoint de mensaje sin sesion_id explícito
@app.post("/api/agente/<nombre>/mensaje")
@login_requerido
def api_mensaje(nombre):
    _agente_o_404(nombre)
    sesion = obtener_o_crear_sesion_activa(nombre)
    return api_mensaje_sesion(sesion["id"])


# ----------------------------------------------------------------------
# API JSON: Bases de Conocimiento
# ----------------------------------------------------------------------


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


if __name__ == "__main__":
    app.run(debug=True)