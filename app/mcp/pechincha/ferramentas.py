"""Chamadas às três ferramentas Pechincha.ai usadas no FIXA."""

from .modelos import BuscaOfertas, normalizar_ofertas
from .transporte import ErroPechincha, chamar_ferramenta


async def buscar_ofertas(busca: BuscaOfertas) -> dict:
    argumentos = busca.model_dump(exclude_none=True)
    conteudo = await chamar_ferramenta("search_deals", argumentos)
    return normalizar_ofertas(conteudo)


async def listar_lojas(query: str | None = None) -> list[dict]:
    conteudo = await chamar_ferramenta("list_stores", {"query": query.strip()} if query and query.strip() else {})
    lojas = conteudo.get("stores")
    if not isinstance(lojas, list) or any(not isinstance(loja, dict) for loja in lojas):
        raise ErroPechincha("protocolo", "Lista de lojas inválida.")
    return lojas


async def listar_categorias() -> list[dict]:
    conteudo = await chamar_ferramenta("list_categories", {})
    categorias = conteudo.get("categories")
    if not isinstance(categorias, list) or any(not isinstance(categoria, dict) for categoria in categorias):
        raise ErroPechincha("protocolo", "Lista de categorias inválida.")
    return categorias
