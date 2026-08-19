# Tetring — AGENTS.md

## Qué es

Plataforma web académica para estudiantes del Instituto Politécnico Nacional (IPN) que sincroniza automáticamente la información escolar desde el **SAES**, gestiona el avance curricular (kárdex, materias pendientes, optativas y electivas) y genera combinaciones óptimas de horarios escolares libres de choques. Toda la interfaz de usuario está en **Español (México)** con diseño *Claymorphism*.

---

## Arquitectura del Proyecto

Tetring opera como una arquitectura desacoplada de 3 servicios:

1. **Frontend (`frontend/`)**:
   - **Stack**: React 19, Vite, Tailwind CSS v4, `@tanstack/react-query`, Lucide Icons, Shadcn UI / Base UI, Zustand.
   - **Características clave**:
     - *Dashboard*: KPIs compactos (Cursadas, Promedio, Pendientes con desglose exacto de obligatorias/optativas), Gráfica de evolución académica SVG interactiva (`PerformanceChart`) y kárdex colapsable agrupado por periodos/semestres.
     - *Scheduler*: Generador de horarios con algoritmo de backtracking, selector de materias pendientes agrupadas por semestre, filtros de turno/hora y **visualizador semanal por bloques de tiempo** (`ScheduleCard`) con *tooltips* detallados y conmutador a tabla tradicional.
     - *Guardados*: Gestión de horarios favoritos.
     - *Sincronización SAES*: Wizard de vinculación con resolución de Captcha.

2. **Backend API (`backend/`)**:
   - **Stack**: FastAPI (Python 3.12+ / 3.14), SQLAlchemy asíncrono con SQLite / PostgreSQL, Pydantic v2, Uvicorn, JWT + Refresh Tokens, Cifrado AES para credenciales SAES.
   - **Servicios clave**:
     - `dashboard_service.py`: Cálculo de métricas, promedios, detección de carreras (`ESCOM` y `ESIATEC`), conteo y reglas de acreditación de optativas por semestre (Plan 2023 de ESIATEC y ESCOM).
     - `schedule_service.py`: Algoritmo de generación de horarios y ponderación de horas libres.
     - `saes_service.py` & `saes_client.py`: Orquestación de sincronización y cliente HTTP con `saes-api`.

3. **SAES Scraper Microservicio (`saes-api/`)**:
   - **Stack**: Node.js, Express, Axios, JSDOM.
   - **Capacidades**:
     - Manejo multi-plantel (`escom`, `esiatec`) mediante cabecera `X-SAES-School` y `AsyncLocalStorage`.
     - Scraping dinámico de Kárdex, Mapa Curricular (Plan 2023 de 10 semestres para Arquitectura/Ingeniería Civil), Horarios y Ocupabilidad de grupos.

---

## Planteles Soportados

- **ESCOM** (`https://www.saes.escom.ipn.mx`):
  - Carreras: *Sistemas Computacionales*, *Ciencia de Datos*, *Inteligencia Artificial*.
- **ESIATEC** (`https://www.saes.esiatec.ipn.mx`):
  - Carreras: *Ingeniero Arquitecto*, *Ingeniero Civil*.
  - Plan de Estudios Vigente: **Plan 2023** (10 semestres, 66 unidades de aprendizaje, exclusión de Servicio Social como materia presencial).

---

## Ejecución en Desarrollo

```bash
# 1. Microservicio SAES API (Puerto 5000)
cd saes-api && npm start

# 2. Backend FastAPI (Puerto 8000)
cd backend && uv run uvicorn app.main:app --reload --port 8000

# 3. Frontend React (Puerto 5173)
cd frontend && npm run dev
```

---

## Convenciones

- **Idioma**: Todas las interfaces de usuario, comentarios, esquemas y mensajes de error están en **Español (México)**.
- **Seguridad**: Las contraseñas y sesiones del SAES se almacenan cifradas con AES-256 en la base de datos local del usuario y nunca se exponen al cliente.
