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