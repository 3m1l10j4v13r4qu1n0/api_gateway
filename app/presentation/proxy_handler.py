import logging

import httpx
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse

from app.core.routing import find_route
from app.infrastructure.http_client import http_pool

logger = logging.getLogger(__name__)

# Headers que no se reenvían (hop-by-hop)
HOP_BY_HOP = frozenset(
    {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
        "host",
        "content-length",
    }
)


async def proxy_handler(request: Request) -> Response:
    """
    Reenvío streaming del request al servicio upstream correspondiente.

    - Busca el servicio por prefijo en la tabla de ruteo.
    - Reenvía method, path literal, query, headers (sin hop-by-hop) y body.
    - Devuelve el response del upstream como StreamingResponse (sin buffers).
    - Si el upstream no está disponible, devuelve 502.
    """
    route = find_route(request.url.path)
    if route is None:
        return Response("Ruta no encontrada", status_code=404)

    client = http_pool.get(route.prefix)

    # Construir headers reenviados (sin hop-by-hop)
    headers = {k: v for k, v in request.headers.items() if k.lower() not in HOP_BY_HOP}

    # Construir body stream
    body = request.stream()

    try:
        upstream_response = await client.request(
            method=request.method,
            url=request.url.path,
            headers=headers,
            content=body,
            params=dict(request.query_params),
        )
    except httpx.ConnectError:
        logger.warning("Servicio no disponible: %s", route.prefix)
        return Response(
            f'{{"error": "servicio no disponible: {route.prefix}"}}',
            status_code=502,
            media_type="application/json",
        )
    except httpx.TimeoutException:
        logger.warning("Timeout esperando respuesta de: %s", route.prefix)
        return Response(
            f'{{"error": "timeout del servicio: {route.prefix}"}}',
            status_code=504,
            media_type="application/json",
        )

    # Headers de respuesta sin hop-by-hop
    response_headers = {
        k: v for k, v in upstream_response.headers.items() if k.lower() not in HOP_BY_HOP
    }

    return StreamingResponse(
        content=upstream_response.aiter_bytes(),
        status_code=upstream_response.status_code,
        headers=response_headers,
    )
