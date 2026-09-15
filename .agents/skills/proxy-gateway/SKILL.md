---
name: proxy-gateway
description: Estandarizar la implementación de nuevas rutas, servicios upstream y componentes del proxy reverso del API Gateway, garantizando que el ruteo sea data-driven (tabla de ruteo), el transporte use streaming con httpx y la inyección de dependencias viva en el lifespan. Usar cuando el usuario pida agregar un servicio nuevo, un prefijo, un endpoint propio (dashboard/health) o modificar el comportamiento del proxy en la API Gateway.
disable-model-invocation: true
---

# Proxy Gateway — API Gateway

Skill para agregar rutas, servicios upstream y componentes propios del **API Gateway**
(FastAPI + httpx, proxy reverso). La gateway es un punto de entrada liviano: **no tiene
dominio ni casos de uso**. El ruteo es **data-driven** y el reenvío es **streaming**.

## Stack tecnológico obligatorio

- Lenguaje: **Python 3.13.5** (ver `app/.python-version`)
- Framework Web: FastAPI + Uvicorn
- Cliente HTTP asíncrono: `httpx` (pool por servicio, streaming)
- Config: pydantic-settings desde `.env` (`app/core/config.py`)
- Testing: Pytest (upstream simulado con `httpx.MockTransport`, sin servicios reales)
- Linter/formatter: `ruff` y `black` (ver comandos en `AGENTS.md`)

## 📜 Reglas Inquebrantables del Proyecto

1. **Punto único de entrada**: el gateway expone `:8000` y rutea hacia auth (`:8001`) y
   afiliados (`:8002`). No agrega lógica de negocio ni valida JWT (passthrough).
2. **Tabla de ruteo como dato**: el destino de cada prefijo vive en `app/core/routing.py`.
   Agregar un servicio = agregar una entrada; **prohibido** `if/elif` sobre paths en handlers.
3. **No reescribir paths**: el request se reenvía literal (`/auth/me` → `AUTH_SERVICE_URL/auth/me`),
   solo cambia el host.
4. **Streaming**: request y response se reenvían con iteradores de bytes de Starlette,
   sin cargar cuerpos en memoria (crítico para `/sync/*`).
5. **Headers**: reenviar `Authorization` y headers relevantes tal cual; **excluir**
   hop-by-hop (`host`, `connection`, `content-length`).
6. **Inyección de dependencias**: el cliente `httpx.AsyncClient` se crea en el lifespan
   de la app y se pasa a los handlers; nunca se instancia dentro de un router.
7. **Errores de upstream**: un servicio caído → `502 {"error": "servicio no disponible: <nombre>"}`
   (único lugar: `app/presentation/handlers.py`). Los errores de negocio de los
   microservicios se devuelven con su status code y body originales.

## 🔄 Flujo de trabajo estándar (6 pasos)

Cada vez que se solicite agregar un servicio/ruuta o componente, seguir este orden y
**esperar confirmación explícita ("Continuar") antes de avanzar al siguiente paso**.

### Paso 1: Configuración (core)
**Ubicación**: `app/core/config.py` · `app/core/routing.py`
1. Si es un servicio nuevo, agregar la variable de entorno en `config.py` (ej. `X_SERVICE_URL`)
   con default local y usa el hostname de network en Docker.
2. Agregar la entrada en la tabla `routing.py`: `prefijo → (URL, timeout, requiere_autorizacion)`.
   No tocar el handler todavía.

### Paso 2: Cliente HTTP (infraestructura)
**Ubicación**: `app/infrastructure/http_client.py`
1. Agregar el `httpx.AsyncClient` del servicio al pool (base URL + `timeout` configurado),
   o crear el pool si no existe.
2. El pool se expone por inyección (función `get_*_client`) y se instancia en el lifespan.

### Paso 3: Handler del proxy (presentación)
**Ubicación**: `app/presentation/proxy_handler.py`
1. Implementar/aplicar el handler genérico de streaming: método + path + query + headers
   (sin hop-by-hop, con `Authorization`) + body stream a `request()` de httpx.
2. Devolver `Response` de Starlette con status/headers/body del upstream, sin reinterpretar.

### Paso 4: Presentación extra (dashboard/health)
**Ubicación**: `app/presentation/`
1. Si hace falta, agregar/actualizar el endpoint propio del servicio (dashboard con estado
   de cada upstream, health) reutilizando el pattern `endpoint_fastapi.py` de
   `.agents/skills/rest-api-design/templates/`.

### Paso 5: Pruebas
**Ubicación**: `tests/`
1. Simular el upstream con `httpx.MockTransport` (sin levantar los microservicios reales).
2. Probar: ruteo correcto, passthrough de `Authorization`, exclusión de hop-by-hop,
   timeout/502 ante upstream caído, y que los errores de negocio pasan con su status/body.
3. Correr desde la raíz del repo: `venv/bin/python -m pytest -q`.

### Paso 6: Memoria y cierre
1. Actualizar la tabla de ruteo/Rutas en `docs/estado_actual_proyecto.md` (sección
   correspondiente, in-place).
2. Agregar entrada nueva en `docs/vitacora_agentica.md` (append-only).

## 📋 Esquema de capas

```text
app/
├── core/
│   ├── config.py                # pydantic-settings: *SERVICE_URL, DEBUG, CORS_ORIGINS
│   └── routing.py               # tabla: prefijo → (url, timeout, requiere_autorizacion)
├── infrastructure/
│   └── http_client.py           # pool de httpx.AsyncClient (uno por servicio)
└── presentation/
    ├── proxy_handler.py         # handler streaming (request/response sin buffers)
    ├── dashboard.py             # estado de los upstreams (HTML simple)
    ├── health.py                # GET / propio del gateway
    └── handlers.py              # 502 servicio no disponible (único lugar)
```

## 🌱 Cultura de Desarrollo de Software

Mantener código limpio, mantenible y con hábitos profesionales.

### Principios
- **Clean Code**: nombres descriptivos, una responsabilidad por función, legibilidad.
- **SOLID**: SRP, Open/Closed, Liskov, Interface Segregation, Dependency Inversion
  (ver `.agents/rules/reglas-solid.md`, adaptada a gateway).
- **KISS / DRY / YAGNI**: solución más simple, sin duplicar lógica (el reenvío se hace
  una sola vez en el proxy handler, configurado por la tabla).

### Estrategia de ramas
Prohibido trabajar directamente sobre `main` o `develop` (ver `.agents/rules/flujo-git.md`):
`develop` → `feature/...`, `fix/...`, `docs/...`.

### Convención de commits
**Conventional Commits en español**, scope en minúscula (ver `AGENTS.md`):
`feat(routing)`, `fix(proxy)`, `test(proxy)`, `chore(cfg)`, `docs(routing)`.

### Calidad del código
Antes de commitear: `venv/bin/ruff check .` · `venv/bin/black --check .` ·
`venv/bin/python -m pytest -q` (desde la raíz).

### Prohibido
- Trabajar sobre `main`/`develop` directamente.
- Commits vagos ("cambios", "arreglos", "update").
- `if/elif` de paths fuera de la tabla de ruteo.
- Reescribir paths al reenviar (salvo decisión explícita).
- Cargar cuerpos en memoria en el proxy (rompe streaming de `/sync/*`).
- Revalidar JWT o reinterpretar errores de negocio de los microservicios (passthrough).

## 🎯 Objetivo

Construir un gateway mantenible, desacoplado y testeable: ruteo como dato, transporte
streaming con httpx e inyección de dependencias en el lifespan.