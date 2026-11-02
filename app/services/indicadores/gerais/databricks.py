"""Validação e execução de consultas de indicadores na API Databricks."""


import asyncio
import re
from datetime import date, datetime
from typing import Any
from urllib.parse import urlsplit

import httpx

from app.core import configuracao
from app.core.clients import databricks as cliente_databricks

from app.core.respostas import MENSAGENS
from app.graph.respostas_padrao import formatar_resposta


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
            MENSAGENS['databricks_host_deve_ser_o_host_https_do_workspace_sem_caminho']
        )

    return (
        f"{partes.scheme}://{partes.netloc}",
        configuracao.DATABRICKS_TOKEN.strip(),
        configuracao.DATABRICKS_WAREHOUSE_ID.strip(),
    )


def _validar_sql(sql: str, parametros: dict[str, Any]) -> None:
    consulta = sql.strip()
    if not consulta or not re.match(r"^SELECT\b", consulta, re.IGNORECASE):
        raise ValueError(MENSAGENS['o_cliente_databricks_aceita_somente_consultas_select'])
    if ";" in consulta.rstrip(";"):
        raise ValueError(MENSAGENS['envie_somente_uma_consulta_sql_por_chamada'])

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
    raise ValueError(MENSAGENS['tipo_de_parametro_sql_nao_suportado'])


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
                MENSAGENS['a_resposta_do_databricks_nao_trouxe_o_esquema_das_colunas']
            )
        return []

    linhas = []
    for linha in dados:
        if not isinstance(linha, list) or len(linha) != len(nomes):
            raise ErroConsultaDatabricks(
                MENSAGENS['a_resposta_do_databricks_trouxe_uma_linha_incompativel_com_o_esquema']
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
            MENSAGENS['a_api_databricks_excedeu_o_tempo_limite_de_comunicacao']
        ) from erro
    except httpx.HTTPStatusError as erro:
        raise ErroHTTPDatabricks(
            formatar_resposta('a_api_databricks_respondeu_http_valor_1', valor_1=erro.response.status_code)
        ) from erro
    except httpx.HTTPError as erro:
        raise ErroHTTPDatabricks(
            MENSAGENS['nao_foi_possivel_estabelecer_comunicacao_com_a_api_databricks']
        ) from erro

    try:
        payload = resposta.json()
    except ValueError as erro:
        raise ErroHTTPDatabricks(
            MENSAGENS['a_api_databricks_retornou_uma_resposta_invalida']
        ) from erro
    if not isinstance(payload, dict):
        raise ErroHTTPDatabricks(
            MENSAGENS['a_api_databricks_retornou_um_formato_de_resposta_invalido']
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
        raise ValueError(MENSAGENS['limite_linhas_deve_estar_entre_1_e_10000'])
    if limite_bytes <= 0:
        raise ValueError(MENSAGENS['limite_bytes_deve_ser_maior_que_zero'])
    if tempo_limite_segundos <= 0:
        raise ValueError(MENSAGENS['tempo_limite_segundos_deve_ser_maior_que_zero'])

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
        raise ValueError(MENSAGENS['tipos_de_parametros_informados_sem_parametros_sql'])

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
                    MENSAGENS['a_api_databricks_nao_retornou_o_identificador_da_consulta_pendente']
                )
            restante = prazo - asyncio.get_running_loop().time()
            if restante <= 0:
                await _cancelar_statement(
                    cliente, host, token, statement_id, warehouse_id,
                )
                raise TimeoutConsultaDatabricks(
                    MENSAGENS['a_consulta_databricks_nao_terminou_dentro_do_tempo_limite']
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
            MENSAGENS['a_consulta_databricks_nao_terminou_dentro_do_tempo_limite']
        )

    if estado != "SUCCEEDED":
        raise ErroConsultaDatabricks(
            "O Databricks não concluiu a consulta: " + _dados_erro(payload)
        )

    manifest = payload.get("manifest") or {}
    if manifest.get("truncated") or (payload.get("result") or {}).get("truncated"):
        raise ResultadoDatabricksTruncado(
            MENSAGENS['o_resultado_excedeu_o_limite_de_linhas_ou_bytes_configurado']
        )

    resultado = payload.get("result") or {}
    linhas = _linhas_resultado(payload)
    proximo_chunk = resultado.get("next_chunk_index")
    while proximo_chunk is not None:
        if asyncio.get_running_loop().time() >= prazo:
            raise TimeoutConsultaDatabricks(
                MENSAGENS['a_leitura_dos_resultados_databricks_excedeu_o_tempo_limite']
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
                MENSAGENS['a_leitura_dos_resultados_databricks_excedeu_o_tempo_limite']
            )
        if chunk.get("truncated"):
            raise ResultadoDatabricksTruncado(
                MENSAGENS['o_resultado_excedeu_o_limite_de_linhas_ou_bytes_configurado']
            )
        linhas.extend(_linhas_resultado({"manifest": manifest, "result": chunk}))
        proximo_chunk = chunk.get("next_chunk_index")
        if len(linhas) > limite_linhas:
            raise ResultadoDatabricksTruncado(
                MENSAGENS['o_resultado_excedeu_o_limite_de_linhas_configurado']
            )
    return linhas
