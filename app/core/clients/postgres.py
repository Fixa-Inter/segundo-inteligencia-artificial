from sqlalchemy import text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core import configuracao


_URLS_POR_PERFIL = {
    "solicitante": configuracao.BANCO_URL_SOLICITANTE,
    "tecnico": configuracao.BANCO_URL_TECNICO,
    "administrador": configuracao.BANCO_URL_GESTOR,
    "gestor": configuracao.BANCO_URL_GESTOR,
}
_MOTORES: dict[tuple[str, str], AsyncEngine] = {}


def _url_asyncpg(valor: str) -> URL:
    url = make_url(valor)
    if url.drivername in {"postgres", "postgresql"}:
        url = url.set(drivername="postgresql+asyncpg")
    elif url.drivername.startswith("postgresql+"):
        url = url.set(drivername="postgresql+asyncpg")
    else:
        raise ValueError("A URL configurada nao usa PostgreSQL.")
    consulta = dict(url.query)
    if "sslmode" in consulta and "ssl" not in consulta:
        consulta["ssl"] = consulta.pop("sslmode")
        url = url.set(query=consulta)
    return url


def _motor_url(perfil: str, valor: str) -> AsyncEngine:
    chave = (perfil, valor)
    if chave not in _MOTORES:
        _MOTORES[chave] = create_async_engine(
            _url_asyncpg(valor),
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=5,
        )
    return _MOTORES[chave]


def obter_motor(perfil: str) -> AsyncEngine:
    if perfil not in _URLS_POR_PERFIL:
        raise PermissionError("Perfil sem acesso ao banco.")
    url = _URLS_POR_PERFIL[perfil]
    if not url:
        raise RuntimeError(f"Configure DATABASE_URL_{perfil.upper()}.")
    return _motor_url(perfil, url)


async def executar_consulta(perfil: str, sql: str, parametros: dict) -> list[dict]:
    motor = obter_motor(perfil)
    async with motor.connect() as conexao:
        resultado = await conexao.execute(text(sql), parametros)
        return [dict(linha) for linha in resultado.mappings().all()]


async def executar_insercao(perfil: str, sql: str, parametros: dict) -> list[dict]:
    """Executa um INSERT em transacao e retorna as linhas de RETURNING, se houver."""
    motor = obter_motor(perfil)
    async with motor.begin() as conexao:
        resultado = await conexao.execute(text(sql), parametros)
        if not resultado.returns_rows:
            return []
        return [dict(linha) for linha in resultado.mappings().all()]


async def fechar_conexoes_postgres() -> None:
    for motor in _MOTORES.values():
        await motor.dispose()
    _MOTORES.clear()
