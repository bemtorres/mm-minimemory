"""Clase principal del agente conversacional.

`Agente` representa a un agente concreto (una carpeta dentro de `agents/`)
y conecta su perfil, su conocimiento, su memoria y su historial con la API
de DeepSeek. Las llamadas a la API se hacen aquí; la persistencia en
archivos se delega al módulo `memoria`.
"""

import csv
import os
from datetime import datetime

import openai
from dotenv import load_dotenv

from memoria import (
    agregar_memorias,
    escribir_identidad,
    escribir_identidad_custom,
    leer_conocimiento,
    leer_identidad,
    leer_identidad_custom,
    leer_memoria,
    leer_perfil,
    ruta_agente,
)
from prompt import (
    construir_prompt_memoria,
    construir_system_prompt,
    procesar_identidad,
)
from identidades import IDENTIDADES

# Modelo de DeepSeek utilizado para la conversación.
MODELO = "deepseek-chat"

# Cantidad de mensajes recientes que se envían como contexto.
HISTORIAL_RECIENTE = 10

# Marcador que devuelve DeepSeek cuando no hay nada nuevo que recordar.
SIN_MEMORIA = "NO_MEMORIA"


class Agente:
    """Representación digital de una persona con memoria persistente."""

    def __init__(self, nombre):
        load_dotenv()
        self.nombre = nombre
        self.perfil = ""
        self.memoria = ""
        self.conocimiento = ""
        self.identidad = ""
        self.identidad_custom = ""
        self.client = self._crear_cliente()
        self.cargar_perfil()
        self.cargar_conocimiento()
        self.cargar_identidad()
        self.cargar_memoria()

    # ------------------------------------------------------------------
    # Configuración
    # ------------------------------------------------------------------

    def _crear_cliente(self):
        """Crea el cliente de DeepSeek usando la API Key del entorno."""
        api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        if not api_key or api_key == "tu_api_key":
            raise ValueError(
                "No se encontró una API Key válida de DeepSeek. "
                "Copia .env.example a .env y agrega tu DEEPSEEK_API_KEY."
            )
        return openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )

    # ------------------------------------------------------------------
    # Datos
    # ------------------------------------------------------------------

    def cargar_perfil(self):
        """Lee perfil.txt del agente. Si no existe, se crea con la plantilla."""
        self.perfil = leer_perfil(self.nombre)

    def cargar_conocimiento(self):
        """Lee conocimiento.txt del agente. Si no existe, se crea vacío."""
        self.conocimiento = leer_conocimiento(self.nombre)

    def cargar_identidad(self):
        """Carga la identidad del agente.

        - identidad.txt         -> clave de una identidad predefinida.
        - identidad_custom.txt  -> prompt personalizado (tiene prioridad).
        """
        self.identidad = leer_identidad(self.nombre)
        self.identidad_custom = leer_identidad_custom(self.nombre)

    def establecer_identidad(self, clave):
        """Usa una identidad predefinida por clave.

        Escribir la clave elimina identidad_custom.txt (exclusión mutua).
        """
        escribir_identidad(self.nombre, clave)
        self.cargar_identidad()
        return self.identidad

    def establecer_identidad_personalizada(self, contenido):
        """Guarda un prompt de identidad propio en identidad_custom.txt.

        Escribir la personalizada elimina identidad.txt (la reemplaza).
        """
        escribir_identidad_custom(self.nombre, contenido)
        self.cargar_identidad()
        return self.identidad_custom

    def _usa_identidad_personalizada(self):
        """True si existe un prompt propio en identidad_custom.txt."""
        return bool(self.identidad_custom.strip())

    def obtener_prompt_identidad(self):
        """Devuelve el prompt de rol de la identidad del agente.

        Prioridad: identidad_custom.txt > clave en identidad.txt > 'basic'.
        """
        if self._usa_identidad_personalizada():
            return self.identidad_custom
        if self.identidad in IDENTIDADES:
            return IDENTIDADES[self.identidad]["prompt"]
        return IDENTIDADES["basic"]["prompt"]

    def info_identidad(self):
        """Devuelve (nombre, descripcion, prompt) de la identidad actual."""
        if self._usa_identidad_personalizada():
            return (
                "Identidad personalizada",
                "Prompt propio guardado en identidad_custom.txt.",
                self.identidad_custom,
            )
        if self.identidad in IDENTIDADES:
            datos = IDENTIDADES[self.identidad]
            return datos["name"], datos["description"], datos["prompt"]
        datos = IDENTIDADES["basic"]
        return datos["name"], datos["description"], datos["prompt"]

    def cargar_memoria(self):
        """Lee memoria.txt del agente. Si no existe, se crea vacía."""
        self.memoria = leer_memoria(self.nombre)

    def obtener_nombre(self):
        """Extrae el nombre de la persona desde el perfil del agente."""
        lineas = self.perfil.splitlines()
        for indice, linea in enumerate(lineas):
            if linea.strip().startswith("NOMBRE:"):
                for siguiente in lineas[indice + 1:]:
                    if siguiente.strip():
                        return siguiente.strip()
        return self.nombre

    def obtener_historial(self, cantidad=HISTORIAL_RECIENTE):
        """Devuelve los últimos `cantidad` mensajes de conversacion.csv.

        Cada elemento es una tupla (rol, mensaje).
        Si el archivo no existe o está corrupto, devuelve una lista vacía.
        """
        ruta = ruta_agente(self.nombre, "conversacion.csv")
        if not os.path.exists(ruta):
            return []
        try:
            with open(ruta, "r", encoding="utf-8", newline="") as archivo:
                filas = list(csv.DictReader(archivo))
        except (UnicodeDecodeError, csv.Error, OSError):
            return []
        return [
            (fila.get("rol", ""), fila.get("mensaje", ""))
            for fila in filas[-cantidad:]
        ]

    def guardar_conversacion(self, rol, mensaje):
        """Guarda un mensaje en conversacion.csv del agente con fecha y hora."""
        ruta = ruta_agente(self.nombre, "conversacion.csv")
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        nuevo = not os.path.exists(ruta)
        # Si el archivo ya existe pero no termina en salto de línea,
        # se agrega uno para no pegar la fila nueva a la última existente.
        if not nuevo:
            with open(ruta, "r", encoding="utf-8") as archivo:
                contenido = archivo.read()
            if contenido and not contenido.endswith("\n"):
                with open(ruta, "a", encoding="utf-8") as archivo:
                    archivo.write("\n")
        ahora = datetime.now()
        mensaje = " ".join(str(mensaje).split())
        with open(ruta, "a", encoding="utf-8", newline="") as archivo:
            escritor = csv.writer(archivo)
            if nuevo:
                escritor.writerow(["fecha", "hora", "rol", "mensaje"])
            escritor.writerow(
                [
                    ahora.strftime("%Y-%m-%d"),
                    ahora.strftime("%H:%M"),
                    rol,
                    mensaje,
                ]
            )

    # ------------------------------------------------------------------
    # Prompts y llamadas a DeepSeek
    # ------------------------------------------------------------------

    def construir_prompt(self):
        """Construye el System Prompt desde la identidad del agente.

        El prompt de rol de la identidad se procesa (se reemplazan los
        marcadores) y luego se le agregan perfil, conocimiento y memoria.
        """
        rol = procesar_identidad(
            self.obtener_prompt_identidad(),
            self.obtener_nombre(),
        )
        return construir_system_prompt(rol, self.perfil, self.conocimiento, self.memoria)

    def preguntar(self, mensaje):
        """Envía un mensaje del usuario a DeepSeek y devuelve la respuesta.

        Guarda automáticamente la conversación en el CSV del agente.
        Lanza RuntimeError con un mensaje claro si algo falla.
        """
        self.guardar_conversacion("user", mensaje)
        historial = self.obtener_historial()

        mensajes = [{"role": "system", "content": self.construir_prompt()}]
        for rol, contenido in historial:
            if contenido:
                mensajes.append({"role": rol, "content": contenido})

        respuesta = self._enviar(mensajes)

        if not respuesta:
            raise RuntimeError("DeepSeek devolvió una respuesta vacía.")

        self.guardar_conversacion("assistant", respuesta)
        return respuesta

    def actualizar_memoria(self, mensaje_usuario, respuesta):
        """Pregunta a DeepSeek si hay información nueva que recordar.

        Si el modelo responde algo distinto de NO_MEMORIA, se agrega a
        memoria.txt del agente evitando duplicados. Los errores se ignoran:
        fallar al recordar no debe interrumpir la conversación.
        """
        conversacion = f"Usuario: {mensaje_usuario}\nAgente: {respuesta}"
        prompt = construir_prompt_memoria(self.memoria, conversacion)
        try:
            contenido = self._enviar([{"role": "user", "content": prompt}])
        except RuntimeError:
            return []

        if not contenido or SIN_MEMORIA in contenido.upper():
            return []

        agregadas = agregar_memorias(self.nombre, contenido)
        if agregadas:
            self.cargar_memoria()
        return agregadas

    def _enviar(self, mensajes):
        """Realiza una llamada a la API de DeepSeek.

        Convierte los errores de conexión y de la API en RuntimeError
        con mensajes comprensibles para el usuario.
        """
        try:
            respuesta = self.client.chat.completions.create(
                model=MODELO,
                messages=mensajes,
                max_tokens=400,
            )
        except openai.AuthenticationError as error:
            raise RuntimeError(
                "La API Key de DeepSeek es inválida. Verifica tu .env."
            ) from error
        except openai.APIConnectionError as error:
            raise RuntimeError(
                "No se pudo conectar con DeepSeek. Revisa tu conexión a internet."
            ) from error
        except openai.RateLimitError as error:
            raise RuntimeError(
                "Límite de solicitudes alcanzado. Espera unos segundos e intenta de nuevo."
            ) from error
        except openai.APIError as error:
            raise RuntimeError(f"Error de la API de DeepSeek: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error inesperado al contactar a DeepSeek: {error}") from error

        contenido = respuesta.choices[0].message.content
        return contenido.strip() if contenido else ""