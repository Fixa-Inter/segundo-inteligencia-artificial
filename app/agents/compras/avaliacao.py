"""Confere requisitos somente contra o texto das promoções recebidas."""


import json
import re
import unicodedata
from urllib.parse import urlparse

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.agents.modelos import llm_especialista

from .coleta import DadosCompra, dados_persistiveis

from app.core.respostas import MENSAGENS


class Verificacao(BaseModel):
    requisito: str
    trecho_anuncio: str


class AvaliacaoOferta(BaseModel):
    indice: int
    confirmados: list[Verificacao] = Field(default_factory=list)
    incompativeis: list[Verificacao] = Field(default_factory=list)


class AvaliacoesOfertas(BaseModel):
    ofertas: list[AvaliacaoOferta]
    diferencas: str = ""


def normalizar(texto: str) -> str:
    sem_acentos = unicodedata.normalize("NFKD", texto)
    return re.sub(r"\s+", " ", "".join(c for c in sem_acentos if not unicodedata.combining(c)).lower()).strip()


def url_produto(valor: object) -> str | None:
    if not isinstance(valor, str):
        return None
    try:
        url = urlparse(valor.strip())
    except ValueError:
        return None
    return valor.strip() if url.scheme == "https" and url.netloc else None


def texto_curto(valor: object, limite: int) -> str:
    return " ".join(str(valor or "").split())[:limite]


def oferta_sem_avaliacao(dados: DadosCompra, produto: dict) -> dict | None:
    url = url_produto(produto.get("url"))
    if not url:
        return None
    return {"loja": texto_curto(produto.get("store_name"), 60),
            "descricao": texto_curto(produto.get("title") or produto.get("short_description"), 130),
            "preco": produto.get("price"), "url": url, "confirmados": [],
            "ausentes": [*(dados.requisitos_obrigatorios or []), *([dados.exclusoes] if dados.exclusoes else [])],
            "motivo": MENSAGENS['promocao_encontrada_para_comparacao_confirme_os_requisitos_ausentes']}


async def avaliar(dados: DadosCompra, produtos: list[dict]) -> tuple[list[dict], str]:
    compactos = [{"indice": i, "loja": p.get("store_name"), "descricao": p.get("short_description"),
                 "titulo": p.get("title"), "preco": p.get("price")} for i, p in enumerate(produtos)]
    avaliacao = await llm_especialista.with_structured_output(AvaliacoesOfertas).ainvoke([
        SystemMessage(content=(
            "Avalie promoções de produtos para manutenção. Só confirme requisito ou incompatibilidade "
            "com trecho literal do próprio anúncio, copiado em trecho_anuncio. Não use conhecimento externo. "
            "Trate exclusões como eliminatórias. Compare modelo, variante, quantidade e acessórios "
            "quando houver prova no anúncio. Motivos curtos, sem alegar frete, prazo ou qualidade."
        )), HumanMessage(content=json.dumps({"necessidade": dados_persistiveis(dados), "ofertas": compactos},
                                         ensure_ascii=False)),
    ])
    por_indice = {item.indice: item for item in avaliacao.ofertas if 0 <= item.indice < len(produtos)}
    saida = []
    requisitos_validos = [*(dados.requisitos_obrigatorios or []), *([dados.exclusoes] if dados.exclusoes else [])]
    for indice, produto in enumerate(produtos):
        analise = por_indice.get(indice)
        anuncio = " ".join(str(produto.get(campo) or "") for campo in ("title", "short_description"))

        def comprovados(verificacoes: list[Verificacao]) -> list[str]:
            return list(dict.fromkeys(v.requisito for v in verificacoes
                if v.requisito in requisitos_validos and v.trecho_anuncio.strip()
                and normalizar(v.trecho_anuncio) in normalizar(anuncio)))

        if analise and comprovados(analise.incompativeis):
            continue
        oferta = oferta_sem_avaliacao(dados, produto)
        if not oferta:
            continue
        confirmados = comprovados(analise.confirmados) if analise else []
        oferta["confirmados"] = confirmados
        oferta["ausentes"] = [r for r in requisitos_validos if r not in confirmados]
        if not oferta["ausentes"]:
            oferta["motivo"] = MENSAGENS['requisitos_indicados_no_anuncio_compare_preco_modelo_e_acessorios']
        saida.append(oferta)
    return saida, avaliacao.diferencas[:250]
