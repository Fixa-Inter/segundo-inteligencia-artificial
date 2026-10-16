"""Interface pública do domínio."""

from .buscarOrdensServico import (
    buscar_ordens_servico,
    consultar_minhas_ordens_servico,
    consultar_todas_ordens_servico,
)

__all__ = [
    "buscar_ordens_servico",
    "consultar_minhas_ordens_servico",
    "consultar_todas_ordens_servico",
]
