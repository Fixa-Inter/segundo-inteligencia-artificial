from typing import Literal, cast

from langchain_core.messages import HumanMessage, AIMessage

from app.graph.context import GraphContext
from app.graph.state import GraphState
from app.graph.workflow import grafo
from app.schemas.UsuarioContexto import UsuarioContexto
from app.memory.persistencia.salvar_mensagem import salvar_mensagem
from app.memory.persistencia.recuperar_mensagens import recuperar_mensagens
from app.memory.persistencia.utilitarios import documento_id_da_sessao


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
) -> GraphState:

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
        "erro": None,
    }


async def executar_grafo(
    mensagem: str,
    usuario: UsuarioContexto,
    thread_id: str,
    imagens: list[str] | None = None,
) -> GraphState:
    usuario_id = usuario.usuario_id

    if not thread_id:
        raise ValueError("O thread_id não pode estar vazio.")

    thread_id_interno = (
        f"{usuario_id}:{thread_id}"
    )
    
    # ANONIMIZAR A ENTRADA E SALVAR A MENSAGEM COM O MÉTODO SALVAR MENSAGEM
    mensagem_anonimizada = ""

    config = {
        "configurable": {
            "thread_id": thread_id_interno
        }
    }
    state = grafo.get_state(config)

    mensagens = []
    if not state.values:
        doc_id = await documento_id_da_sessao(thread_id,usuario_id)
        historico = await recuperar_mensagens(doc_id,usuario_id)

        for item in historico:
            if item["role"] == "human":
                mensagens.append(HumanMessage(content=item["content"]))
            elif item["role"] == "assistant":
                mensagens.append(AIMessage(content=item["content"]))

    mensagens.append(HumanMessage(content=mensagem_anonimizada))

    await salvar_mensagem(thread_id,"human",mensagem_anonimizada,usuario.usuario_id)
    
    estado_inicial = criar_estado_inicial(
        mensagens=mensagens,
        usuario=usuario,
    )

    contexto: GraphContext = {
        "usuario": usuario,
        "imagens": list(imagens or []),
    }

    resultado = await grafo.ainvoke(
        estado_inicial,
        config=config,
        context=contexto,
    )

    await salvar_mensagem(thread_id,"assistant",resultado["resposta_final"],usuario_id)

    return resultado
