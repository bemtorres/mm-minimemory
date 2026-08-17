# Agentes Personales con DeepSeek

## Descripción

Proyecto educativo en **Python** que implementa agentes conversacionales basados en la
API de **DeepSeek**. El programa soporta **varios agentes a la vez**: al iniciar te
pregunta con quién quieres conversar y cada agente tiene sus propios datos.

Un agente representa a una persona específica. Sus respuestas se basan en:

- **Identidad** — el rol y estilo de respuesta del agente (`identidad.txt`).
- **Perfil** — datos de la persona representada.
- **Conocimiento previo** — conocimientos `conocimiento.txt` en los que se apoyan las respuestas.
- **Memoria** — información aprendida en conversaciones (sobrevive al cerrar el programa).
- **Historial** — las conversaciones anteriores.

La información se almacena en archivos de texto locales, sin base de datos:

```
agents/<nombre_del_agente>/
├── identidad.txt        -> clave del rol (solo si es predefinida).
├── identidad_custom.txt -> prompt de rol personalizado (solo si es personalizada).
├── perfil.txt           -> datos de la persona.
├── conocimiento.txt     -> conocimientos previos del agente.
├── memoria.txt          -> lo aprendido en conversaciones.
└── conversacion.csv     -> historial completo.
```

No utiliza base de datos, framework web ni Docker. Es un prototipo sencillo pensado
para que un estudiante de programación lo entienda y modifique fácilmente.

## Requisitos

- Python 3.11 o superior.
- Una cuenta y una API Key de [DeepSeek](https://platform.deepseek.com/).
- Conexión a internet para consultar la API.

## Instalación

1. Clona o descarga el proyecto y entra a la carpeta:

   ```bash
   cd agente_deepseek
   ```

2. Crea un entorno virtual:

   ```bash
   python -m venv venv
   ```

   Actívalo en Windows:

   ```bash
   venv\Scripts\activate
   ```

   Actívalo en Linux/macOS:

   ```bash
   source venv/bin/activate
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

## Configuración

1. Copia el archivo de ejemplo:

   ```bash
   copy .env.example .env     # Windows
   cp .env.example .env       # Linux/macOS
   ```

2. Edita `.env` y agrega tu API Key de DeepSeek:

   ```env
   DEEPSEEK_API_KEY=tu_api_key_real
   ```

   La API Key nunca se escribe en el código: se lee desde el archivo `.env`
   (que está excluido de Git mediante `.gitignore`).

## Ejecución

```bash
python main.py
```

Al iniciar, el programa muestra los agentes disponibles y te pregunta con quién
quieres conversar:

```text
Agentes disponibles:
  1. benjamin

¿Con quién vas a hablar? (número o nombre):
```

Escribe el número de un agente existente o un nombre nuevo: si el nombre no
existe, se crea un agente nuevo con su propia carpeta.

```text
========================================
    AGENTES PERSONALES - DEEPSEEK
========================================

Tú: ¿Qué es Django?

Agente:
Django es un framework web de Python que sigue el patrón
Modelo-Template-Vista e incluye un ORM...
```

## Cómo crear un agente nuevo

Hay dos formas:

1. **Desde la terminal**: al elegir agente, escribe un nombre que no exista.
   El programa crea la carpeta, te pide los conocimientos previos (línea por
   línea, termina con `FIN`) y luego la **identidad** (rol) del agente.
2. **Directamente en los archivos**: crea una carpeta dentro de `agents/` con
   los archivos (`identidad.txt`, `perfil.txt`, `conocimiento.txt`,
   `memoria.txt`, `conversacion.csv`), o copia la carpeta de un agente
   existente y edítala.

Cada agente es independiente: tiene su propia identidad, conversación, memoria
y conocimiento.

## Identidades

Cada agente tiene una **identidad** que define cómo responde. Las identidades
predefinidas se definen en `identidades.py` (diccionario `IDENTIDADES`). Las
disponibles son:

| Clave           | Nombre                   | Estilo                                   |
| --------------- | ------------------------ | ---------------------------------------- |
| `basic`         | Básico                   | Respuestas claras, lógicas y directas.   |
| `advanced`      | Avanzado                 | Instrucciones estructuradas.             |
| `wikipedia`     | Wikipedia                | Responde en primera persona.             |
| `storyteller`   | Narrador de historias    | Convierte la información en relatos.     |
| `teacher`       | Profesor                 | Explica paso a paso con ejemplos.        |
| `coach`         | Coach motivacional       | Inspira y orienta.                       |
| `analyst`       | Analista                 | Conclusiones objetivas y razonadas.      |
| `journalist`    | Periodista               | Relatos precisos e imparciales.          |
| `scientist`     | Científico               | Rigor y evidencia.                       |
| `philosopher`   | Filósofo                 | Reflexión y preguntas que invitan a pensar. |
| `child_friendly`| Amigable para niños      | Simple, divertida y visual.              |
| `historian`     | Historiador              | Contexto y precisión cronológica.        |
| `detective`     | Detective                | Deducciones lógicas e intrigantes.       |
| `futurist`      | Futurista                | Visión innovadora del futuro.            |
| `poet`          | Poeta                    | Belleza, emoción y ritmo.                |

### Identidades personalizadas

El agente usa **uno de dos archivos** para su identidad (nunca los dos a la vez):

| Archivo                | Cuándo existe                                  |
| ---------------------- | ---------------------------------------------- |
| `identidad.txt`        | Cuando se usa una identidad predefinida.       |
| `identidad_custom.txt` | Cuando se usa una identidad personalizada.     |

Son **mutuamente excluyentes**:

- Al escribir una identidad **personalizada** se elimina `identidad.txt`
  (la personalizada reemplaza a la predefinida).
- Al elegir una identidad **predefinida** se elimina `identidad_custom.txt`.

Si no existe ninguno de los dos, el agente usa la identidad `basic`.

Para escribir una identidad personalizada tienes tres opciones:

- Al **crear** un agente, elige la opción `0. Escribir identidad personalizada`.
- Con el comando `/crear_identidad`, que pide el prompt línea por línea
  (termina con `FIN`).
- Editando `agents/<nombre>/identidad_custom.txt` directamente con cualquier
  editor (y eliminando `identidad.txt` si existiera).

Los prompts personalizados pueden usar los mismos marcadores:

- `[____]` → se reemplaza por el nombre de la persona representada.
- `[información del documento]` → se reemplaza por la referencia a la base de
  conocimiento.

El System Prompt final es el **prompt de rol de la identidad** más las
secciones `PERFIL`, `BASE DE CONOCIMIENTO` y `MEMORIA`. Puedes cambiar la
identidad en cualquier momento con `/cambiar_identidad` (una identidad
predefinida borra la personalizada, y la opción `0` escribe una nueva
personalizada).

## Agentes de ejemplo

La carpeta `agents/` incluye tres agentes de ejemplo:

| Agente            | Identidad                  | Descripción                              |
| ----------------- | -------------------------- | ---------------------------------------- |
| `benjamin`        | `teacher` (predefinida)    | Profesor que explica paso a paso.        |
| `elon_musk`       | Personalizada              | Responde como Elon Musk en 1.ª persona.  |
| `albert_einstein` | Personalizada              | Responde como Albert Einstein en 1.ª persona. |

Cada uno tiene su propio `perfil.txt`, `conocimiento.txt`, `memoria.txt` y
`conversacion.csv`.

## Arquitectura

```text
agents/<nombre>/
├── identidad.txt     (rol/estilo de respuesta)
├── perfil.txt        (quién es la persona)
├── conocimiento.txt  (en qué se basan las respuestas)
├── memoria.txt       (qué aprendió el agente)
└── conversacion.csv  (historial completo)
         │
         ↓
System Prompt (identidad + perfil + conocimiento + memoria)
         ↓
DeepSeek (deepseek-chat)
         ↓
respuesta
         ↓
memoria (segunda llamada: decide qué recordar)
```

Flujo paso a paso:

1. `main.py` pregunta con qué agente conversar y crea la instancia `Agente`.
2. `Agente` carga `identidad.txt`, `perfil.txt`, `conocimiento.txt` y
   `memoria.txt` del agente.
3. El usuario escribe un mensaje.
4. `Agente` construye el System Prompt con la identidad (marcadores
   reemplazados), perfil, conocimiento y memoria, y agrega las últimas 10
   interacciones del CSV como contexto.
5. Envía todo a DeepSeek (`deepseek-chat`) y obtiene la respuesta.
6. Guarda el mensaje y la respuesta en `conversacion.csv` del agente.
7. Hace una segunda llamada a DeepSeek para decidir si hay información nueva que
   valga la pena recordar. Si la hay, la agrega a `memoria.txt` del agente
   (evitando duplicados) para que sobreviva a futuras ejecuciones.

### Módulos

| Archivo           | Responsabilidad                                          |
| ----------------- | -------------------------------------------------------- |
| `main.py`         | Interfaz de consola, selección de agente y comandos.     |
| `agente.py`       | Clase `Agente`: llama a DeepSeek y coordina los datos.   |
| `memoria.py`      | Carpetas `agents/`, lectura/escritura de archivos.       |
| `identidades.py`  | Diccionario `IDENTIDADES` con los roles disponibles.     |
| `prompt.py`       | Construcción del System Prompt y análisis de memoria.    |

### Comandos

| Comando          | Acción                                                     |
| ---------------- | ---------------------------------------------------------- |
| `/memoria`       | Muestra la memoria almacenada del agente.                  |
| `/perfil`        | Muestra el perfil de la persona.                           |
| `/conocimiento`  | Muestra los conocimientos previos del agente.              |
| `/identidad`     | Muestra la identidad actual y su prompt de rol.            |
| `/cambiar_identidad` | Cambia la identidad (predefinida o personalizada).    |
| `/crear_identidad`   | Escribe una identidad personalizada en identidad.txt.  |
| `/historial`     | Muestra las últimas conversaciones.                        |
| `/limpiar`       | Pide confirmación y borra la memoria (no el perfil).       |
| `/cambiar`       | Cambia de agente dentro de la misma sesión.                |
| `/salir`         | Cierra el programa.                                        |

## Ejemplo de conversación

```text
Tú: ¿Qué tecnologías utilizas?

Agente:
Tengo experiencia con Python, Django, Laravel,
Angular, MySQL y otras tecnologías...

Tú: Estoy desarrollando un agente con DeepSeek.

Agente:
Es una buena alternativa para este tipo de proyecto...

[El sistema analiza si debe guardar esta información]

Tú: /memoria

MEMORIA DEL AGENTE
------------------
El usuario está desarrollando un agente digital
utilizando Python y DeepSeek.
```

## Cómo funciona la memoria automática

Después de cada intercambio, el agente hace una segunda llamada a DeepSeek con
la conversación reciente y la memoria actual. DeepSeek responde:

- `NO_MEMORIA` si no hay nada nuevo que valga la pena recordar, o
- las frases que deberían guardarse.

`memoria.py` limpia la respuesta, descarta los duplicados mediante una
comparación básica de texto y agrega lo nuevo a `memoria.txt`. De esta forma
el agente no guarda todo lo que se dice, sino solo lo relevante.

## Manejo de errores

El programa muestra mensajes claros (sin trazas técnicas) cuando:

- falta o es inválida la API Key en `.env`,
- no hay conexión a internet,
- DeepSeek devuelve un error o una respuesta vacía,
- se supera el límite de solicitudes,
- el usuario interrumpe con `Ctrl + C`.

Si los archivos de un agente no existen, el programa los crea automáticamente.