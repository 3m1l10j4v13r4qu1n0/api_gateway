# AGENTS.md

API Gateway en Python/FastAPI que enruta el tráfico HTTP del ecosistema hacia los
microservicios de autenticación y de afiliados. Responder siempre en español (latino).

## Arquitectura

```text
Frontend (React)
   │ HTTP
   ▼
API Gateway  :8000   (este repo)
   │
   ├── /auth/*, /usuarios/*, /roles/*   →  Auth Service     :8001  (repositorio api_usuario-roles)
   └── /afiliados/*, /sync/*            →  Afiliados API    :8002  (repositorio api_normalizacion_afiliados)
```

La gateway es un **punto de entrada único y liviano**: no contiene dominio, casos de
uso ni lógica de negocio de los servicios. Toda la validación de JWT la hacen los
microservicios (passthrough de autorización). Capas:

- `app/core/` — `config.py` (pydantic-settings) y `routing.py` (tabla de ruteo):
  prefijo → servicio upstream (URL, timeout, requiere autorización).
- `app/presentation/` — routers del gateway (`proxy_handler.py`, dashboard, health) y
  `handlers.py` (mapeo de errores de proxy → HTTP).
- `app/infrastructure/` — cliente `httpx.AsyncClient` (pool por servicio, timeouts).

La tabla de ruteo **no reescribe paths**: reenvía el request literal hacia el
servicio (`/auth/me` → `AUTH_SERVICE_URL/auth/me`).

## Comandos

- Todo se ejecuta **desde la raíz del repo** (los imports son `app.*`).
- Levantar gateway: `uvicorn app.main:app --reload --port 8000`
- Tests: `pytest` desde la raíz.
- Lint y formato antes de cada commit:
  - `venv/bin/ruff check .`
  - `venv/bin/black --check .`
  - `venv/bin/python -m pytest -q`

## Setup / gotchas

- `requirements.txt` está en **`app/requirements.txt`** (no en la raíz).
- Python fijado a **3.13.5** (`app/.python-version`). No hay venv commitado.
- Config lee variables de entorno via pydantic-settings desde `.env`
  (`app/core/config.py`). Vars:
  - `AUTH_SERVICE_URL` (default `http://localhost:8001`)
  - `AFILIADOS_SERVICE_URL` (default `http://localhost:8002`)
  - `DEBUG` (default `False`)
  - `CORS_ORIGINS` (default `["http://localhost:5173","http://localhost:3000"]`)
- En Docker las URLs se inyectan con los hostnames del docker-compose
  (`http://auth_service:8001`, `http://afiliados_service:8002`).
- Si un upstream está caído, el proxy responde `502` con payload
  `{"error": "servicio no disponible: <nombre>"}`.

## Convenciones

- **Un archivo = una responsabilidad** (SRP): no mezclar ruteo, transporte y
  presentación en el mismo módulo.
- **Tabla de ruteo como dato**: agregar un servicio nuevo es agregar una entrada en
  `app/core/routing.py`; no escribir `if/elif` de paths en el handler.
- **Streaming**: el proxy reenvía request/response con streaming (`httpx` + iterador
  de bytes de Starlette), sin cargar cuerpos en memoria (crítico para `/sync/*`).
- **Headers**: reenviar `Authorization` y el resto de headers relevantes tal cual
  (excepto hop-by-hop: `host`, `connection`, `content-length`).
- Errores de negocio de los microservicios no se reinterpretan: se devuelven con su
  status code y body originales.
- Inyección de dependencias: el cliente HTTP se crea en el lifespan de la app y se
  pasa a los handlers, nunca se instancia adentro del router.

## Flujo de implementación (reglas duras)

### Al recibir una tarea

1. **Leer `docs/estado_actual_proyecto.md`** completo antes de tocar código.
2. **Verificar** que la funcionalidad no exista ya (leer código relevante, no asumir).
3. **Planificar** en pasos chicos (un servicio nuevo, un componente, o un endpoint por vez).
4. **Preguntar** ante ambigüedad; no decidir por cuenta propia.

### Al escribir código

- Respetar las capas y la tabla de ruteo (ver "Arquitectura").
- **Releer después de escribir**: verificar que el archivo quedó como se planeó.
- **Trabajo en pasos chicos**: mostrar qué se hizo y qué falta antes de seguir.

### Al commitear

- **Conventional Commits en español**, scope en minúscula:
  - `feat(routing): se agrega ruteo hacia el servicio de X`
  - `fix(proxy): se corrige reenvio de headers de autorizacion`
  - `test(proxy): se agrega test del proxy con upstream simulado`
- **Un tema por commit** (commits atómicos). Si necesita "y", son dos commits.
- **Prohibido** mensajes vagos ("cambios", "update", "cosas varias").
- **Checklist** antes de commit:
  ```bash
  venv/bin/ruff check .
  venv/bin/black --check .
  venv/bin/python -m pytest -q
  ```

### Flujo de ramas y merges (regla dura: `.agents/rules/flujo-git.md`)

- **Prohibido** trabajar directo sobre `main` o `develop`.
- Crear `feature/<tema>` o `fix/<tema>` **siempre desde `develop`**.
- Una rama = una tarea/HU coherente. Mantener ramas cortas.
- **Antes de mergear a develop**:
  1. Integrar `origin/develop` dentro de la rama feature (`git fetch` + `git merge origin/develop`) y resolver conflictos ahí.
  2. Checklist en verde: `ruff check` · `black --check` · `pytest`.
  3. Solo entonces mergear a develop.
- **Push/merge SOLO con aprobación explícita del usuario**.

### Versionado por fases (regla dura: `.agents/rules/versionado-fases.md`)

- **Tag anotado** al cerrar cada fase, **no** push por ahora.
- Versión semver: cada fase incrementa la versión menor (`v1.0.0` → `v1.1.0` → …).
- **Nunca** push de rama o tag sin aprobación explícita del usuario.
- Si una fase se corrige después del tag, versionar con patch (`vX.Y.Z+1`).

## Reglas de verificación y anti-alucinación (`.agents/rules/Reglas-anti-alucinacion.md`)

- **Verificar antes de afirmar**: leer el archivo/símbolo en la sesión actual, no asumir de memoria.
- **No inventar superficie de código**: nombres de clases, rutas, endpoints — solo si se vieron en código real o se marcan como "nuevo, a crear".
- **No inventar dependencias**: solo citar librerías verificadas en `app/requirements.txt`.
- **Ambigüedad → pregunta**: no decidir por cuenta propia.
- **Confirmación explícita en cambios transversales**: cambios que toquen más de un servicio/upstream requieren OK del usuario.
- **Reporte de cada paso**: 1) qué se verificó, 2) qué se propone/cambió, 3) qué queda pendiente.

## Fuente de verdad

- `docs/` es la única fuente de verdad para requerimientos, especificaciones y reglas de negocio.
- No inventar endpoints, campos, puertos ni contratos de los microservicios: la fuente es cada repo (`api_usuario-roles`, `api_normalizacion_afiliados`).
- Si el código real contradice `docs/estado_actual_proyecto.md`, avisar antes de asumir cuál es la fuente.

## Notas

- El skill `proxy-gateway` en `.agents/skills/` define el flujo de 6 pasos para agregar
  rutas/servicios a esta gateway.
- El skill `rest-api-design` tiene guías y templates para diseñar endpoints REST (incluye
  `references/fastapi-conventions.md`). El template `endpoint_fastapi.py` es útil para
  endpoints propios de la gateway (dashboard, health).
- Reglas copiadas y adaptadas del repositorio `api_normalizacion_afiliados`: flujo de git,
  versionado por fases, anti-alucinación, SOLID (recortada a gateway) y APA.

## Rutas expuestas por la gateway

| Prefijo | Servicio upstream | Puerto |
|---|---|---|
| `/auth`, `/usuarios`, `/roles` | Auth Service (`api_usuario-roles`) | 8001 |
| `/afiliados`, `/sync` | Afiliados API (`api_normalizacion_afiliados`) | 8002 |
| `/`, `/dashboard` | Propios del gateway | 8000 |

## Estado del proyecto

- ⏳ En andamiaje: repositorio sin código de la gateway todavía.
- `docs/plan_implementacion.md` define el plan por fases (gateway local → docker compose).
- `docs/estado_actual_proyecto.md` y `docs/vitacora_agentica.md` son la memoria del proyecto.

## Memoria del proyecto (docs/estado_actual_proyecto.md y docs/vitacora_agentica.md)

- Antes de tocar código, leer `docs/estado_actual_proyecto.md` completo para tener el contexto actual del proyecto.
- Al terminar una implementación, eliminación o edición relevante (nueva ruta, servicio upstream, refactor del proxy, dependencia core):
  1. Actualizar la sección correspondiente de `docs/estado_actual_proyecto.md` (editar in-place, no reescribir todo el archivo).
  2. Agregar una entrada nueva al final de `docs/vitacora_agentica.md` con: fecha, qué se hizo, decisiones tomadas, archivos tocados y estado resultante. Nunca editar entradas previas de la vitácora.
- No generar entradas de vitácora por cambios triviales (typos, formateo, renames cosméticos).
- Si el código real contradice lo que dice `estado_actual_proyecto.md`, avisar antes de asumir cuál es la fuente de verdad.