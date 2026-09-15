import httpx

from app.main import app
from tests.helpers import register_all_mocks
from tests.mock_upstreams import all_ok_handler


def _make_gw_client(handler=None):
    """Crea un cliente de test contra la gateway con el mock handler indicado."""
    register_all_mocks(handler or all_ok_handler)
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")
