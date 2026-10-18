"""Interface pública do domínio."""

from .buscarOcorrencias import (
    buscar_equipamento_por_codigo,
    consultar_minhas_ocorrencias,
)
from .criarOcorrencia import (
    adicionar_ocorrencia,
)

__all__ = [
    "buscar_equipamento_por_codigo",
    "consultar_minhas_ocorrencias",
    "adicionar_ocorrencia",
]
