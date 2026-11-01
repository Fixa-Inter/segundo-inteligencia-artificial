"""Evidencias extraidas dos resultados reais das tools, sem chamadas ao LLM."""

import json
from app.observability.metricas import registrar_operacao

from langchain_core.messages import AIMessage, ToolMessage, SystemMessage
from app.agents.prompts.reutilizaveis import construir_contexto_temporal


def ids_chamadas(mensagens) -> set[str]:
    ids = set()
    for mensagem in mensagens:
        if isinstance(mensagem, AIMessage):
            ids.update(chamada["id"] for chamada in mensagem.tool_calls)
        elif isinstance(mensagem, ToolMessage):
            ids.add(mensagem.tool_call_id)
    return ids


def extrair_evidencias(mensagens, ids_anteriores: set[str], formato_saida: str) -> list[str]:
    chamadas = {
        chamada["id"]: chamada["name"]
        for mensagem in mensagens
        if isinstance(mensagem, AIMessage)
        for chamada in mensagem.tool_calls
        if chamada["id"] not in ids_anteriores
        and chamada["name"] != formato_saida
    }
    evidencias = []
    registrados = set()
    for mensagem in mensagens:
        if not isinstance(mensagem, ToolMessage):
            continue
        chamada_id = mensagem.tool_call_id
        if chamada_id not in chamadas or chamada_id in registrados:
            continue
        resultado = mensagem.content
        if isinstance(resultado, str):
            try:
                resultado = json.loads(resultado)
            except ValueError:
                pass
        # O status de transporte nao equivale ao sucesso da operacao de negocio.
        status = resultado.get("status") if isinstance(resultado, dict) else None
        if chamadas[chamada_id] in {"criar_solicitacao", "criar_ocorrencia"}:
            texto_status = str(status or "").upper()
            resultado_operacao = (
                "success" if texto_status == "SUCESSO"
                else "indeterminate" if "INDETERMINADO" in texto_status
                else "pending" if texto_status.startswith(("AGUARDANDO", "CONFIRMACAO", "RASCUNHO", "OPERACAO_PREPARADA"))
                else "denied" if "ACESSO_NEGADO" in texto_status
                else "error"
            )
            registrar_operacao(
                "solicitacao" if chamadas[chamada_id] == "criar_solicitacao" else "ocorrencia",
                resultado_operacao,
            )
        evidencias.append(json.dumps({
            "ferramenta": chamadas[chamada_id],
            "chamada_id": chamada_id,
            "status_execucao": mensagem.status,
            "status_operacao": status,
            "resultado": resultado,
        }, ensure_ascii=False))
        registrados.add(chamada_id)
    return evidencias


async def executar_com_evidencias(agente, estado, contexto, formato_saida):
    mensagens = list(estado.get("messages", []))
    # Captura antes do invoke: o agente pode atribuir IDs ou alterar mensagens.
    anteriores = ids_chamadas(mensagens)
    mensagens.insert(0, SystemMessage(content=(
        contexto.get("contexto_temporal") or construir_contexto_temporal()
    )))
    resultado = await agente.ainvoke({"messages": mensagens}, context=contexto)
    novas = extrair_evidencias(
        resultado.get("messages", []), anteriores, formato_saida.__name__,
    )
    return resultado, [*estado.get("evidencias", []), *novas]
