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
        output_dimensionality=config.EMBEDDING_DIMENSIONS_EQUIPAMENTO_LOCAL,
    )
    return _embeddings


async def gerar_embedding_documento(texto: str) -> list[float]:
    embeddings = obter_embeddings()
    # A integração instalada injeta RETRIEVAL_QUERY automaticamente. Embedding 2
    # não aceita task_type; usar seu cliente Google com instrução textual explícita.
    if "gemini-embedding-2" in config.EMBEDDING_MODEL:
        resultado = await embeddings.client.aio.models.embed_content(
            model=config.EMBEDDING_MODEL,
            contents=f"task: search result | query: {texto}",
            config=types.EmbedContentConfig(output_dimensionality=config.EMBEDDING_DIMENSIONS_EQUIPAMENTO_LOCAL),
        )
        return list(resultado.embeddings[0].values)
    return await embeddings.aembed_query(texto)

async def gerar_embeddings_documentos(textos: list[str]) -> list[list[float]]:
    if not textos:
        return []

    embeddings = obter_embeddings()

    if "gemini-embedding-2" in config.EMBEDDING_MODEL:
        documentos = [
            types.Content(
                parts=[
                    types.Part.from_text(
                        text=f"title: none | text: {texto}"
                    )
                ]
            )
            for texto in textos
        ]

        resultado = await embeddings.client.aio.models.embed_content(
            model=config.EMBEDDING_MODEL,
            contents=documentos,
            config=types.EmbedContentConfig(
                output_dimensionality=config.EMBEDDING_DIMENSIONS_EQUIPAMENTO_LOCAL
            ),
        )

        vetores = resultado.embeddings or []

        if len(vetores) != len(textos):
            raise ValueError(
                "A quantidade de embeddings difere da quantidade de textos."
            )

        return [list(vetor.values) for vetor in vetores]

    return await embeddings.aembed_documents(textos)


def gerar_point_id(cnpj_endereco: str, campo_id: int) -> str:
    """Contrato para o indexador: UUID5(NAMESPACE_URL, 'sede:id_operacional').

    O separador impede que (1, 23) e (12, 3) gerem a mesma entrada. O mesmo UUID
    pode existir nas duas collections, pois elas são independentes.
    """
    if any(type(valor) is not int or valor <= 0 for valor in (campo_id,)):
        raise ValueError("ID operacional deve ser um inteiro positivo.")
    return str(uuid5(UUID(config.QDRANT_POINT_NAMESPACE), f"{cnpj_endereco}:{campo_id}"))
