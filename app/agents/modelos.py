from langchain_openai import ChatOpenAI
from app.core.configuracao import OPENAI_CHAVE_API

llm_luna = ChatOpenAI(
    model="gpt-6-luna",
    api_key=OPENAI_CHAVE_API,
    use_responses_api=True,
    reasoning={"effort": "medium"},
)

llm_rapido = llm_luna

llm_especialista = llm_luna
