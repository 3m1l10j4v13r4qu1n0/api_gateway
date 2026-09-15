# Vitácora Agéntica

> Historial cronológico y append-only. NUNCA se borra ni se reescribe una entrada pasada.
> Cada entrada corresponde a una sesión/tarea significativa de trabajo del agente sobre el proyecto.
> Cuando este archivo crezca demasiado, archivar entradas viejas en `vitacora_YYYY-QX.md` y dejar acá solo un índice + las últimas entradas.

---

## 2026-09-15 — Andamiaje de reglas, skills y documentación de la gateway

**Qué se hizo:** se creó la base del repositorio de la API Gateway (FastAPI):
`AGENTS.md` adaptado (arquitectura, comandos, convenciones de git/anti-alucinación), reglas
en `.agents/rules/` y skills en `.agents/skills/` copiados/adaptados de
`api_normalizacion_afiliados` y `api_usuario-roles`, más `docs/` con el plan por fases, el
estado actual del proyecto y la vitácora, y `.gitignore`.

**Decisiones de arquitectura:** la gateway es un punto de entrada liviano sin dominio ni
casos de uso; ruteo data-driven en `app/core/routing.py`; passthrough de autorización
(validan los microservicios); transporte con `httpx` streaming. Se creó el skill
`proxy-gateway` (6 pasos) en lugar de adaptar `di-architect-scaffold`, que es específico de
Clean Architecture/UCs. Se omitió `pdf-to-markdown` y la regla de Obsidian
(`instructions.md`). `.claude/skills/rest-api-design` queda como symlink a `.agents/skills/`.

**Archivos/módulos tocados:**
- `AGENTS.md` — base de reglas de la gateway (nuevo, adaptado)
- `.agents/rules/versionado-fases.md`, `auditoria-documentacion.md`, `reglas-solid.md` — adaptadas a gateway
- `.agents/rules/flujo-git.md`, `Reglas-anti-alucinacion.md`, `apa-software.md`, `apa-formato.md` — copias
- `.agents/skills/proxy-gateway/SKILL.md` — nuevo
- `.agents/skills/rest-api-design/SKILL.md` — referencia a gateway (sección "Applying to FastAPI")
- `.agents/skills/estado-actual-proyecto/`, `vitacora-agentica/`, `apa-software-doc/` — copias
- `.claude/skills/rest-api-design` — symlink
- `docs/plan_implementacion.md`, `docs/estado_actual_proyecto.md`, `docs/vitacora_agentica.md` — nuevos
- `.gitignore` — nuevo

**Estado resultante:** repositorio en andamiaje (sin código de la gateway todavía). Queda
pendiente la Fase 2 (gateway local FastAPI + httpx), el git init con rama `develop` y la
Fase 3 (Docker Compose).

---

## 2026-09-15 — Renombrado del repositorio a api_gateway

**Qué se hizo:** se renombró la carpeta del repo de `api_gatewey` a `api_gateway` y se
actualizaron las referencias en AGENTS.md, skills y docs.

**Decisiones de arquitectura:** el nombre definitivo del repositorio es `api_gateway`
(resuelto).

**Archivos/módulos tocados:**
- Renombrado de directorio: `api_gatewey` → `api_gateway`
- `.agents/skills/rest-api-design/SKILL.md`, `references/fastapi-conventions.md` — referencia al nombre
- `docs/plan_implementacion.md`, `docs/estado_actual_proyecto.md` — nombre definitivo

**Estado resultante:** API Gateway con nombre definitivo `api_gateway`; pendientes: Fase 2
(código de la gateway), git init con `develop`, Fase 3 (Docker Compose).

---

## 2026-09-15 — Fase 2: gateway local FastAPI + httpx

**Qué se hizo:** se implementó el código del API Gateway (proxy reverso) siguiendo el
skill `proxy-gateway` y los patrones de `api_normalizacion_afiliados`.

**Decisiones de arquitectura:**
- Ruteo data-driven en `app/core/routing.py` (prefijo → Route) con `find_route()`; sin
  `if/elif` de paths. 5 prefijos activos.
- Clientes `httpx.AsyncClient` en un pool (`HttpClientPool`) creado en el lifespan y
  cerrado al apagar; `register()` acepta transport inyectable para tests con
  `httpx.MockTransport`.
- Proxy streaming: headers sin hop-by-hop (host, connection, content-length, etc.),
  reenvío de `Authorization` y headers custom, body por iterador de bytes, y el
  status/headers/body del upstream se devuelven tal cual (passthrough de errores de negocio).
- Errores de upstream: 502 `servicio no disponible` (ConnectError) y 504 `timeout` — ambos
  en la única capa de error (proxy_handler).
- `CORS_ORIGINS` como lista JSON para pydantic-settings v2. `model_config =
  SettingsConfigDict(...)` moderno (evita deprecación de `class Config`).

**Archivos/módulos tocados:**
- `app/core/config.py`, `app/core/routing.py` — config y tabla de ruteo
- `app/infrastructure/http_client.py` — pool de clientes
- `app/presentation/proxy_handler.py`, `handlers.py`, `health.py`, `dashboard.py`
- `app/main.py` — lifespan, CORS, routers propios + catch-alls por prefijo
- `app/requirements.txt`, `app/requirements-dev.txt`, `pyproject.toml`
- `.env.example`, `.env`
- `tests/` — conftest, helpers, mock_upstreams, test_gateway (12 tests)

**Estado resultante:** Fase 2 completa. Checklist en verde: `ruff check .`, `black --check .`,
`pytest` (12 passed). Smoke test real: health OK, dashboard muestra 5 servicios/estado,
proxy a servicio caído devuelve 502. Verificación end-to-end con microservicios reales
todavía pendiente (no estaban corriendo). Sigue Fase 3 (Docker Compose).

---

## 2026-09-15 — Fase 3: Docker Compose del ecosistema

**Qué se hizo:** se orquestó el ecosistema completo en contenedores (postgres + auth_service +
afiliados_service + api_gateway) desde `docker/`, usando los microservicios como **submódulos git**
anclados a `main`.

**Decisiones de arquitectura:**
- **Submódulos** en vez de copias: `docker/auth_service` → `api_usuario-roles`, `docker/afiliados_service`
  → `api_normalizacion_afiliados`, ambos con `branch = main` en `.gitmodules`.
  Fueron anclados al `main` remoto post-contenedorización (SHA `0022860` y `6defbff`).
- **Dockerfiles en cada repo hermano** (no en la gateway): cada microservicio ganó `Dockerfile` +
  `docker-entrypoint.sh` + `.dockerignore` en su propio repo (flujo feature → develop → main, pusheados
  a origin con OK del usuario).
- **Entrypoint único** en cada microservicio: espera a la DB (loop hasta 30×2s), `alembic upgrade head`,
  `python -m app.infrastructure.database.seed_runner` y luego `uvicorn` (8001 auth / 8002 afiliados).
- **Un solo Postgres compartido** (`postgres:16-alpine`) con `docker/init-db.sh` montado en
  `/docker-entrypoint-initdb.d/` que crea `auth_db` y `afiliados_db`. No se publica el 5432 al host
  (los servicios se hablan por la red interna; el 5432 local estaba ocupado).
- **Dockerfile del gateway** en `docker/gateway/Dockerfile` con build context `..` (raíz del repo,
  copia `app/` nada más). `.dockerignore` en raíz excluye venv, docs, tests y los submódulos.
- **URLs por hostname** inyectadas al gateway: `AUTH_SERVICE_URL=http://auth_service:8001`,
  `AFILIADOS_SERVICE_URL=http://afiliados_service:8002`. Healthchecks por servicio:
  postgres con `pg_isready`, los tres FastAPI con `urlopen` al `/`.
- `docker compose down` al final (sin borrar el volumen `postgres_data`).

**Archivos/módulos tocados:**
- `docker/docker-compose.yml` — 4 servicios, healthchecks, dependencias con `condition: service_healthy`
- `docker/gateway/Dockerfile` — imagen del gateway (python:3.13-slim + uvicorn)
- `docker/init-db.sh` — crea `auth_db` y `afiliados_db`
- `.gitmodules` + `docker/auth_service/` + `docker/afiliados_service/` — submódulos
- `.dockerignore` — context de build del gateway
- Repos hermanos: `Dockerfile`, `docker-entrypoint.sh`, `.dockerignore` (feature → develop → main)

**Estado resultante:** Fase 3 completa. `docker compose up -d --build` → 4 contenedores
healthy. End-to-end verificado por `http://localhost:8000`: registro de usuario → login → `/auth/me`
→ crear afiliado → listar → PATCH (200). El 500 inicial de afiliados fue por payload incompleto
(`numero_legajo` NOT NULL), no por la gateway. Verificación y `docker compose down` OK.