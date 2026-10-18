"""Interface pública do domínio."""

from .configuracao import (
    gerar_vetor_documento,
    gerar_vetores_documentos,
    gerar_vetor_operacional,
    gerar_ponto_id,
)

__all__ = [
    "gerar_vetor_documento",
    "gerar_vetores_documentos",
    "gerar_vetor_operacional",
    "gerar_ponto_id",
]
