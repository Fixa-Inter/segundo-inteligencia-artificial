"""Converte filtros informados pela pessoa nos parâmetros aceitos pelo MCP."""


import unicodedata

from app.mcp.pechincha import buscar_ofertas, listar_categorias, listar_lojas
from app.mcp.pechincha.modelos import BuscaOfertas
from app.mcp.pechincha.transporte import ErroPechincha

from .coleta import DadosCompra

from app.core.respostas import MENSAGENS
from app.graph.respostas_padrao import formatar_resposta


def _normalizar(valor: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", valor.casefold())
                   if not unicodedata.combining(c)).strip()


def _slug_exato(valor: str, opcoes: list[dict], campo: str) -> str:
    procurado = _normalizar(valor)
    for opcao in opcoes:
        if any(procurado == _normalizar(str(opcao.get(chave) or ""))
               for chave in ("slug", "name", "nome")):
            slug = opcao.get("slug")
            if isinstance(slug, str) and slug:
                return slug
    raise ErroPechincha("filtro_invalido", formatar_resposta('valor_1_nao_encontrada_no_pechincha_ai_valor_2', valor_1=campo, valor_2=valor))


async def consultar(dados: DadosCompra) -> dict:
    filtros = {"query": (dados.item or "").strip(), "min_price": dados.min_price,
               "max_price": dados.max_price}
    if dados.loja:
        filtros["store"] = _slug_exato(dados.loja, await listar_lojas(dados.loja), "Loja")
    if dados.categoria:
        filtros["category"] = _slug_exato(dados.categoria, await listar_categorias(), "Categoria")
    try:
        busca = BuscaOfertas(**filtros)
    except ValueError as exc:
        raise ErroPechincha("filtro_invalido", MENSAGENS['confira_a_palavra_chave_e_a_faixa_de_preco_informadas']) from exc
    resultado = await buscar_ofertas(busca)
    resultado["ofertas"] = resultado["ofertas"][:5]
    return resultado
