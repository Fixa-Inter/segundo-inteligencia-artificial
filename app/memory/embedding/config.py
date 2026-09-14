from functools import lru_cache
from uuid import UUID, uuid5

from google.genai import types
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core import config


@lru_cache(maxsize=1)
def obter_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Inicialização sob demanda: importar o projeto não exige credenciais."""
    if not config.GEMINI_API_KEY:
        raise ValueError("Configure GEMINI_API_KEY para gerar embeddings.")
    _embeddings = GoogleGenerativeAIEmbeddings(
        model=config.EMBEDDING_MODEL,
        google_api_key=config.GEMINI_API_KEY,
        output_dimensionality=config.EMBEDDING_DIMENSIONS,
    )
    return _embeddings


async def gerar_embedding_consulta(descricao: str) -> list[float]:
    embeddings = obter_embeddings()
    # A integração instalada injeta RETRIEVAL_QUERY automaticamente. Embedding 2
    # não aceita task_type; usar seu cliente Google com instrução textual explícita.
    if "gemini-embedding-2" in config.EMBEDDING_MODEL:
        resultado = await embeddings.client.aio.models.embed_content(
            model=config.EMBEDDING_MODEL,
            contents=f"task: search result | query: {descricao}",
            config=types.EmbedContentConfig(output_dimensionality=config.EMBEDDING_DIMENSIONS),
        )
        return list(resultado.embeddings[0].values)
    return await embeddings.aembed_query(descricao)


def gerar_point_id(endereco_id: int, campo_id: int) -> str:
    """Contrato para o indexador: UUID5(NAMESPACE_URL, 'sede:id_operacional').

    O separador impede que (1, 23) e (12, 3) gerem a mesma entrada. O mesmo UUID
    pode existir nas duas collections, pois elas são independentes.
    """
    if any(type(valor) is not int or valor <= 0 for valor in (endereco_id, campo_id)):
        raise ValueError("Sede e ID operacional devem ser inteiros positivos.")
    return str(uuid5(UUID(config.QDRANT_POINT_NAMESPACE), f"{endereco_id}:{campo_id}"))
