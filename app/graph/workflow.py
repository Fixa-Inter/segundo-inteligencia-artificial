import inspect
import time
from functools import wraps

from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from .state import GraphState
from .context import GraphContext
from app.agents.juiz import revisar_resposta
from .nodes import (
    validar_entrada,
    supervisionar,
    executar_faq,
    executar_solicitacao,
    executar_analytics,
    executar_visualizacao,
    executar_feedback,
    julgar_resposta,
    validar_saida,
    tratar_erro,
)
from .edges import ( 
    selecionar_especialista, 
    decidir_apos_julgamento, 
    decidir_apos_entrada
)
from app.observability.metrics import GRAPH_NODE_RUNS, GRAPH_NODE_SECONDS


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
                GRAPH_NODE_SECONDS.labels(nome).observe(time.perf_counter() - inicio)
                GRAPH_NODE_RUNS.labels(nome, resultado).inc()
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
            GRAPH_NODE_SECONDS.labels(nome).observe(time.perf_counter() - inicio)
            GRAPH_NODE_RUNS.labels(nome, resultado).inc()
    return executar


def construir_grafo():
    builder = StateGraph(
        state_schema=GraphState,
        context_schema=GraphContext,
    )

# sem () pq o langgraph vai chamar a função quando for executar o nó, e não na hora de construir o grafo
    builder.add_node("guardrail_entrada", _instrumentar_no("guardrail_entrada", validar_entrada))
    builder.add_node("supervisor", _instrumentar_no("supervisor", supervisionar))
    builder.add_node("agente_faq", _instrumentar_no("agente_faq", executar_faq))
    builder.add_node("agente_solicitacao", _instrumentar_no("agente_solicitacao", executar_solicitacao))
    builder.add_node("agente_analytics", _instrumentar_no("agente_analytics", executar_analytics))
    builder.add_node("agente_visualizacao", _instrumentar_no("agente_visualizacao", executar_visualizacao))
    builder.add_node("agente_feedback", _instrumentar_no("agente_feedback", executar_feedback))
    builder.add_node("juiz", _instrumentar_no("juiz", julgar_resposta))
    builder.add_node("revisar_resposta", _instrumentar_no("revisar_resposta", revisar_resposta))
    builder.add_node("guardrail_saida", _instrumentar_no("guardrail_saida", validar_saida))
    builder.add_node("fallback", _instrumentar_no("fallback", tratar_erro))

    builder.add_edge(START, "guardrail_entrada")
    builder.add_conditional_edges(
        "guardrail_entrada",
        decidir_apos_entrada,
       {
        "supervisor": "supervisor",
        "fallback": "fallback",
       },
    )

    builder.add_conditional_edges(
        "supervisor",
        selecionar_especialista,
        {
            "faq": "agente_faq",
            "fora_de_escopo": "fallback",
            "solicitacao": "agente_solicitacao",
            "ocorrencia": "agente_solicitacao",
            "analytics": "agente_analytics",
            "visualizacao": "agente_visualizacao",
            "feedback": "agente_feedback",
            "fallback": "fallback"
        },
    )

    builder.add_edge("agente_faq", "juiz")
    builder.add_edge("agente_solicitacao", "juiz")
    builder.add_edge("agente_analytics", "juiz")
    builder.add_edge("agente_visualizacao", "juiz")
    builder.add_edge("agente_feedback", "juiz")

    builder.add_conditional_edges(
        "juiz",
        decidir_apos_julgamento,
        {
            "guardrail_saida": "guardrail_saida",
            "revisar_resposta": "revisar_resposta",
            "fallback": "fallback",
        },
    )

    builder.add_edge("guardrail_saida", END)
    builder.add_edge("revisar_resposta", "juiz")
    builder.add_edge("fallback", END)

    memory = MemorySaver()
    return builder.compile(checkpointer=memory)


grafo = construir_grafo()
