from langchain.agents import create_agent
from app.graph import ContextoGrafo
from app.tools.memoria import buscar_historico
from app.schemas.resultados_agentes import RetornoUsuarioResultado

def criar_agente_retorno_usuario(modelo, instrucao: str, ferramentas=None):
    """Compõe agente de retorno usuario com ferramentas e contrato do perfil. Usado pelo fluxo de agents."""
    return create_agent(
        model=modelo,
        system_prompt=instrucao,
        tools=[*(ferramentas or []), buscar_historico],
        context_schema=ContextoGrafo,
        response_format=RetornoUsuarioResultado,
    )
