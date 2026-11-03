"""Renderização determinística de textos, usada pelo grafo, tools e serviços."""

from app.core import (
    MENSAGENS,
    NOMES_CAMPOS,
    RESPOSTAS_OPERACAO_SUCESSO,
    RESPOSTAS_OPERACAO_FALHA,
    TEXTOS_CONFIRMACAO,
    RESPOSTAS_BLOQUEIO,
    TEXTOS_COMPRAS,
    COMPLEMENTOS_BASE_CALCULO,
)

def formatar_resposta(chave: str, **valores) -> str:
    """Interpola somente um template conhecido do catálogo de mensagens."""
    return MENSAGENS[chave].format(**valores)


def escolher_resposta(condicao, quando_sim: str, quando_nao: str) -> str:
    """Seleciona um texto do catálogo a partir de um resultado já apurado."""
    return MENSAGENS[quando_sim if condicao else quando_nao]


def resposta_bloqueio_seguranca(categoria: str) -> dict | None:
    """Obtém motivo/texto padronizados para a categoria de segurança. Usado pelo fluxo de apresentacao."""
    if categoria in RESPOSTAS_BLOQUEIO:
        return {"bloqueado": True, **RESPOSTAS_BLOQUEIO[categoria]}
    return None


def resultado_indeterminado() -> dict:
    """Retorna orientação que impede declarar sucesso/falha definitiva ou repetir envio incerto. Usado por texto_resultados."""
    return {"status": "RESULTADO_INDETERMINADO",
            "mensagem": MENSAGENS['o_processamento_pode_ter_ocorrido_confira_seus_registros_antes_de_repetir_o']}


def texto_resultados(resultados: list[dict]) -> str:
    """Renderiza resultados separados de operações, preservando sucessos e falhas parciais. Usado pelo fluxo de apresentacao."""
    mensagens = []
    for item in resultados:
        resultado = item["resultado"]
        status = resultado.get("status")
        if item["tipo"] in {"atualizacao_solicitacao", "atualizacao_ocorrencia"}:
            prefixo = "ocorrencia_atualizacao" if item["tipo"] == "atualizacao_ocorrencia" else "atualizacao"
            mensagens.append(resultado_indeterminado()["mensagem"] if status == "RESULTADO_INDETERMINADO" else
                             MENSAGENS[f"{prefixo}_sucesso" if status == "SUCESSO" else f"{prefixo}_falha"])
            continue
        if status == "SUCESSO":
            mensagem = RESPOSTAS_OPERACAO_SUCESSO[item["tipo"]]
        elif status == "RESULTADO_INDETERMINADO":
            mensagem = resultado_indeterminado()["mensagem"]
        else:
            mensagem = RESPOSTAS_OPERACAO_FALHA[item["tipo"]]
        mensagens.append(mensagem)
    return "\n\n".join(mensagens)
