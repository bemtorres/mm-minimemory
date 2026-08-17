// Lógica de la página de inicio: gestión independiente de agentes y bases de conocimiento.
(function () {
  "use strict";

  // Elementos principales
  var seccionAgentes = document.getElementById("seccion-agentes");
  var seccionFuentes = document.getElementById("seccion-fuentes");
  var btnTabAgentes = document.getElementById("tab-btn-agentes");
  var btnTabFuentes = document.getElementById("tab-btn-fuentes");

  // Modal Crear Agente
  var modalCrear = document.getElementById("modal-crear");
  var formCrear = document.getElementById("form-crear");
  var campoNombre = document.getElementById("campo-nombre");
  var campoPerfil = document.getElementById("campo-perfil");
  var selectIdentidad = document.getElementById("campo-identidad");
  var bloquePersonalizada = document.getElementById("bloque-personalizada");
  var campoCustom = document.getElementById("campo-identidad-custom");
  var botonCrear = document.getElementById("boton-crear");
  var listaFuentesCrear = document.getElementById("lista-fuentes-crear");

  // Modal Crear / Editar Base de Conocimiento
  var modalFuente = document.getElementById("modal-fuente");
  var formFuente = document.getElementById("form-fuente");
  var tituloModalFuente = document.getElementById("titulo-modal-fuente");
  var campoFuenteId = document.getElementById("campo-fuente-id");
  var campoFuenteNombre = document.getElementById("campo-fuente-nombre");
  var campoFuenteContenido = document.getElementById("campo-fuente-contenido");
  var botonGuardarFuente = document.getElementById("boton-guardar-fuente");

  // Modal Eliminar Base de Conocimiento
  var modalEliminarFuente = document.getElementById("modal-eliminar-fuente");
  var nombreEliminarFuente = document.getElementById("nombre-eliminar-fuente");
  var botonConfirmarEliminarFuente = document.getElementById("boton-confirmar-eliminar-fuente");
  var fuenteAEliminarId = null;

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
      (esExito ? "bg-emerald-600" : "bg-rose-600");
    iconoToast.setAttribute("data-lucide", esExito ? "check-circle-2" : "triangle-alert");
    toast.classList.remove("hidden");
    clearTimeout(toast._temporizador);
    toast._temporizador = setTimeout(function () {
      toast.classList.add("hidden");
    }, 4500);
    if (window.lucide) lucide.createIcons();
  }

  // ------------------------------------------------------------------
  // Cambio de pestañas principales (Agentes / Bases de Conocimiento)
  // ------------------------------------------------------------------
  window.cambiarTabPrincipal = function (tab) {
    if (tab === "agentes") {
      seccionAgentes.classList.remove("hidden");
      seccionFuentes.classList.add("hidden");
      btnTabAgentes.className =
        "inline-flex items-center gap-2 rounded-xl bg-white px-5 py-2 text-sm font-bold text-slate-900 shadow-sm transition";
      btnTabAgentes.querySelector("i").className = "h-4 w-4 text-brand-600";
      btnTabFuentes.className =
        "inline-flex items-center gap-2 rounded-xl px-5 py-2 text-sm font-semibold text-slate-600 transition hover:text-slate-900";
      btnTabFuentes.querySelector("i").className = "h-4 w-4 text-slate-400";
    } else {
      seccionAgentes.classList.add("hidden");
      seccionFuentes.classList.remove("hidden");
      btnTabFuentes.className =
        "inline-flex items-center gap-2 rounded-xl bg-white px-5 py-2 text-sm font-bold text-slate-900 shadow-sm transition";
      btnTabFuentes.querySelector("i").className = "h-4 w-4 text-brand-600";
      btnTabAgentes.className =
        "inline-flex items-center gap-2 rounded-xl px-5 py-2 text-sm font-semibold text-slate-600 transition hover:text-slate-900";
      btnTabAgentes.querySelector("i").className = "h-4 w-4 text-slate-400";
    }
    if (window.lucide) lucide.createIcons();
  };

  // ------------------------------------------------------------------
  // Gestión de Agentes
  // ------------------------------------------------------------------
  window.abrirModalCrear = function () {
    recargarListaFuentesEnModalCrear();
    modalCrear.classList.remove("hidden");
    modalCrear.classList.add("flex");
    setTimeout(function () {
      campoNombre.focus();
    }, 50);
  };

  window.cerrarModalCrear = function () {
    modalCrear.classList.add("hidden");
    modalCrear.classList.remove("flex");
  };

  selectIdentidad.addEventListener("change", function () {
    var esPersonalizada = selectIdentidad.value === "personalizada";
    bloquePersonalizada.classList.toggle("hidden", !esPersonalizada);
  });

  formCrear.addEventListener("submit", function (evento) {
    evento.preventDefault();
    botonCrear.disabled = true;

    var seleccionadas = [];
    formCrear.querySelectorAll("input[name='fuentes_seleccionadas']:checked").forEach(function (cb) {
      seleccionadas.push(parseInt(cb.value, 10));
    });

    var cuerpo = {
      nombre: campoNombre.value.trim(),
      perfil: campoPerfil.value.trim(),
      fuentes_ids: seleccionadas,
    };

    if (selectIdentidad.value === "personalizada") {
      cuerpo.identidad_custom = campoCustom.value.trim();
    } else if (selectIdentidad.value) {
      cuerpo.identidad = selectIdentidad.value;
    }

    fetch("/api/agentes", {
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
          throw new Error(resultado.datos.error || "No se pudo crear el agente.");
        }
        window.location.href = "/agente/" + encodeURIComponent(resultado.datos.nombre);
      })
      .catch(function (motivo) {
        mostrarToast(motivo.message);
      })
      .finally(function () {
        botonCrear.disabled = false;
      });
  });

  function recargarListaFuentesEnModalCrear() {
    fetch("/api/fuentes")
      .then(function (res) {
        return res.json();
      })
      .then(function (datos) {
        var fuentes = datos.fuentes || [];
        listaFuentesCrear.innerHTML = "";
        if (!fuentes.length) {
          listaFuentesCrear.innerHTML =
            '<p class="py-2 text-center text-xs text-slate-400">No hay bases de conocimiento creadas aún.</p>';
          return;
        }
        fuentes.forEach(function (f) {
          var label = document.createElement("label");
          label.className =
            "flex cursor-pointer items-start gap-2.5 rounded-lg bg-white p-2.5 shadow-sm transition hover:bg-violet-50/50";
          label.innerHTML =
            '<input type="checkbox" name="fuentes_seleccionadas" value="' +
            f.id +
            '" class="mt-0.5 h-4 w-4 shrink-0 rounded accent-brand-600">' +
            '<div class="min-w-0 flex-1">' +
            '  <p class="text-xs font-bold text-slate-800">' +
            f.nombre +
            "</p>" +
            '  <p class="truncate text-[11px] text-slate-400">' +
            (f.contenido || "(Sin contenido)") +
            "</p>" +
            "</div>";
          listaFuentesCrear.appendChild(label);
        });
        if (window.lucide) lucide.createIcons();
      })
      .catch(function () {});
  }

  // ------------------------------------------------------------------
  // Gestión de Bases de Conocimiento (Crear / Editar / Eliminar)
  // ------------------------------------------------------------------
  window.abrirModalCrearFuente = function () {
    campoFuenteId.value = "";
    campoFuenteNombre.value = "";
    campoFuenteContenido.value = "";
    tituloModalFuente.textContent = "Nueva Base de Conocimiento";
    modalFuente.classList.remove("hidden");
    modalFuente.classList.add("flex");
    setTimeout(function () {
      campoFuenteNombre.focus();
    }, 50);
  };

  window.abrirModalEditarFuente = function (id) {
    fetch("/api/fuentes/" + id)
      .then(function (res) {
        return res.json();
      })
      .then(function (datos) {
        campoFuenteId.value = datos.id;
        campoFuenteNombre.value = datos.nombre;
        campoFuenteContenido.value = datos.contenido || "";
        tituloModalFuente.textContent = "Editar Base de Conocimiento";
        modalFuente.classList.remove("hidden");
        modalFuente.classList.add("flex");
        setTimeout(function () {
          campoFuenteNombre.focus();
        }, 50);
      })
      .catch(function (error) {
        mostrarToast("No se pudo cargar la base de conocimiento.");
      });
  };

  window.cerrarModalFuente = function () {
    modalFuente.classList.add("hidden");
    modalFuente.classList.remove("flex");
  };

  formFuente.addEventListener("submit", function (evento) {
    evento.preventDefault();
    botonGuardarFuente.disabled = true;

    var id = campoFuenteId.value;
    var nombre = campoFuenteNombre.value.trim();
    var contenido = campoFuenteContenido.value.trim();

    if (!nombre) {
      mostrarToast("Escribe un nombre para la base de conocimiento.");
      botonGuardarFuente.disabled = false;
      return;
    }

    var url = id ? "/api/fuentes/" + id : "/api/fuentes";
    var metodo = id ? "POST" : "POST";

    fetch(url, {
      method: metodo,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nombre: nombre, contenido: contenido }),
    })
      .then(function (respuesta) {
        return respuesta.json().then(function (datos) {
          return { ok: respuesta.ok, datos: datos };
        });
      })
      .then(function (resultado) {
        if (!resultado.ok) {
          throw new Error(resultado.datos.error || "No se pudo guardar la base de conocimiento.");
        }
        cerrarModalFuente();
        mostrarToast("Base de conocimiento guardada correctamente.", "exito");
        setTimeout(function () {
          window.location.reload();
        }, 600);
      })
      .catch(function (motivo) {
        mostrarToast(motivo.message);
      })
      .finally(function () {
        botonGuardarFuente.disabled = false;
      });
  });

  window.confirmarEliminarFuente = function (id, nombre) {
    fuenteAEliminarId = id;
    nombreEliminarFuente.textContent = nombre;
    modalEliminarFuente.classList.remove("hidden");
    modalEliminarFuente.classList.add("flex");
  };

  window.cerrarModalEliminarFuente = function () {
    modalEliminarFuente.classList.add("hidden");
    modalEliminarFuente.classList.remove("flex");
    fuenteAEliminarId = null;
  };

  botonConfirmarEliminarFuente.addEventListener("click", function () {
    if (!fuenteAEliminarId) return;
    botonConfirmarEliminarFuente.disabled = true;

    fetch("/api/fuentes/" + fuenteAEliminarId, {
      method: "DELETE",
    })
      .then(function (res) {
        return res.json();
      })
      .then(function () {
        cerrarModalEliminarFuente();
        mostrarToast("Base de conocimiento eliminada.", "exito");
        setTimeout(function () {
          window.location.reload();
        }, 600);
      })
      .catch(function () {
        mostrarToast("No se pudo eliminar la base de conocimiento.");
      })
      .finally(function () {
        botonConfirmarEliminarFuente.disabled = false;
      });
  });

  // Cerrar modales con Escape
  document.addEventListener("keydown", function (evento) {
    if (evento.key === "Escape") {
      cerrarModalCrear();
      cerrarModalFuente();
      cerrarModalEliminarFuente();
    }
  });
})();