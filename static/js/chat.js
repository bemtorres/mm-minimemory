// Lógica del Chat Google AI: Hilos, Memoria, Sugerencias, Gestión y Ergonomía
(function () {
  "use strict";

  var contenedorMensajes = document.getElementById("mensajes");
  var formMensaje = document.getElementById("form-mensaje");
  var campoMensaje = document.getElementById("campo-mensaje");
  var botonEnviar = document.getElementById("boton-enviar");
  var listaSesionesSidebar = document.getElementById("lista-sesiones-sidebar");
  var sidebar = document.getElementById("chat-sidebar");

  var modalRenombrar = document.getElementById("modal-renombrar-sesion");
  var campoRenombrarId = document.getElementById("renombrar-sesion-id");
  var campoRenombrarTitulo = document.getElementById("campo-renombrar-titulo");

  var modalLimpiarMemoria = document.getElementById("modal-limpiar-memoria");
  var modalGestionAgente = document.getElementById("modal-gestion-agente");
  var formGestionAgente = document.getElementById("form-gestion-agente");
  var selectIdentidad = document.getElementById("editar-identidad");
  var bloqueCustom = document.getElementById("bloque-identidad-custom");

  var nombreAgente = document.body.dataset.agente;
  var sesionActivaId = parseInt(document.body.dataset.sesionId, 10) || null;

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
    }, 4000);
    if (window.lucide) lucide.createIcons();
  }

  // ------------------------------------------------------------------
  // Control de Barra Lateral y Selector de Agente
  // ------------------------------------------------------------------
  window.toggleSidebarChat = function () {
    if (sidebar) {
      sidebar.classList.toggle("hidden");
    }
  };

  window.cambiarAgenteActivo = function (nuevoNombre) {
    if (nuevoNombre && nuevoNombre !== nombreAgente) {
      window.location.href = "/agente/" + encodeURIComponent(nuevoNombre);
    }
  };

  window.filtrarHilosSidebar = function (query) {
    var q = (query || "").toLowerCase().trim();
    document.querySelectorAll("#lista-sesiones-sidebar [data-sesion-item]").forEach(function (el) {
      var tit = (el.dataset.sesionTitulo || "").toLowerCase();
      el.classList.toggle("hidden", q !== "" && tit.indexOf(q) === -1);
    });
  };

  // ------------------------------------------------------------------
  // Sugerencias de Inicio Rápido
  // ------------------------------------------------------------------
  window.usarSugerencia = function (texto) {
    campoMensaje.value = texto;
    formMensaje.requestSubmit();
  };

  // ------------------------------------------------------------------
  // Copiar al Portapapeles
  // ------------------------------------------------------------------
  window.copiarTexto = function (texto, btn) {
    if (!navigator.clipboard) return;
    navigator.clipboard.writeText(texto).then(function () {
      var htmlOriginal = btn.innerHTML;
      btn.innerHTML = '<i data-lucide="check" class="h-3 w-3 inline text-[#34A853]"></i> <span class="text-[#34A853]">¡Copiado!</span>';
      if (window.lucide) lucide.createIcons();
      setTimeout(function () {
        btn.innerHTML = htmlOriginal;
        if (window.lucide) lucide.createIcons();
      }, 2000);
    });
  };

  // ------------------------------------------------------------------
  // Carga y Renderizado de Mensajes
  // ------------------------------------------------------------------
  function cargarMensajesSesion(sesionId) {
    contenedorMensajes.innerHTML =
      '<div class="flex h-64 items-center justify-center text-xs text-[#5f6368] dark:text-[#c4c7c5]">' +
      '  <span class="animate-pulse">Cargando conversación…</span>' +
      '</div>';

    fetch("/api/sesion/" + sesionId)
      .then(function (r) { return r.json(); })
      .then(function (datos) {
        contenedorMensajes.innerHTML = "";
        var mensajes = datos.mensajes || [];

        if (!mensajes.length) {
          // Welcome Screen con sugerencias de inicio rápido estilo Google Gemini
          contenedorMensajes.innerHTML =
            '<div class="mx-auto max-w-2xl py-10 text-center animate-fade-in">' +
            '  <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-3xl bg-gradient-to-tr from-[#1a73e8] via-[#a142f4] to-[#ea4335] text-white shadow-xl shadow-[#1a73e8]/25 mb-4">' +
            '    <i data-lucide="sparkles" class="h-8 w-8"></i>' +
            '  </div>' +
            '  <h3 class="text-xl font-bold text-[#202124] dark:text-white">¡Hola! Soy ' + nombreAgente + '</h3>' +
            '  <p class="text-xs text-[#5f6368] dark:text-[#c4c7c5] mt-1 max-w-md mx-auto">Pregúntame cualquier duda sobre mis bases de conocimiento o pídemelo en tu estilo preferido.</p>' +
            '  <div class="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-left max-w-xl mx-auto">' +
            '    <button onclick="usarSugerencia(\'¿Qué conocimientos o documentos tienes disponibles?\')" class="rounded-2xl border border-black/10 dark:border-white/10 bg-white dark:bg-[#1e1f20] hover:border-[#1a73e8] dark:hover:border-[#8ab4f8] p-3.5 text-xs text-[#202124] dark:text-[#e3e3e3] shadow-sm transition hover:scale-[1.02] active:scale-95 text-left">' +
            '      <p class="font-bold flex items-center gap-1.5"><i data-lucide="book-open" class="h-3.5 w-3.5 text-[#1e8e3e] dark:text-[#81c995]"></i> Bases Temáticas</p>' +
            '      <p class="text-[11px] text-[#5f6368] dark:text-[#c4c7c5] mt-1">¿Qué conocimientos tienes disponibles?</p>' +
            '    </button>' +
            '    <button onclick="usarSugerencia(\'Resume los puntos clave de la información que conoces.\')" class="rounded-2xl border border-black/10 dark:border-white/10 bg-white dark:bg-[#1e1f20] hover:border-[#1a73e8] dark:hover:border-[#8ab4f8] p-3.5 text-xs text-[#202124] dark:text-[#e3e3e3] shadow-sm transition hover:scale-[1.02] active:scale-95 text-left">' +
            '      <p class="font-bold flex items-center gap-1.5"><i data-lucide="file-text" class="h-3.5 w-3.5 text-[#1a73e8] dark:text-[#8ab4f8]"></i> Resumen Rápido</p>' +
            '      <p class="text-[11px] text-[#5f6368] dark:text-[#c4c7c5] mt-1">Resume los puntos clave de tus bases.</p>' +
            '    </button>' +
            '    <button onclick="usarSugerencia(\'Explícame cómo funciona tu memoria en nuestras conversaciones.\')" class="rounded-2xl border border-black/10 dark:border-white/10 bg-white dark:bg-[#1e1f20] hover:border-[#1a73e8] dark:hover:border-[#8ab4f8] p-3.5 text-xs text-[#202124] dark:text-[#e3e3e3] shadow-sm transition hover:scale-[1.02] active:scale-95 text-left">' +
            '      <p class="font-bold flex items-center gap-1.5"><i data-lucide="database" class="h-3.5 w-3.5 text-[#f9ab00] dark:text-[#fdd663]"></i> Memoria Viva</p>' +
            '      <p class="text-[11px] text-[#5f6368] dark:text-[#c4c7c5] mt-1">¿Cómo funciona tu memoria activa?</p>' +
            '    </button>' +
            '    <button onclick="usarSugerencia(\'Proponme una idea o desafío para resolver juntos hoy.\')" class="rounded-2xl border border-black/10 dark:border-white/10 bg-white dark:bg-[#1e1f20] hover:border-[#1a73e8] dark:hover:border-[#8ab4f8] p-3.5 text-xs text-[#202124] dark:text-[#e3e3e3] shadow-sm transition hover:scale-[1.02] active:scale-95 text-left">' +
            '      <p class="font-bold flex items-center gap-1.5"><i data-lucide="lightbulb" class="h-3.5 w-3.5 text-[#d93025] dark:text-[#f28b82]"></i> Pregunta Creativa</p>' +
            '      <p class="text-[11px] text-[#5f6368] dark:text-[#c4c7c5] mt-1">Proponme un desafío para empezar.</p>' +
            '    </button>' +
            '  </div>' +
            '</div>';
          if (window.lucide) lucide.createIcons();
          return;
        }

        mensajes.forEach(function (m) {
          renderizarMensaje(m.rol, m.mensaje, m.fecha, m.hora);
        });

        desplazarAlFinal();
      })
      .catch(function () {
        contenedorMensajes.innerHTML =
          '<div class="flex h-full items-center justify-center text-xs text-[#d93025] dark:text-[#f28b82]">Error al cargar la conversación.</div>';
      });
  }

  function renderizarMensaje(rol, texto, fecha, hora) {
    var esUsuario = rol === "user";
    var fila = document.createElement("div");
    fila.className = "flex " + (esUsuario ? "justify-end" : "justify-start") + " animate-fade-in";

    var caja = document.createElement("div");
    caja.className = "max-w-[90%] sm:max-w-[80%] lg:max-w-[70%]";

    var burbuja = document.createElement("div");
    if (esUsuario) {
      burbuja.className = "rounded-3xl rounded-br-sm bg-[#1a73e8] px-5 py-3.5 text-sm text-white shadow-md";
      burbuja.textContent = texto;
    } else {
      burbuja.className = "rounded-3xl rounded-bl-sm border border-black/10 dark:border-white/10 bg-white dark:bg-[#1e1f20] px-5 py-4 text-sm leading-relaxed text-[#202124] dark:text-[#e3e3e3] shadow-sm prose-chat";
      if (window.marked && window.DOMPurify) {
        burbuja.innerHTML = DOMPurify.sanitize(marked.parse(texto, { breaks: true, gfm: true }));
      } else {
        burbuja.textContent = texto;
      }
    }

    var pie = document.createElement("div");
    pie.className = "mt-1.5 flex items-center justify-between text-[10px] text-[#5f6368] dark:text-[#c4c7c5] px-1";
    
    if (esUsuario) {
      pie.innerHTML = '<span class="ml-auto">Tú ' + (hora ? '· ' + hora : '') + '</span>';
    } else {
      var safeText = encodeURIComponent(texto);
      pie.innerHTML =
        '<span>' + nombreAgente + (hora ? ' · ' + hora : '') + '</span>' +
        '<button onclick="copiarTexto(decodeURIComponent(\'' + safeText + '\'), this)" class="inline-flex items-center gap-1 text-[11px] text-[#5f6368] dark:text-[#c4c7c5] hover:text-[#1a73e8] dark:hover:text-[#8ab4f8] transition">' +
        '  <i data-lucide="copy" class="h-3 w-3"></i>' +
        '  <span>Copiar</span>' +
        '</button>';
    }

    caja.appendChild(burbuja);
    caja.appendChild(pie);
    fila.appendChild(caja);
    contenedorMensajes.appendChild(fila);

    if (window.lucide) lucide.createIcons();
  }

  function renderizarBurbujaCargando() {
    var fila = document.createElement("div");
    fila.id = "burbuja-cargando";
    fila.className = "flex justify-start animate-fade-in";
    fila.innerHTML =
      '<div class="flex items-center gap-2 rounded-3xl rounded-bl-sm border border-black/10 dark:border-white/10 bg-white dark:bg-[#1e1f20] px-5 py-3.5 shadow-sm text-xs text-[#5f6368] dark:text-[#c4c7c5]">' +
      '  <div class="flex items-center gap-1">' +
      '    <span class="h-2 w-2 animate-bounce rounded-full bg-[#4285F4]"></span>' +
      '    <span class="h-2 w-2 animate-bounce rounded-full bg-[#EA4335] [animation-delay:0.15s]"></span>' +
      '    <span class="h-2 w-2 animate-bounce rounded-full bg-[#FBBC04] [animation-delay:0.3s]"></span>' +
      '    <span class="h-2 w-2 animate-bounce rounded-full bg-[#34A853] [animation-delay:0.45s]"></span>' +
      '  </div>' +
      '  <span>Pensando con DeepSeek…</span>' +
      '</div>';
    contenedorMensajes.appendChild(fila);
    desplazarAlFinal();
  }

  function quitarBurbujaCargando() {
    var el = document.getElementById("burbuja-cargando");
    if (el) el.remove();
  }

  function desplazarAlFinal() {
    contenedorMensajes.scrollTop = contenedorMensajes.scrollHeight;
  }

  // ------------------------------------------------------------------
  // Enviar Mensaje y Auto-Crecimiento de Textarea
  // ------------------------------------------------------------------
  campoMensaje.addEventListener("input", function () {
    this.style.height = "auto";
    this.style.height = Math.min(this.scrollHeight, 180) + "px";
  });

  campoMensaje.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      formMensaje.requestSubmit();
    }
  });

  formMensaje.addEventListener("submit", function (e) {
    e.preventDefault();
    var texto = campoMensaje.value.trim();
    if (!texto || botonEnviar.disabled) return;

    if (!sesionActivaId) {
      mostrarToast("No hay una conversación activa.");
      return;
    }

    // Limpiar pantalla de bienvenida
    var bienvenida = contenedorMensajes.querySelector("h3");
    if (bienvenida && bienvenida.textContent.indexOf("¡Hola!") !== -1) {
      contenedorMensajes.innerHTML = "";
    }

    var ahora = new Date();
    var hora = ahora.getHours().toString().padStart(2, "0") + ":" + ahora.getMinutes().toString().padStart(2, "0");
    renderizarMensaje("user", texto, null, hora);
    desplazarAlFinal();

    campoMensaje.value = "";
    campoMensaje.style.height = "auto";
    botonEnviar.disabled = true;
    renderizarBurbujaCargando();

    fetch("/api/sesion/" + sesionActivaId + "/mensaje", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mensaje: texto }),
    })
      .then(function (r) {
        return r.json().then(function (d) { return { ok: r.ok, datos: d }; });
      })
      .then(function (res) {
        quitarBurbujaCargando();
        if (!res.ok) throw new Error(res.datos.error || "Error al comunicarse con DeepSeek.");

        renderizarMensaje("assistant", res.datos.respuesta, null, hora);
        desplazarAlFinal();

        if (res.datos.memoria_guardada) {
          mostrarToast("Hecho relevante aprendido en memoria viva.", "exito");
        }

        actualizarListaSesionesSidebar();
      })
      .catch(function (error) {
        quitarBurbujaCargando();
        mostrarToast(error.message);
      })
      .finally(function () {
        botonEnviar.disabled = false;
        setTimeout(function () { campoMensaje.focus(); }, 50);
      });
  });

  // ------------------------------------------------------------------
  // Gestión de Sesiones (Hilos)
  // ------------------------------------------------------------------
  window.crearNuevaConversacion = function () {
    fetch("/api/agente/" + encodeURIComponent(nombreAgente) + "/sesiones", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    })
      .then(function (r) { return r.json(); })
      .then(function (ses) {
        sesionActivaId = ses.id;
        document.body.dataset.sesionId = ses.id;
        cargarMensajesSesion(ses.id);
        actualizarListaSesionesSidebar();
        mostrarToast("Nueva conversación iniciada.", "exito");
        setTimeout(function () { campoMensaje.focus(); }, 50);
      })
      .catch(function () {
        mostrarToast("No se pudo iniciar una nueva conversación.");
      });
  };

  window.cambiarSesionActiva = function (sesionId) {
    if (sesionId === sesionActivaId) return;
    sesionActivaId = sesionId;
    document.body.dataset.sesionId = sesionId;
    cargarMensajesSesion(sesionId);
    actualizarListaSesionesSidebar();
  };

  function actualizarListaSesionesSidebar() {
    fetch("/api/agente/" + encodeURIComponent(nombreAgente) + "/sesiones")
      .then(function (r) { return r.json(); })
      .then(function (datos) {
        var sesiones = datos.sesiones || [];
        listaSesionesSidebar.innerHTML = "";

        sesiones.forEach(function (s) {
          var esActiva = s.id === sesionActivaId;
          var div = document.createElement("div");
          div.setAttribute("data-sesion-item", s.id);
          div.setAttribute("data-sesion-titulo", s.titulo);
          div.className =
            "group relative flex items-center justify-between rounded-xl border p-2.5 transition " +
            (esActiva
              ? "border-[#1a73e8] bg-[#1a73e8]/10 font-bold text-[#1a73e8] dark:text-[#8ab4f8]"
              : "border-transparent hover:bg-black/5 dark:hover:bg-white/5 text-[#202124] dark:text-[#e3e3e3]");

          var safeTitle = (s.titulo || "").replace(/'/g, "\\'");
          div.innerHTML =
            '<button onclick="cambiarSesionActiva(' + s.id + ')" class="min-w-0 flex-1 text-left">' +
            '  <p class="truncate text-xs" title="' + safeTitle + '">' + s.titulo + '</p>' +
            '  <p class="mt-0.5 text-[10px] text-[#5f6368] dark:text-[#c4c7c5] font-normal">' + s.total_mensajes + ' msgs · ' + (s.actualizado_en ? s.actualizado_en.slice(0, 10) : "") + '</p>' +
            '</button>' +
            '<div class="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition">' +
            '  <button onclick="abrirModalRenombrarSesion(' + s.id + ', \'' + safeTitle + '\')" title="Renombrar" class="rounded-lg p-1 text-[#5f6368] dark:text-[#c4c7c5] hover:bg-black/10 dark:hover:bg-white/10 hover:text-black dark:hover:text-white"><i data-lucide="pencil" class="h-3 w-3"></i></button>' +
            '  <button onclick="confirmarEliminarSesion(' + s.id + ')" title="Eliminar" class="rounded-lg p-1 text-[#5f6368] dark:text-[#c4c7c5] hover:bg-[#EA4335]/20 hover:text-[#d93025] dark:hover:text-[#f28b82]"><i data-lucide="trash-2" class="h-3 w-3"></i></button>' +
            '</div>';

          listaSesionesSidebar.appendChild(div);
        });

        if (window.lucide) lucide.createIcons();
      });
  }

  window.abrirModalRenombrarSesion = function (sesionId, tituloActual) {
    campoRenombrarId.value = sesionId;
    campoRenombrarTitulo.value = tituloActual || "";
    modalRenombrar.classList.remove("hidden");
    modalRenombrar.classList.add("flex");
    setTimeout(function () { campoRenombrarTitulo.focus(); }, 50);
  };

  window.cerrarModalRenombrarSesion = function () {
    modalRenombrar.classList.add("hidden");
    modalRenombrar.classList.remove("flex");
  };

  window.guardarRenombrarSesion = function () {
    var id = campoRenombrarId.value;
    var nuevoTitulo = campoRenombrarTitulo.value.trim();
    if (!nuevoTitulo) {
      mostrarToast("El título no puede estar vacío.");
      return;
    }

    fetch("/api/sesion/" + id, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ titulo: nuevoTitulo }),
    })
      .then(function (r) { return r.json(); })
      .then(function () {
        cerrarModalRenombrarSesion();
        mostrarToast("Conversación renombrada.", "exito");
        actualizarListaSesionesSidebar();
      })
      .catch(function () {
        mostrarToast("Error al renombrar la conversación.");
      });
  };

  window.confirmarEliminarSesion = function (sesionId) {
    if (!confirm("¿Deseas eliminar este hilo de conversación y sus mensajes?")) return;

    fetch("/api/sesion/" + sesionId, { method: "DELETE" })
      .then(function (r) { return r.json(); })
      .then(function () {
        mostrarToast("Conversación eliminada.", "exito");
        if (sesionId === sesionActivaId) {
          fetch("/api/agente/" + encodeURIComponent(nombreAgente) + "/sesiones")
            .then(function (res) { return res.json(); })
            .then(function (d) {
              if (d.sesiones && d.sesiones.length) {
                cambiarSesionActiva(d.sesiones[0].id);
              } else {
                crearNuevaConversacion();
              }
            });
        } else {
          actualizarListaSesionesSidebar();
        }
      })
      .catch(function () {
        mostrarToast("Error al eliminar la conversación.");
      });
  };

  // ------------------------------------------------------------------
  // Modal de Gestión Integral del Agente
  // ------------------------------------------------------------------
  window.abrirModalGestionAgente = function () {
    modalGestionAgente.classList.remove("hidden");
    modalGestionAgente.classList.add("flex");
  };

  window.cerrarModalGestionAgente = function () {
    modalGestionAgente.classList.add("hidden");
    modalGestionAgente.classList.remove("flex");
  };

  window.cambiarTabModalGestion = function (tab) {
    var tabs = ["perfil", "fuentes", "rol", "memoria"];
    tabs.forEach(function (t) {
      var seccion = document.getElementById("tab-gestion-" + t);
      var btn = document.getElementById("btn-tab-modal-" + t);
      if (seccion) seccion.classList.toggle("hidden", t !== tab);
      if (btn) {
        if (t === tab) {
          btn.className = "px-3 py-1.5 rounded-xl font-bold bg-black/10 dark:bg-white/15 text-[#202124] dark:text-white";
        } else {
          btn.className = "px-3 py-1.5 rounded-xl font-semibold text-[#5f6368] dark:text-[#c4c7c5] hover:text-black dark:hover:text-white";
        }
      }
    });
  };

  selectIdentidad.addEventListener("change", function () {
    bloqueCustom.classList.toggle("hidden", selectIdentidad.value !== "personalizada");
  });

  // ------------------------------------------------------------------
  // Manejo de Avatar e Imágenes en Chat
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

  formGestionAgente.addEventListener("submit", function (e) {
    e.preventDefault();
    var perfil = document.getElementById("editar-perfil").value.trim();
    var custom = document.getElementById("editar-identidad-custom").value.trim();
    var clave = selectIdentidad.value;
    var avatarUrl = document.getElementById("chat-campo-avatar-url") ? document.getElementById("chat-campo-avatar-url").value.trim() : "";

    var seleccionadas = [];
    document.querySelectorAll("input[name=editar_fuentes]:checked").forEach(function (cb) {
      seleccionadas.push(parseInt(cb.value, 10));
    });

    var payload = { perfil: perfil, avatar_url: avatarUrl, fuentes: seleccionadas };
    if (clave === "personalizada") payload.identidad_custom = custom;
    else payload.identidad = clave;

    fetch("/api/agente/" + encodeURIComponent(nombreAgente) + "/editar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(function (r) { return r.json(); })
      .then(function () {
        cerrarModalGestionAgente();
        mostrarToast("Agente actualizado correctamente.", "exito");
        setTimeout(function () { window.location.reload(); }, 500);
      })
      .catch(function () {
        mostrarToast("Error al actualizar el agente.");
      });
  });

  window.abrirModalLimpiarMemoria = function () {
    modalLimpiarMemoria.classList.remove("hidden");
    modalLimpiarMemoria.classList.add("flex");
  };

  window.cerrarModalLimpiarMemoria = function () {
    modalLimpiarMemoria.classList.add("hidden");
    modalLimpiarMemoria.classList.remove("flex");
  };

  window.ejecutarLimpiarMemoria = function () {
    fetch("/api/agente/" + encodeURIComponent(nombreAgente) + "/limpiar", { method: "POST" })
      .then(function (r) { return r.json(); })
      .then(function () {
        cerrarModalLimpiarMemoria();
        if (modalGestionAgente) cerrarModalGestionAgente();
        mostrarToast("Memoria viva del agente limpiada.", "exito");
        setTimeout(function () { window.location.reload(); }, 500);
      });
  };

  // Carga inicial
  if (sesionActivaId) {
    cargarMensajesSesion(sesionActivaId);
  } else {
    crearNuevaConversacion();
  }

  // Tecla Escape para modales
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      cerrarModalGestionAgente();
      cerrarModalLimpiarMemoria();
      cerrarModalRenombrarSesion();
    }
  });
})();