from sqlalchemy import text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core import config


_URLS_POR_PERFIL = {
    "solicitante": config.DATABASE_URL_SOLICITANTE,
    "tecnico": config.DATABASE_URL_TECNICO,
    "gestor": config.DATABASE_URL_GESTOR,
}
_ENGINES: dict[tuple[str, str], AsyncEngine] = {}


def _url_asyncpg(valor: str) -> URL:
    url = make_url(valor)
    if url.drivername in {"postgres", "postgresql"}:
        url = url.set(drivername="postgresql+asyncpg")
    elif url.drivername.startswith("postgresql+"):
        url = url.set(drivername="postgresql+asyncpg")
    else:
        raise ValueError("A URL configurada nao usa PostgreSQL.")
    query = dict(url.query)
    if "sslmode" in query and "ssl" not in query:
        query["ssl"] = query.pop("sslmode")
        url = url.set(query=query)
    return url


def _engine_para_url(perfil: str, valor: str) -> AsyncEngine:
    chave = (perfil, valor)
    if chave not in _ENGINES:
        _ENGINES[chave] = create_async_engine(
            _url_asyncpg(valor),
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=5,
        )
    return _ENGINES[chave]


def obter_engine(perfil: str) -> AsyncEngine:
    if perfil not in _URLS_POR_PERFIL:
        raise PermissionError("Perfil sem acesso ao banco.")
    url = _URLS_POR_PERFIL[perfil]
    if not url:
        raise RuntimeError(f"Configure DATABASE_URL_{perfil.upper()}.")
    return _engine_para_url(perfil, url)


async def executar_select(perfil: str, sql: str, parametros: dict) -> list[dict]:
    engine = obter_engine(perfil)
    async with engine.connect() as conexao:
        resultado = await conexao.execute(text(sql), parametros)
        return [dict(linha) for linha in resultado.mappings().all()]


async def executar_insert(perfil: str, sql: str, parametros: dict) -> list[dict]:
    """Executa um INSERT em transacao e retorna as linhas de RETURNING, se houver."""
    engine = obter_engine(perfil)
    async with engine.begin() as conexao:
        resultado = await conexao.execute(text(sql), parametros)
        if not resultado.returns_rows:
            return []
        return [dict(linha) for linha in resultado.mappings().all()]


async def fechar_conexoes_postgres() -> None:
    for engine in _ENGINES.values():
        await engine.dispose()
    _ENGINES.clear()
