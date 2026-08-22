# 🚀 Guía de Instalación y Despliegue — THEYTHINK AI

Bienvenido a la guía oficial de instalación de **THEYTHINK AI**. Esta plataforma modular de agentes inteligentes desarrollada en Python y Flask te permite crear, personalizar e interactuar con agentes autónomos impulsados por **DeepSeek**.

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de contar con los siguientes elementos:

| Requisito | Versión Recomendada | Enlace / Nota |
| :--- | :--- | :--- |
| **Python** | 3.10 o superior (3.11+ ideal) | [Descargar Python](https://www.python.org/downloads/) *(Asegúrate de marcar "Add python.exe to PATH")* |
| **DeepSeek API Key** | V3 / Chat | [DeepSeek Platform](https://platform.deepseek.com/) |
| **Sistema Operativo** | Windows 10/11, macOS, Linux | Guía optimizada con instalador `.bat` para Windows |

---

## ⚡ Opción 1: Instalación Rápida Automática (Windows)

Para facilitarte todo el proceso, hemos creado un script automatizado que realiza cada paso por ti.

### Pasos:

1. **Ejecutar el instalador:**  
   Haz doble clic sobre el archivo [`install.bat`](file:///c:/Users/benja/Desktop/minimind/agente_deepseek/install.bat) o ejecútalo desde tu terminal:
   ```cmd
   install.bat
   ```

2. **¿Qué hace el instalador automáticamente?**
   - ✅ Comprueba que Python esté instalado en tu sistema.
   - 📦 Crea un entorno virtual aislado (`venv`).
   - 🔄 Activa el entorno virtual y actualiza `pip`.
   - 📥 Instala todas las dependencias requeridas desde [`requirements.txt`](file:///c:/Users/benja/Desktop/minimind/agente_deepseek/requirements.txt) (`flask`, `openai`, `python-dotenv`).
   - ⚙️ Crea el archivo `.env` a partir de [`.env.example`](file:///c:/Users/benja/Desktop/minimind/agente_deepseek/.env.example) y te permite ingresar tu clave de DeepSeek en el momento.
   - 🗄️ Inicializa y puebla la base de datos SQLite [`agentes.db`](file:///c:/Users/benja/Desktop/minimind/agente_deepseek/agentes.db) mediante [`seed.py`](file:///c:/Users/benja/Desktop/minimind/agente_deepseek/seed.py).
   - 🚀 Te ofrece iniciar el servidor inmediatamente abriendo tu navegador.

---

## 🛠️ Opción 2: Instalación Manual Paso a Paso

Si prefieres realizar el proceso de forma manual o estás en Linux/macOS, sigue los siguientes pasos:

### 1. Clonar o acceder a la carpeta del proyecto
Abre una terminal (PowerShell, CMD o Bash) en la raíz del proyecto:
```bash
cd agente_deepseek
```

### 2. Crear y activar el entorno virtual
Es una buena práctica aislar las librerías del proyecto.

- **En Windows:**
  ```cmd
  python -m venv venv
  venv\Scripts\activate
  ```
- **En Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalar las dependencias
Con el entorno virtual activado:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno
Crea una copia del archivo `.env.example` con el nombre `.env`:

- **En Windows (CMD):**
  ```cmd
  copy .env.example .env
  ```
- **En Linux / macOS / PowerShell:**
  ```bash
  cp .env.example .env
  ```

Abre el archivo [`.env`](file:///c:/Users/benja/Desktop/minimind/agente_deepseek/.env) en tu editor y coloca tu API Key de DeepSeek:
```env
DEEPSEEK_API_KEY=tu_clave_api_aqui_sk-...
```

### 5. Inicializar la base de datos
Ejecuta el script seeder para crear las tablas necesarias e insertar los perfiles y agentes predeterminados:
```bash
python seed.py
```
> **Nota:** Si en algún momento deseas reiniciar la base de datos a su estado de fábrica, puedes ejecutar:
> ```bash
> python seed.py --force
> ```

### 6. Iniciar la aplicación
Ejecuta el servidor web con Flask:
```bash
python app.py
```

Abre tu navegador e ingresa a:  
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)** (o **[http://localhost:5000](http://localhost:5000)**)

---

## 🚦 Inicios Posteriores

Una vez completada la instalación inicial, cada vez que desees usar **THEYTHINK AI**:

- **En Windows:**  
  Simplemente haz doble clic en el acceso directo [`iniciar.bat`](file:///c:/Users/benja/Desktop/minimind/agente_deepseek/iniciar.bat).
- **Desde la terminal:**
  ```cmd
  venv\Scripts\activate
  python app.py
  ```

---

## 🔍 Estructura de Archivos Clave

- [`app.py`](file:///c:/Users/benja/Desktop/minimind/agente_deepseek/app.py): Servidor web principal en Flask y rutas de la API REST.
- [`basededatos.py`](file:///c:/Users/benja/Desktop/minimind/agente_deepseek/basededatos.py): Capa de acceso a datos y esquemas SQLite.
- [`seed.py`](file:///c:/Users/benja/Desktop/minimind/agente_deepseek/seed.py): Poblador inicial de agentes, identidades y conocimiento.
- [`requirements.txt`](file:///c:/Users/benja/Desktop/minimind/agente_deepseek/requirements.txt): Dependencias de Python (`openai`, `flask`, `python-dotenv`).
- [`.env`](file:///c:/Users/benja/Desktop/minimind/agente_deepseek/.env): Configuración privada (Clave de API de DeepSeek).
- [`install.bat`](file:///c:/Users/benja/Desktop/minimind/agente_deepseek/install.bat): Script instalador automatizado para Windows.
- [`iniciar.bat`](file:///c:/Users/benja/Desktop/minimind/agente_deepseek/iniciar.bat): Script de inicio rápido de la aplicación.

---

## ❓ Solución de Problemas Frecuentes

### 1. "Python no se reconoce como un comando interno o externo"
- **Causa:** Python no se agregó a la variable de entorno `PATH` durante la instalación.
- **Solución:** Reinstala Python desde [python.org](https://www.python.org/downloads/) asegurándote de marcar la casilla **"Add Python to PATH"** en la primera pantalla del instalador.

### 2. Error de autenticación con DeepSeek
- **Causa:** La clave `DEEPSEEK_API_KEY` en el archivo `.env` no es válida o está vacía.
- **Solución:** Abre el archivo [`.env`](file:///c:/Users/benja/Desktop/minimind/agente_deepseek/.env) y asegúrate de que contenga una clave válida emitida en [platform.deepseek.com](https://platform.deepseek.com).

### 3. Puerto 5000 en uso
- **Causa:** Otra aplicación está utilizando el puerto 5000.
- **Solución:** Cierra el proceso que ocupa el puerto o modifica el puerto al final de [`app.py`](file:///c:/Users/benja/Desktop/minimind/agente_deepseek/app.py):
  ```python
  app.run(debug=True, port=5001)
  ```

---

¡Disfruta construyendo y conversando con tus agentes inteligentes en **THEYTHINK AI**!
