// Lógica del Dashboard OpenAI / shadcn UI, Mantenedor de Usuarios, Roles y Conversaciones
(function () {
  "use strict";

  // Secciones y botones de pestaña
  var seccionAgentes = document.getElementById("dash-seccion-agentes");
  var seccionFuentes = document.getElementById("dash-seccion-fuentes");
  var seccionRoles = document.getElementById("dash-seccion-roles");
  var seccionUsuarios = document.getElementById("dash-seccion-usuarios");
  var seccionHistorial = document.getElementById("dash-seccion-historial");

  var btnTabAgentes = document.getElementById("btn-tab-dash-agentes");
  var btnTabFuentes = document.getElementById("btn-tab-dash-fuentes");
  var btnTabRoles = document.getElementById("btn-tab-dash-roles");
  var btnTabUsuarios = document.getElementById("btn-tab-dash-usuarios");
  var btnTabHistorial = document.getElementById("btn-tab-dash-historial");
  var btnAccionCrear = document.getElementById("btn-accion-crear");

  // Modal Agente
  var modalAgente = document.getElementById("modal-agente-dash");
  var formAgente = document.getElementById("form-agente-dash");
  var tituloModalAgente = document.getElementById("titulo-modal-agente-dash");
  var campoAgenteModo = document.getElementById("dash-agente-modo");
  var campoAgenteNombre = document.getElementById("dash-campo-nombre");
  var campoAgentePerfil = document.getElementById("dash-campo-perfil");
  var selectAgenteIdentidad = document.getElementById("dash-select-identidad");
  var bloqueAgenteCustom = document.getElementById("dash-bloque-personalizada");
  var campoAgenteCustom = document.getElementById("dash-identidad-custom");
  var listaAgenteFuentes = document.getElementById("dash-lista-fuentes");
  var btnGuardarAgente = document.getElementById("btn-guardar-agente-dash");

  // Modal Base de Conocimiento
  var modalFuente = document.getElementById("modal-fuente-dash");
  var formFuente = document.getElementById("form-fuente-dash");
  var tituloModalFuente = document.getElementById("titulo-modal-fuente-dash");
  var campoFuenteId = document.getElementById("dash-fuente-id");
  var campoFuenteNombre = document.getElementById("dash-fuente-nombre");
  var campoFuenteContenido = document.getElementById("dash-fuente-contenido");
  var btnGuardarFuente = document.getElementById("btn-guardar-fuente-dash");

  // Modal Rol / Identidad
  var modalRol = document.getElementById("modal-rol-dash");
  var formRol = document.getElementById("form-rol-dash");
  var tituloModalRol = document.getElementById("titulo-modal-rol-dash");
  var campoRolId = document.getElementById("dash-rol-id");
  var campoRolClave = document.getElementById("dash-rol-clave");
  var campoRolNombre = document.getElementById("dash-rol-nombre");
  var campoRolDescripcion = document.getElementById("dash-rol-descripcion");
  var campoRolPrompt = document.getElementById("dash-rol-prompt");
  var btnGuardarRol = document.getElementById("btn-guardar-rol-dash");

  // Modales Usuario (Show / Edit / Create)
  var modalShowUsuario = document.getElementById("modal-show-usuario");
  var showUsuarioAvatar = document.getElementById("show-usuario-avatar");
  var showUsuarioNombre = document.getElementById("show-usuario-nombre");
  var showUsuarioId = document.getElementById("show-usuario-id");
  var showUsuarioRol = document.getElementById("show-usuario-rol");
  var showUsuarioFecha = document.getElementById("show-usuario-fecha");
  var idUsuarioShowActual = null;

  var modalUsuario = document.getElementById("modal-usuario-dash");
  var formUsuario = document.getElementById("form-usuario-dash");
  var tituloModalUsuario = document.getElementById("titulo-modal-usuario-dash");
  var campoUsuarioId = document.getElementById("dash-usuario-id");
  var campoUsuarioModo = document.getElementById("dash-usuario-modo");
  var campoUsuarioNombre = document.getElementById("dash-usuario-nombre");
  var campoUsuarioRol = document.getElementById("dash-usuario-rol");
  var campoUsuarioPassword = document.getElementById("dash-usuario-password");
  var campoUsuarioPwdAyuda = document.getElementById("dash-usuario-pwd-ayuda");
  var btnGuardarUsuario = document.getElementById("btn-guardar-usuario-dash");

  // Modal Mi Perfil
  var modalMiPerfil = document.getElementById("modal-mi-perfil");
  var formMiPerfil = document.getElementById("form-mi-perfil");
  var campoPerfilNombre = document.getElementById("perfil-nombre");
  var campoPerfilPassword = document.getElementById("perfil-password");
  var btnGuardarMiPerfil = document.getElementById("btn-guardar-mi-perfil");

  // Modal Eliminar
  var modalEliminar = document.getElementById("modal-eliminar-dash");
  var tituloEliminar = document.getElementById("titulo-eliminar-dash");
  var descEliminar = document.getElementById("desc-eliminar-dash");
  var btnConfirmarEliminar = document.getElementById("btn-confirmar-eliminar-dash");

  // Visor de transcripción
  var filtroAgenteConversaciones = document.getElementById("filtro-agente-conversaciones");
  var contadorMantenedor = document.getElementById("contador-mantenedor-sesiones");
  var listaHilos = document.getElementById("dash-lista-hilos");
  var visorTitulo = document.getElementById("visor-titulo-sesion");
  var visorAgente = document.getElementById("visor-agente-sesion");
  var visorBadgeAgente = document.getElementById("visor-badge-agente");
  var visorContenedor = document.getElementById("visor-contenedor-mensajes");
  var btnEliminarSesionVisor = document.getElementById("btn-eliminar-sesion-visor");
  var btnAbrirChatVisor = document.getElementById("btn-abrir-chat-visor");
  var sesionActivaVisorId = null;

  var accionEliminarCallback = null;

  // Toast
  var toast = document.getElementById("toast");
  var contenidoToast = document.getElementById("toast-contenido");
  var iconoToast = document.getElementById("toast-icono");
  var textoToast = document.getElementById("texto-toast");

  function mostrarToast(mensaje, tipo) {
    var esExito = tipo === "exito";
    textoToast.textContent = mensaje;
    contenidoToast.className =
      "flex items-center gap-2.5 rounded-2xl px-5 py-3 text-sm font-semibold text-white shadow-2xl " +
      (esExito ? "bg-[#34A853]" : "bg-[#EA4335]");
    iconoToast.setAttribute("data-lucide", esExito ? "check-circle-2" : "alert-circle");
    toast.classList.remove("hidden");
    clearTimeout(toast._temporizador);
    toast._temporizador = setTimeout(function () {
      toast.classList.add("hidden");
    }, 4500);
    if (window.lucide) lucide.createIcons();
  }

  // ------------------------------------------------------------------
  // Pestañas del Dashboard
  // ------------------------------------------------------------------
  window.cambiarTabDashboard = function (tab) {
    seccionAgentes.classList.toggle("hidden", tab !== "agentes");
    seccionFuentes.classList.toggle("hidden", tab !== "fuentes");
    if (seccionRoles) seccionRoles.classList.toggle("hidden", tab !== "roles");
    if (seccionUsuarios) seccionUsuarios.classList.toggle("hidden", tab !== "usuarios");
    seccionHistorial.classList.toggle("hidden", tab !== "historial");

    var estiloActivo = "inline-flex items-center gap-2 rounded-xl bg-white/15 px-3.5 py-1.5 text-xs font-bold text-white shadow-sm transition";
    var estiloInactivo = "inline-flex items-center gap-2 rounded-xl px-3.5 py-1.5 text-xs font-semibold text-zinc-400 transition hover:bg-white/5 hover:text-white";

    btnTabAgentes.className = tab === "agentes" ? estiloActivo : estiloInactivo;
    btnTabFuentes.className = tab === "fuentes" ? estiloActivo : estiloInactivo;
    if (btnTabRoles) btnTabRoles.className = tab === "roles" ? estiloActivo : estiloInactivo;
    if (btnTabUsuarios) btnTabUsuarios.className = tab === "usuarios" ? estiloActivo : estiloInactivo;
    btnTabHistorial.className = tab === "historial" ? estiloActivo : estiloInactivo;

    if (tab === "agentes") {
      btnAccionCrear.classList.remove("hidden");
      btnAccionCrear.onclick = abrirModalCrearAgenteDash;
      btnAccionCrear.querySelector("span").textContent = "Nuevo Agente";
    } else if (tab === "fuentes") {
      btnAccionCrear.classList.remove("hidden");
      btnAccionCrear.onclick = abrirModalCrearFuenteDash;
      btnAccionCrear.querySelector("span").textContent = "Nueva Base";
    } else if (tab === "roles") {
      btnAccionCrear.classList.remove("hidden");
      btnAccionCrear.onclick = abrirModalCrearRolDash;
      btnAccionCrear.querySelector("span").textContent = "Nuevo Rol";
    } else if (tab === "usuarios") {
      btnAccionCrear.classList.remove("hidden");
      btnAccionCrear.onclick = abrirModalCrearUsuarioDash;
      btnAccionCrear.querySelector("span").textContent = "Nuevo Usuario";
    } else {
      btnAccionCrear.classList.add("hidden");
    }

    if (window.lucide) lucide.createIcons();
  };

  // ------------------------------------------------------------------
  // Módulo de Usuarios (Show -> Edit -> Update)
  // ------------------------------------------------------------------
  window.verDetalleUsuario = function (id) {
    idUsuarioShowActual = id;
    fetch("/api/usuario/" + id)
      .then(function (res) { return res.json(); })
      .then(function (u) {
        showUsuarioAvatar.textContent = (u.usuario || "US").slice(0, 2).toUpperCase();
        showUsuarioNombre.textContent = u.usuario;
        showUsuarioId.textContent = "ID: " + u.id;
        showUsuarioRol.textContent = u.rol === "admin" ? "Administrador" : "Usuario Estándar";
        showUsuarioFecha.textContent = u.creado_en ? u.creado_en.slice(0, 16) : "Reciente";

        modalShowUsuario.classList.remove("hidden");
        modalShowUsuario.classList.add("flex");
        if (window.lucide) lucide.createIcons();
      })
      .catch(function () {
        mostrarToast("No se pudo cargar la ficha del usuario.");
      });
  };

  window.cerrarModalShowUsuario = function () {
    modalShowUsuario.classList.add("hidden");
    modalShowUsuario.classList.remove("flex");
    idUsuarioShowActual = null;
  };

  window.procederEditarDesdeShow = function () {
    var id = idUsuarioShowActual;
    cerrarModalShowUsuario();
    if (id) abrirModalEditarUsuarioDash(id);
  };

  window.abrirModalCrearUsuarioDash = function () {
    campoUsuarioId.value = "";
    campoUsuarioModo.value = "crear";
    campoUsuarioNombre.value = "";
    campoUsuarioRol.value = "usuario";
    campoUsuarioPassword.value = "";
    campoUsuarioPassword.required = true;
    campoUsuarioPwdAyuda.textContent = "(obligatoria)";
    tituloModalUsuario.textContent = "Nuevo Usuario";

    modalUsuario.classList.remove("hidden");
    modalUsuario.classList.add("flex");
    setTimeout(function () { campoUsuarioNombre.focus(); }, 50);
  };

  window.abrirModalEditarUsuarioDash = function (id) {
    fetch("/api/usuario/" + id)
      .then(function (res) { return res.json(); })
      .then(function (u) {
        campoUsuarioId.value = u.id;
        campoUsuarioModo.value = "editar";
        campoUsuarioNombre.value = u.usuario;
        campoUsuarioRol.value = u.rol || "usuario";
        campoUsuarioPassword.value = "";
        campoUsuarioPassword.required = false;
        campoUsuarioPwdAyuda.textContent = "(dejar en blanco para mantener la actual)";
        tituloModalUsuario.textContent = "Editar Usuario: " + u.usuario;

        modalUsuario.classList.remove("hidden");
        modalUsuario.classList.add("flex");
      })
      .catch(function () {
        mostrarToast("No se pudo cargar la información del usuario.");
      });
  };

  window.cerrarModalUsuarioDash = function () {
    modalUsuario.classList.add("hidden");
    modalUsuario.classList.remove("flex");
  };

  formUsuario.addEventListener("submit", function (e) {
    e.preventDefault();
    btnGuardarUsuario.disabled = true;

    var modo = campoUsuarioModo.value;
    var id = campoUsuarioId.value;
    var nombre = campoUsuarioNombre.value.trim();
    var rol = campoUsuarioRol.value;
    var password = campoUsuarioPassword.value.trim();

    if (!nombre) {
      mostrarToast("El nombre de usuario es obligatorio.");
      btnGuardarUsuario.disabled = false;
      return;
    }
    if (modo === "crear" && !password) {
      mostrarToast("La contraseña es obligatoria para un nuevo usuario.");
      btnGuardarUsuario.disabled = false;
      return;
    }

    var url = modo === "crear" ? "/api/usuarios" : "/api/usuario/" + id;
    var payload = { usuario: nombre, rol: rol };
    if (password) payload.password = password;

    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(function (res) { return res.json().then(function (d) { return { ok: res.ok, datos: d }; }); })
      .then(function (resultado) {
        if (!resultado.ok) throw new Error(resultado.datos.error || "Error al guardar el usuario.");
        cerrarModalUsuarioDash();
        mostrarToast(modo === "crear" ? "Usuario creado exitosamente." : "Usuario actualizado (Update).", "exito");
        setTimeout(function () { window.location.reload(); }, 600);
      })
      .catch(function (error) {
        mostrarToast(error.message);
      })
      .finally(function () {
        btnGuardarUsuario.disabled = false;
      });
  });

  window.confirmarEliminarUsuarioDash = function (id, nombre) {
    tituloEliminar.textContent = "¿Eliminar usuario '" + nombre + "'?";
    descEliminar.textContent = "Se revocarán todos los permisos de acceso para esta cuenta. Esta acción no se puede deshacer.";
    accionEliminarCallback = function () {
      fetch("/api/usuario/" + id, { method: "DELETE" })
        .then(function (res) { return res.json().then(function (d) { return { ok: res.ok, datos: d }; }); })
        .then(function (resultado) {
          if (!resultado.ok) throw new Error(resultado.datos.error || "No se pudo eliminar el usuario.");
          cerrarModalEliminarDash();
          mostrarToast("Usuario eliminado.", "exito");
          setTimeout(function () { window.location.reload(); }, 600);
        })
        .catch(function (error) {
          mostrarToast(error.message);
        });
    };
    modalEliminar.classList.remove("hidden");
    modalEliminar.classList.add("flex");
  };

  // ------------------------------------------------------------------
  // Modal Mi Perfil (Configurar Cuenta en Sesión)
  // ------------------------------------------------------------------
  window.abrirModalMiPerfil = function () {
    campoPerfilPassword.value = "";
    modalMiPerfil.classList.remove("hidden");
    modalMiPerfil.classList.add("flex");
  };

  window.cerrarModalMiPerfil = function () {
    modalMiPerfil.classList.add("hidden");
    modalMiPerfil.classList.remove("flex");
  };

  formMiPerfil.addEventListener("submit", function (e) {
    e.preventDefault();
    btnGuardarMiPerfil.disabled = true;

    var nombre = campoPerfilNombre.value.trim();
    var password = campoPerfilPassword.value.trim();

    fetch("/api/perfil", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ usuario: nombre, password: password }),
    })
      .then(function (res) { return res.json().then(function (d) { return { ok: res.ok, datos: d }; }); })
      .then(function (resultado) {
        if (!resultado.ok) throw new Error(resultado.datos.error || "Error al actualizar perfil.");
        cerrarModalMiPerfil();
        mostrarToast("Perfil actualizado correctamente.", "exito");
        setTimeout(function () { window.location.reload(); }, 600);
      })
      .catch(function (error) {
        mostrarToast(error.message);
      })
      .finally(function () {
        btnGuardarMiPerfil.disabled = false;
      });
  });

  // ------------------------------------------------------------------
  // Manejo de Avatar e Imágenes
  // ------------------------------------------------------------------
  window.subirAvatarArchivo = function (input, prefijo) {
    if (!input.files || !input.files[0]) return;
    var file = input.files[0];
    var formData = new FormData();
    formData.append("avatar", file);

    mostrarToast("Subiendo imagen…", "exito");
    fetch("/api/upload/avatar", {
      method: "POST",
      body: formData,
    })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (!d.ok) throw new Error(d.error || "Error al subir imagen.");
        window.actualizarAvatarUrlInput(d.url, prefijo);
        mostrarToast("Imagen cargada con éxito.", "exito");
      })
      .catch(function (err) {
        mostrarToast(err.message);
      });
  };

  window.actualizarAvatarUrlInput = function (url, prefijo) {
    var urlLimpia = (url || "").trim();
    var previewImg = document.getElementById(prefijo + "-avatar-preview-img");
    var previewInitials = document.getElementById(prefijo + "-avatar-preview-initials");
    var campoUrl = document.getElementById(prefijo + "-campo-avatar-url");
    var campoInput = document.getElementById(prefijo + "-campo-avatar-url-input");

    if (campoUrl) campoUrl.value = urlLimpia;
    if (campoInput && campoInput.value !== urlLimpia) campoInput.value = urlLimpia;

    if (previewImg && previewInitials) {
      if (urlLimpia) {
        previewImg.src = urlLimpia;
        previewImg.classList.remove("hidden");
        previewInitials.classList.add("hidden");
      } else {
        previewImg.src = "";
        previewImg.classList.add("hidden");
        previewInitials.classList.remove("hidden");
      }
    }
  };

  window.limpiarAvatarSeleccionado = function (prefijo) {
    window.actualizarAvatarUrlInput("", prefijo);
    var inputFile = document.getElementById(prefijo + "-input-avatar-file");
    if (inputFile) inputFile.value = "";
  };

  // ------------------------------------------------------------------
  // Modal Agente (Crear / Editar)
  // ------------------------------------------------------------------
  window.abrirModalCrearAgenteDash = function () {
    campoAgenteModo.value = "crear";
    campoAgenteNombre.value = "";
    campoAgenteNombre.disabled = false;
    campoAgentePerfil.value = "";
    selectAgenteIdentidad.value = "";
    campoAgenteCustom.value = "";
    bloqueAgenteCustom.classList.add("hidden");
    tituloModalAgente.textContent = "Crear Nuevo Agente";

    window.limpiarAvatarSeleccionado("dash");

    listaAgenteFuentes.querySelectorAll("input[type=checkbox]").forEach(function (cb) {
      cb.checked = false;
    });

    modalAgente.classList.remove("hidden");
    modalAgente.classList.add("flex");
    setTimeout(function () { campoAgenteNombre.focus(); }, 50);
  };

  window.abrirModalEditarAgenteDash = function (nombre) {
    fetch("/api/agente/" + encodeURIComponent(nombre))
      .then(function (res) { return res.json(); })
      .then(function (datos) {
        campoAgenteModo.value = "editar";
        campoAgenteNombre.value = datos.nombre;
        campoAgenteNombre.disabled = true;
        campoAgentePerfil.value = datos.perfil || "";
        tituloModalAgente.textContent = "Editar Agente: " + datos.nombre;

        if (datos.avatar_url) {
          window.actualizarAvatarUrlInput(datos.avatar_url, "dash");
        } else {
          window.limpiarAvatarSeleccionado("dash");
          var initSpan = document.getElementById("dash-avatar-preview-initials");
          if (initSpan) initSpan.textContent = (datos.nombre || "AG").slice(0, 2).toUpperCase();
        }

        var fuentesIds = (datos.fuentes || []).map(function (f) { return f.id; });
        listaAgenteFuentes.querySelectorAll("input[type=checkbox]").forEach(function (cb) {
          cb.checked = fuentesIds.indexOf(parseInt(cb.value, 10)) !== -1;
        });

        if (datos.identidad.personalizada) {
          selectAgenteIdentidad.value = "personalizada";
          campoAgenteCustom.value = datos.identidad.prompt || "";
          bloqueAgenteCustom.classList.remove("hidden");
        } else {
          selectAgenteIdentidad.value = datos.identidad.clave || "";
          campoAgenteCustom.value = "";
          bloqueAgenteCustom.classList.add("hidden");
        }

        modalAgente.classList.remove("hidden");
        modalAgente.classList.add("flex");
      })
      .catch(function () {
        mostrarToast("No se pudo cargar la información del agente.");
      });
  };

  window.cerrarModalAgenteDash = function () {
    modalAgente.classList.add("hidden");
    modalAgente.classList.remove("flex");
  };

  selectAgenteIdentidad.addEventListener("change", function () {
    var esCustom = selectAgenteIdentidad.value === "personalizada";
    bloqueAgenteCustom.classList.toggle("hidden", !esCustom);
    if (!esCustom) campoAgenteCustom.value = "";
  });

  formAgente.addEventListener("submit", function (e) {
    e.preventDefault();
    btnGuardarAgente.disabled = true;

    var modo = campoAgenteModo.value;
    var nombre = campoAgenteNombre.value.trim();
    var perfil = campoAgentePerfil.value.trim();
    var custom = campoAgenteCustom.value.trim();
    var clave = selectAgenteIdentidad.value;
    var avatarUrl = document.getElementById("dash-campo-avatar-url") ? document.getElementById("dash-campo-avatar-url").value.trim() : "";

    var seleccionadas = [];
    listaAgenteFuentes.querySelectorAll("input[type=checkbox]:checked").forEach(function (cb) {
      seleccionadas.push(parseInt(cb.value, 10));
    });

    var url = modo === "crear" ? "/api/agentes" : "/api/agente/" + encodeURIComponent(nombre) + "/editar";
    var payload = {
      nombre: nombre,
      perfil: perfil,
      avatar_url: avatarUrl,
      fuentes: seleccionadas,
    };

    if (custom) payload.identidad_custom = custom;
    else if (clave && clave !== "personalizada") payload.identidad = clave;

    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(function (res) { return res.json().then(function (d) { return { ok: res.ok, datos: d }; }); })
      .then(function (resultado) {
        if (!resultado.ok) throw new Error(resultado.datos.error || "Error al guardar el agente.");
        cerrarModalAgenteDash();
        mostrarToast("Agente guardado exitosamente.", "exito");
        setTimeout(function () { window.location.reload(); }, 600);
      })
      .catch(function (error) {
        mostrarToast(error.message);
      })
      .finally(function () {
        btnGuardarAgente.disabled = false;
      });
  });

  // ------------------------------------------------------------------
  // Modal Base de Conocimiento (Crear / Editar)
  // ------------------------------------------------------------------
  window.abrirModalCrearFuenteDash = function () {
    campoFuenteId.value = "";
    campoFuenteNombre.value = "";
    campoFuenteContenido.value = "";
    tituloModalFuente.textContent = "Nueva Base de Conocimiento";
    modalFuente.classList.remove("hidden");
    modalFuente.classList.add("flex");
    setTimeout(function () { campoFuenteNombre.focus(); }, 50);
  };

  window.abrirModalEditarFuenteDash = function (id) {
    fetch("/api/fuentes/" + id)
      .then(function (res) { return res.json(); })
      .then(function (datos) {
        campoFuenteId.value = datos.id;
        campoFuenteNombre.value = datos.nombre;
        campoFuenteContenido.value = datos.contenido || "";
        tituloModalFuente.textContent = "Editar Base de Conocimiento";
        modalFuente.classList.remove("hidden");
        modalFuente.classList.add("flex");
      })
      .catch(function () {
        mostrarToast("No se pudo cargar la base de conocimiento.");
      });
  };

  window.cerrarModalFuenteDash = function () {
    modalFuente.classList.add("hidden");
    modalFuente.classList.remove("flex");
  };

  formFuente.addEventListener("submit", function (e) {
    e.preventDefault();
    btnGuardarFuente.disabled = true;

    var id = campoFuenteId.value;
    var nombre = campoFuenteNombre.value.trim();
    var contenido = campoFuenteContenido.value.trim();

    if (!nombre) {
      mostrarToast("Escribe un nombre para la base.");
      btnGuardarFuente.disabled = false;
      return;
    }

    var url = id ? "/api/fuentes/" + id : "/api/fuentes";

    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nombre: nombre, contenido: contenido }),
    })
      .then(function (res) { return res.json().then(function (d) { return { ok: res.ok, datos: d }; }); })
      .then(function (resultado) {
        if (!resultado.ok) throw new Error(resultado.datos.error || "Error al guardar la base.");
        cerrarModalFuenteDash();
        mostrarToast("Base de conocimiento guardada.", "exito");
        setTimeout(function () { window.location.reload(); }, 600);
      })
      .catch(function (error) {
        mostrarToast(error.message);
      })
      .finally(function () {
        btnGuardarFuente.disabled = false;
      });
  });

  // ------------------------------------------------------------------
  // Modal Rol e Identidad (Crear / Editar)
  // ------------------------------------------------------------------
  window.abrirModalCrearRolDash = function () {
    campoRolId.value = "";
    campoRolClave.value = "";
    campoRolClave.disabled = false;
    campoRolNombre.value = "";
    campoRolDescripcion.value = "";
    campoRolPrompt.value = "";
    tituloModalRol.textContent = "Nuevo Rol / Identidad";
    modalRol.classList.remove("hidden");
    modalRol.classList.add("flex");
    setTimeout(function () { campoRolClave.focus(); }, 50);
  };

  window.abrirModalEditarRolDash = function (id) {
    fetch("/api/roles/" + id)
      .then(function (res) { return res.json(); })
      .then(function (datos) {
        campoRolId.value = datos.id;
        campoRolClave.value = datos.clave;
        campoRolNombre.value = datos.nombre;
        campoRolDescripcion.value = datos.descripcion || "";
        campoRolPrompt.value = datos.prompt || "";
        tituloModalRol.textContent = "Editar Rol: " + datos.nombre;
        modalRol.classList.remove("hidden");
        modalRol.classList.add("flex");
      })
      .catch(function () {
        mostrarToast("No se pudo cargar la información del rol.");
      });
  };

  window.cerrarModalRolDash = function () {
    modalRol.classList.add("hidden");
    modalRol.classList.remove("flex");
  };

  formRol.addEventListener("submit", function (e) {
    e.preventDefault();
    btnGuardarRol.disabled = true;

    var id = campoRolId.value;
    var clave = campoRolClave.value.trim().toLowerCase();
    var nombre = campoRolNombre.value.trim();
    var descripcion = campoRolDescripcion.value.trim();
    var prompt = campoRolPrompt.value.trim();

    if (!clave || !nombre || !prompt) {
      mostrarToast("La clave, el nombre y el prompt son obligatorios.");
      btnGuardarRol.disabled = false;
      return;
    }

    var url = id ? "/api/roles/" + id : "/api/roles";

    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        clave: clave,
        nombre: nombre,
        descripcion: descripcion,
        prompt: prompt,
      }),
    })
      .then(function (res) { return res.json().then(function (d) { return { ok: res.ok, datos: d }; }); })
      .then(function (resultado) {
        if (!resultado.ok) throw new Error(resultado.datos.error || "Error al guardar el rol.");
        cerrarModalRolDash();
        mostrarToast("Rol guardado exitosamente.", "exito");
        setTimeout(function () { window.location.reload(); }, 600);
      })
      .catch(function (error) {
        mostrarToast(error.message);
      })
      .finally(function () {
        btnGuardarRol.disabled = false;
      });
  });

  // ------------------------------------------------------------------
  // Eliminaciones de Agente, Base, Rol con Confirmación
  // ------------------------------------------------------------------
  window.confirmarEliminarAgenteDash = function (nombre) {
    tituloEliminar.textContent = "¿Eliminar al agente '" + nombre + "'?";
    descEliminar.textContent = "Se eliminará toda la memoria, perfil, hilos de chat y mensajes de este agente. Esta acción no se puede deshacer.";
    accionEliminarCallback = function () {
      fetch("/api/agente/" + encodeURIComponent(nombre), { method: "DELETE" })
        .then(function (r) { return r.json(); })
        .then(function () {
          cerrarModalEliminarDash();
          mostrarToast("Agente eliminado.", "exito");
          setTimeout(function () { window.location.reload(); }, 600);
        })
        .catch(function () {
          mostrarToast("No se pudo eliminar el agente.");
        });
    };
    modalEliminar.classList.remove("hidden");
    modalEliminar.classList.add("flex");
  };

  window.confirmarEliminarFuenteDash = function (id, nombre) {
    tituloEliminar.textContent = "¿Eliminar base '" + nombre + "'?";
    descEliminar.textContent = "Se desvinculará de todos los agentes que la utilizan.";
    accionEliminarCallback = function () {
      fetch("/api/fuentes/" + id, { method: "DELETE" })
        .then(function (r) { return r.json(); })
        .then(function () {
          cerrarModalEliminarDash();
          mostrarToast("Base de conocimiento eliminada.", "exito");
          setTimeout(function () { window.location.reload(); }, 600);
        })
        .catch(function () {
          mostrarToast("No se pudo eliminar la base.");
        });
    };
    modalEliminar.classList.remove("hidden");
    modalEliminar.classList.add("flex");
  };

  window.confirmarEliminarRolDash = function (id, nombre) {
    tituloEliminar.textContent = "¿Eliminar rol '" + nombre + "'?";
    descEliminar.textContent = "Los agentes que utilicen este rol se reasignarán automáticamente al rol Básico por defecto.";
    accionEliminarCallback = function () {
      fetch("/api/roles/" + id, { method: "DELETE" })
        .then(function (r) { return r.json(); })
        .then(function () {
          cerrarModalEliminarDash();
          mostrarToast("Rol eliminado.", "exito");
          setTimeout(function () { window.location.reload(); }, 600);
        })
        .catch(function () {
          mostrarToast("No se pudo eliminar el rol.");
        });
    };
    modalEliminar.classList.remove("hidden");
    modalEliminar.classList.add("flex");
  };

  window.cerrarModalEliminarDash = function () {
    modalEliminar.classList.add("hidden");
    modalEliminar.classList.remove("flex");
    accionEliminarCallback = null;
  };

  btnConfirmarEliminar.addEventListener("click", function () {
    if (accionEliminarCallback) accionEliminarCallback();
  });

  // ------------------------------------------------------------------
  // Mantenedor de Conversaciones (Filtro, Explorador, Transcripciones)
  // ------------------------------------------------------------------
  window.verConversacionesAgente = function (nombre) {
    cambiarTabDashboard("historial");
    if (filtroAgenteConversaciones) {
      filtroAgenteConversaciones.value = nombre;
    }
    filtrarConversacionesPorAgente(nombre);
  };

  window.filtrarConversacionesPorAgente = function (agenteNombre) {
    var url = agenteNombre ? "/api/sesiones?agente=" + encodeURIComponent(agenteNombre) : "/api/sesiones";
    fetch(url)
      .then(function (r) { return r.json(); })
      .then(function (datos) {
        var sesiones = datos.sesiones || [];
        if (contadorMantenedor) {
          contadorMantenedor.textContent = sesiones.length + " conversaciones";
        }
        listaHilos.innerHTML = "";
        if (!sesiones.length) {
          listaHilos.innerHTML = '<p class="text-center text-xs text-zinc-500 py-12">No hay conversaciones registradas' + (agenteNombre ? ' para ' + agenteNombre : '') + '.</p>';
          return;
        }

        sesiones.forEach(function (ses) {
          var btn = document.createElement("button");
          btn.className = "w-full text-left rounded-2xl border border-white/5 bg-white/[0.02] p-4 transition hover:border-[#006FEE]/40 hover:bg-white/[0.06] focus:border-[#006FEE] focus:bg-white/[0.06]";
          btn.innerHTML =
            '<div class="flex items-center justify-between">' +
            '  <span class="heroui-chip heroui-chip-primary text-[10px] py-0.5 px-2 font-bold">' + ses.agente_nombre + '</span>' +
            '  <span class="text-[11px] text-zinc-500">' + (ses.actualizado_en ? ses.actualizado_en.slice(0, 16) : "") + '</span>' +
            '</div>' +
            '<p class="mt-2 truncate text-xs font-bold text-white">' + ses.titulo + '</p>' +
            '<p class="mt-1 text-[11px] text-zinc-400 truncate">' + (ses.ultimo_mensaje || '(Sin mensajes aún)') + '</p>' +
            '<div class="mt-2 flex items-center gap-2 text-[10px] text-zinc-500">' +
            '  <i data-lucide="message-circle" class="h-3 w-3"></i>' +
            '  <span>' + ses.total_mensajes + ' mensaje(s)</span>' +
            '</div>';

          btn.addEventListener("click", function () {
            cargarTranscripcionSesion(ses.id, ses.agente_nombre, ses.titulo);
          });
          listaHilos.appendChild(btn);
        });

        if (window.lucide) lucide.createIcons();

        if (sesiones[0]) {
          cargarTranscripcionSesion(sesiones[0].id, sesiones[0].agente_nombre, sesiones[0].titulo);
        }
      });
  };

  window.cargarTranscripcionSesion = function (sesionId, agenteNombre, titulo) {
    sesionActivaVisorId = sesionId;
    visorTitulo.textContent = titulo || "Conversación";
    visorAgente.textContent = "Historial completo con " + agenteNombre;
    
    visorBadgeAgente.textContent = agenteNombre;
    visorBadgeAgente.classList.remove("hidden");
    
    btnEliminarSesionVisor.classList.remove("hidden");
    btnAbrirChatVisor.classList.remove("hidden");
    btnAbrirChatVisor.href = "/agente/" + encodeURIComponent(agenteNombre);

    visorContenedor.innerHTML = '<div class="py-12 text-center text-xs text-zinc-400">Cargando transcripción…</div>';

    fetch("/api/sesion/" + sesionId)
      .then(function (r) { return r.json(); })
      .then(function (datos) {
        var mensajes = datos.mensajes || [];
        visorContenedor.innerHTML = "";
        if (!mensajes.length) {
          visorContenedor.innerHTML = '<div class="py-12 text-center text-xs text-zinc-500">No hay mensajes en esta conversación aún.</div>';
          return;
        }

        mensajes.forEach(function (m) {
          var fila = document.createElement("div");
          fila.className = "flex " + (m.rol === "user" ? "justify-end" : "justify-start");
          
          var caja = document.createElement("div");
          caja.className = "max-w-[85%]";

          var burbuja = document.createElement("div");
          if (m.rol === "user") {
            burbuja.className = "rounded-2xl rounded-br-sm bg-[#1a73e8] px-4 py-3 text-xs text-white shadow";
            burbuja.textContent = m.mensaje;
          } else {
            burbuja.className = "rounded-2xl rounded-bl-sm border border-white/10 bg-[#1e1f20] px-4 py-3 text-xs leading-relaxed text-[#e3e3e3] shadow prose-chat";
            if (window.marked && window.DOMPurify) {
              burbuja.innerHTML = DOMPurify.sanitize(marked.parse(m.mensaje, { breaks: true, gfm: true }));
            } else {
              burbuja.textContent = m.mensaje;
            }
          }

          var meta = document.createElement("div");
          meta.className = "text-[10px] text-[#c4c7c5] mt-1 " + (m.rol === "user" ? "text-right" : "text-left");
          meta.textContent = (m.rol === "user" ? "Usuario" : agenteNombre) + " · " + (m.fecha || "") + " " + (m.hora || "");

          caja.appendChild(burbuja);
          caja.appendChild(meta);
          fila.appendChild(caja);
          visorContenedor.appendChild(fila);
        });

        visorContenedor.scrollTop = visorContenedor.scrollHeight;
      })
      .catch(function () {
        visorContenedor.innerHTML = '<div class="py-12 text-center text-xs text-[#f28b82]">Error al cargar la transcripción.</div>';
      });
  };

  window.eliminarSesionDesdeVisor = function () {
    if (!sesionActivaVisorId) return;
    if (!confirm("¿Deseas eliminar este hilo de conversación del mantenedor?")) return;

    fetch("/api/sesion/" + sesionActivaVisorId, { method: "DELETE" })
      .then(function (r) { return r.json(); })
      .then(function () {
        mostrarToast("Conversación eliminada del mantenedor.", "exito");
        setTimeout(function () { window.location.reload(); }, 600);
      });
  };

  // Escape para cerrar modales
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      cerrarModalAgenteDash();
      cerrarModalFuenteDash();
      if (window.cerrarModalRolDash) cerrarModalRolDash();
      if (window.cerrarModalShowUsuario) cerrarModalShowUsuario();
      if (window.cerrarModalUsuarioDash) cerrarModalUsuarioDash();
      if (window.cerrarModalMiPerfil) cerrarModalMiPerfil();
      cerrarModalEliminarDash();
    }
  });
})();
