# Plan de Implementación — api_gateway (API Gateway)

> Referencia única para el trabajo por fases. Al terminar cada fase, taggear con semver
> (`v1.0.0`, `v1.1.0`, …). No pushear rama ni tag sin aprobación explícita del usuario
> (ver `.agents/rules/versionado-fases.md`).

---

## Fase 1 — Andamiaje ✅ completada

Crear la base de reglas, skills y documentación del repo, heredada de
`api_normalizacion_afiliados` y `api_usuario-roles`, adaptada a un API Gateway.

### Entregables
- [x] `AGENTS.md` adaptado (arquitectura gateway, comandos, convenciones, git, anti-alucinación)
- [x] `.agents/rules/` — `flujo-git.md`, `Reglas-anti-alucinacion.md`, `reglas-solid.md`
      (recortada a gateway), `versionado-fases.md`, `apa-software.md`, `apa-formato.md`,
      `auditoria-documentacion.md` (adaptadas)
- [x] `.agents/skills/` — `proxy-gateway` (nuevo, 6 pasos), `estado-actual-proyecto`,
      `vitacora-agentica`, `apa-software-doc`, `rest-api-design` (adaptado a gateway)
- [x] `.claude/skills/rest-api-design` → symlink a `.agents/skills/rest-api-design`
- [x] `docs/` — `plan_implementacion.md`, `estado_actual_proyecto.md`, `vitacora_agentica.md`
- [x] `.gitignore`

### Notas
- Se omitió el skill `pdf-to-markdown` (no aplica a esta API).
- La regla `instructions.md` de Obsidian de `api_normalizacion_afiliados` no aplica.

---

## Fase 2 — Gateway local (FastAPI + httpx) ✅ completada

Crear el código del proxy reverso en `:8000` ruteando a los microservicios locales.

### Entregables
- [x] `app/core/config.py` — pydantic-settings (`AUTH_SERVICE_URL`, `AFILIADOS_SERVICE_URL`, `DEBUG`, `CORS_ORIGINS`)
- [x] `app/core/routing.py` — tabla de ruteo: prefijo → (URL, timeout, requiere_autorización)
- [x] `app/infrastructure/http_client.py` — pool de `httpx.AsyncClient` (uno por servicio, transport inyectable)
- [x] `app/presentation/proxy_handler.py` — reenvío streaming (headers sin hop-by-hop, passthrough de `Authorization`)
- [x] `app/presentation/handlers.py` — errores de upstream: 502 servicio no disponible / 504 timeout
- [x] `app/presentation/health.py` / `dashboard.py` — `GET /` y `GET /dashboard`
- [x] `app/main.py` — lifespan (pool HTTP), CORS, routers propios + catch-alls por prefijo
- [x] `app/requirements.txt` (fastapi, uvicorn, httpx, pydantic-settings) + `pyproject.toml` (ruff/black/pytest)
- [x] `.env.example` + `.env`
- [x] `tests/` con `httpx.MockTransport` (12 tests: ruteo, passthrough de auth, timeouts/502/504)

### Verificación
- Checklist en verde: `ruff check .` · `black --check .` · `pytest` (12 passed).
- Smoke test real: health OK, dashboard con 5 servicios y estado "no disponible",
  proxy a servicio caído → 502.
- ⬜ Pendiente: end-to-end completo con los 3 servicios locales levantados
  (`POST /usuarios/` → `POST /auth/login` → `GET /auth/me` → `GET /afiliados/` → `PATCH /afiliados/{id}`).

---

## Fase 3 — Docker Compose ✅ completada

Orquestar gateway + auth + afiliados + PostgreSQL desde `docker/`.

### Entregables
- [x] `docker/docker-compose.yml` — 4 servicios (postgres, auth_service, afiliados_service, api_gateway)
- [x] Dockerfiles por servicio — en cada repo hermano (`Dockerfile` + `docker-entrypoint.sh`:
      espera DB → `alembic upgrade head` → seed → uvicorn) y `docker/gateway/Dockerfile`
- [x] `docker/init-db.sh` — crea `auth_db` y `afiliados_db` en un solo Postgres
- [x] Microservicios como **submódulos git** anclados a `main` en `docker/auth_service/` y `docker/afiliados_service/`
- [x] Healthchecks por servicio; URLs por hostname de red (`http://auth_service:8001`, `http://afiliados_service:8002`)

### Verificación
- `docker compose up -d --build` → 4 contenedores healthy. ✅
- Flujo end-to-end por `http://localhost:8000`: registro → login → `/auth/me` → crear/listar/PATCH afiliado. ✅
- `docker compose down`. ✅

### Notas
- Los repos hermanos fueron tocados (Dockerfile/entrypoint) y pusheados a `main` con OK del usuario.
- El puerto 5432 no se publica al host (queda interno; el local estaba ocupado).

---

## Decisiones pendientes

| # | Pregunta | Estado |
|---|---|---|
| 1 | Nombre del repo: `api_gateway` | ✅ Resuelto |
| 2 | ¿Git init con `main` + `develop` como los hermanos? | ✅ Resuelto (en uso: `develop` + ramas feature) |
| 3 | ¿Copiar los microservicios a `docker/` o usar submódulos? | ✅ Resuelto: submódulos anclados a `main` |