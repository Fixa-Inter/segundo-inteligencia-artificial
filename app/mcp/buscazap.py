"""Cliente JSON-RPC para as ferramentas públicas do MCP BuscaZap."""

import asyncio
import json
import logging
import os
from typing import Any

import httpx
from app.observability.metricas import ACESSO_BUSCAZAP, REQUISICOES_BUSCAZAP


URL = "https://www.buscazap.com.br/mcp"
LOGGER = logging.getLogger(__name__)


class ErroBuscaZap(RuntimeError):
    def __init__(self, codigo: str, mensagem: str):
        self.codigo = codigo
        super().__init__(mensagem)


async def _rpc(metodo: str, parametros: dict | None = None) -> dict:
    corpo: dict[str, Any] = {"jsonrpc": "2.0", "id": 1, "method": metodo}
    if parametros is not None:
        corpo["params"] = parametros
    token = os.getenv("BUSCAZAP_MCP_TOKEN", "").strip()
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=5.0), follow_redirects=False) as cliente:
        for tentativa in range(2):
            try:
                resposta = await cliente.post(URL, json=corpo, headers=headers)
                if resposta.status_code in {429, 502, 503, 504} and tentativa == 0:
                    if resposta.status_code == 429:
                        raise ErroBuscaZap("limite_http", "O serviço limitou as chamadas.")
                    await asyncio.sleep(0.4)
                    continue
                resposta.raise_for_status()
                dados = resposta.json()
                if not isinstance(dados, dict) or dados.get("jsonrpc") != "2.0":
                    raise ErroBuscaZap("protocolo", "Resposta MCP inválida.")
                if isinstance(dados.get("error"), dict):
                    raise ErroBuscaZap("protocolo", str(dados["error"].get("message", "Erro de protocolo.")))
                resultado = dados.get("result")
                if not isinstance(resultado, dict):
                    raise ErroBuscaZap("protocolo", "Resultado MCP ausente.")
                conteudo = resultado.get("structuredContent") or {}
                tier = resultado.get("tier") or (conteudo.get("tier") if isinstance(conteudo, dict) else None)
                if tier not in {"anonymous", "free", "growth", "enterprise"}:
                    atribuicao = (resultado.get("attribution") or
                                  (conteudo.get("attribution") if isinstance(conteudo, dict) else None))
                    tier = "anonymous_attribution" if atribuicao else "unknown"
                ACESSO_BUSCAZAP.labels(str(bool(token)).lower(), tier).inc()
                if token and tier in {"anonymous", "anonymous_attribution"}:
                    LOGGER.warning("BuscaZap MCP parece ter usado acesso anônimo apesar de credencial configurada")
                REQUISICOES_BUSCAZAP.labels(metodo, "success").inc()
                LOGGER.info(
                    "BuscaZap MCP: metodo=%s credencial_configurada=%s tier_reportado=%s",
                    metodo, bool(token), tier,
                )
                return resultado
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                if tentativa == 0:
                    await asyncio.sleep(0.4)
                    continue
                REQUISICOES_BUSCAZAP.labels(metodo, "network_error").inc()
                raise ErroBuscaZap("indisponivel", "BuscaZap indisponível no momento.") from exc
            except httpx.HTTPStatusError as exc:
                REQUISICOES_BUSCAZAP.labels(metodo, "http_error").inc()
                raise ErroBuscaZap("indisponivel", f"BuscaZap retornou HTTP {exc.response.status_code}.") from exc
            except ValueError as exc:
                raise ErroBuscaZap("protocolo", "BuscaZap retornou JSON inválido.") from exc
    raise ErroBuscaZap("indisponivel", "BuscaZap não respondeu.")


async def buscar_produtos(contexto: str, *, limite: int = 5) -> dict:
    if not contexto.strip():
        raise ValueError("O contexto da busca é obrigatório.")
    ferramentas = await _rpc("tools/list")
    nomes = {item.get("name") for item in ferramentas.get("tools", []) if isinstance(item, dict)}
    if "buscar_produtos_por_contexto" not in nomes:
        raise ErroBuscaZap("ferramenta_ausente", "Ferramenta de busca indisponível.")
    resultado = await _rpc("tools/call", {"name": "buscar_produtos_por_contexto", "arguments": {
        "context": contexto, "limit": limite, "recomendar": True,
    }})
    if resultado.get("isError") is True:
        erro = resultado.get("error")
        if not isinstance(erro, str):
            erro = str(erro or "execucao")
        REQUISICOES_BUSCAZAP.labels("tools/call", erro if erro in {"quota_exceeded", "tier_required"} else "tool_error").inc()
        raise ErroBuscaZap(erro, f"A busca retornou {erro}.")
    conteudo = resultado.get("structuredContent")
    if not isinstance(conteudo, dict) or not isinstance(conteudo.get("products"), list):
        raise ErroBuscaZap("protocolo", "BuscaZap não retornou uma lista de produtos válida.")
    produtos = conteudo["products"]
    if any(not isinstance(produto, dict) for produto in produtos):
        raise ErroBuscaZap("protocolo", "Produto MCP em formato inválido.")
    return {"products": produtos[:limite], "recomendacao": conteudo.get("recomendacao")}


async def listar_lojas() -> dict:
    ferramentas = await _rpc("tools/list")
    nomes = {item.get("name") for item in ferramentas.get("tools", []) if isinstance(item, dict)}
    if "listar_lojas" not in nomes:
        raise ErroBuscaZap("ferramenta_ausente", "Lista de lojas indisponível.")
    resultado = await _rpc("tools/call", {"name": "listar_lojas", "arguments": {}})
    if resultado.get("isError") is True:
        codigo = str(resultado.get("error") or "execucao")
        raise ErroBuscaZap(codigo, "Não foi possível consultar as lojas.")
    conteudo = resultado.get("structuredContent")
    if not isinstance(conteudo, dict):
        blocos = resultado.get("content") or []
        texto = next((bloco.get("text") for bloco in blocos
                      if isinstance(bloco, dict) and isinstance(bloco.get("text"), str)), "")
        try:
            conteudo = json.loads("{" + texto.rsplit("\n\n{", 1)[1]) if "\n\n{" in texto else {}
        except (ValueError, IndexError):
            conteudo = {}
    categorias = conteudo.get("categorias")
    if not isinstance(categorias, list):
        raise ErroBuscaZap("protocolo", "BuscaZap não retornou a cobertura de lojas em formato válido.")
    return {"categorias": categorias, "total_claim": conteudo.get("total_claim")}
