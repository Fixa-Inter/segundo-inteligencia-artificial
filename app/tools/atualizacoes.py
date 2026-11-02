"""Regras compartilhadas de versionamento e identificação de registros."""

import re

from app.core.confirmacoes import aceite_explicito, normalizar_mensagem
from app.core.respostas import MENSAGENS


async def salvar_proposta(contexto: dict, rascunho: dict, atualizar, **campos) -> dict:
    campos = {**campos, "versao": rascunho["versao"] + 1, "turno_id": contexto["turno_id"]}
    alterou = await atualizar(
        contexto["session_id"], contexto["usuario"].usuario_id, campos,
        tipo=rascunho["tipo"], rascunho_id=rascunho["id"], versao=rascunho["versao"],
        status_esperados={rascunho["status_fluxo"]}, exigir_ativo=True,
    )
    if not alterou:
        raise ValueError(MENSAGENS["atualizacao_proposta_mudou"])
    return {**rascunho, **campos}


def confirmou_selecao(texto: str) -> bool:
    """Identificar o registro não autoriza gravar a proposta final."""
    if "?" in texto:
        return False
    normalizada = normalizar_mensagem(texto)
    if aceite_explicito(texto) or normalizada in {
        "e essa", "e essa mesma", "essa mesma", "sim e essa", "sim e essa mesma", "sim essa mesma",
    }:
        return True
    return bool(re.fullmatch(
        r"(?:sim(?: e essa(?: mesma)?)?|e essa(?: mesma)?|essa mesma) "
        r"(?:(?:pode|quero) )?(?:adicionar|adicione|substituir|substitua) "
        r"(?:todas )?(?:as )?(?:novas )?(?:fotos|imagens)(?: as existentes)?",
        normalizada,
    ))
