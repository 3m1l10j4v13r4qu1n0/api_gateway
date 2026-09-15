import httpx


def auth_handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path

    if path == "/auth/me":
        return httpx.Response(
            200,
            json={"usuario": "test_user", "rol": "admin"},
            headers={"x-servicio": "auth"},
        )

    if path == "/auth/login":
        return httpx.Response(
            200,
            json={"token": "fake.jwt.token"},
            headers={"x-servicio": "auth"},
        )

    return httpx.Response(
        404,
        json={"error": "auth endpoint not found"},
        headers={"x-servicio": "auth"},
    )


def afiliados_handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path

    if path == "/afiliados":
        return httpx.Response(
            200,
            json=[{"id": 1, "nombre": "Juan"}, {"id": 2, "nombre": "Ana"}],
            headers={"x-servicio": "afiliados"},
        )

    return httpx.Response(
        200,
        json={"path": path},
        headers={"x-servicio": "afiliados"},
    )


def all_ok_handler(request: httpx.Request) -> httpx.Response:
    """Simula ambos servicios respondiendo OK, inspeccionando el puerto del request URL."""
    if request.url.port == 8001:
        return auth_handler(request)
    if request.url.port == 8002:
        return afiliados_handler(request)
    return httpx.Response(404, json={"error": "unknown upstream"})


def timeout_handler(request: httpx.Request) -> httpx.Response:
    raise httpx.ReadTimeout("upstream timeout")


def connect_error_handler(request: httpx.Request) -> httpx.Response:
    raise httpx.ConnectError("connection refused")
