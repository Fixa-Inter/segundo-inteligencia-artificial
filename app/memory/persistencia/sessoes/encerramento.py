from qdrant_client import models
from app.memory.persistencia import obter_documento_sessao_id, sessoes_ativas, agora, gerar_resumo
from app.core.clients import abrir_cliente_mongo, abrir_cliente_qdrant
from app.core import MONGO_BANCO_DADOS, MONGO_COLECAO_SESSOES, QDRANT_COLECAO_HISTORICO
from app.memory.embedding import gerar_vetor_documento

async def encerrar_sessao(sessao_id: str, usuario_id: int) -> dict[str, str] | None:
    """Encerra conversa própria e persiste/indexa resumo quando aplicável. Usado pelo fluxo de sessoes."""
    chave = (usuario_id, sessao_id)
    documento_id = await obter_documento_sessao_id(sessao_id, usuario_id)

    if documento_id is None:
        return None

    # Lógica: executa esta etapa e preserva o tratamento de falhas do domínio.
    async with abrir_cliente_mongo() as cliente:
        banco = cliente[MONGO_BANCO_DADOS]
        colecao_sessoes = banco[MONGO_COLECAO_SESSOES]

        documento = await colecao_sessoes.find_one(
            {"_id": documento_id, "user_id": usuario_id, "esta_ativo": True}
        )

        if documento is None:
            sessoes_ativas.pop(chave, None)
            return None

        if documento.get("mensagens"):
            gerado = await gerar_resumo(documento["mensagens"])
            titulo, resumo = gerado.titulo, gerado.resumo
        else:
            titulo, resumo = "", ""

        atualizacao = await colecao_sessoes.update_one(
            {"_id": documento_id, "user_id": usuario_id, "esta_ativo": True},
            {"$set": {"titulo": titulo, "resumo": resumo, "atualizada_em": agora()}},
        )
        sessoes_ativas.pop(chave, None)

        if atualizacao.matched_count == 0:
            return None

        if resumo:
            vetor = await gerar_vetor_documento(resumo)
            async with abrir_cliente_qdrant() as cliente_qdrant:
                await cliente_qdrant.upsert(
                    collection_name=QDRANT_COLECAO_HISTORICO,points=[
                        models.PointStruct(
                            id=documento_id,
                            vector=vetor,
                            payload={
                                "user_id":     usuario_id,
                                "session_id":  sessao_id,
                                "titulo":     titulo,
                                "resumo":      resumo,
                                "iniciada_em": documento["iniciada_em"].isoformat(),
                            },
                        )
                    ],
                )

    return {"titulo": titulo, "resumo": resumo}
