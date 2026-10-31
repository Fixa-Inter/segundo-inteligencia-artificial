# Importando o state.py do app.graph para poder acessar o estado do grafo
from .estado import EstadoGrafo

def decidir_apos_entrada(estado: EstadoGrafo) -> str:
    if estado.get("entrada_valida"):
        return "supervisor"

    return "fallback"

def selecionar_especialista(estado: EstadoGrafo) -> str:
    if estado.get("erro"):
        return "fallback"
    if estado.get("esclarecimento_roteamento"):
        return "esclarecimento"

    return estado.get("intencao") or "fallback"

def decidir_apos_visualizacao(estado: EstadoGrafo) -> str:
    if estado.get("motivo_bloqueio") == "visualizacao_mobile":
        return "classificar_emocao"
    return "juiz"


def decidir_apos_julgamento(estado: EstadoGrafo) -> str:
    veredito = estado.get("veredito")

    if veredito == "aprovado":
        return "proteger_saida"

    if veredito == "revisar" and estado.get("tentativas", 0) == 1 and not estado.get("erro"):
        return "revisar_resposta"

    return "fallback"
