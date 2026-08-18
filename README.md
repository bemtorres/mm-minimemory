# THEYTHINK — Intelligent Multi-Agent AI Platform

<p align="center">
  <strong>Autonomous, Modular, Multi-Persona Conversational Platform powered by DeepSeek AI</strong><br>
  <em>Persistent Active Memory · Decoupled Knowledge Bases · Dynamic Role Engine · Ergonomic Multi-Thread Chat · Light & Dark Themes</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/Framework-Flask-000000?style=flat&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/Database-SQLite-003B57?style=flat&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/LLM-DeepSeek_Chat-4D6BFE?style=flat" alt="DeepSeek AI" />
  <img src="https://img.shields.io/badge/Design-Google_Material_%2F_HeroUI-4285F4?style=flat" alt="Design" />
  <a href="https://github.com/bemtorres"><img src="https://img.shields.io/badge/Author-Bemtorres-181717?style=flat&logo=github&logoColor=white" alt="Author Bemtorres" /></a>
</p>

---

## 🌐 Language Navigation
- [English Documentation](#-english-documentation)
- [Documentación en Español](#-documentación-en-español)

---

# 🇺🇸 English Documentation

## 🌟 Overview

**THEYTHINK** is a state-of-the-art web platform engineered in Python (Flask) with an embedded SQLite persistence engine, designed to create, orchestrate, customize, and converse with autonomous AI agents powered by the **DeepSeek API**.

Featuring **live persistent memory**, **decoupled multi-source knowledge bases**, **dynamic system prompt and role engineering**, **avatar/image asset uploads**, and an ergonomic **Material You / HeroUI** design with seamless **Dark / Light theme toggling**.

---

## ✨ Key Features

### 1. 💬 Ergonomic Multi-Thread Chat Interface
- **Multiple Chat Threads per Agent**: Spawn parallel conversations without cluttering or overflowing the LLM context.
- **Collapsible Sidebar with Live Search**: Filter, rename, and delete conversation threads in real time.
- **Quick Agent Switcher**: Seamlessly toggle between characters directly in the chat header.
- **Contextual One-Click Suggestions**: Start engaging immediately with tailored prompt cards.
- **Instant Response Copy**: One-click markdown copy to clipboard with visual feedback.
- **Hot-Settings Modal**: Inspect and modify persona traits, linked knowledge bases, and memory facts without leaving the chat room.

### 2. 📊 Comprehensive Administrative Dashboard
- **Real-Time KPI Metrics**: Live counters for total agents, knowledge bases, custom roles, registered users, and messages.
- **Agent Manager**: Create and refine agents with full profile customization, avatar preview, and $N:M$ knowledge base assignment.
- **Decoupled Knowledge Bases**: Independent topic sources reusable across multiple agents.
- **Role & System Prompt Engineering**: In-browser CRUD to polish identity prompts and personality directives.
- **User Administration (Show $\rightarrow$ Edit $\rightarrow$ Update)**: Detailed user profile cards, role hierarchy, and secure credential resets.
- **Conversation Audit Explorer**: Global timeline view of all chats and messages across the platform.

### 3. 🌓 Universal Light & Dark Mode
- Global ☀️ / 🌙 theme switch persisted in `localStorage`.
- Zero-flicker inline script ensuring smooth initial renders.
- Tailored color palette inspired by Google Gemini & Material Design (`#1a73e8`, `#ea4335`, `#fbbc04`, `#34a853`).

### 4. 🖼️ Avatar & Image Management
- Secure local image uploads (`PNG`, `JPG`, `WEBP`, `GIF`, `SVG`) via `/api/upload/avatar`.
- Remote image URL support with real-time preview in modals, catalog cards, and chat headers.

### 5. 🧠 Persistent Active Memory
- Evaluates dialogue turn-by-turn and extracts key facts and user preferences into SQLite, automatically de-duplicating memories.
- Review and clear memory at any time through the agent configuration modal.

### 6. 🎭 Preconfigured Personas & Canonical Figures
Out of the box, **THEYTHINK** includes rich, authentic characters with verified knowledge sources:
- **🌟 The Little Prince (`el_principito`)**: Philosophical, pure, and poetic voice from Asteroid B-612.
- **🔍 Sherlock Holmes (`sherlock_holmes`)**: Razor-sharp Victorian deduction master from 221B Baker Street.
- **⚔️ Don Quixote (`don_quijote`)**: Chivalrous Golden Age defender of justice and noble ideals.
- **🏛️ Socrates (`socrates`)**: Socratic dialogue master and moral inquisitor of the Athenian Agora.
- **⚡ Nikola Tesla (`nikola_tesla`)**: Visionary of alternating current, electromagnetism, and wireless energy.
- **⚽ Colo-Colo Fan (`hincha_colocolo`)**: Passionate Chilean football fan, 1991 Copa Libertadores and club history expert.
- **🦉 Universidad de Chile Fan (`hincha_udechile`)**: Unconditional *Romántico Viajero* fan, Ballet Azul and 2011 Copa Sudamericana expert.
- **🧢 Chilean Urban Character (`el_flaite_chileno`)**: Authentic Chilean street slang (*coa*), urban culture, and neighborhood wisdom.
- **👨‍🏫 Benjamin (`benjamin`)**, **🚀 Elon Musk (`elon_musk`)**, and **⚛️ Albert Einstein (`albert_einstein`)**.

---

## 🏗️ Project Architecture

```
agente_deepseek/
├── app.py                  -> Main Flask web server, REST API, auth decorators & routes.
├── basededatos.py          -> SQLite layer (agentes.db), AgenteDB engine, schema migrations & seeders.
├── identidades.py          -> System prompt templates, identity processors & role catalog.
├── prompt.py               -> Dynamic prompt compiler & memory extraction builder.
├── seed.py                 -> Standalone database seeder with personas & starter dialogues.
├── requirements.txt        -> Python package requirements.
├── .env.example            -> Environment variables template.
├── templates/              -> Jinja2 HTML templates:
│   ├── base.html           -> Root layout (themes, toast alerts, modals, Lucide icons).
│   ├── index.html          -> Public landing page & visual agent showcase.
│   ├── dashboard.html      -> Admin control suite (Agents, Bases, Roles, Users, History).
│   ├── chat.html           -> Workspace chat room with sidebar, thread manager & live settings.
│   └── login.html          -> Authentication portal.
├── static/
│   ├── css/
│   │   └── app.css         -> Design system tokens, light/dark themes & micro-animations.
│   ├── js/
│   │   ├── dashboard.js    -> Dashboard state management, avatar uploads & CRUD handlers.
│   │   └── chat.js         -> Real-time chat client, streaming UI, markdown & clipboard.
│   └── uploads/
│       └── avatars/        -> Directory for uploaded agent profile pictures.
└── __old__/                -> Archived legacy CLI scripts (main.py, memoria.py, agents/).
```

---

## 🚀 Quickstart Guide

### 1. Clone Repository
```bash
git clone <repository-url>
cd agente_deepseek
```

### 2. Set Up Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

Set your DeepSeek API key:
```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
FLASK_SECRET_KEY=custom_session_secret_key_here
```

### 5. Seed the Database (Optional)
Populate sample agents, knowledge bases, and dialogue history:
```bash
python seed.py
```
*(Use `python seed.py --force` to reset the database at any time).*

### 6. Launch the Server
```bash
python app.py
```

Navigate to:
👉 **[http://localhost:5000](http://localhost:5000)**

---

## 🔑 Default Credentials

- **Username:** `admin`
- **Password:** `admin123`

*(Can be updated anytime from the Admin Dashboard $\rightarrow$ My Account).*

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/login` | User session authentication. |
| `GET` | `/logout` | Terminate session. |
| `GET` | `/api/agentes` | List all registered agents. |
| `POST` | `/api/agentes` | Create a new agent. |
| `GET` | `/api/agente/<nombre>` | Retrieve agent details, profile, role, and linked bases. |
| `POST` | `/api/agente/<nombre>/editar` | Update agent configuration, profile, avatar, or sources. |
| `DELETE` | `/api/agente/<nombre>` | Delete agent and associated history. |
| `POST` | `/api/agente/<nombre>/chat` | Send message to DeepSeek and trigger active memory. |
| `POST` | `/api/agente/<nombre>/sesiones` | Spawn a new conversation thread. |
| `PUT` | `/api/sesion/<id>` | Rename conversation thread title. |
| `DELETE` | `/api/sesion/<id>` | Delete conversation thread. |
| `GET` | `/api/fuentes` | List decoupled knowledge bases. |
| `POST` | `/api/fuentes` | Create a knowledge base. |
| `POST` | `/api/upload/avatar` | Upload agent profile picture. |
| `GET` | `/api/roles` | List available system and custom roles. |
---

## 👨‍💻 Author & Credits

- **Developer:** [Bemtorres](https://github.com/bemtorres)
- **GitHub:** [https://github.com/bemtorres](https://github.com/bemtorres)
- **Engine:** Backed by SQLite · Powered by DeepSeek AI

---
---

# 🇪🇸 Documentación en Español

## 🌟 Descripción General

**THEYTHINK** es una plataforma web desarrollada en **Python (Flask)** con base de datos **SQLite**, diseñada para crear, personalizar y conversar con agentes inteligentes respaldados por el modelo **DeepSeek**, con **memoria viva persistente**, **bases de conocimiento desacopladas**, **roles dinámicos**, **avatares personalizados** y una interfaz moderna con **Modo Claro / Modo Oscuro** inspirada en **Google Gemini** y **HeroUI**.

---

## ✨ Funcionalidades Destacadas

### 1. 💬 Sala de Chat Multihilo y Ergonómica
- **Múltiples hilos de chat** por agente para organizar conversaciones por tema.
- **Barra lateral colapsable** con buscador en tiempo real y gestión de hilos.
- **Selector rápido** de agente en la cabecera sin salir del chat.
- **Preguntas sugeridas** de un clic para iniciar de forma ágil.
- **Botón de copiado** con feedback visual instantáneo.
- **Modal de ajustes en caliente** para calibrar perfil, rol, bases y memoria en vivo.

### 2. 📊 Dashboard Administrativo Completo
- **Tarjetas KPI** con métricas en tiempo real de agentes, bases, roles, usuarios y mensajes.
- **Gestión de Agentes**: Creación y edición con previsualización de avatar y asociación $N:M$ de bases de conocimiento.
- **Bases de Conocimiento Desacopladas**: Fuentes reutilizables entre múltiples agentes.
- **Mantenedor de Roles**: Creación y edición de System Prompts personalizados directamente desde la web.
- **Administración de Usuarios (Show $\rightarrow$ Edit $\rightarrow$ Update)**: Fichas de detalle y actualización de credenciales.
- **Explorador de Historiales**: Auditoría global de conversaciones y mensajes.

### 3. 🌓 Modo Claro y Modo Oscuro
- Conmutador universal Sol ☀️ / Luna 🌙 con persistencia en `localStorage`.
- Script anti-parpadeo inline para carga instantánea sin saltos de color.
- Paleta Google Material You (`#1a73e8`, `#ea4335`, `#fbbc04`, `#34a853`).

### 4. 🖼️ Soporte de Imágenes y Avatares
- Carga de imágenes locales (`PNG`, `JPG`, `WEBP`, `GIF`, `SVG`) mediante `/api/upload/avatar`.
- URLs externas con previsualización inmediata.

### 5. 🧠 Memoria Viva Inteligente
- Extracción y consolidación automática de hechos aprendidos durante las conversaciones, evitando duplicados.

### 6. 🎭 Catálogo de Personajes
- **El Principito (`el_principito`)**, **Sherlock Holmes (`sherlock_holmes`)**, **Don Quijote (`don_quijote`)**, **Sócrates (`socrates`)**, **Nikola Tesla (`nikola_tesla`)**, **Hincha de Colo-Colo (`hincha_colocolo`)**, **Hincha de la U (`hincha_udechile`)**, **Flaite Chileno (`el_flaite_chileno`)**, **Benjamin (`benjamin`)**, **Elon Musk (`elon_musk`)** y **Albert Einstein (`albert_einstein`)**.

---

## 🚀 Instalación y Uso Rápido

```bash
# 1. Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\activate      # Windows
source venv/bin/activate    # Linux / macOS

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env        # Configura tu DEEPSEEK_API_KEY

# 4. Poblar datos iniciales (opcional)
python seed.py

# 5. Iniciar la plataforma
python app.py
```

Abre en tu navegador: **[http://localhost:5000](http://localhost:5000)**

---

## 🔑 Credenciales por Defecto

- **Usuario:** `admin`
- **Contraseña:** `admin123`

---

## 👨‍💻 Autor y Créditos

- **Desarrollador:** [Bemtorres](https://github.com/bemtorres)
- **GitHub:** [https://github.com/bemtorres](https://github.com/bemtorres)
- **Motor:** Respaldado en SQLite · Impulsado por DeepSeek AI