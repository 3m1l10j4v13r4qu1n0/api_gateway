import httpx


class HttpClientPool:
    """Pool de clientes httpx.AsyncClient, uno por servicio upstream."""

    def __init__(self) -> None:
        self._clients: dict[str, httpx.AsyncClient] = {}

    def register(
        self,
        name: str,
        base_url: str,
        timeout: float,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._clients[name] = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            transport=transport,
        )

    def get(self, name: str) -> httpx.AsyncClient:
        if name not in self._clients:
            raise KeyError(f"Servicio '{name}' no registrado en el pool")
        return self._clients[name]

    async def close_all(self) -> None:
        for client in self._clients.values():
            await client.aclose()
        self._clients.clear()


# Singleton del pool
http_pool = HttpClientPool()
