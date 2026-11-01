import logging
from typing import Literal, cast
from uuid import uuid4
from app.observability.tracing import somente_metricas

from langchain_core.messages import HumanMessage, AIMessage
from fastapi import HTTPException, status

from app.graph.contexto import ContextoGrafo
from app.graph.estado import EstadoGrafo, limpar_visualizacao
from app.graph.fluxo import grafo
from app.graph.operacoes import resposta_resultados
from app.schemas import UsuarioContexto
from app.core import Emocao
from app.memory.persistencia import salvar_mensagem
from app.memory.persistencia.salvar_mensagem import marcar_confirmacao_mensagem
from app.memory.persistencia import recuperar_mensagens
from app.memory.persistencia import obter_documento_sessao_id
from app.memory.persistencia import (
    obter_rascunho_solicitacao,
    obter_quantidade_anexos_pendentes,
)
from app.memory.persistencia import obter_acao
from app.memory.persistencia.analise_compra import obter_analise_compra
from app.memory.persistencia import atualizar_rascunho_solicitacao

from app.guardrails import anonimizar_entrada
from app.core.propostas import campos_pendentes, resumo_confirmacao
from app.agents.prompts.reutilizaveis import construir_contexto_temporal
from app.services.visualizacoes.publicacao import publicar_visualizacao, LimiteVisualizacaoExcedido
from app.observability.metricas import (
    MonitorMetricas,
    finalizar_resolucoes,
    marcar_falha_requisicao,
)


Perfil = Literal[
    "solicitante",
    "tecnico",
    "gestor",
    "administrador"
]

PERFIS_VALIDOS = {
    "solicitante",
    "tecnico",
    "gestor",
    "administrador"
}


def criar_estado_inicial(
    mensagens: list[AIMessage|HumanMessage],
    usuario: UsuarioContexto,
) -> EstadoGrafo:

    if not mensagens:
        raise ValueError("A mensagem não pode estar vazia.")

    perfil_normalizado = usuario.tipo_acesso.strip().lower()

    if perfil_normalizado not in PERFIS_VALIDOS:
        raise ValueError("O perfil de usuário é inválido.")

    perfil = cast(Perfil, perfil_normalizado)

    return {
        **limpar_visualizacao(),
        "messages": mensagens,
        "user_id": usuario.usuario_id,
        "perfil": perfil,
        "tentativas": 0,
        "resposta_final": "",
        "emocao": Emocao.NEUTRO.value,
        "saida_bloqueada": False,
        "resposta_especialista": "",
        "resposta_candidata": "",
        "feedback_juiz": "",
        "evidencias": [],
        "operacoes_pendentes": [],
        "aprovacao_operacoes": None,
        "resultados_operacoes": [],
        "erro": None,
        "entrada_valida": False,
        "mensagem_anonimizada": "",
        "mapa_pii": {},
        "motivo_bloqueio": None,
        "justificativa_roteamento": "",
        "veredito": None,
        "intencao": None,
        "analise_compra_pendente": None,
        "esclarecimento_roteamento": False,
        "propostas_apresentadas": [],
        "cadastro_em_andamento": False,
        "continua_pendente": False,
        "contexto_temporal": construir_contexto_temporal(),
    }


@somente_metricas
async def executar_grafo(
    mensagem: str,
    usuario: UsuarioContexto,
    thread_id: str,
    imagens: list[str] | None = None,
    plataforma: Literal["web", "mobile"] = "web",
) -> EstadoGrafo:
    usuario_id = usuario.usuario_id

    if not thread_id:
        raise ValueError("O thread_id não pode estar vazio.")

    sessao_id_interno = (
        f"{usuario_id}:{thread_id}"
    )
    
    # ANONIMIZAR A ENTRADA E SALVAR A MENSAGEM COM O MÉTODO SALVAR MENSAGEM
    mensagem_anonimizada, mapa_pii = anonimizar_entrada(
        mensagem
    )

    configuracao = {
        "configurable": {
            "thread_id": sessao_id_interno
        },
        "callbacks": [MonitorMetricas()] if MonitorMetricas else [],
    }
    estado = grafo.get_state(configuracao)

    mensagens = []
    if not estado.values:
        documento_id = await obter_documento_sessao_id(thread_id,usuario_id)
        historico = await recuperar_mensagens(documento_id,usuario_id)

        for item in historico:
            if item["role"] == "human":
                mensagens.append(HumanMessage(content=item["content"]))
            elif item["role"] == "assistant":
                mensagens.append(AIMessage(content=item["content"]))

    mensagens.append(HumanMessage(content=mensagem_anonimizada))

    await salvar_mensagem(
        thread_id,
        "human",
        mensagem_anonimizada,
        usuario.usuario_id,
        imagens=imagens,
        associar_imagens=False,
    )

    rascunho_solicitacao = await obter_rascunho_solicitacao(
        sessao_id=thread_id,
        usuario_id=usuario_id,
    )
    
    estado_inicial = criar_estado_inicial(
        mensagens=mensagens,
        usuario=usuario,
    )
    estado_inicial["mensagem_anonimizada"] = mensagem_anonimizada
    estado_inicial["mapa_pii"] = mapa_pii
    estado_inicial["solicitacao_pendente"] = rascunho_solicitacao
    estado_inicial["ocorrencia_pendente"] = await obter_rascunho_solicitacao(
        thread_id, usuario_id, tipo="ocorrencia",
    )
    estado_inicial["ajuda_geral_pendente"] = await obter_acao(thread_id, usuario_id)
    estado_inicial["analise_compra_pendente"] = await obter_analise_compra(thread_id, usuario_id)
    estado_inicial["imagens_recebidas"] = bool(imagens)
    estado_inicial["anexos_pendentes"] = await obter_quantidade_anexos_pendentes(
        thread_id, usuario_id,
    )

    contexto: ContextoGrafo = {
        "usuario": usuario,
        "imagens": list(imagens or []),
        "session_id": thread_id,
        "mensagem_atual": mensagem_anonimizada,
        "turno_id": str(uuid4()),
        "contexto_temporal": estado_inicial["contexto_temporal"],
        "plataforma": plataforma,
        "operacoes_pendentes": [],
        "resultados_operacoes": [],
    }

    try:
        resultado = await grafo.ainvoke(
            estado_inicial,
            config=configuracao,
            context=contexto,
        )
    except Exception:
        if not contexto["resultados_operacoes"]:
            raise
        logging.getLogger(__name__).exception("Falha do grafo após executar uma operação")
        tipo = contexto["resultados_operacoes"][-1]["tipo"]
        resultado = {**limpar_visualizacao(), **resposta_resultados(contexto["resultados_operacoes"]),
                     "intencao": "ajuda_geral" if tipo == "edicao" else tipo, "emocao": Emocao.ALERTA.value}
    finally:
        finalizar_resolucoes()

    if contexto["resultados_operacoes"] and (
        resultado.get("erro") or resultado.get("saida_bloqueada")
        or not isinstance(resultado.get("resposta_final"), str)
        or not resultado["resposta_final"].strip()
    ):
        # Uma falha de apresentação não apaga um resultado operacional conhecido.
        # A recuperação contém apenas as mensagens fixas, sem dados livres do serviço.
        resultado.update(resposta_resultados(contexto["resultados_operacoes"]))

    if resultado.get("erro"):
        marcar_falha_requisicao()

    if not isinstance(resultado.get("resposta_final"), str) or not resultado["resposta_final"].strip():
        marcar_falha_requisicao()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="A Manu não conseguiu gerar uma resposta. Sua mensagem foi preservada na conversa.",
        )

    try:
        visualizacao = publicar_visualizacao(resultado, contexto)
    except LimiteVisualizacaoExcedido as erro:
        raise HTTPException(status_code=413, detail=str(erro)) from None
    except (ValueError, TypeError, KeyError):
        raise HTTPException(status_code=502, detail="Não foi possível validar a visualização para entrega.") from None
    visualizacao_json = visualizacao.model_dump(mode="json") if visualizacao is not None else None
    try:
        await salvar_mensagem(
            thread_id, "assistant", resultado["resposta_final"], usuario_id,
            emocao=resultado.get("emocao", Emocao.NEUTRO),
            turno_id=contexto["turno_id"],
            **({"visualizacao": visualizacao_json} if visualizacao_json is not None else {}),
        )
    except Exception:
        if not resultado.get("resultados_operacoes"):
            raise
        logging.getLogger(__name__).exception("Resultado da operação sem persistir mensagem do chat")
        resultado["resposta_final"] += "\n\nNão consegui atualizar o histórico da conversa. O resultado da operação informado acima permanece válido."
        resultado["confirmacao"] = "nao"
        return resultado
    # Só fica disponível à API depois de confirmar a persistência da mensagem.
    resultado["visualizacao_publica"] = visualizacao_json
    propostas_apresentadas = resultado.get("propostas_apresentadas", [])
    resultado["confirmacao"] = "nao"
    for proposta in propostas_apresentadas:
        apresentada = await atualizar_rascunho_solicitacao(
            thread_id, usuario_id,
            {"turno_apresentacao": contexto["turno_id"], "versao_apresentada": proposta["versao"],
             "dados_apresentados": proposta["dados"]},
            tipo=proposta["tipo"], rascunho_id=proposta["proposta_id"],
            versao=proposta["versao"], status_esperados={"aguardando_confirmacao", "aguardando_imagem", "erro_api"},
            exigir_ativo=True,
        )
        if apresentada and len(propostas_apresentadas) == 1:
            resultado["confirmacao"] = "sim"

    if not propostas_apresentadas and resultado.get("intencao") in {"solicitacao", "ocorrencia"}:
        rascunho = resultado.get(f"{resultado['intencao']}_pendente")
        if (
            isinstance(rascunho, dict)
            and rascunho.get("status_fluxo") in {"aguardando_confirmacao", "aguardando_imagem", "erro_api"}
            and not rascunho.get("pausado")
            and not rascunho.get("confirmado")
            and campos_pendentes(rascunho)
            and rascunho.get("versao_apresentada") == rascunho.get("versao")
            and rascunho.get("dados_apresentados") == rascunho.get("dados")
            and rascunho.get("turno_apresentacao")
            and resumo_confirmacao(rascunho) in resultado["resposta_final"]
        ):
            resultado["confirmacao"] = "sim"

    if resultado["confirmacao"] == "sim":
        await marcar_confirmacao_mensagem(thread_id, usuario_id, contexto["turno_id"])

    return resultado
