"""Validações pequenas compartilhadas pelos contratos de cadastro."""

from app.core import MENSAGENS

def validar_titulo_cadastro(valor: str) -> str:
    """Exige até dez palavras sem alterar texto; usada por evento e solicitação."""
    if len(valor.split()) > 10:
        raise ValueError(MENSAGENS['o_titulo_deve_conter_no_maximo_10_palavras'])
    return valor
