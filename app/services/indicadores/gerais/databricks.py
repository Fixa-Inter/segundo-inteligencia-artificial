"""Validação e execução de consultas de indicadores na API Databricks."""

import asyncio
import re
from datetime import date, datetime
from typing import Any
from urllib.parse import urlsplit

import httpx

from app.core import configuracao
from app.core.clients import databricks as cliente_databricks


_WAIT_TIMEOUT = "10s"
_TEMPO_MAXIMO_EXECUCAO_SEGUNDOS = 60.0
_INTERVALO_POLL_SEGUNDOS = 0.5
_LIMITE_LINHAS_PADRAO = 1000
_LIMITE_BYTES_PADRAO = 2_000_000
_MARCADOR_SQL = re.compile(r"(?<!:):([A-Za-z][A-Za-z0-9_]*)")


class ErroDatabricks(RuntimeError):
    """Erro base para falhas de configuração ou consulta no Databricks."""


class ConfiguracaoDatabricksAusente(ErroDatabricks):
    """Uma variável necessária para consultar o workspace está ausente."""


class ErroHTTPDatabricks(ErroDatabricks):
    """A API Databricks recusou ou não respondeu à requisição."""


class ErroConsultaDatabricks(ErroDatabricks):
    """O warehouse não conseguiu executar o SQL enviado."""


class TimeoutConsultaDatabricks(ErroDatabricks):
    """A consulta não terminou dentro do tempo limite configurado."""


class ResultadoDatabricksTruncado(ErroDatabricks):
    """O limite de resultado configurado cortou linhas da resposta."""


def _configuracoes() -> tuple[str, str, str]:
    ausentes = [
        nome
        for nome, valor in (
            ("DATABRICKS_HOST", configuracao.DATABRICKS_HOST),
            ("DATABRICKS_TOKEN", configuracao.DATABRICKS_TOKEN),
            ("DATABRICKS_WAREHOUSE_ID", configuracao.DATABRICKS_WAREHOUSE_ID),
        )
        if not isinstance(valor, str) or not valor.strip()
    ]
    if ausentes:
        raise ConfiguracaoDatabricksAusente(
            "Configure as variáveis: " + ", ".join(ausentes) + "."
        )

    host = configuracao.DATABRICKS_HOST.strip().rstrip("/")
    if not host.startswith(("https://", "http://")):
        host = f"https://{host}"
    partes = urlsplit(host)
    if (
        partes.scheme != "https"
        or not partes.netloc
        or partes.username
        or partes.password
        or partes.path not in {"", "/"}
        or partes.query
        or partes.fragment
    ):
        raise ConfiguracaoDatabricksAusente(
            "DATABRICKS_HOST deve ser o host HTTPS do workspace, sem caminho."
        )

    return (
        f"{partes.scheme}://{partes.netloc}",
        configuracao.DATABRICKS_TOKEN.strip(),
        configuracao.DATABRICKS_WAREHOUSE_ID.strip(),
    )


def _validar_sql(sql: str, parametros: dict[str, Any]) -> None:
    consulta = sql.strip()
    if not consulta or not re.match(r"^SELECT\b", consulta, re.IGNORECASE):
        raise ValueError("O cliente Databricks aceita somente consultas SELECT.")
    if ";" in consulta.rstrip(";"):
        raise ValueError("Envie somente uma consulta SQL por chamada.")

    marcadores = set(_MARCADOR_SQL.findall(consulta))
    nomes_recebidos = set(parametros)
    faltantes = marcadores - nomes_recebidos
    extras = nomes_recebidos - marcadores
    if faltantes or extras:
        detalhes = []
        if faltantes:
            detalhes.append("parâmetros sem valor: " + ", ".join(sorted(faltantes)))
        if extras:
            detalhes.append("parâmetros não usados: " + ", ".join(sorted(extras)))
        raise ValueError("; ".join(detalhes) + ".")


def _valor_parametro(valor: Any) -> str | None:
    if valor is None:
        return None
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    if isinstance(valor, bool):
        return "true" if valor else "false"
    if isinstance(valor, (str, int, float)):
        return str(valor)
    raise ValueError("Tipo de parâmetro SQL não suportado.")


def _parametros_api(
    parametros: dict[str, Any], tipos_parametros: dict[str, str] | None,
) -> list[dict[str, str]]:
    tipos = tipos_parametros or {}
    desconhecidos = set(tipos) - set(parametros)
    if desconhecidos:
        raise ValueError(
            "Tipos definidos para parâmetros inexistentes: "
            + ", ".join(sorted(desconhecidos))
            + "."
        )

    resultado = []
    for nome, valor in parametros.items():
        item = {"name": nome}
        valor_serializado = _valor_parametro(valor)
        if valor_serializado is not None:
            item["value"] = valor_serializado
        if nome in tipos:
            item["type"] = tipos[nome]
        resultado.append(item)
    return resultado


def _dados_erro(payload: dict[str, Any]) -> str:
    status = payload.get("status") or {}
    erro = status.get("error") or {}
    codigo = erro.get("error_code") or status.get("state") or "ERRO_DESCONHECIDO"
    mensagem = erro.get("message")
    if isinstance(mensagem, str) and mensagem.strip():
        return f"{codigo}: {mensagem.strip()}"
    return str(codigo)


def _linhas_resultado(payload: dict[str, Any]) -> list[dict[str, Any]]:
    manifest = payload.get("manifest") or {}
    colunas = (manifest.get("schema") or {}).get("columns") or []
    dados = (payload.get("result") or {}).get("data_array") or []
    nomes = [coluna.get("name") for coluna in colunas]
    if not nomes or any(not isinstance(nome, str) or not nome for nome in nomes):
        if dados:
            raise ErroConsultaDatabricks(
                "A resposta do Databricks não trouxe o esquema das colunas."
            )
        return []

    linhas = []
    for linha in dados:
        if not isinstance(linha, list) or len(linha) != len(nomes):
            raise ErroConsultaDatabricks(
                "A resposta do Databricks trouxe uma linha incompatível com o esquema."
            )
        linhas.append(dict(zip(nomes, linha)))
    return linhas


async def _requisicao_json(
    cliente: httpx.AsyncClient,
    host: str,
    token: str,
    metodo: str,
    caminho: str,
    **opcoes: Any,
) -> dict[str, Any]:
    try:
        resposta = await cliente.request(
            metodo,
            f"{host}{caminho}",
            headers={"Authorization": f"Bearer {token}"},
            **opcoes,
        )
        resposta.raise_for_status()
    except httpx.TimeoutException as erro:
        raise TimeoutConsultaDatabricks(
            "A API Databricks excedeu o tempo limite de comunicação."
        ) from erro
    except httpx.HTTPStatusError as erro:
        raise ErroHTTPDatabricks(
            f"A API Databricks respondeu HTTP {erro.response.status_code}."
        ) from erro
    except httpx.HTTPError as erro:
        raise ErroHTTPDatabricks(
            "Não foi possível estabelecer comunicação com a API Databricks."
        ) from erro

    try:
        payload = resposta.json()
    except ValueError as erro:
        raise ErroHTTPDatabricks(
            "A API Databricks retornou uma resposta inválida."
        ) from erro
    if not isinstance(payload, dict):
        raise ErroHTTPDatabricks(
            "A API Databricks retornou um formato de resposta inválido."
        )
    return payload


async def _cancelar_statement(
    cliente: httpx.AsyncClient,
    host: str,
    token: str,
    statement_id: str,
    warehouse_id: str,
) -> None:
    try:
        resposta = await cliente.post(
            f"{host}/api/2.0/sql/statements/{statement_id}/cancel",
            headers={"Authorization": f"Bearer {token}"},
            json={"warehouse_id": warehouse_id},
        )
        resposta.raise_for_status()
    except httpx.HTTPError:
        # Preserva o timeout/cancelamento original; não mascara a falha principal.
        pass


async def executar_consulta(
    sql: str,
    parametros: dict[str, Any] | None = None,
    *,
    tipos_parametros: dict[str, str] | None = None,
    limite_linhas: int = _LIMITE_LINHAS_PADRAO,
    limite_bytes: int = _LIMITE_BYTES_PADRAO,
    tempo_limite_segundos: float = _TEMPO_MAXIMO_EXECUCAO_SEGUNDOS,
) -> list[dict[str, Any]]:
    """Executa um SELECT parametrizado no warehouse e devolve linhas como dicionários."""
    valores = parametros or {}
    _validar_sql(sql, valores)
    if not 1 <= limite_linhas <= 10_000:
        raise ValueError("limite_linhas deve estar entre 1 e 10000.")
    if limite_bytes <= 0:
        raise ValueError("limite_bytes deve ser maior que zero.")
    if tempo_limite_segundos <= 0:
        raise ValueError("tempo_limite_segundos deve ser maior que zero.")

    host, token, warehouse_id = _configuracoes()
    cliente = cliente_databricks.obter_cliente_databricks()
    corpo = {
        "statement": sql.strip().rstrip(";"),
        "warehouse_id": warehouse_id,
        "wait_timeout": _WAIT_TIMEOUT,
        "on_wait_timeout": "CONTINUE",
        "disposition": "INLINE",
        "format": "JSON_ARRAY",
        "row_limit": limite_linhas,
        "byte_limit": limite_bytes,
    }
    if valores:
        corpo["parameters"] = _parametros_api(valores, tipos_parametros)
    elif tipos_parametros:
        raise ValueError("Tipos de parâmetros informados sem parâmetros SQL.")

    prazo = asyncio.get_running_loop().time() + tempo_limite_segundos
    payload = await _requisicao_json(
        cliente, host, token, "POST", "/api/2.0/sql/statements", json=corpo,
    )
    status = payload.get("status") or {}
    estado = status.get("state")
    statement_id = payload.get("statement_id")
    try:
        while estado in {"PENDING", "RUNNING"}:
            if not statement_id:
                raise ErroConsultaDatabricks(
                    "A API Databricks não retornou o identificador da consulta pendente."
                )
            restante = prazo - asyncio.get_running_loop().time()
            if restante <= 0:
                await _cancelar_statement(
                    cliente, host, token, statement_id, warehouse_id,
                )
                raise TimeoutConsultaDatabricks(
                    "A consulta Databricks não terminou dentro do tempo limite."
                )
            await asyncio.sleep(min(_INTERVALO_POLL_SEGUNDOS, restante))
            payload = await _requisicao_json(
                cliente,
                host,
                token,
                "GET",
                f"/api/2.0/sql/statements/{statement_id}",
                params={"warehouse_id": warehouse_id},
            )
            status = payload.get("status") or {}
            estado = status.get("state")
    except asyncio.CancelledError:
        if statement_id and estado in {"PENDING", "RUNNING"}:
            try:
                await asyncio.shield(
                    _cancelar_statement(
                        cliente, host, token, statement_id, warehouse_id,
                    )
                )
            except asyncio.CancelledError:
                pass
        raise

    if asyncio.get_running_loop().time() >= prazo:
        raise TimeoutConsultaDatabricks(
            "A consulta Databricks não terminou dentro do tempo limite."
        )

    if estado != "SUCCEEDED":
        raise ErroConsultaDatabricks(
            "O Databricks não concluiu a consulta: " + _dados_erro(payload)
        )

    manifest = payload.get("manifest") or {}
    if manifest.get("truncated") or (payload.get("result") or {}).get("truncated"):
        raise ResultadoDatabricksTruncado(
            "O resultado excedeu o limite de linhas ou bytes configurado."
        )

    resultado = payload.get("result") or {}
    linhas = _linhas_resultado(payload)
    proximo_chunk = resultado.get("next_chunk_index")
    while proximo_chunk is not None:
        if asyncio.get_running_loop().time() >= prazo:
            raise TimeoutConsultaDatabricks(
                "A leitura dos resultados Databricks excedeu o tempo limite."
            )
        chunk = await _requisicao_json(
            cliente,
            host,
            token,
            "GET",
            f"/api/2.0/sql/statements/{statement_id}/result/chunks/{proximo_chunk}",
            params={"warehouse_id": warehouse_id},
        )
        if asyncio.get_running_loop().time() >= prazo:
            raise TimeoutConsultaDatabricks(
                "A leitura dos resultados Databricks excedeu o tempo limite."
            )
        if chunk.get("truncated"):
            raise ResultadoDatabricksTruncado(
                "O resultado excedeu o limite de linhas ou bytes configurado."
            )
        linhas.extend(_linhas_resultado({"manifest": manifest, "result": chunk}))
        proximo_chunk = chunk.get("next_chunk_index")
        if len(linhas) > limite_linhas:
            raise ResultadoDatabricksTruncado(
                "O resultado excedeu o limite de linhas configurado."
            )
    return linhas
