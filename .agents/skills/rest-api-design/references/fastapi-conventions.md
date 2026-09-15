# Aplicación de REST design en este proyecto (FastAPI — API Gateway)

> Guía local para aplicar las buenas prácticas del skill a `api_gateway` (API Gateway).
> Fuente de verdad: `app/core/routing.py`, `app/presentation/` (proxy_handler, dashboard, health, handlers).

## Particularidad del repo

La gateway es un **proxy reverso**: los endpoints de negocio (`/auth/*`, `/usuarios/*`,
`/roles/*`, `/afiliados/*`, `/sync/*`) NO se diseñan acá — viven en los microservicios
(`api_usuario-roles`, `api_normalizacion_afiliados`) y se reenvían según la tabla de ruteo
sin reescribir paths. El único código REST propio es el del gateway: `GET /` (health) y
`GET /dashboard` (estado de upstreams).

## Convenciones vigentes del repo

- **Prefijo**: los routers propios NO llevan `/api` ni `/v1` (se montan directo). Si en el
  futuro se versiona, usar URL path versioning (`/api/v1/...`).
- **Ruteo de los microservicios**: tabla data-driven en `app/core/routing.py`, prefijo →
  (URL, timeout, requiere_autorización). Prohibido `if/elif` de paths en los handlers.
- **Métodos de los endpoints propios**:
  - `GET /` → health del gateway (`{"estado": "ok", ...}`).
  - `GET /dashboard` → HTML simple con el estado de cada upstream.
- **Fechas**: ISO 8601 si algún endpoint propio devuelve timestamps.

## Status codes (mapeo de errores de proxy → `handlers.py`)

| Condición | HTTP | Payload |
|---|---|---|
| Upstream caído / timeout | 502 | `{"error": "servicio no disponible: <nombre>"}` |
| Error de negocio del microservicio | el que devuelva el upstream | body original (passthrough) |
| Bug/error inesperado | 500 | default de FastAPI |

**Nota**: no se reinterpreta el status ni el body de los errores de negocio de los
microservicios; se devuelven tal cual llegan del upstream.

## Reglas para endpoints nuevos (propios del gateway)

- ✅ Endpoints chicos y de una sola responsabilidad (SRP): el proxy vive en su módulo, el
  dashboard en el suyo, el health en el suyo.
- ✅ Config detector de errores en un solo lugar (`app/presentation/handlers.py`), no en
  cada router.
- ✅ Reenvío streaming con `httpx` + iterador de bytes de Starlette; sin cargar cuerpos en
  memoria.
- ✅ Envión de headers: reenviar `Authorization` y headers relevantes; excluir hop-by-hop
  (`host`, `connection`, `content-length`).
- ❌ No agregar lógica de negocio/validación de dominio en la gateway (passthrough).
- ❌ No validar JWT en la gateway (lo hacen los microservicios).
- ❌ No devolver 200 para errores ni variar el formato de error entre endpoints.
- ❌ No introducir `/api` en los paths reenviados (el request se reenvía literal).

## Validación

- Para verificar el contrato de un endpoint nuevo propio, revisar el OpenAPI autogenerado
  en `/docs` (FastAPI) y correr la suite:

```bash
venv/bin/python -m pytest -q
```

- Template de referencia: `templates/endpoint_fastapi.py`.
- Para agregar rutas hacia servicios nuevos, seguir el skill `proxy-gateway` (flujo de 6 pasos).