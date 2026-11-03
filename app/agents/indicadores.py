from langchain.agents import create_agent
from app.graph import ContextoGrafo
from app.tools.memoria import buscar_historico
from app.tools.metricas_kpis import FERRAMENTAS_INDICADORES
from app.schemas.resultados_agentes import IndicadoresResultado

def criar_agente_indicadores(modelo, instrucao: str, ferramentas=None):
    """Compõe agente de indicadores com ferramentas e contrato do perfil. Usado pelo fluxo de agents."""
    ferramentas_por_nome = {}
    for ferramenta in [
        *FERRAMENTAS_INDICADORES,
        *(ferramentas or []),
        buscar_historico,
    ]:
        ferramentas_por_nome.setdefault(ferramenta.name, ferramenta)
    return create_agent(
        model=modelo,
        system_prompt=instrucao,
        tools=list(ferramentas_por_nome.values()),
        context_schema=ContextoGrafo,
        response_format=IndicadoresResultado,
    )
