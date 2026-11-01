"""Executa somente operações que passaram pelo juiz e produz confirmações factuais."""

import logging
from types import SimpleNamespace

from langchain_core.messages import AIMessage

from app.services.operacoes import aprovacao_operacoes, resumo
from app.observability.metricas import registrar_operacao

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
    if tipo == "feedback":
        from app.services.feedback import criar_feedback
        return await criar_feedback(contexto["usuario"], **dados)
    if tipo == "edicao":
        from app.memory.persistencia import obter_acao
        from app.tools.ajuda_geral.edicoes import _executar_pendente
        acao = await obter_acao(contexto["session_id"], contexto["usuario"].usuario_id)
        if not acao:
            return {"status": "ERRO_VALIDACAO", "mensagem": "A proposta de alteração não está mais disponível."}
        return await _executar_pendente(
            contexto, contexto["usuario"], contexto["session_id"], acao, operacao_aprovada=dados,
        )
    raise ValueError("Operação não permitida.")


def resultado_indeterminado() -> dict:
    return {"status": "RESULTADO_INDETERMINADO",
            "mensagem": "O processamento pode ter ocorrido. Confira seus registros antes de repetir o pedido."}


def texto_resultados(resultados: list[dict]) -> str:
    mensagens = []
    nomes = {"solicitacao": "Solicitação cadastrada com sucesso.",
             "ocorrencia": "Ocorrência cadastrada com sucesso.",
             "feedback": "Feedback registrado com sucesso.", "edicao": "Alteração realizada com sucesso."}
    for item in resultados:
        resultado = item["resultado"]
        status = resultado.get("status")
        if status == "SUCESSO":
            mensagem = nomes[item["tipo"]]
        elif status == "RESULTADO_INDETERMINADO":
            mensagem = resultado_indeterminado()["mensagem"]
        else:
            mensagem = {
                "solicitacao": "A solicitação não foi enviada. Confira os dados e sua permissão antes de tentar novamente.",
                "ocorrencia": "A ocorrência não foi enviada. Confira os dados e sua permissão antes de tentar novamente.",
                "feedback": "O feedback não foi registrado. Confira o comentário e sua permissão antes de tentar novamente.",
                "edicao": "A alteração não foi realizada. Confira a proposta e sua permissão antes de tentar novamente.",
            }[item["tipo"]]
        mensagens.append(mensagem)
    return "\n\n".join(mensagens)


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
        texto = "Não foi possível validar a aprovação. Nenhuma nova operação foi enviada."
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
            if operacao["tipo"] in {"solicitacao", "ocorrencia"}:
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
