import uuid
import time
from app.observability.tracing import somente_metricas
from fastapi import HTTPException, status
from app.graph.executor import PERFIS_VALIDOS, executar_grafo
from app.schemas import UsuarioContexto
from app.schemas import ConversaEntrada, ConversaSaida
from app.core import Emocao
from app.services.visualizacoes.publicacao import validar_visualizacao_publica
from app.services.visualizacoes import PERFIS_VISUALIZACOES
from app.memory.persistencia.sessoes import iniciar_sessao
from app.memory.persistencia.utilitarios import sessao_acessivel
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

from app.core.respostas import MENSAGENS


async def _processar_chat(
    dados: ConversaEntrada,
    usuario: UsuarioContexto,
) -> ConversaSaida:
    if usuario.tipo_acesso.strip().lower() not in PERFIS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=MENSAGENS['perfil_sem_permissao_de_acesso_ao_chat'],
        )

    if dados.thread_id is None:
        sessao_id = str(uuid.uuid4())
        dados.thread_id = sessao_id
        await iniciar_sessao(sessao_id=sessao_id,usuario_id=usuario.usuario_id)
    else:
        acessivel = await sessao_acessivel(
            sessao_id=dados.thread_id,
            usuario_id=usuario.usuario_id,
        )

        if not acessivel:
            raise HTTPException(
                status_code=404,
                detail=MENSAGENS['conversa_nao_encontrada'],
            )

    
    resultado = await executar_grafo(
        mensagem=dados.mensagem,
        usuario=usuario,
        thread_id=dados.thread_id,
        imagens=dados.imagens,
        plataforma=dados.plataforma,
    )

    resposta = resultado.get("resposta_final")
    if not isinstance(resposta, str) or not resposta.strip():
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=MENSAGENS['a_manu_nao_conseguiu_gerar_uma_resposta_sua_mensagem_foi_preservada_na'],
        )

    visualizacao = resultado.get("visualizacao_publica")
    if visualizacao is not None:
        if (
            usuario.tipo_acesso.strip().lower() not in PERFIS_VISUALIZACOES
            or resultado.get("intencao") != "visualizacao"
            or resultado.get("erro") or resultado.get("saida_bloqueada")
        ):
            raise HTTPException(status_code=502, detail=MENSAGENS['visualizacao_indisponivel_para_esta_resposta'])
        visualizacao = validar_visualizacao_publica(visualizacao)
    return ConversaSaida(
        thread_id=dados.thread_id,
        emocao=resultado.get("emocao", Emocao.NEUTRO),
        intencao=resultado.get("intencao"),
        resposta=resposta,
        confirmacao=resultado.get("confirmacao", "nao"),
        visualizacao=visualizacao,
    )


@somente_metricas
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
