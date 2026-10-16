from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from app.core.configuracao import GROQ_CHAVE_API, OPENAI_CHAVE_API

llm_luna = ChatOpenAI(
    model="gpt-6-luna",
    api_key=OPENAI_CHAVE_API,
    use_responses_api=True,
    reasoning={"effort": "medium"},
)

llm_groq = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.7,
    api_key=GROQ_CHAVE_API,
)

llm_rapido = llm_luna

llm_especialista = llm_luna
