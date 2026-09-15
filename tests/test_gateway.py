import httpx

from app.main import app
from tests.helpers import clear_pool, register_all_mocks
from tests.mock_upstreams import all_ok_handler, connect_error_handler, timeout_handler


def _gw_client(handler=None):
    register_all_mocks(handler or all_ok_handler)
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")


class TestRuteo:
    async def test_auth_me(self):
        client = _gw_client()
        async with client as c:
            resp = await c.get("/auth/me")
        assert resp.status_code == 200
        assert resp.json()["usuario"] == "test_user"
        assert resp.headers.get("x-servicio") == "auth"
        clear_pool()

    async def test_auth_login(self):
        client = _gw_client()
        async with client as c:
            resp = await c.post("/auth/login", json={"user": "x", "pass": "y"})
        assert resp.status_code == 200
        assert "token" in resp.json()
        clear_pool()

    async def test_afiliados_listar(self):
        client = _gw_client()
        async with client as c:
            resp = await c.get("/afiliados")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 2
        clear_pool()

    async def test_afiliados_por_id(self):
        client = _gw_client()
        async with client as c:
            resp = await c.get("/afiliados/42")
        assert resp.status_code == 200
        assert resp.json()["path"] == "/afiliados/42"
        clear_pool()

    async def test_sync_prefijo(self):
        client = _gw_client()
        async with client as c:
            resp = await c.get("/sync/sheets/import")
        assert resp.status_code == 200
        clear_pool()

    async def test_404_ruta_desconocida(self):
        client = _gw_client()
        async with client as c:
            resp = await c.get("/foo/bar")
        assert resp.status_code == 404
        clear_pool()


class TestPassthrough:
    async def test_auth_header_se_reenvia(self):
        captured = {}

        def capturing_handler(request: httpx.Request) -> httpx.Response:
            captured["authorization"] = request.headers.get("authorization")
            captured["x-custom"] = request.headers.get("x-custom")
            return httpx.Response(200, json={"ok": True})

        client = _gw_client(capturing_handler)
        async with client as c:
            resp = await c.get(
                "/auth/me",
                headers={
                    "Authorization": "Bearer mi-token-jwt",
                    "X-Custom": "valor-custom",
                },
            )

        assert resp.status_code == 200
        assert captured["authorization"] == "Bearer mi-token-jwt"
        assert captured["x-custom"] == "valor-custom"
        clear_pool()

    async def test_upstream_status_se_pasa(self):
        def not_found_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                404,
                json={"error": "no existe el afiliado"},
            )

        client = _gw_client(not_found_handler)
        async with client as c:
            resp = await c.get("/afiliados/999")
        assert resp.status_code == 404
        assert resp.json()["error"] == "no existe el afiliado"
        clear_pool()

    async def test_upstream_error_422_se_pasa(self):
        def invalid_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                422,
                json={"error": "campo requerido faltante"},
            )

        client = _gw_client(invalid_handler)
        async with client as c:
            resp = await c.post("/afiliados", json={})
        assert resp.status_code == 422
        clear_pool()


class TestErroresUpstream:
    async def test_502_upstream_caido(self):
        client = _gw_client(connect_error_handler)
        async with client as c:
            resp = await c.get("/auth/me")
        assert resp.status_code == 502
        body = resp.json()
        assert "servicio no disponible" in body["error"]
        clear_pool()

    async def test_504_upstream_timeout(self):
        client = _gw_client(timeout_handler)
        async with client as c:
            resp = await c.get("/auth/me")
        assert resp.status_code == 504
        body = resp.json()
        assert "timeout" in body["error"]
        clear_pool()


class TestRuteoPorPrefijo:
    async def test_auth_y_afiliados_independientes(self):
        client = _gw_client()
        async with client as c:
            resp_auth = await c.get("/auth/me")
            resp_afil = await c.get("/afiliados")
        assert resp_auth.headers.get("x-servicio") == "auth"
        assert resp_afil.headers.get("x-servicio") == "afiliados"
        clear_pool()
