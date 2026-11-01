from functools import lru_cache
from uuid import UUID, uuid5

from langchain_openai import OpenAIEmbeddings

from app.core import configuracao


@lru_cache(maxsize=1)
def obter_vetorizador() -> OpenAIEmbeddings:
    """Inicialização sob demanda: importar o projeto não exige credenciais."""
    from app.agents.modelos import obter_modelo_embedding

    return obter_modelo_embedding(configuracao.DIMENSOES_VETORIZACAO_FAQ)


async def gerar_vetor_documento(texto: str) -> list[float]:
    vetorizador = obter_vetorizador()
    return await vetorizador.aembed_query(texto)

async def gerar_vetores_documentos(textos: list[str]) -> list[list[float]]:
    if not textos:
        return []

    vetorizador = obter_vetorizador()

    return await vetorizador.aembed_documents(textos)


@lru_cache(maxsize=1)
def obter_vetorizador_operacional() -> OpenAIEmbeddings:
    from app.agents.modelos import obter_modelo_embedding

    return obter_modelo_embedding(configuracao.DIMENSOES_VETORIZACAO_OPERACIONAL)


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
