from qdrant_client import AsyncQdrantClient, models

from app.core import config
from app.memory.embedding.config import gerar_embedding_consulta


def _id_field(collection: str) -> str:
    if collection == config.QDRANT_CATEGORIA_COLLECTION:
        return config.QDRANT_CATEGORIA_ID_FIELD
    if collection == config.QDRANT_LOCAL_COLLECTION:
        return config.QDRANT_LOCAL_ID_FIELD
    raise ValueError("Collection não permitida.")

def _campo(payload: dict, caminho: str):
    valor = payload
    for parte in caminho.split("."):
        valor = valor[parte]
    return valor

def _filtro(endereco_id: int, registro_id: int | None = None, collection: str = ""):
    if type(endereco_id) is not int or endereco_id <= 0:
        raise ValueError("Sede autenticada obrigatória para todas as consultas.")
    condicoes = [models.FieldCondition(
        key=config.QDRANT_TENANT_FIELD, match=models.MatchValue(value=endereco_id)
    )]
    if registro_id is not None:
        condicoes.append(models.FieldCondition(
            key=_id_field(collection), match=models.MatchValue(value=registro_id)
        ))
    return models.Filter(must=condicoes)

def _registro(ponto, endereco_id: int, collection: str) -> tuple[int, str]:
    payload = ponto.payload or {}
    try:
        sede = _campo(payload, config.QDRANT_TENANT_FIELD)
        registro_id = _campo(payload, _id_field(collection))
        descricao = _campo(payload, config.QDRANT_DESCRIPTION_FIELD)
    except (KeyError, TypeError):
        raise ValueError("Payload Qdrant incompatível com os campos configurados.") from None
    if type(sede) is not int or sede != endereco_id:
        raise ValueError("Resultado fora da sede autenticada.")
    if type(registro_id) is not int or registro_id <= 0:
        raise ValueError("O payload deve conter o ID operacional inteiro positivo.")
    if not isinstance(descricao, str) or not descricao.strip():
        raise ValueError("Descrição ausente no payload.")
    return registro_id, descricao.strip()

async def _buscar(collection: str, texto: str, endereco_id: int, client: AsyncQdrantClient) -> dict[int, str]:
    filtro = _filtro(endereco_id)
    if not texto.strip() or not 1 <= config.VECTOR_SEARCH_LIMIT <= 20:
        raise ValueError("Informe uma descrição e um limite entre 1 e 20.")
    vetor = await gerar_embedding_consulta(texto.strip())
    if len(vetor) != config.EMBEDDING_DIMENSIONS:
        raise ValueError("Dimensão do embedding incompatível com a collection.")
    resultado = await client.query_points(
        collection_name=collection, query=vetor, using=config.QDRANT_VECTOR_NAME,
        query_filter=filtro, limit=config.VECTOR_SEARCH_LIMIT, score_threshold=config.VECTOR_SCORE_THRESHOLD,
        with_payload=True, with_vectors=False,
    )
    registros = {}
    for ponto in resultado.points:
        registro_id, descricao = _registro(ponto, endereco_id, collection)
        if registro_id in registros and registros[registro_id] != descricao:
            raise ValueError("ID operacional duplicado com descrições diferentes.")
        registros[registro_id] = descricao
    return registros

async def buscar_categoria_equipamento(descricao: str, endereco_id: int, client: AsyncQdrantClient) -> dict[int, str]:
    return await _buscar(config.QDRANT_CATEGORIA_COLLECTION, descricao, endereco_id, client)

async def buscar_local_endereco(descricao: str, endereco_id: int, client: AsyncQdrantClient) -> dict[int, str]:
    return await _buscar(config.QDRANT_LOCAL_COLLECTION, descricao, endereco_id, client)

async def validar_selecao(collection: str, registro_id: int,
                          descricao: str, endereco_id: int, client: AsyncQdrantClient) -> None:
    if collection not in (config.QDRANT_CATEGORIA_COLLECTION, config.QDRANT_LOCAL_COLLECTION):
        raise ValueError("Collection não permitida.")
    pontos, _ = await client.scroll(
        collection_name=collection,
        scroll_filter=_filtro(endereco_id, registro_id, collection),
        limit=2, with_payload=True, with_vectors=False,
    )
    if len(pontos) != 1 or _registro(pontos[0], endereco_id, collection) != (registro_id, descricao):
        raise ValueError("Cadastro alterado ou indisponível. Consulte e confirme novamente.")
