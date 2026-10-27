"""Integração de compras com o servidor MCP do Pechincha.ai."""

from .ferramentas import buscar_ofertas, listar_categorias, listar_lojas
from .transporte import ErroPechincha

__all__ = ["ErroPechincha", "buscar_ofertas", "listar_categorias", "listar_lojas"]
