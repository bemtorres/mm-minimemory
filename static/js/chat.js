// Lógica de la página de chat: conversación, pestañas y configuración.
(function () {
  "use strict";

  var nombreAgente = document.body.dataset.agente;
  var contenedor = document.getElementById("mensajes");
  var form = document.getElementById("form-mensaje");
  var campo = document.getElementById("campo-mensaje");
  var boton = document.getElementById("boton-enviar");
  var indicadorMemoria = document.getElementById("indicador-memoria");
  var toast = document.getElementById("toast");
  var contenidoToast = document.getElementById("toast-contenido");
  var iconoToast = document.getElementById("toast-icono");
  var textoToast = document.getElementById("texto-toast");
  var mensajeEnProceso = false;

  // ------------------------------------------------------------------
  // Utilidades
  // ------------------------------------------------------------------

  function escapar(texto) {
    var div = document.createElement("div");
    div.textContent = texto;
    return div.innerHTML;
  }

  function marcar(texto) {
    if (window.marked && window.DOMPurify) {
      var html = marked.parse(texto, { breaks: true, gfm: true });
      return DOMPurify.sanitize(html);
    }
    return escapar(texto).replace(/\n/g, "<br>");
  }

  function mostrarToast(mensaje, tipo) {
    var esExito = tipo === "exito";
    textoToast.textContent = mensaje;
    contenidoToast.className =
      "flex items-center gap-2.5 rounded-2xl px-5 py-3 text-sm font-semibold text-white shadow-2xl " +
      (esExito ? "bg-emerald-600" : "bg-rose-600");
    iconoToast.setAttribute("data-lucide", esExito ? "check-circle-2" : "triangle-alert");
    toast.classList.remove("hidden");
    clearTimeout(toast._temporizador);
    toast._temporizador = setTimeout(function () {
      toast.classList.add("hidden");
    }, 4500);
    if (window.lucide) lucide.createIcons();
  }

  function desplazarAlFinal() {
    contenedor.scrollTop = contenedor.scrollHeight;
  }

  // ------------------------------------------------------------------
  // Burbujas de mensaje
  // ------------------------------------------------------------------

  function crearBurbuja(rol, contenido, esNuevo) {
    var envoltura = document.createElement("div");
    envoltura.className =
      "mensaje-burbuja flex " + (rol === "user" ? "justify-end" : "justify-start");

    if (rol === "user") {
      var burbujaUsuario = document.createElement("div");
      burbujaUsuario.className =
        "max-w-[78%] rounded-3xl rounded-br-lg bg-gradient-to-r from-brand-600 to-fuchsia-600 px-5 py-3 text-sm leading-relaxed text-white shadow-lg shadow-brand-600/20";
      burbujaUsuario.textContent = contenido;
      envoltura.appendChild(burbujaUsuario);
    } else {
      var burbujaAgente = document.createElement("div");
      burbujaAgente.className =
        "prose-chat max-w-[82%] rounded-3xl rounded-bl-lg border border-slate-200/80 bg-white px-5 py-3.5 text-sm text-slate-700 shadow-[0_6px_20px_rgb(124,58,237,0.07)]";
      burbujaAgente.innerHTML = marcar(contenido);
      envoltura.appendChild(burbujaAgente);
    }

    if (esNuevo) contenedor.appendChild(envoltura);
    else contenedor.insertBefore(envoltura, contenedor.firstChild);
    return envoltura;
  }

  function crearIndicadorEscritura() {
    var envoltura = document.createElement("div");
    envoltura.id = "escribiendo";
    envoltura.className = "mensaje-burbuja flex justify-start";
    var caja = document.createElement("div");
    caja.className =
      "flex items-center gap-1.5 rounded-3xl rounded-bl-lg border border-slate-200/80 bg-white px-5 py-4 shadow-[0_6px_20px_rgb(124,58,237,0.07)]";
    for (var i = 0; i < 3; i++) {
      var punto = document.createElement("span");
      punto.className = "punto-escritura h-2 w-2 rounded-full bg-brand-400";
      caja.appendChild(punto);
    }
    envoltura.appendChild(caja);
    contenedor.appendChild(envoltura);
    desplazarAlFinal();
  }

  function quitarIndicadorEscritura() {
    var indicador = document.getElementById("escribiendo");
    if (indicador) indicador.remove();
  }

  // ------------------------------------------------------------------
  // Conversación
  // ------------------------------------------------------------------

  function cargarHistorial() {
    fetch("/api/agente/" + encodeURIComponent(nombreAgente) + "/historial")
      .then(function (respuesta) {
        return respuesta.json();
      })
      .then(function (datos) {
        var mensajes = (datos.mensajes || []).filter(function (m) {
          return m.mensaje;
        });
        if (!mensajes.length) {
          mostrarMensajeBienvenida();
          return;
        }
        mensajes.forEach(function (m) {
          crearBurbuja(m.rol, m.mensaje, true);
        });
        desplazarAlFinal();
      })
      .catch(function () {
        mostrarMensajeBienvenida();
      });
  }

  function mostrarMensajeBienvenida() {
    contenedor.innerHTML = "";
    var envoltura = document.createElement("div");
    envoltura.className = "flex h-full flex-col items-center justify-center text-center";
    envoltura.innerHTML =
      '<div class="flex h-16 w-16 items-center justify-center rounded-3xl bg-gradient-to-br from-brand-500 to-fuchsia-500 text-white shadow-xl shadow-brand-500/25">' +
      '  <i data-lucide="message-circle" class="h-8 w-8"></i>' +
      "</div>" +
      '<h2 class="mt-5 text-xl font-bold text-slate-900">Hola, soy ' +
      escapar(document.querySelector("header h1").textContent) +
      "</h2>" +
      '<p class="mt-2 max-w-md text-sm text-slate-500">Escribe tu primer mensaje y empezaremos a conversar. ' +
      "Tengo mi propia identidad, conocimientos y memoria.</p>";
    contenedor.appendChild(envoltura);
    if (window.lucide) lucide.createIcons();
  }

  function enviarMensaje() {
    var texto = campo.value.trim();
    if (!texto || mensajeEnProceso) return;

    mensajeEnProceso = true;
    boton.disabled = true;
    campo.value = "";
    campo.style.height = "auto";

    if (!contenedor.querySelector(".mensaje-burbuja")) {
      contenedor.innerHTML = "";
    }
    crearBurbuja("user", texto, true);
    crearIndicadorEscritura();
    desplazarAlFinal();

    fetch("/api/agente/" + encodeURIComponent(nombreAgente) + "/mensaje", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mensaje: texto }),
    })
      .then(function (respuesta) {
        return respuesta.json().then(function (datos) {
          return { ok: respuesta.ok, datos: datos };
        });
      })
      .then(function (resultado) {
        quitarIndicadorEscritura();
        if (!resultado.ok) {
          throw new Error(resultado.datos.error || "No se pudo obtener respuesta.");
        }
        crearBurbuja("assistant", resultado.datos.respuesta, true);
        if (resultado.datos.memoria_guardada) {
          mostrarNotaMemoria();
        }
        desplazarAlFinal();
      })
      .catch(function (motivo) {
        quitarIndicadorEscritura();
        mostrarToast(motivo.message);
      })
      .finally(function () {
        mensajeEnProceso = false;
        boton.disabled = false;
        campo.focus();
      });
  }

  function mostrarNotaMemoria() {
    indicadorMemoria.classList.remove("hidden");
    indicadorMemoria.classList.add("inline-flex");
    clearTimeout(indicadorMemoria._temporizador);
    indicadorMemoria._temporizador = setTimeout(function () {
      indicadorMemoria.classList.add("hidden");
      indicadorMemoria.classList.remove("inline-flex");
    }, 3000);
  }

  // ------------------------------------------------------------------
  // Pestañas del panel lateral
  // ------------------------------------------------------------------

  window.cambiarPestana = function (clave) {
    document.querySelectorAll("[data-pestana-contenido]").forEach(function (el) {
      el.classList.toggle("hidden", el.dataset.pestanaContenido !== clave);
      el.classList.toggle("pestana-activa", el.dataset.pestanaContenido === clave);
    });
    document.querySelectorAll("[data-pestana-boton]").forEach(function (el) {
      var activo = el.dataset.pestanaBoton === clave;
      el.classList.toggle("bg-white/15", activo);
      el.classList.toggle("text-white", activo);
      el.classList.toggle("text-brand-300", !activo);
      el.classList.toggle("hover:text-white", !activo);
    });
    if (window.lucide) lucide.createIcons();
  };

  // ------------------------------------------------------------------
  // Edición del usuario (modal)
  // ------------------------------------------------------------------

  var modalEditar = document.getElementById("modal-editar");
  var formEditar = document.getElementById("form-editar");
  var editarPerfil = document.getElementById("editar-perfil");
  var editarSelect = document.getElementById("editar-select-identidad");
  var editarBloqueCustom = document.getElementById("editar-bloque-personalizada");
  var editarCustom = document.getElementById("editar-identidad-custom");
  var editarFuentes = document.getElementById("editar-fuentes");
  var nuevaFuenteNombre = document.getElementById("nueva-fuente-nombre");
  var nuevaFuenteContenido = document.getElementById("nueva-fuente-contenido");
  var botonGuardarEditar = document.getElementById("boton-guardar-editar");

  function crearFilaFuente(fuente, seleccionada) {
    var etiqueta = document.createElement("label");
    etiqueta.className = "flex items-start gap-2.5 rounded-lg bg-white px-3 py-2 shadow-sm";

    var checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = fuente.id;
    checkbox.className = "mt-0.5 h-4 w-4 shrink-0 accent-brand-600";
    checkbox.checked = seleccionada;

    var texto = document.createElement("div");
    texto.className = "min-w-0 flex-1";
    var nombre = document.createElement("p");
    nombre.className = "text-sm font-semibold text-slate-800";
    nombre.textContent = fuente.nombre;
    var contenido = document.createElement("p");
    contenido.className = "truncate text-xs text-slate-500";
    contenido.textContent = fuente.contenido || "(sin contenido)";
    texto.appendChild(nombre);
    texto.appendChild(contenido);

    var botonBorrar = document.createElement("button");
    botonBorrar.type = "button";
    botonBorrar.title = "Eliminar fuente";
    botonBorrar.className =
      "shrink-0 rounded-full p-1.5 text-slate-400 transition hover:bg-rose-50 hover:text-rose-600";
    botonBorrar.innerHTML = '<i data-lucide="trash-2" class="h-3.5 w-3.5"></i>';
    botonBorrar.addEventListener("click", function (evento) {
      evento.preventDefault();
      eliminarFuente(fuente.id);
    });

    etiqueta.appendChild(checkbox);
    etiqueta.appendChild(texto);
    etiqueta.appendChild(botonBorrar);
    return etiqueta;
  }

  function renderizarCheckboxesFuentes(fuentes, seleccionadas) {
    editarFuentes.innerHTML = "";
    var lista = fuentes || [];
    if (!lista.length) {
      editarFuentes.innerHTML =
        '<p class="text-xs text-slate-400">Todavía no hay fuentes. Agrega una debajo.</p>';
      return;
    }
    lista.forEach(function (fuente) {
      var activa = seleccionadas.indexOf(fuente.id) !== -1;
      editarFuentes.appendChild(crearFilaFuente(fuente, activa));
    });
    if (window.lucide) lucide.createIcons();
  }

  window.abrirModalEditar = function () {
    modalEditar.classList.remove("hidden");
    modalEditar.classList.add("flex");
    fetch("/api/agente/" + encodeURIComponent(nombreAgente))
      .then(function (respuesta) {
        return respuesta.json();
      })
      .then(function (datos) {
        editarPerfil.value = datos.perfil || "";
        var seleccionadas = (datos.fuentes || []).map(function (f) {
          return f.id;
        });
        renderizarCheckboxesFuentes(datos.todas_fuentes, seleccionadas);
        if (datos.identidad.personalizada) {
          editarSelect.value = "personalizada";
          editarCustom.value = datos.identidad.prompt || "";
          editarBloqueCustom.classList.remove("hidden");
        } else {
          editarSelect.value = datos.identidad.clave || "";
          editarCustom.value = "";
          editarBloqueCustom.classList.add("hidden");
        }
      })
      .catch(function () {
        cerrarModalEditar();
        mostrarToast("No se pudo cargar la información del agente.");
      });
  };

  window.cerrarModalEditar = function () {
    modalEditar.classList.add("hidden");
    modalEditar.classList.remove("flex");
  };

  window.agregarFuente = function () {
    var nombre = nuevaFuenteNombre.value.trim();
    var contenido = nuevaFuenteContenido.value.trim();
    if (!nombre) {
      mostrarToast("Escribe un nombre para la fuente.");
      nuevaFuenteNombre.focus();
      return;
    }
    fetch("/api/fuentes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nombre: nombre, contenido: contenido }),
    })
      .then(function (r) {
        return r.json();
      })
      .then(function (datos) {
        if (datos.error) throw new Error(datos.error);
        if (!editarFuentes.querySelector("input[type=checkbox]")) {
          editarFuentes.innerHTML = "";
        }
        editarFuentes.appendChild(crearFilaFuente(datos, true));
        nuevaFuenteNombre.value = "";
        nuevaFuenteContenido.value = "";
        if (window.lucide) lucide.createIcons();
        mostrarToast("Base de conocimiento agregada y asociada.", "exito");
      })
      .catch(function (motivo) {
        mostrarToast(motivo.message);
      });
  };

  function eliminarFuente(id) {
    fetch("/api/fuentes/" + id, { method: "DELETE" })
      .then(function (r) {
        return r.json();
      })
      .then(function (datos) {
        if (datos.error) throw new Error(datos.error);
        var fila = editarFuentes.querySelector('input[value="' + id + '"]');
        if (fila) fila.closest("label").remove();
        if (!editarFuentes.querySelector("input[type=checkbox]")) {
          editarFuentes.innerHTML =
            '<p class="text-xs text-slate-400">Todavía no hay bases de conocimiento creadas.</p>';
        }
        mostrarToast("Base de conocimiento eliminada.", "exito");
      })
      .catch(function (motivo) {
        mostrarToast(motivo.message);
      });
  }

  editarSelect.addEventListener("change", function () {
    var esPersonalizada = editarSelect.value === "personalizada";
    editarBloqueCustom.classList.toggle("hidden", !esPersonalizada);
    if (!esPersonalizada) editarCustom.value = "";
  });

  formEditar.addEventListener("submit", function (evento) {
    evento.preventDefault();
    botonGuardarEditar.disabled = true;

    var perfil = editarPerfil.value.trim();
    var custom = editarCustom.value.trim();
    var clave = editarSelect.value;

    var cuerpo = { perfil: perfil };
    var fuentesIds = Array.prototype.slice.call(
      editarFuentes.querySelectorAll("input[type=checkbox]:checked")
    ).map(function (casilla) {
      return parseInt(casilla.value, 10);
    });
    cuerpo.fuentes = fuentesIds;
    if (custom) {
      cuerpo.identidad_custom = custom;
    } else if (clave && clave !== "personalizada") {
      cuerpo.identidad = clave;
    } else {
      mostrarToast("Elige una identidad o escribe una personalizada.");
      botonGuardarEditar.disabled = false;
      return;
    }

    fetch("/api/agente/" + encodeURIComponent(nombreAgente) + "/editar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cuerpo),
    })
      .then(function (respuesta) {
        return respuesta.json().then(function (datos) {
          return { ok: respuesta.ok, datos: datos };
        });
      })
      .then(function (resultado) {
        if (!resultado.ok) {
          throw new Error(resultado.datos.error || "No se pudieron guardar los cambios.");
        }
        cerrarModalEditar();
        refrescarAgente(resultado.datos);
        mostrarToast("Cambios guardados correctamente.", "exito");
      })
      .catch(function (motivo) {
        mostrarToast(motivo.message);
      })
      .finally(function () {
        botonGuardarEditar.disabled = false;
      });
  });

  function refrescarAgente(datos) {
    if (!datos) return;
    var persona = datos.persona || "";
    var pSidebar = document.getElementById("persona-sidebar");
    var pHeader = document.getElementById("persona-header");
    if (pSidebar) pSidebar.textContent = persona;
    if (pHeader) pHeader.textContent = "Hablando con " + persona;

    var iniciales = datos.iniciales || "";
    var iniSidebar = document.getElementById("iniciales-sidebar");
    var iniHeader = document.getElementById("iniciales-header");
    if (iniSidebar) iniSidebar.textContent = iniciales;
    if (iniHeader) iniHeader.textContent = iniciales;

    var verPerfil = document.getElementById("ver-perfil");
    if (verPerfil) verPerfil.textContent = datos.perfil || "";

    var verFuentes = document.getElementById("ver-fuentes");
    if (verFuentes) {
      verFuentes.innerHTML = "";
      var lista = datos.fuentes || [];
      if (!lista.length) {
        var vacio = document.createElement("p");
        vacio.className = "rounded-xl bg-white/5 p-4 text-[13px] text-brand-200";
        vacio.textContent = "(Sin bases de conocimiento asociadas)";
        verFuentes.appendChild(vacio);
      } else {
        lista.forEach(function (fuente) {
          var tarjeta = document.createElement("div");
          tarjeta.className = "rounded-xl bg-white/5 p-3";
          var nombre = document.createElement("p");
          nombre.className = "text-xs font-bold text-white";
          nombre.textContent = fuente.nombre;
          var contenido = document.createElement("p");
          contenido.className =
            "mt-1 whitespace-pre-wrap break-words text-[12px] leading-relaxed text-brand-200";
          contenido.textContent = fuente.contenido || "";
          tarjeta.appendChild(nombre);
          tarjeta.appendChild(contenido);
          verFuentes.appendChild(tarjeta);
        });
      }
    }

    var verIdNombre = document.getElementById("ver-identidad-nombre");
    var verIdDesc = document.getElementById("ver-identidad-descripcion");
    if (verIdNombre) verIdNombre.textContent = datos.identidad.nombre;
    if (verIdDesc) verIdDesc.textContent = datos.identidad.descripcion;

    var badge = document.getElementById("identidad-badge-text");
    if (badge) badge.textContent = datos.identidad.nombre;

    var verPrompt = document.getElementById("ver-identidad-prompt");
    if (verPrompt) {
      if (datos.identidad.personalizada) {
        verPrompt.classList.remove("hidden");
        verPrompt.textContent = datos.identidad.prompt || "";
      } else {
        verPrompt.classList.add("hidden");
        verPrompt.textContent = "";
      }
    }

    if (window.lucide) lucide.createIcons();
  }

  // ------------------------------------------------------------------
  // Acciones del panel
  // ------------------------------------------------------------------

  window.abrirModalLimpiarMemoria = function () {
    var modal = document.getElementById("modal-limpiar-memoria");
    modal.classList.remove("hidden");
    modal.classList.add("flex");
  };

  window.cerrarModalLimpiarMemoria = function () {
    var modal = document.getElementById("modal-limpiar-memoria");
    modal.classList.add("hidden");
    modal.classList.remove("flex");
  };

  window.confirmarLimpiarMemoria = function () {
    cerrarModalLimpiarMemoria();
    fetch("/api/agente/" + encodeURIComponent(nombreAgente) + "/limpiar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    })
      .then(function (r) {
        return r.json();
      })
      .then(function (datos) {
        if (datos.error) throw new Error(datos.error);
        var preMemoria = document.querySelector('[data-pestana-contenido="memoria"] pre');
        if (preMemoria) preMemoria.textContent = "(La memoria está vacía)";
        mostrarToast("Memoria borrada.", "exito");
      })
      .catch(function (motivo) {
        mostrarToast(motivo.message);
      });
  };

  // ------------------------------------------------------------------
  // Eventos
  // ------------------------------------------------------------------

  form.addEventListener("submit", function (evento) {
    evento.preventDefault();
    enviarMensaje();
  });

  // Enter envía; Shift+Enter hace salto de línea. Ajuste de altura.
  campo.addEventListener("keydown", function (evento) {
    if (evento.key === "Enter" && !evento.shiftKey) {
      evento.preventDefault();
      enviarMensaje();
    }
  });

  // Cierra los modales con la tecla Escape.
  document.addEventListener("keydown", function (evento) {
    if (evento.key !== "Escape") return;
    cerrarModalLimpiarMemoria();
    cerrarModalEditar();
  });

  campo.addEventListener("input", function () {
    campo.style.height = "auto";
    campo.style.height = Math.min(campo.scrollHeight, 160) + "px";
  });

  // Inicio
  cargarHistorial();
  campo.focus();
})();