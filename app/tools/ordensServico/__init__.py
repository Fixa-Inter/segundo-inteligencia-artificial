"""Interface pública do domínio."""

from .buscarOrdensServico import (
    buscar_ordem_servico,
)
from .listarMinhasOrdensServico import (
    listar_minhas_ordens_servico,
)
from .listarTodasOrdensServico import (
    listar_todas_ordens_servico,
)

__all__ = [
    "buscar_ordem_servico",
    "listar_minhas_ordens_servico",
    "listar_todas_ordens_servico",
]
