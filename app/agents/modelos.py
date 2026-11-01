from functools import lru_cache

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from app.core.configuracao import OPENAI_CHAVE_API

llm_luna = ChatOpenAI(
    model="gpt-6-luna",
    api_key=OPENAI_CHAVE_API,
    use_responses_api=True,
    reasoning={"effort": "medium"},
)

llm_rapido = llm_luna

llm_especialista = llm_luna


@lru_cache(maxsize=2)
def obter_modelo_embedding(dimensoes: int) -> OpenAIEmbeddings:
    """Reutiliza o modelo de embedding conforme a dimensão da coleção."""
    if not OPENAI_CHAVE_API:
        raise ValueError("Configure OPENAI_API_KEY para gerar embeddings.")
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        dimensions=dimensoes,
        api_key=OPENAI_CHAVE_API,
    )
