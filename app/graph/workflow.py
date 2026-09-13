from langgraph.graph import END, START, StateGraph

from .state import GraphState
from .nodes import (
    validar_entrada,
    supervisionar,
    executar_faq,
    julgar_resposta,
    validar_saida,
    tratar_erro,
)
from .edges import ( 
    selecionar_especialista, 
    decidir_apos_julgamento, 
    decidir_apos_entrada
)


def construir_grafo():
    builder = StateGraph(GraphState)

# sem () pq o langgraph vai chamar a função quando for executar o nó, e não na hora de construir o grafo
    builder.add_node("guardrail_entrada", validar_entrada)
    builder.add_node("supervisor", supervisionar)
    builder.add_node("agente_faq", executar_faq)
    builder.add_node("juiz", julgar_resposta)
    builder.add_node("guardrail_saida", validar_saida)
    builder.add_node("fallback", tratar_erro)

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
            "solicitacao": "fallback",
            "analytics": "fallback",
            "visualizacao": "fallback",
            "feedback": "fallback",
            "fallback": "fallback"
        },
    )

    builder.add_edge("agente_faq", "juiz")

    builder.add_conditional_edges(
        "juiz",
        decidir_apos_julgamento,
        {
            "guardrail_saida": "guardrail_saida",
            "fallback": "fallback",
        },
    )

    builder.add_edge("guardrail_saida", END)
    builder.add_edge("fallback", END)

    return builder.compile()


grafo = construir_grafo()