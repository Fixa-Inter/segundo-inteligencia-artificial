from functools import lru_cache
from uuid import UUID, uuid5

from google.genai import types
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings

from app.core import configuracao


@lru_cache(maxsize=1)
def obter_vetorizador() -> GoogleGenerativeAIEmbeddings:
    """Inicialização sob demanda: importar o projeto não exige credenciais."""
    if not configuracao.GEMINI_CHAVE_API:
        raise ValueError("Configure GEMINI_API_KEY para gerar embeddings.")
    _vetorizador = GoogleGenerativeAIEmbeddings(
        model=configuracao.MODELO_VETORIZACAO,
        google_api_key=configuracao.GEMINI_CHAVE_API,
        output_dimensionality=configuracao.DIMENSOES_VETORIZACAO_FAQ,
    )
    return _vetorizador


async def gerar_vetor_documento(texto: str) -> list[float]:
    vetorizador = obter_vetorizador()
    # A integração instalada injeta RETRIEVAL_QUERY automaticamente. Embedding 2
    # não aceita task_type; usar seu cliente Google com instrução textual explícita.
    if "gemini-embedding-2" in configuracao.MODELO_VETORIZACAO:
        resultado = await vetorizador.client.aio.models.embed_content(
            model=configuracao.MODELO_VETORIZACAO,
            contents=f"task: search result | query: {texto}",
            config=types.EmbedContentConfig(output_dimensionality=configuracao.DIMENSOES_VETORIZACAO_FAQ),
        )
        return list(resultado.embeddings[0].values)
    return await vetorizador.aembed_query(texto)

async def gerar_vetores_documentos(textos: list[str]) -> list[list[float]]:
    if not textos:
        return []

    vetorizador = obter_vetorizador()

    if "gemini-embedding-2" in configuracao.MODELO_VETORIZACAO:
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

        resultado = await vetorizador.client.aio.models.embed_content(
            model=configuracao.MODELO_VETORIZACAO,
            contents=documentos,
            config=types.EmbedContentConfig(
                output_dimensionality=configuracao.DIMENSOES_VETORIZACAO_FAQ
            ),
        )

        vetores = resultado.embeddings or []

        if len(vetores) != len(textos):
            raise ValueError(
                "A quantidade de embeddings difere da quantidade de textos."
            )

        return [list(vetor.values) for vetor in vetores]

    return await vetorizador.aembed_documents(textos)


@lru_cache(maxsize=1)
def obter_vetorizador_operacional() -> OpenAIEmbeddings:
    if not configuracao.OPENAI_CHAVE_API:
        raise ValueError("Configure OPENAI_API_KEY para buscar nas collections operacionais.")
    return OpenAIEmbeddings(
        model=configuracao.MODELO_VETORIZACAO_OPERACIONAL,
        dimensions=configuracao.DIMENSOES_VETORIZACAO_OPERACIONAL,
        api_key=configuracao.OPENAI_CHAVE_API,
    )


async def gerar_vetor_operacional(texto: str) -> list[float]:
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("Informe um texto para a busca semântica.")
    vetor = await obter_vetorizador_operacional().aembed_query(texto.strip())
    if len(vetor) != configuracao.DIMENSOES_VETORIZACAO_OPERACIONAL:
        raise ValueError("Dimensão do embedding incompatível com as collections operacionais.")
    return vetor


def gerar_ponto_id(cnpj_endereco: str, campo_id: int) -> str:
    """Contrato para o indexador: UUID5(NAMESPACE_URL, 'sede:id_operacional').

    O separador impede que (1, 23) e (12, 3) gerem a mesma entrada. O mesmo UUID
    pode existir nas duas collections, pois elas são independentes.
    """
    if any(type(valor) is not int or valor <= 0 for valor in (campo_id,)):
        raise ValueError("ID operacional deve ser um inteiro positivo.")
    return str(uuid5(UUID(configuracao.QDRANT_ESPACO_NOMES_PONTOS), f"{cnpj_endereco}:{campo_id}"))
