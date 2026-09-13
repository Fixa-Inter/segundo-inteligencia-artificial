# Importando o state.py do app.graph para poder acessar o estado do grafo
from .state import GraphState

def decidir_apos_entrada(state: GraphState) -> str:
    if state.get("entrada_valida"):
        return "supervisor"

    return "fallback"

def selecionar_especialista(state: GraphState) -> str:
    if state.get("erro"):
        return "fallback"

    return state.get("intencao", "fallback")

def decidir_apos_julgamento(state: GraphState) -> str:
    veredito = state.get("veredito")

    if veredito == "aprovado":
        return "guardrail_saida"

    return "fallback"