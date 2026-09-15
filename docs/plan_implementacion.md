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

## Fase 2 — Gateway local (FastAPI + httpx)

Crear el código del proxy reverso en `:8000` ruteando a los microservicios locales.

### Entregables
- [ ] `app/core/config.py` — pydantic-settings (`AUTH_SERVICE_URL`, `AFILIADOS_SERVICE_URL`, `DEBUG`, `CORS_ORIGINS`)
- [ ] `app/core/routing.py` — tabla de ruteo: prefijo → (URL, timeout, requiere_autorización)
- [ ] `app/infrastructure/http_client.py` — pool de `httpx.AsyncClient` (uno por servicio)
- [ ] `app/presentation/proxy_handler.py` — reenvío streaming (headers sin hop-by-hop, passthrough de `Authorization`)
- [ ] `app/presentation/handlers.py` — `502 {"error": "servicio no disponible: <nombre>"}`
- [ ] `app/presentation/health.py` / `dashboard.py` — `GET /` y `GET /dashboard`
- [ ] `app/main.py` — lifespan (cliente HTTP), CORS, routers
- [ ] `app/requirements.txt` (fastapi, uvicorn, httpx, pydantic-settings) + `pyproject.toml` (ruff/black)
- [ ] `.env.example` + `.env`
- [ ] `tests/` con `httpx.MockTransport` (ruteo, passthrough de auth, timeout/502)

### Verificación
- Levantar los 3 servicios locales y probar end-to-end por `:8000`:
  `POST /usuarios/` → `POST /auth/login` → `GET /auth/me` (token) → `GET /afiliados/` → `PATCH /afiliados/{id}`.
- Contra-ruta: `/afiliados` sin token responde (público); `/roles/` sin token responde 401 del auth service.
- Checklist en verde: `ruff check .` · `black --check .` · `pytest`.

---

## Fase 3 — Docker Compose

Orquestar gateway + auth + afiliados + PostgreSQL desde `docker/`.

### Entregables
- [ ] `docker/docker-compose.yml` — 4 servicios (postgres, auth_service, afiliados_service, api_gateway)
- [ ] Dockerfiles por servicio (instalación desde `app/requirements.txt`, `alembic upgrade head` + seed)
- [ ] `docker/init-db.sh` — crear `auth_db` y `afiliados_db` en un solo Postgres
- [ ] Códigos de los microservicios copiados a `docker/auth_service/` y `docker/afiliados_service/`
- [ ] Healthchecks por servicio; URLs por hostname de red (`http://auth_service:8001`, `http://afiliados_service:8002`)

### Verificación
- `docker compose up -d --build` → contenedores healthy.
- Repetir el flujo end-to-end por `http://localhost:8000`.
- `docker compose down`.

---

## Decisiones pendientes

| # | Pregunta | Estado |
|---|---|---|
| 1 | Nombre del repo: `api_gateway` | ✅ Resuelto |
| 2 | ¿Git init con `main` + `develop` como los hermanos? | ⏳ Por confirmar |
| 3 | ¿Copiar los microservicios a `docker/` o usar submódulos? | ⏳ Fase 3 |