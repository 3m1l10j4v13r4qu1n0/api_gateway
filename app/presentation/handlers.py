from fastapi import FastAPI


def registrar_handlers(app: FastAPI) -> None:
    """Registra handlers globales de errores de la gateway."""
    # Por ahora no hay handlers de excepción custom.
    # Los errores de negocio de los microservicios se devuelven tal cual (passthrough).
