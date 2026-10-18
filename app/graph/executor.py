from typing import Literal, cast
from uuid import uuid4

from langchain_core.messages import HumanMessage, AIMessage

from app.graph.contexto import ContextoGrafo
from app.graph.estado import EstadoGrafo
from app.graph.fluxo import grafo
from app.schemas import UsuarioContexto
from app.core import Emocao
from app.memory.persistencia import salvar_mensagem
from app.memory.persistencia import recuperar_mensagens
from app.memory.persistencia import obter_documento_sessao_id
from app.memory.persistencia import (
    obter_rascunho_solicitacao,
)
from app.memory.persistencia import obter_acao
from app.memory.persistencia import atualizar_rascunho_solicitacao

from app.guardrails import anonimizar_entrada
from app.agents.prompts.reutilizaveis import construir_contexto_temporal
from app.observability.metricas import (
    MonitorMetricas,
    finalizar_resolucoes,
    marcar_falha_requisicao,
)


Perfil = Literal[
    "solicitante",
    "tecnico",
    "gestor",
]

PERFIS_VALIDOS = {
    "solicitante",
    "tecnico",
    "gestor",
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
        "messages": mensagens,
        "user_id": usuario.usuario_id,
        "perfil": perfil,
        "tentativas": 0,
        "resposta_final": "",
        "emocao": Emocao.NEUTRO.value,
        "saida_bloqueada": False,
        "resposta_especialista": "",
        "feedback_juiz": "",
        "evidencias": [],
        "erro": None,
        "entrada_valida": False,
        "mensagem_anonimizada": "",
        "mapa_pii": {},
        "motivo_bloqueio": None,
        "justificativa_roteamento": "",
        "veredito": None,
        "intencao": None,
        "esclarecimento_roteamento": False,
        "propostas_apresentadas": [],
        "contexto_temporal": construir_contexto_temporal(),
    }


async def executar_grafo(
    mensagem: str,
    usuario: UsuarioContexto,
    thread_id: str,
    imagens: list[str] | None = None,
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
    estado_inicial["imagens_recebidas"] = bool(imagens)

    contexto: ContextoGrafo = {
        "usuario": usuario,
        "imagens": list(imagens or []),
        "session_id": thread_id,
        "mensagem_atual": mensagem_anonimizada,
        "turno_id": str(uuid4()),
        "contexto_temporal": estado_inicial["contexto_temporal"],
    }

    try:
        resultado = await grafo.ainvoke(
            estado_inicial,
            config=configuracao,
            context=contexto,
        )
    finally:
        finalizar_resolucoes()

    if resultado.get("erro"):
        marcar_falha_requisicao()

    await salvar_mensagem(
        thread_id, "assistant", resultado["resposta_final"], usuario_id,
        emocao=resultado.get("emocao", Emocao.NEUTRO),
    )
    for proposta in resultado.get("propostas_apresentadas", []):
        await atualizar_rascunho_solicitacao(
            thread_id, usuario_id,
            {"turno_apresentacao": contexto["turno_id"], "versao_apresentada": proposta["versao"],
             "dados_apresentados": proposta["dados"]},
            tipo=proposta["tipo"], rascunho_id=proposta["proposta_id"],
            versao=proposta["versao"], status_esperados={"aguardando_confirmacao", "aguardando_imagem", "erro_api"},
            exigir_ativo=True,
        )

    return resultado
