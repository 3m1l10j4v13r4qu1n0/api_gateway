# Reglas de buenas prácticas para código Python (API Gateway, FastAPI, proxy reverso)

## Principios generales
- Cada módulo/función/clase debe tener **una única responsabilidad** bien definida. Si mezcla ruteo, transporte y presentación sin necesidad, separalo.
- Antes de escribir código, pensá en el **contrato**: qué recibe (parámetros/tipos), qué devuelve (tipo de retorno), y qué efectos secundarios tiene (llamadas upstream, timeouts, excepciones que lanza).
- Preferí **composición sobre herencia**: decoradores, mixins chicos y colaboración de objetos, no jerarquías profundas de clases.
- La gateway es un **punto de entrada liviano**: no contiene dominio ni casos de uso de los microservicios. Toda lógica de negocio vive en los servicios upstream (auth y afiliados).
- Toda dependencia externa (cliente HTTP, timeouts, URLs de upstream) debe inyectarse o encapsularse detrás de un componente propio, nunca usarse directa y dispersa por los handlers.
- No aplicar estos principios a rajatabla en todos lados: ver sección "Cuándo NO aplicar esto a rajatabla" al final.

## Estructura y organización (equivalente a SRP)
- Un archivo = una responsabilidad. No mezclar tabla de ruteo, configuración, transporte y presentación en la misma función.
- Respetar las capas del proyecto: `app/core/` (config + tabla de ruteo), `app/infrastructure/` (cliente HTTP, pool por servicio), `app/presentation/` (proxy handler, dashboard, health, handlers de error).
- La **tabla de ruteo es dato**: los prefijos y sus destinos viven en `app/core/routing.py`; el handler recorre la tabla, no escribe `if/elif` de paths.
- El punto de entrada (`app/main.py`) inicializa y orquesta (lifespan: cliente HTTP; CORS; routers), no contiene lógica de transporte.
- La creación del cliente HTTP se hace **una vez en el lifespan** y se inyecta a los handlers; nunca se instancia adentro de un router.

## Abierto a extensión, cerrado a modificación
- Preferir agregar un servicio nuevo **agregando una entrada a la tabla de ruteo**, en vez de modificar el proxy handler con condicionales (`if path.startswith('/x')`) que crecen sin límite.
- Agregar timeouts, retries o políticas por servicio como **datos en la config/tabla**, no como ramas nuevas en el handler.

## Sustitución de contratos (equivalente a LSP)
- Un componente que expone una interfaz debe comportarse de forma consistente con lo que el consumidor espera: mismos tipos de retorno, mismas excepciones, mismos casos de borde (ej. el upstream simulado en tests y el real deben tener la misma semántica de respuesta).
- Respetar las firmas declaradas: un cliente fake en tests debe responder igual que el `httpx.AsyncClient` real salvo el efecto de red.

## Interfaces pequeñas (equivalente a ISP)
- Preferir componentes y funciones **pequeños y específicos** antes que un handler monolítico que rutea, transforma y responde todo junto.
- No sobrecargar un módulo con responsabilidades que la mayoría de usos no consume; dividir en helpers chicos y específicos.

## Inversión de dependencias
- El proxy handler no debe construir clientes ni conocer URLs hardcodeadas: recibe el cliente y la tabla de ruteo (o el router destino) por inyección.
- El ensamblaje (`app/main.py`, lifespan) es el único lugar permitido para instanciar clientes concretos (`httpx.AsyncClient`).
- Los handlers de error traducen fallos de proxy a HTTP en un solo lugar (`app/presentation/handlers.py`), no en cada router.

## Reglas específicas de Python
- Tipar todo lo que se pueda: anotaciones en parámetros y retornos; `Optional[T]`/`T | None` en lugar de valores por defecto sin tipo.
- Manejo de errores: los fallos de upstream (timeout, conexión rechazada) se traducen a `502 {"error": "servicio no disponible: <nombre>"}` una sola vez; no tragar excepciones con `except Exception: pass`.
- Preferir `with`/context managers para recursos (clientes, sesiones); evitar abrir/cerrar a mano.
- No importar desde `app/...` con rutas relativas desde dentro de `app/`; ejecutar desde la raíz del repo (imports `app.*`).
- **Async por omisión** (httpx + Starlette): no bloquear el event loop con llamadas sync en endpoints.

## Cuándo NO aplicar esto a rajatabla
- No crear una abstracción para una dependencia que se usa una sola vez y no hay plan de reutilizarla o testearla por separado.
- No dividir una función corta (pocas líneas, alta cohesión) solo por "separación de responsabilidades" si no hay motivo de cambio independiente.
- Scripts únicos, POCs o código de un solo uso no necesitan la misma rigurosidad que el código de producción reutilizable.

## Señales de alerta (smells)
- Router instanciando `httpx.AsyncClient` o con URLs de upstream hardcodeadas → violación de inversión de dependencias.
- Handler con `if/elif` de paths en vez de recorrer la tabla de ruteo → lógica de ruteo fuera de `core/routing.py`.
- Reintroducir lógica de negocio/dominio en la gateway (validación de reglas de afiliados, verificación de JWT, etc.) → eso vive en los microservicios (passthrough).
- Módulos genéricos tipo `utils.py`, `helpers.py`, `common.py` que terminan acumulando de todo → posible God Object.