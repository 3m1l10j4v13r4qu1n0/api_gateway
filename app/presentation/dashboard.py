import httpx
from fastapi import APIRouter

from app.core.config import settings
from app.core.routing import ROUTES
from app.infrastructure.http_client import http_pool

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard")
async def dashboard():
    """
    Muestra el estado de cada servicio upstream.
    Intenta hacer GET / (health) en cada uno.
    """
    servicios = []
    for route in ROUTES:
        try:
            client = http_pool.get(route.prefix)
            resp = await client.get("/", timeout=5.0)
            estado = "ok" if resp.status_code == 200 else f"error ({resp.status_code})"
        except KeyError:
            estado = "no registrado"
        except httpx.ConnectError:
            estado = "no disponible"
        except httpx.TimeoutException:
            estado = "timeout"

        servicios.append(
            {
                "nombre": route.prefix,
                "target": route.target,
                "timeout": route.timeout,
                "requiere_auth": route.requires_auth,
                "estado": estado,
            }
        )

    return {"gateway": settings.APP_NAME, "version": settings.APP_VERSION, "servicios": servicios}
