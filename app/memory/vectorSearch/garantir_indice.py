"""Garante os índices usados pelos filtros do Qdrant."""

from qdrant_client import models

from app.core import configuracao
from app.core.clients.qdrant import abrir_cliente_qdrant


async def garantir_indice_historico() -> None:
    async with abrir_cliente_qdrant() as cliente:
        await cliente.create_payload_index(
            collection_name=configuracao.QDRANT_COLECAO_HISTORICO,
            field_name="user_id",
            field_schema=models.PayloadSchemaType.INTEGER,
            wait=True,
        )


async def garantir_indice_faq() -> None:
    """Garante o índice usado para filtrar o FAQ pelo perfil autenticado."""
    async with abrir_cliente_qdrant() as cliente:
        informacoes = await cliente.get_collection(
            collection_name=configuracao.QDRANT_COLECAO_FAQ,
        )
        if "perfil" not in (informacoes.payload_schema or {}):
            await cliente.create_payload_index(
                collection_name=configuracao.QDRANT_COLECAO_FAQ,
                field_name="perfil",
                field_schema=models.PayloadSchemaType.KEYWORD,
                wait=True,
            )


async def garantir_indices_operacionais() -> None:
    """Indexa unidade, atividade, ID e texto nas collections já existentes."""
    indice_textual = models.TextIndexParams(
        type=models.TextIndexType.TEXT,
        tokenizer=models.TokenizerType.WORD,
        lowercase=True,
        min_token_len=1,
        phrase_matching=True,
    )
    async with abrir_cliente_qdrant() as cliente:
        for colecao in sorted(configuracao.QDRANT_COLECOES_OPERACIONAIS):
            informacoes = await cliente.get_collection(collection_name=colecao)
            indices = informacoes.payload_schema or {}
            campos = {
                configuracao.QDRANT_CAMPO_ATIVO: models.PayloadSchemaType.BOOL,
                configuracao.QDRANT_CAMPO_ENTIDADE_ID: models.PayloadSchemaType.INTEGER,
            }
            if colecao != "marca_equipamento":
                campos[configuracao.QDRANT_CAMPO_UNIDADE] = models.PayloadSchemaType.INTEGER
            for campo, tipo in campos.items():
                if campo not in indices:
                    await cliente.create_payload_index(
                        collection_name=colecao,
                        field_name=campo,
                        field_schema=tipo,
                        wait=True,
                    )

            indice_texto = indices.get(configuracao.QDRANT_CAMPO_TEXTO)
            parametros = getattr(indice_texto, "params", None)
            if indice_texto is not None and getattr(parametros, "phrase_matching", None) is not True:
                await cliente.delete_payload_index(
                    collection_name=colecao,
                    field_name=configuracao.QDRANT_CAMPO_TEXTO,
                    wait=True,
                )
                indice_texto = None
            if indice_texto is None:
                await cliente.create_payload_index(
                    collection_name=colecao,
                    field_name=configuracao.QDRANT_CAMPO_TEXTO,
                    field_schema=indice_textual,
                    wait=True,
                )
