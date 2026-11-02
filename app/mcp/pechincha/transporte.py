"""Transporte Streamable HTTP e tratamento dos erros do MCP."""

import asyncio
import json
from typing import Any

import httpx

from app.observability.metricas import REQUISICOES_PECHINCHA
from app.core.configuracao import URL_PECHINCHA, VERSAO_PROTOCOLO


class ErroPechincha(RuntimeError):
    def __init__(self, codigo: str, mensagem: str):
        self.codigo = codigo
        super().__init__(mensagem)


def _ler_resposta(resposta: httpx.Response) -> dict[str, Any]:
    try:
        if "text/event-stream" in resposta.headers.get("content-type", ""):
            eventos = []
            for bloco in resposta.text.replace("\r\n", "\n").split("\n\n"):
                dados = "\n".join(linha[5:].lstrip() for linha in bloco.splitlines()
                                  if linha.startswith("data:"))
                if dados:
                    eventos.append(json.loads(dados))
            payload = next((evento for evento in reversed(eventos)
                            if isinstance(evento, dict) and ("result" in evento or "error" in evento)), None)
        else:
            payload = resposta.json()
    except (ValueError, UnicodeError) as exc:
        raise ErroPechincha("protocolo", "Resposta MCP inválida.") from exc
    if not isinstance(payload, dict) or payload.get("jsonrpc") != "2.0":
        raise ErroPechincha("protocolo", "Resposta MCP inválida.")
    if payload.get("error"):
        erro = payload["error"]
        mensagem = erro.get("message", "Erro MCP.") if isinstance(erro, dict) else str(erro)
        raise ErroPechincha("protocolo", str(mensagem))
    resultado = payload.get("result")
    if not isinstance(resultado, dict):
        raise ErroPechincha("protocolo", "Resultado MCP ausente.")
    return resultado


async def _post(cliente: httpx.AsyncClient, corpo: dict, headers: dict) -> httpx.Response:
    for tentativa in range(2):
        try:
            resposta = await cliente.post(URL_PECHINCHA, json=corpo, headers=headers)
            if resposta.status_code in {502, 503, 504} and tentativa == 0:
                await asyncio.sleep(0.4)
                continue
            if resposta.status_code == 429:
                raise ErroPechincha("limite_http", "O serviço limitou as chamadas.")
            resposta.raise_for_status()
            return resposta
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            if tentativa == 0:
                await asyncio.sleep(0.4)
                continue
            raise ErroPechincha("indisponivel", "Pechincha.ai indisponível.") from exc
        except httpx.HTTPStatusError as exc:
            raise ErroPechincha("indisponivel", f"Pechincha.ai retornou HTTP {exc.response.status_code}.") from exc
    raise ErroPechincha("indisponivel", "Pechincha.ai não respondeu.")


async def chamar_ferramenta(nome: str, argumentos: dict) -> dict:
    """Abre uma sessão MCP, chama uma ferramenta e devolve seu conteúdo estruturado."""
    headers = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=5.0), follow_redirects=False) as cliente:
            inicio = await _post(cliente, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
                "protocolVersion": VERSAO_PROTOCOLO,
                "capabilities": {}, "clientInfo": {"name": "fixa", "version": "1.0"},
            }}, headers)
            inicializacao = _ler_resposta(inicio)
            sessao = inicio.headers.get("mcp-session-id")
            if sessao:
                headers["Mcp-Session-Id"] = sessao
            headers["MCP-Protocol-Version"] = inicializacao.get("protocolVersion", VERSAO_PROTOCOLO)
            await _post(cliente, {"jsonrpc": "2.0", "method": "notifications/initialized"}, headers)
            resposta = await _post(cliente, {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                                           "params": {"name": nome, "arguments": argumentos}}, headers)
            resultado = _ler_resposta(resposta)
            if resultado.get("isError"):
                blocos = resultado.get("content") or []
                mensagem = next((b.get("text") for b in blocos if isinstance(b, dict) and b.get("text")), "Erro na ferramenta.")
                raise ErroPechincha("ferramenta", str(mensagem)[:300])
            conteudo = resultado.get("structuredContent")
            if conteudo is None:
                blocos = resultado.get("content") or []
                texto = next((b.get("text") for b in blocos if isinstance(b, dict) and isinstance(b.get("text"), str)), "")
                try:
                    conteudo = json.loads(texto)
                except ValueError as exc:
                    raise ErroPechincha("protocolo", "A ferramenta não retornou dados estruturados.") from exc
            if not isinstance(conteudo, dict):
                raise ErroPechincha("protocolo", "Conteúdo MCP inválido.")
            REQUISICOES_PECHINCHA.labels(nome, "success").inc()
            return conteudo
    except ErroPechincha as exc:
        REQUISICOES_PECHINCHA.labels(nome, exc.codigo).inc()
        raise
