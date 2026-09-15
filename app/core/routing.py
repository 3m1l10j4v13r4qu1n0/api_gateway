from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True, slots=True)
class Route:
    prefix: str
    target: str
    timeout: float
    requires_auth: bool = True


# ──────────────────────────────────────────────────────────────────────
# Tabla de ruteo: orden importa (FastAPI matchea el primero más específico).
# Cada entrada: prefijo → URL base del servicio upstream + config.
# ──────────────────────────────────────────────────────────────────────

ROUTES: list[Route] = [
    # Auth Service (:8001)
    Route(prefix="/auth", target=settings.AUTH_SERVICE_URL, timeout=10.0),
    Route(prefix="/usuarios", target=settings.AUTH_SERVICE_URL, timeout=10.0),
    Route(prefix="/roles", target=settings.AUTH_SERVICE_URL, timeout=10.0),
    # Afiliados API (:8002)
    Route(prefix="/afiliados", target=settings.AFILIADOS_SERVICE_URL, timeout=30.0),
    Route(
        prefix="/sync", target=settings.AFILIADOS_SERVICE_URL, timeout=120.0, requires_auth=False
    ),
]

# Mapa rápido prefix → route (para lookup O(1))
ROUTE_MAP: dict[str, Route] = {r.prefix: r for r in ROUTES}


def find_route(path: str) -> Route | None:
    """Busca la ruta cuyo prefijo coincida con el inicio de `path`."""
    for route in ROUTES:
        if path.startswith(route.prefix):
            return route
    return None
