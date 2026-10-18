from fastapi import HTTPException, status
from app.core import Emocao
from app.memory.persistencia.sessoes import iniciar_sessao
from app.memory.persistencia.utilitarios import obter_documento_sessao_id, agora
from app.memory.persistencia.rascunho_solicitacao import (
    adicionar_imagens_sessao,
)
from app.core.clients.mongo import abrir_cliente_mongo
from app.core.configuracao import MONGO_BANCO_DADOS, MONGO_COLECAO_SESSOES


async def salvar_mensagem(
    sessao_id: str,
    papel: str,
    conteudo: str,
    usuario_id: int,
    imagens: list[str] | None = None,
    *, associar_imagens: bool = True,
    emocao: Emocao | str | None = None,
) -> None:

    documento_id = await obter_documento_sessao_id(sessao_id, usuario_id)
    if not documento_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inicie uma conversa para salvar a mensagem!",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    mensagem = {"role": papel, "content": conteudo}
    if papel == "assistant":
        mensagem["emocao"] = Emocao(emocao or Emocao.NEUTRO).value
    imagens_validas = [
        url.strip()
        for url in (imagens or [])
        if isinstance(url, str) and url.strip()
    ]
    if papel == "human" and imagens_validas:
        mensagem["imagens"] = imagens_validas

    async with abrir_cliente_mongo() as cliente:
        banco = cliente[MONGO_BANCO_DADOS]
        colecao_sessoes = banco[MONGO_COLECAO_SESSOES]
        await colecao_sessoes.update_one(
            {"_id": documento_id, "user_id": usuario_id},
            {
                "$push": {"mensagens": mensagem},
                "$set":  {"atualizada_em": agora()},
            },
        )

    if papel == "human" and imagens_validas and associar_imagens:
        await adicionar_imagens_sessao(
            sessao_id=sessao_id,
            usuario_id=usuario_id,
            imagens=imagens_validas,
        )
