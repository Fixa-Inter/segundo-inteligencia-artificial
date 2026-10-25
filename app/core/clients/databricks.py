"""Pool HTTP compartilhado para acesso aos serviços Databricks."""

import httpx


_CLIENTE_HTTP: httpx.AsyncClient | None = None


def obter_cliente_databricks() -> httpx.AsyncClient:
    """Retorna um cliente assíncrono reutilizável com pool de conexões."""
    global _CLIENTE_HTTP
    if _CLIENTE_HTTP is None or _CLIENTE_HTTP.is_closed:
        _CLIENTE_HTTP = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=5.0, read=20.0, write=10.0, pool=5.0),
            limits=httpx.Limits(
                max_connections=10,
                max_keepalive_connections=5,
            ),
            follow_redirects=False,
        )
    return _CLIENTE_HTTP


async def fechar_cliente_databricks() -> None:
    """Fecha o pool HTTP compartilhado durante o encerramento da aplicação."""
    global _CLIENTE_HTTP
    if _CLIENTE_HTTP is not None:
        await _CLIENTE_HTTP.aclose()
        _CLIENTE_HTTP = None
