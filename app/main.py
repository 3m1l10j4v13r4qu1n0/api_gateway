from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.routing import ROUTES
from app.infrastructure.http_client import http_pool
from app.presentation.dashboard import router as dashboard_router
from app.presentation.handlers import registrar_handlers
from app.presentation.health import router as health_router
from app.presentation.proxy_handler import proxy_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Inicio: crear pool de clientes HTTP ────────────────────────────
    for route in ROUTES:
        http_pool.register(route.prefix, route.target, route.timeout)
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} — {len(ROUTES)} rutas activas")
    yield
    # ── Cierre: cerrar pool ────────────────────────────────────────────
    await http_pool.close_all()
    print(f"👋 {settings.APP_NAME} cerrado")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="API Gateway — proxy reverso hacia microservicios",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Handlers de errores ──────────────────────────────────────────────
registrar_handlers(app)

# ── Routers propios del gateway ──────────────────────────────────────
app.include_router(health_router)
app.include_router(dashboard_router)

# ── Catch-all: proxy reverso ──────────────────────────────────────────
# Se registra al final para que los routers propios tengan prioridad.
# Los prefijos en la tabla de ruteo capturan /auth, /auth/*, /usuarios, etc.
for route in ROUTES:
    for template in (route.prefix, f"{route.prefix}/{{path:path}}"):
        app.add_api_route(
            template,
            endpoint=proxy_handler,
            methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
            include_in_schema=False,
        )
