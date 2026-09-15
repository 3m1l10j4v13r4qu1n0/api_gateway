import httpx

from app.core.routing import ROUTES
from app.infrastructure.http_client import http_pool


def register_all_mocks(handler) -> None:
    """Registra el mismo handler mock para todos los servicios upstream."""
    transport = httpx.MockTransport(handler)
    for route in ROUTES:
        http_pool.register(route.prefix, route.target, route.timeout, transport=transport)


def clear_pool() -> None:
    http_pool._clients.clear()
