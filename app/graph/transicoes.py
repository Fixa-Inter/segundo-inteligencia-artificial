from .estado import EstadoGrafo

# Importando o state.py do app.graph para poder acessar o estado do grafo

def decidir_apos_entrada(estado: EstadoGrafo) -> str:
    """Seleciona supervisor ou fallback conforme validação da entrada. Usado pelo fluxo de graph."""
    if estado.get("entrada_valida"):
        return "supervisor"

    return "fallback"

def selecionar_especialista(estado: EstadoGrafo) -> str:
    """Seleciona o próximo nó por intenção, erro e necessidade de esclarecimento. Usado pelo fluxo de graph."""
    if estado.get("erro"):
        return "fallback"
    if estado.get("esclarecimento_roteamento"):
        return "esclarecimento"

    return estado.get("intencao") or "fallback"

def decidir_apos_visualizacao(estado: EstadoGrafo) -> str:
    """Decide se visualização segue para julgamento ou finalização sem consulta. Usado pelo fluxo de graph."""
    if estado.get("motivo_bloqueio") == "visualizacao_mobile":
        return "classificar_emocao"
    return "juiz"


def decidir_apos_julgamento(estado: EstadoGrafo) -> str:
    """Decide entre proteção de saída, execução de operações, revisão textual ou fallback. Usado pelo fluxo de graph."""
    veredito = estado.get("veredito")

    if veredito == "aprovado":
        if estado.get("operacoes_pendentes"):
            return "executar_operacoes"
        return "proteger_saida"

    if veredito == "revisar" and estado.get("tentativas", 0) == 1 and not estado.get("erro"):
        return "revisar_resposta"

    return "fallback"
