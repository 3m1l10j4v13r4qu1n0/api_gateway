# API Gateway

🚪 Punto de entrada único del ecosistema de microservicios  
⚡ FastAPI + Uvicorn  
🔀 Proxy reverso liviano con streaming (httpx)  
🐍 Python 3.13.5  
🗄️ Ruteo data-driven (tabla de prefijos → servicios upstream)

---

## 📌 Descripción general

Este proyecto implementa un **API Gateway** que actúa como puerta de entrada única del
ecosistema: enruta el tráfico HTTP del Frontend (React) hacia los microservicios de
**autenticación** y de **afiliados**, sin contener lógica de negocio propia.

```text
Frontend (React)
   │ HTTP
   ▼
API Gateway  :8000   (este repo)
   │
   ├── /auth/*, /usuarios/*, /roles/*   →  Auth Service     :8001  (api_usuario-roles)
   └── /afiliados/*, /sync/*            →  Afiliados API    :8002  (api_normalizacion_afiliados)
```

La gateway es un **punto de entrada único y liviano**: no contiene dominio, casos de uso
ni lógica de negocio de los servicios. Toda la validación de JWT la hacen los
microservicios (passthrough de autorización).

El proyecto está diseñado como ejercicio práctico de **análisis funcional + desarrollo
backend**, simulando un sistema real de microservicios detras de un gateway.

---

## 🎯 Objetivos del proyecto

- Exponer un único punto de entrada HTTP (`:8000`) para todo el ecosistema
- Enrutar por prefijo hacia el servicio upstream correspondiente sin reescribir paths
- Reenviar requests/responses en **streaming** sin cargar cuerpos en memoria
- Pasar la autorización tal cual a los microservicios (sin reinterpretar JWT)
- Mantener la gateway desacoplada y testeable (ruteo como dato, inyección de dependencias)

---

## 📚 Documentación

La documentación del proyecto se encuentra en `docs/`:

- `estado_actual_proyecto.md` — foto actual del proyecto (fuente de verdad)
- `plan_implementacion.md` — plan por fases (andamiaje → gateway local → docker compose)
- `vitacora_agentica.md` — historial cronológico append-only de decisiones
- `.agents/` — reglas y skills del proyecto (flujo de git, versionado, anti-alucinación)
- `AGENTS.md` — reglas y convenciones del proyecto para agentes

---

## ⚙️ Funcionalidades principales

- Ruteo data-driven: agregar un servicio = agregar una entrada en `app/core/routing.py`
- Proxy streaming con `httpx.AsyncClient` (pool por servicio en el lifespan, timeouts)
- Passthrough de `Authorization` y headers relevantes (sin hop-by-hop)
- Errores de upstream: `502` servicio no disponible / `504` timeout con payload
  `{"error": "servicio no disponible: <nombre>"}`
- Errores de negocio de los microservicios se devuelven con su status y body originales
- `GET /` (health) y `GET /dashboard` (estado de los upstreams), propios del gateway
- DNS de red interna en Docker Compose (`http://auth_service:8001`, `http://afiliados_service:8002`)

---

## 🔌 Rutas expuestas

| Prefijo | Servicio upstream | Puerto | Timeout | Requiere auth |
|---|---|---|---|---|
| `/auth` | Auth Service | 8001 | 10 s | ✅ |
| `/usuarios` | Auth Service | 8001 | 10 s | ✅ |
| `/roles` | Auth Service | 8001 | 10 s | ✅ |
| `/afiliados` | Afiliados API | 8002 | 30 s | ✅ |
| `/sync` | Afiliados API | 8002 | 120 s | ❌ |
| `/` | Health propio del gateway | — | — | — |
| `/dashboard` | Estado de los upstreams | — | — | — |

> La tabla de ruteo **no reescribe paths**: reenvía el request literal hacia el servicio
> (`/auth/me` → `AUTH_SERVICE_URL/auth/me`).

---

## 🏗️ Estructura del Proyecto

```
api_gateway/
│
├── app/
│   ├── main.py
│   │   💬 Punto de entrada de la aplicación (FastAPI, lifespan del pool HTTP)
│   │
│   ├── core/   ⚙️ CONFIGURACIÓN + RUTEO
│   │   ├── config.py
│   │   │   💬 pydantic-settings: AUTH_SERVICE_URL, AFILIADOS_SERVICE_URL, DEBUG, CORS_ORIGINS
│   │   └── routing.py
│   │       💬 Tabla de ruteo: prefijo → (URL, timeout, requiere_autorización)
│   │
│   ├── infrastructure/  🟨 TRANSPORTE
│   │   └── http_client.py
│   │       💬 Pool de httpx.AsyncClient (uno por servicio, transport inyectable para tests)
│   │
│   ├── presentation/  🟦 PRESENTACIÓN (Proxy + propios)
│   │   ├── proxy_handler.py
│   │   │   💬 Reenvío streaming (sin hop-by-hop, Body por iterador, passthrough)
│   │   ├── handlers.py
│   │   │   💬 502 servicio no disponible / 504 timeout (única capa de error de upstream)
│   │   ├── health.py
│   │   │   💬 GET / propio del gateway
│   │   └── dashboard.py
│   │       💬 GET /dashboard con estado de cada upstream
│   │
│   └── requirements.txt
│       💬 fastapi, uvicorn, httpx, pydantic, pydantic-settings, python-dotenv
│
├── docker/  🐳 DOCKER COMPOSE (ecosistema completo)
│   ├── docker-compose.yml
│   ├── init-db.sh             ← crea auth_db y afiliados_db en un solo Postgres
│   ├── gateway/               ← Dockerfile del gateway
│   ├── auth_service/          ← submódulo → api_usuario-roles
│   └── afiliados_service/     ← submódulo → api_normalizacion_afiliados
│
├── tests/  🧪 TESTING
│   └── (12 tests con httpx.MockTransport: ruteo, passthrough de auth, 502/504)
│
├── docs/
│   💬 Memoria del proyecto (estado actual, plan por fases, vitácora)
│
├── AGENTS.md
│   💬 Reglas y convenciones del proyecto para agentes
│
└── .env.example
    💬 Variables de entorno de ejemplo
```

---

## 🧠 Resumen de Arquitectura

```
Frontend (React)
     │  HTTP :8000
     ▼
API Gateway (FastAPI)
  ├── routing.py   ← tabla de ruteo (dato)
  ├── http_client  ← pool httpx (streaming)
  └── proxy_handler ← reenvío literal (headers sin hop-by-hop)
     │
     ├── Auth Service      :8001  (login, usuarios, roles)
     └── Afiliados API     :8002  (afiliados, sync Google Sheets)
```

### Decisiones vigentes

- **Ruteo como dato**: agregar un servicio nuevo = agregar una entrada en `routing.py`;
  nunca `if/elif` de paths en el handler.
- **Streaming**: request y response se reenvían con iteradores de bytes de Starlette, sin
  cargar cuerpos en memoria (crítico para `/sync/*`).
- **Passthrough de autorización**: la gateway reenvía `Authorization` tal cual; los
  microservicios validan el JWT.
- **Config tolerante**: el `Settings` usa `extra="ignore"` para ignorar variables del
  `.env` que pertenecen a otros servicios.

---

## 🚀 Instalación y configuración

### Local

```bash
# Clonar el repo (incluye los submódulos de docker/)
git clone --recurse-submodules git@github.com:usuario/api_gateway.git

# Crear entorno virtual
python -m venv venv

# Linux
source venv/bin/activate

# Instalar dependencias (requirements.txt está dentro de app/)
pip install -r app/requirements.txt

# Configurar variables de entorno
cp .env.example .env

# Levantar la gateway
uvicorn app.main:app --reload --port 8000
```

> La gateway reenvía a `http://localhost:8001` y `http://localhost:8002` por defecto:
> para el ecosistema completo conviene levantar los microservicios o usar Docker Compose.

### Docker Compose (ecosistema completo)

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

Levanta 4 servicios: **postgres** (compartido, crea `auth_db` y `afiliados_db`),
**auth_service** (:8001), **afiliados_service** (:8002) y **api_gateway** (:8000), todos
con healthcheck. Los microservicios se montan como submódulos git anclados a `main` y cada
entrypoint corre `alembic upgrade head` + seed antes de arrancar uvicorn.

> `docker compose` lee las variables del proyecto desde `.env` de la raíz: el archivo
> `docker/.env` es un symlink a `../.env`.

### Google Sheets (endpoints `/sync`)

Para probar `/sync/*` con un spreadsheet real, configurar en `.env`:

| Variable | Descripción |
|---|---|
| `GOOGLE_SHEETS_ID` | ID del Google Sheet a sincronizar |
| `GOOGLE_CREDENTIALS_HOST_PATH` | Ruta en el host del `service_account.json` de la service account |
| `GOOGLE_CREDENTIALS_PATH` | Ruta dentro del contenedor de `afiliados_service` (`.credentials/service_account.json`, relativa a `/app`) |

En Compose el service account se monta con **bind-mount read-only**
(`${GOOGLE_CREDENTIALS_HOST_PATH}:/app/.credentials/service_account.json:ro`) y nunca se
commitea al repositorio (`.credentials/` y `.env` están en `.gitignore`).

---

## 🧪 Testing

```bash
# Tests con upstream simulado (httpx.MockTransport), sin servicios reales — 12 tests
venv/bin/python -m pytest -q

# Lint y formato
venv/bin/ruff check .
venv/bin/black --check .
```

---

## ✅ Estado del proyecto

✔ **Fase 1 — Andamiaje:** COMPLETADA  
Reglas, skills y documentación del repo adaptadas de los microservicios hermanos.

✔ **Fase 2 — Gateway local:** COMPLETADA  
Código FastAPI + httpx: ruteo data-driven (5 prefijos), proxy streaming, dashboard,
health, 12 tests con `httpx.MockTransport`.

✔ **Fase 3 — Docker Compose:** COMPLETADA  
`docker/docker-compose.yml` con 4 servicios healthy, microservicios como submódulos y
flujo end-to-end verificado por `:8000`.

✔ **Corrección Fase 3 — `/sync/*` con credenciales reales:** COMPLETADA  
`POST /sync/sheets/import` (39 procesados/36 válidos), `/sync/sheets/export` (37) y
`/sync/sheets/reimport` (3 pendientes) verificados por la gateway con el service account
montado read-only dentro del compose.

Versión actual: tag **`v1.1.1`**.

📄 Ver detalle en: `docs/estado_actual_proyecto.md` y `docs/plan_implementacion.md`.

---

## 🗺️ Roadmap

- Fase 1: Andamiaje ✔
- Fase 2: Gateway local (ruteo + streaming + tests) ✔
- Fase 3: Docker Compose del ecosistema ✔
- Corrección Fase 3: `/sync/*` con credenciales reales de Google en compose ✔
- Futuro (no bloqueante): release `develop → main`, rate limiting, tracing de requests

---

## 🧠 Perfil objetivo

Este proyecto está pensado como material demostrativo para:

- Analista Funcional Jr
- Analista Técnico Funcional
- Primeros roles en proyectos de software administrativo

El foco está puesto en análisis, documentación, trazabilidad y coherencia funcional.

---

## Autor

Emilio Javier Aquino  
Estudiante de Analista de Sistemas

## 📄 Licencia

Proyecto de uso educativo y demostrativo.