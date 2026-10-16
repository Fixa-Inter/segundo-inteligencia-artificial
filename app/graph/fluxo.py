import inspect
import time
from functools import wraps

from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from .estado import EstadoGrafo
from .contexto import ContextoGrafo
from app.agents.juiz import revisar_resposta
from .nos import (
    validar_entrada,
    supervisionar,
    executar_faq,
    executar_ajuda_geral,
    executar_solicitacao,
    executar_indicadores,
    executar_visualizacao,
    executar_retorno_usuario,
    julgar_resposta,
    validar_saida,
    tratar_erro,
)
from .transicoes import ( 
    selecionar_especialista, 
    decidir_apos_julgamento, 
    decidir_apos_entrada
)
from app.observability.metricas import EXECUCOES_NO_GRAFO, DURACAO_NO_GRAFO


def _instrumentar_no(nome, funcao):
    """Mede duração e erros dos nós sem alterar sua lógica de negócio."""
    if inspect.iscoroutinefunction(funcao):
        @wraps(funcao)
        async def executar(*args, **kwargs):
            inicio = time.perf_counter()
            resultado = "error"
            try:
                saida = await funcao(*args, **kwargs)
                resultado = "error" if isinstance(saida, dict) and saida.get("erro") else "success"
                return saida
            finally:
                DURACAO_NO_GRAFO.labels(nome).observe(time.perf_counter() - inicio)
                EXECUCOES_NO_GRAFO.labels(nome, resultado).inc()
        return executar

    @wraps(funcao)
    def executar(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = "error"
        try:
            saida = funcao(*args, **kwargs)
            resultado = "error" if isinstance(saida, dict) and saida.get("erro") else "success"
            return saida
        finally:
            DURACAO_NO_GRAFO.labels(nome).observe(time.perf_counter() - inicio)
            EXECUCOES_NO_GRAFO.labels(nome, resultado).inc()
    return executar


def construir_grafo():
    construtor = StateGraph(
        state_schema=EstadoGrafo,
        context_schema=ContextoGrafo,
    )

# sem () pq o langgraph vai chamar a função quando for executar o nó, e não na hora de construir o grafo
    construtor.add_node("proteger_entrada", _instrumentar_no("proteger_entrada", validar_entrada))
    construtor.add_node("supervisor", _instrumentar_no("supervisor", supervisionar))
    construtor.add_node("agente_faq", _instrumentar_no("agente_faq", executar_faq))
    construtor.add_node("agente_ajuda_geral", _instrumentar_no("agente_ajuda_geral", executar_ajuda_geral))
    construtor.add_node("agente_solicitacao", _instrumentar_no("agente_solicitacao", executar_solicitacao))
    construtor.add_node("agente_analytics", _instrumentar_no("agente_analytics", executar_indicadores))
    construtor.add_node("agente_visualizacao", _instrumentar_no("agente_visualizacao", executar_visualizacao))
    construtor.add_node("agente_feedback", _instrumentar_no("agente_feedback", executar_retorno_usuario))
    construtor.add_node("juiz", _instrumentar_no("juiz", julgar_resposta))
    construtor.add_node("revisar_resposta", _instrumentar_no("revisar_resposta", revisar_resposta))
    construtor.add_node("proteger_saida", _instrumentar_no("proteger_saida", validar_saida))
    construtor.add_node("fallback", _instrumentar_no("fallback", tratar_erro))

    construtor.add_edge(START, "proteger_entrada")
    construtor.add_conditional_edges(
        "proteger_entrada",
        decidir_apos_entrada,
       {
        "supervisor": "supervisor",
        "fallback": "fallback",
       },
    )

    construtor.add_conditional_edges(
        "supervisor",
        selecionar_especialista,
        {
            "faq": "agente_faq",
            "ajuda_geral": "agente_ajuda_geral",
            "fora_de_escopo": "fallback",
            "solicitacao": "agente_solicitacao",
            "ocorrencia": "agente_solicitacao",
            "analytics": "agente_analytics",
            "visualizacao": "agente_visualizacao",
            "feedback": "agente_feedback",
            "fallback": "fallback",
            "esclarecimento": "juiz",
        },
    )

    construtor.add_edge("agente_faq", "juiz")
    construtor.add_edge("agente_ajuda_geral", "juiz")
    construtor.add_edge("agente_solicitacao", "juiz")
    construtor.add_edge("agente_analytics", "juiz")
    construtor.add_edge("agente_visualizacao", "juiz")
    construtor.add_edge("agente_feedback", "juiz")

    construtor.add_conditional_edges(
        "juiz",
        decidir_apos_julgamento,
        {
            "proteger_saida": "proteger_saida",
            "revisar_resposta": "revisar_resposta",
            "fallback": "fallback",
        },
    )

    construtor.add_edge("proteger_saida", END)
    construtor.add_edge("revisar_resposta", "juiz")
    construtor.add_edge("fallback", END)

    memoria = MemorySaver()
    return construtor.compile(checkpointer=memoria)


grafo = construir_grafo()
