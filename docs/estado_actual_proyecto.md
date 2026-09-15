# Estado Actual del Proyecto

> Última actualización: 2026-09-15
> Este archivo es una FOTO del presente, no un historial. Para el historial de cambios ver `vitacora_agentica.md`.
> El agente debe leer este archivo completo al iniciar cualquier tarea sobre el proyecto.

## 1. Resumen del proyecto

API Gateway en Python/FastAPI (`:8000`) que actúa como punto de entrada único del
ecosistema: rutea el tráfico HTTP hacia el Auth Service (`:8001`) y la Afiliados API
(`:8002`) con reenvío streaming, sin lógica de negocio propia.

## 2. Arquitectura

- Gateway liviana: **sin dominio ni casos de uso**. Passthrough de autorización
  (los microservicios validan JWT).
- Ruteo data-driven en `app/core/routing.py` (prefijo → servicio upstream); el proxy
  reenvía el path literal (no reescribe).
- Transporte con `httpx.AsyncClient` (pool por servicio, timeouts), creado en el lifespan.
- Capas: `app/core/` (config + ruteo), `app/infrastructure/` (cliente HTTP),
  `app/presentation/` (proxy handler, dashboard, health, handlers de error).

## 3. Entidades / Modelos de dominio

- Ninguna. La gateway no contiene dominio.

## 4. Casos de uso / Servicios implementados

- Ninguno propio. Reenvía los endpoints de los microservicios (ver sección 5).

## 5. Endpoints / Interfaces expuestas

| Método | Ruta | Descripción | Estado |
|---|---|---|---|
| * | `/auth/*` | → Auth Service :8001 (login, me) | ✅ Verificado |
| * | `/usuarios/*` | → Auth Service :8001 | ✅ Verificado |
| * | `/roles/*` | → Auth Service :8001 | ✅ Verificado |
| * | `/afiliados/*` | → Afiliados API :8002 | ✅ Verificado |
| * | `/sync/*` | → Afiliados API :8002 (streaming) | ✅ Verificado |
| GET | `/` | Health propio del gateway | ✅ Verificado |
| GET | `/dashboard` | Estado de los upstreams | ✅ Verificado |

Leyenda: ✅ verificado | 🟡 parcial | ⏳ en proceso

## 6. Infraestructura / Integraciones

- Variables de entorno (`app/core/config.py`): `AUTH_SERVICE_URL`
  (default `http://localhost:8001`), `AFILIADOS_SERVICE_URL` (default
  `http://localhost:8002`), `DEBUG`, `CORS_ORIGINS`.
- En Docker se inyectan los hostnames del docker-compose.
- Dependencias: `app/requirements.txt` (fastapi, uvicorn, httpx, pydantic-settings) +
  `app/requirements-dev.txt` (pytest, pytest-asyncio, ruff, black).
- Tests con `httpx.MockTransport` (sin servicios reales): 12 casos (ruteo, passthrough
  de headers, status/body de errores de negocio, 502/504).

## 7. Pendientes / TODO conocidos

- [x] Código de la gateway (Fase 2): core, infraestructura, presentación, main.
- [x] `app/requirements.txt`, `pyproject.toml`, `.env.example`, `.env`.
- [x] Tests con `httpx.MockTransport` (12 verdes).
- [ ] Verificación end-to-end con los microservicios reales levantados.
- [ ] Docker Compose (Fase 3).
- [x] Confirmar nombre del repo: `api_gateway`.

## 8. Decisiones y convenciones vigentes

- Respetar `AGENTS.md`: capas `core → infrastructure → presentation`, ruteo como dato,
  streaming sin buffers, passthrough de `Authorization`, errores de negocio sin reinterpretar.
- La fuente de verdad de los contratos son los repos de los microservicios
  (`api_usuario-roles`, `api_normalizacion_afiliados`).
- Reglas y skills heredados y adaptados desde `api_normalizacion_afiliados`.