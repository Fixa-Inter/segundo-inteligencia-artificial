"""Validação do escopo obrigatório das consultas de indicadores."""

from app.core.respostas import MENSAGENS


def validar_unidade_id(unidade_id: int) -> dict | None:
    """Rejeita IDs inválidos; booleanos não representam uma unidade."""
    if type(unidade_id) is not int or unidade_id <= 0:
        return {
            "status": "ERRO_VALIDACAO",
            "mensagem": MENSAGENS['unidade_invalida_para_consultar_indicadores'],
        }
    return None
