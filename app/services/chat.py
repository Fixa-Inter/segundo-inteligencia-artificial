import uuid
import time
from fastapi import HTTPException, status
from app.graph.executor import PERFIS_VALIDOS, executar_grafo
from app.schemas import UsuarioContexto
from app.schemas import ConversaEntrada, ConversaSaida
from app.core import Emocao
from app.memory.persistencia.sessoes import iniciar_sessao
from app.memory.persistencia import obter_documento_sessao_id
from app.observability.metricas import (
    DURACAO_RESPOSTA_CONVERSA,
    REQUISICOES_CONVERSA,
    reiniciar_custo_requisicao,
    restaurar_custo_requisicao,
    reiniciar_resultado_requisicao,
    restaurar_resultado_requisicao,
    marcar_falha_requisicao,
    requisicao_falhou,
    reiniciar_resolucoes_pendentes,
    restaurar_resolucoes_pendentes,
)


async def _processar_chat(
    dados: ConversaEntrada,
    usuario: UsuarioContexto,
) -> ConversaSaida:
    if usuario.tipo_acesso.strip().lower() not in PERFIS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Perfil sem permissão de acesso ao chat.",
        )

    if dados.thread_id is None:
        sessao_id = str(uuid.uuid4())
        dados.thread_id = sessao_id
        await iniciar_sessao(sessao_id=sessao_id,usuario_id=usuario.usuario_id)
    else:
        documento_id = await obter_documento_sessao_id(
            sessao_id=dados.thread_id,
            usuario_id=usuario.usuario_id,
        )

        if documento_id is None:
            raise HTTPException(
                status_code=404,
                detail="Conversa não encontrada.",
            )
    
    resultado = await executar_grafo(
        mensagem=dados.mensagem,
        usuario=usuario,
        thread_id=dados.thread_id,
        imagens=dados.imagens,
    )

    return ConversaSaida(
        thread_id=dados.thread_id,
        emocao=resultado.get("emocao", Emocao.NEUTRO),
        intencao=resultado.get("intencao"),
        resposta=resultado.get(
            "resposta_final",
            "Não foi possível produzir uma resposta.",
        ),
    )


async def processar_chat(
    dados: ConversaEntrada,
    usuario: UsuarioContexto,
) -> ConversaSaida:
    inicio = time.perf_counter()
    token_custo = reiniciar_custo_requisicao()
    token_resultado = reiniciar_resultado_requisicao()
    token_resolucoes = reiniciar_resolucoes_pendentes()
    try:
        return await _processar_chat(dados, usuario)
    except Exception:
        # Falhas antes de o grafo iniciar também entram no denominador.
        marcar_falha_requisicao()
        raise
    finally:
        REQUISICOES_CONVERSA.labels("error" if requisicao_falhou() else "success").inc()
        DURACAO_RESPOSTA_CONVERSA.observe(time.perf_counter() - inicio)
        restaurar_custo_requisicao(token_custo)
        restaurar_resultado_requisicao(token_resultado)
        restaurar_resolucoes_pendentes(token_resolucoes)
