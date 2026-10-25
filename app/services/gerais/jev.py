"""Cliente e validação das decisões estruturadas do JEV."""

import asyncio
import json
import logging
import math
import time

import httpx

from app.core.configuracao import JEV_MODELO, JEV_URL, TYPESAFE_API_KEY
from app.observability.metricas import DURACAO_JEV, REQUISICOES_JEV, registrar_uso_modelo


registrador = logging.getLogger(__name__)


class ErroJEV(RuntimeError):
    """A decisão não pôde ser obtida ou validada."""


class DecisaoIncertaJEV(ErroJEV):
    """A resposta válida não teve certeza suficiente para alterar o fluxo."""


async def consultar_jev(estado: dict, perguntas: dict, *, operacao: str = "outra") -> dict:
    inicio = time.perf_counter()
    resultado = "error"
    try:
        if not TYPESAFE_API_KEY:
            raise ErroJEV("Chave do JEV ausente.")
        corpo = {"model": JEV_MODELO, "state": estado, "questions": perguntas}
        try:
            json.dumps(corpo, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ErroJEV("Estado do JEV não é JSON válido.") from exc

        async with httpx.AsyncClient(timeout=30, follow_redirects=False) as cliente:
            for tentativa in range(2):
                resposta = await cliente.post(
                    JEV_URL,
                    json=corpo,
                    headers={"Authorization": f"Bearer {TYPESAFE_API_KEY}"},
                )
                if resposta.status_code in {429, 529} and tentativa == 0:
                    await asyncio.sleep(0.5)
                    continue
                resposta.raise_for_status()
                dados = resposta.json()
                if not isinstance(dados, dict) or not isinstance(dados.get("answers"), dict):
                    raise ErroJEV("Resposta do JEV sem answers válidos.")
                uso = dados.get("usage") or {}
                if isinstance(uso, dict):
                    registrar_uso_modelo(
                        "typesafe", str(dados.get("model") or JEV_MODELO),
                        uso.get("input_tokens", 0), uso.get("output_tokens", 0),
                    )
                registrador.info(
                    "JEV: operacao=%s modelo=%s duracao=%.3fs",
                    operacao, dados.get("model"), time.perf_counter() - inicio,
                )
                resultado = "success"
                return dados
        raise ErroJEV("JEV não retornou uma decisão.")
    except httpx.HTTPStatusError as exc:
        raise ErroJEV(f"JEV retornou HTTP {exc.response.status_code}.") from exc
    except httpx.TimeoutException as exc:
        raise ErroJEV("Tempo do JEV esgotado.") from exc
    except httpx.RequestError as exc:
        raise ErroJEV("Conexão com o JEV indisponível.") from exc
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ErroJEV("JEV retornou JSON inválido.") from exc
    finally:
        DURACAO_JEV.labels(operacao).observe(time.perf_counter() - inicio)
        REQUISICOES_JEV.labels(operacao, resultado).inc()


def ler_choice(respostas: dict, nome: str, opcoes: set[str]) -> tuple[str, float]:
    resposta = respostas.get(nome)
    if not isinstance(resposta, dict) or resposta.get("type") != "choice":
        raise ErroJEV(f"Choice {nome} inválido.")
    escolha = resposta.get("choice")
    confianca = resposta.get("confidence")
    if escolha not in opcoes or isinstance(confianca, bool) or not isinstance(confianca, (float, int)):
        raise ErroJEV(f"Choice {nome} inválido.")
    if not math.isfinite(confianca) or not 0 <= confianca <= 1:
        raise ErroJEV(f"Confiança de {nome} inválida.")
    return escolha, float(confianca)


def ler_noul(respostas: dict, nome: str) -> float:
    resposta = respostas.get(nome)
    if not isinstance(resposta, dict) or resposta.get("type") != "noul":
        raise ErroJEV(f"Noul {nome} inválido.")
    valor = resposta.get("noul")
    if isinstance(valor, bool) or not isinstance(valor, (float, int)):
        raise ErroJEV(f"Noul {nome} inválido.")
    if not math.isfinite(valor) or not 0 <= valor <= 1:
        raise ErroJEV(f"Noul {nome} fora do intervalo.")
    return float(valor)
