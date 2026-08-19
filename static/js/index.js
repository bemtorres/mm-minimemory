/**
 * Lógica de la página de inicio pública: gestión de agentes y bases de conocimiento.
 * Código escrito en inglés con comentarios y docstrings en español.
 */
(function () {
  "use strict";

  // Elementos principales del DOM
  var agentsSection = document.getElementById("seccion-agentes");
  var sourcesSection = document.getElementById("seccion-fuentes");
  var tabAgentsButton = document.getElementById("tab-btn-agentes");
  var tabSourcesButton = document.getElementById("tab-btn-fuentes");

  // Modal Crear Agente
  var createAgentModal = document.getElementById("modal-crear");
  var createAgentForm = document.getElementById("form-crear");
  var agentNameInput = document.getElementById("campo-nombre");
  var agentProfileInput = document.getElementById("campo-perfil");
  var agentIdentitySelect = document.getElementById("campo-identidad");
  var agentCustomBlock = document.getElementById("bloque-personalizada");
  var agentCustomPromptInput = document.getElementById("campo-identidad-custom");
  var createAgentButton = document.getElementById("boton-crear");
  var agentSourcesCreateList = document.getElementById("lista-fuentes-crear");

  // Modal Crear / Editar Base de Conocimiento
  var sourceModal = document.getElementById("modal-fuente");
  var sourceForm = document.getElementById("form-fuente");
  var sourceModalTitle = document.getElementById("titulo-modal-fuente");
  var sourceIdInput = document.getElementById("campo-fuente-id");
  var sourceNameInput = document.getElementById("campo-fuente-nombre");
  var sourceContentInput = document.getElementById("campo-fuente-contenido");
  var sourceSaveButton = document.getElementById("boton-guardar-fuente");

  // Modal Eliminar Base de Conocimiento
  var deleteSourceModal = document.getElementById("modal-eliminar-fuente");
  var deleteSourceName = document.getElementById("nombre-eliminar-fuente");
  var deleteSourceConfirmButton = document.getElementById("boton-confirmar-eliminar-fuente");
  var sourceToDeleteId = null;

  // Toast
  var toastElement = document.getElementById("toast");
  var toastContent = document.getElementById("toast-contenido");
  var toastIcon = document.getElementById("toast-icono");
  var toastText = document.getElementById("texto-toast");

  /**
   * Muestra un aviso flotante.
   * @param {string} message - Texto del aviso.
   * @param {string} [type='error'] - Tipo ('exito' o 'error').
   */
  function showToast(message, type) {
    var isSuccess = type === "exito" || type === "success";
    toastText.textContent = message;
    toastContent.className =
      "flex items-center gap-2.5 rounded-2xl px-5 py-3 text-sm font-semibold text-white shadow-2xl " +
      (isSuccess ? "bg-emerald-600" : "bg-rose-600");
    toastIcon.setAttribute("data-lucide", isSuccess ? "check-circle-2" : "triangle-alert");
    toastElement.classList.remove("hidden");
    clearTimeout(toastElement._timer);
    toastElement._timer = setTimeout(function () {
      toastElement.classList.add("hidden");
    }, 4500);
    if (window.lucide) lucide.createIcons();
  }

  // ------------------------------------------------------------------
  // Cambio de pestañas principales (Agentes / Bases de Conocimiento)
  // ------------------------------------------------------------------
  function switchMainTab(tab) {
    if (tab === "agentes") {
      if (agentsSection) agentsSection.classList.remove("hidden");
      if (sourcesSection) sourcesSection.classList.add("hidden");
      if (tabAgentsButton) {
        tabAgentsButton.className =
          "inline-flex items-center gap-2 rounded-xl bg-white px-5 py-2 text-sm font-bold text-slate-900 shadow-sm transition";
        var i1 = tabAgentsButton.querySelector("i");
        if (i1) i1.className = "h-4 w-4 text-brand-600";
      }
      if (tabSourcesButton) {
        tabSourcesButton.className =
          "inline-flex items-center gap-2 rounded-xl px-5 py-2 text-sm font-semibold text-slate-600 transition hover:text-slate-900";
        var i2 = tabSourcesButton.querySelector("i");
        if (i2) i2.className = "h-4 w-4 text-slate-400";
      }
    } else {
      if (agentsSection) agentsSection.classList.add("hidden");
      if (sourcesSection) sourcesSection.classList.remove("hidden");
      if (tabSourcesButton) {
        tabSourcesButton.className =
          "inline-flex items-center gap-2 rounded-xl bg-white px-5 py-2 text-sm font-bold text-slate-900 shadow-sm transition";
        var i3 = tabSourcesButton.querySelector("i");
        if (i3) i3.className = "h-4 w-4 text-brand-600";
      }
      if (tabAgentsButton) {
        tabAgentsButton.className =
          "inline-flex items-center gap-2 rounded-xl px-5 py-2 text-sm font-semibold text-slate-600 transition hover:text-slate-900";
        var i4 = tabAgentsButton.querySelector("i");
        if (i4) i4.className = "h-4 w-4 text-slate-400";
      }
    }
    if (window.lucide) lucide.createIcons();
  }

  // ------------------------------------------------------------------
  // Gestión de Agentes
  // ------------------------------------------------------------------
  function openCreateAgentModal() {
    reloadSourcesListInCreateModal();
    if (createAgentModal) {
      createAgentModal.classList.remove("hidden");
      createAgentModal.classList.add("flex");
      setTimeout(function () {
        if (agentNameInput) agentNameInput.focus();
      }, 50);
    }
  }

  function closeCreateAgentModal() {
    if (createAgentModal) {
      createAgentModal.classList.add("hidden");
      createAgentModal.classList.remove("flex");
    }
  }

  if (agentIdentitySelect) {
    agentIdentitySelect.addEventListener("change", function () {
      var isCustom = agentIdentitySelect.value === "personalizada";
      if (agentCustomBlock) agentCustomBlock.classList.toggle("hidden", !isCustom);
    });
  }

  if (createAgentForm) {
    createAgentForm.addEventListener("submit", function (e) {
      e.preventDefault();
      if (createAgentButton) createAgentButton.disabled = true;

      var selectedSources = [];
      createAgentForm.querySelectorAll("input[name='fuentes_seleccionadas']:checked").forEach(function (cb) {
        selectedSources.push(parseInt(cb.value, 10));
      });

      var body = {
        nombre: agentNameInput.value.trim(),
        perfil: agentProfileInput.value.trim(),
        fuentes_ids: selectedSources,
      };

      if (agentIdentitySelect.value === "personalizada") {
        body.identidad_custom = agentCustomPromptInput.value.trim();
      } else if (agentIdentitySelect.value) {
        body.identidad = agentIdentitySelect.value;
      }

      fetch("/api/agentes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      })
        .then(function (response) {
          return response.json().then(function (data) {
            return { ok: response.ok, data: data };
          });
        })
        .then(function (result) {
          if (!result.ok) {
            throw new Error(result.data.error || "No se pudo crear el agente.");
          }
          window.location.href = "/agente/" + encodeURIComponent(result.data.nombre);
        })
        .catch(function (error) {
          showToast(error.message);
        })
        .finally(function () {
          if (createAgentButton) createAgentButton.disabled = false;
        });
    });
  }

  function reloadSourcesListInCreateModal() {
    if (!agentSourcesCreateList) return;
    fetch("/api/fuentes")
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        var sources = data.fuentes || [];
        agentSourcesCreateList.innerHTML = "";
        if (!sources.length) {
          agentSourcesCreateList.innerHTML =
            '<p class="py-2 text-center text-xs text-slate-400">No hay bases de conocimiento creadas aún.</p>';
          return;
        }
        sources.forEach(function (f) {
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
          agentSourcesCreateList.appendChild(label);
        });
        if (window.lucide) lucide.createIcons();
      })
      .catch(function () {});
  }

  // ------------------------------------------------------------------
  // Gestión de Bases de Conocimiento (Crear / Editar / Eliminar)
  // ------------------------------------------------------------------
  function openCreateSourceModal() {
    if (!sourceModal) return;
    sourceIdInput.value = "";
    sourceNameInput.value = "";
    sourceContentInput.value = "";
    sourceModalTitle.textContent = "Nueva Base de Conocimiento";
    sourceModal.classList.remove("hidden");
    sourceModal.classList.add("flex");
    setTimeout(function () {
      sourceNameInput.focus();
    }, 50);
  }

  function openEditSourceModal(id) {
    if (!sourceModal) return;
    fetch("/api/fuentes/" + id)
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        sourceIdInput.value = data.id;
        sourceNameInput.value = data.nombre;
        sourceContentInput.value = data.contenido || "";
        sourceModalTitle.textContent = "Editar Base de Conocimiento";
        sourceModal.classList.remove("hidden");
        sourceModal.classList.add("flex");
        setTimeout(function () {
          sourceNameInput.focus();
        }, 50);
      })
      .catch(function () {
        showToast("No se pudo cargar la base de conocimiento.");
      });
  }

  function closeSourceModal() {
    if (sourceModal) {
      sourceModal.classList.add("hidden");
      sourceModal.classList.remove("flex");
    }
  }

  if (sourceForm) {
    sourceForm.addEventListener("submit", function (e) {
      e.preventDefault();
      sourceSaveButton.disabled = true;

      var id = sourceIdInput.value;
      var name = sourceNameInput.value.trim();
      var content = sourceContentInput.value.trim();

      if (!name) {
        showToast("Escribe un nombre para la base de conocimiento.");
        sourceSaveButton.disabled = false;
        return;
      }

      var url = id ? "/api/fuentes/" + id : "/api/fuentes";

      fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre: name, contenido: content }),
      })
        .then(function (response) {
          return response.json().then(function (data) {
            return { ok: response.ok, data: data };
          });
        })
        .then(function (result) {
          if (!result.ok) {
            throw new Error(result.data.error || "No se pudo guardar la base de conocimiento.");
          }
          closeSourceModal();
          showToast("Base de conocimiento guardada correctamente.", "exito");
          setTimeout(function () {
            window.location.reload();
          }, 600);
        })
        .catch(function (error) {
          showToast(error.message);
        })
        .finally(function () {
          sourceSaveButton.disabled = false;
        });
    });
  }

  function confirmDeleteSource(id, name) {
    sourceToDeleteId = id;
    if (deleteSourceName) deleteSourceName.textContent = name;
    if (deleteSourceModal) {
      deleteSourceModal.classList.remove("hidden");
      deleteSourceModal.classList.add("flex");
    }
  }

  function closeDeleteSourceModal() {
    if (deleteSourceModal) {
      deleteSourceModal.classList.add("hidden");
      deleteSourceModal.classList.remove("flex");
    }
    sourceToDeleteId = null;
  }

  if (deleteSourceConfirmButton) {
    deleteSourceConfirmButton.addEventListener("click", function () {
      if (!sourceToDeleteId) return;
      deleteSourceConfirmButton.disabled = true;

      fetch("/api/fuentes/" + sourceToDeleteId, {
        method: "DELETE",
      })
        .then(function (res) {
          return res.json();
        })
        .then(function () {
          closeDeleteSourceModal();
          showToast("Base de conocimiento eliminada.", "exito");
          setTimeout(function () {
            window.location.reload();
          }, 600);
        })
        .catch(function () {
          showToast("No se pudo eliminar la base de conocimiento.");
        })
        .finally(function () {
          deleteSourceConfirmButton.disabled = false;
        });
    });
  }

  // Exponer funciones en window
  window.cambiarTabPrincipal = switchMainTab;
  window.abrirModalCrear = openCreateAgentModal;
  window.cerrarModalCrear = closeCreateAgentModal;
  window.abrirModalCrearFuente = openCreateSourceModal;
  window.abrirModalEditarFuente = openEditSourceModal;
  window.cerrarModalFuente = closeSourceModal;
  window.confirmarEliminarFuente = confirmDeleteSource;
  window.cerrarModalEliminarFuente = closeDeleteSourceModal;

  // Cerrar modales con Escape
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      closeCreateAgentModal();
      closeSourceModal();
      closeDeleteSourceModal();
    }
  });
})();