"""Executa somente operações que passaram pelo juiz e produz confirmações factuais."""


import logging
from types import SimpleNamespace

from langchain_core.messages import AIMessage

from app.services.operacoes import aprovacao_operacoes, resumo
from app.observability.metricas import registrar_operacao

from app.core.respostas import MENSAGENS, RESPOSTA_APROVACAO_INVALIDA
from app.graph.respostas_padrao import texto_resultados, resultado_indeterminado

registrador = logging.getLogger(__name__)


async def executar_servico(documento: dict, contexto: dict) -> dict:
    """Lista explícita de serviços permitidos; o modelo não escolhe funções Python."""
    tipo, dados = documento["tipo"], documento["dados"]
    runtime = SimpleNamespace(context=contexto)
    if tipo == "solicitacao":
        from app.tools.solicitacoes.criarSolicitacao import processar_solicitacao
        return await processar_solicitacao(runtime, operacao_aprovada=dados)
    if tipo == "ocorrencia":
        from app.tools.ocorrencias.criarOcorrencia import processar_ocorrencia
        return await processar_ocorrencia(runtime, operacao_aprovada=dados)
    if tipo == "evento":
        from app.tools.eventos.criarEvento import processar_evento
        return await processar_evento(runtime, operacao_aprovada=dados)
    if tipo == "feedback":
        from app.services.feedback import criar_feedback
        return await criar_feedback(contexto["usuario"], **dados)
    if tipo == "edicao":
        from app.memory.persistencia import obter_acao
        from app.tools.ajuda_geral.edicoes import _executar_pendente
        acao = await obter_acao(contexto["session_id"], contexto["usuario"].usuario_id)
        if not acao:
            return {"status": "ERRO_VALIDACAO", "mensagem": MENSAGENS['a_proposta_de_alteracao_nao_esta_mais_disponivel']}
        return await _executar_pendente(
            contexto, contexto["usuario"], contexto["session_id"], acao, operacao_aprovada=dados,
        )
    raise ValueError("Operação não permitida.")


def resposta_resultados(resultados: list[dict]) -> dict:
    texto = texto_resultados(resultados)
    return {"resultados_operacoes": resultados, "resposta_especialista": texto,
            "resposta_candidata": texto, "resposta_final": texto,
            "messages": [AIMessage(content=texto)], "propostas_apresentadas": [],
            "erro": None, "saida_bloqueada": False}


async def executar_operacoes(estado: dict, runtime) -> dict:
    from app.memory.persistencia import operacoes as persistencia

    contexto = runtime.context
    operacoes = estado.get("operacoes_pendentes", [])
    if (not operacoes or estado.get("veredito") != "aprovado" or estado.get("erro")
            or estado.get("aprovacao_operacoes") != aprovacao_operacoes(operacoes, contexto)):
        texto = RESPOSTA_APROVACAO_INVALIDA
        return {"erro": "Não foi possível validar a aprovação da operação.",
                "resposta_especialista": texto, "resposta_candidata": texto}

    resultados = []
    for operacao in operacoes:
        iniciou = False
        try:
            documento = await persistencia.obter(
                operacao["id"], contexto["usuario"].usuario_id, contexto["session_id"],
            )
            if documento is None or resumo(documento) != operacao:
                raise ValueError("Os dados da operação não correspondem à aprovação.")
            if documento["estado"] == "concluida":
                resultado = documento["resultado"]
            elif documento["estado"] != "preparada":
                resultado = resultado_indeterminado()
            else:
                iniciou = await persistencia.iniciar(documento, estado["aprovacao_operacoes"])
                if iniciou:
                    try:
                        resultado = await executar_servico(documento, contexto)
                    except Exception:
                        registrador.exception("Resultado da operação %s indeterminado", documento["_id"])
                        resultado = resultado_indeterminado()
                else:
                    resultado = resultado_indeterminado()
        except Exception:
            registrador.exception("Falha ao validar ou iniciar operação")
            # A falha pode ter acontecido depois de adquirir a operação no Mongo.
            # Não repete a escrita quando não foi possível confirmar o estado.
            resultado = resultado_indeterminado()
        if not isinstance(resultado, dict) or not isinstance(resultado.get("status"), str):
            resultado = resultado_indeterminado()
        item = {"operacao_id": operacao["id"], "tipo": operacao["tipo"], "resultado": resultado}
        resultados.append(item)
        contexto.setdefault("resultados_operacoes", []).append(item)
        if iniciou:
            if operacao["tipo"] in {"solicitacao", "ocorrencia", "evento"}:
                status = resultado["status"]
                desfecho = ("success" if status == "SUCESSO" else
                            "indeterminate" if status == "RESULTADO_INDETERMINADO" else "error")
                registrar_operacao(operacao["tipo"], desfecho)
            try:
                await persistencia.finalizar(documento, resultado)
            except Exception:
                # O resultado real continua disponível para a resposta desta requisição.
                # O estado executando impede uma nova escrita até a reconciliação.
                registrador.exception("Resultado da operação %s não persistido", operacao["id"])
    return resposta_resultados(resultados)
