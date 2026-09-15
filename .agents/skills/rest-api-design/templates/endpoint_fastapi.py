"""Scaffold de endpoint FastAPI para este proyecto (api_normalizacion_afiliados).

Convenciones que sigue el repo (ver AGENTS.md y .agents/rules/reglas-solid.md):
- El router solo delega en el caso de uso inyectado con `Depends(get_*)`.
- La validación de entrada es con schemas Pydantic dedicados (input vs response).
- Errores de negocio se lanzan como excepciones de dominio y se traducen a HTTP
  únicamente en `app/presentation/handlers.py` (nunca try/except en el router).
- Cablear la nueva función `get_*` en `app/infrastructure/dependencies/dependency_injection.py`.

Ejemplo: recurso de ejemplo sobre el recurso `afiliados`.
"""

from app.application.use_cases.ucN_xx import XxUseCase
from fastapi import APIRouter, Depends, status

from app.infrastructure.dependencies.dependency_injection import get_xx_ucN
from app.presentation.schemas.afiliados_schema import XxResponse, XxUpdate

router = APIRouter(prefix="/afiliados", tags=["Afiliados"])


@router.get("/{afiliado_id}", response_model=XxResponse, status_code=status.HTTP_200_OK)
async def obtener_afiliado(
    afiliado_id: int,
    uc: XxUseCase = Depends(get_xx_ucN),
) -> XxResponse:
    """Obtiene un recurso por id. Errores: 404 (AfiliadoNoEncontradoError)."""
    return await uc.execute(afiliado_id=afiliado_id)


@router.patch(
    "/{afiliado_id}", response_model=XxResponse, status_code=status.HTTP_200_OK
)
async def actualizar_afiliado(
    afiliado_id: int,
    payload: XxUpdate,
    uc: XxUseCase = Depends(get_xx_ucN),
) -> XxResponse:
    """Actualización parcial. Errores: 404, 409 (EmailDuplicadoError), 422."""
    return await uc.execute(afiliado_id=afiliado_id, datos=payload)
