"""Continuação, pausa e cancelamento de propostas da sessão."""

from app.core import classificar_manifestacao, normalizar_mensagem, MENSAGENS
from app.memory.persistencia import atualizar_acao, atualizar_rascunho_solicitacao, atualizar_analise_compra
from app.graph.respostas_padrao import escolher_resposta, resposta_interrupcao_proposta
from app.core.continuacoes import _chave_estado, propostas_pendentes, STATUS_RASCUNHO, STATUS_ACAO

def esclarecer_continuacao(mensagem: str) -> dict:
    """Monta resposta que pede identificação da proposta a continuar. Usado por tratar_continuacao."""
    return {"intencao": None, "resposta_especialista": mensagem,
            "esclarecimento_roteamento": True, "erro": None}


async def alterar_continuacao(tipo: str, proposta: dict, contexto: dict, **campos) -> dict:
    """Persiste alterações de continuidade no armazenamento do tipo de proposta. Usado por pausar_outros_fluxos, tratar_continuacao."""
    usuario = contexto["usuario"]
    if tipo == "analista_compras":
        return await atualizar_analise_compra(
            contexto["session_id"], usuario.usuario_id,
            id_analise=proposta["id"], versao=proposta["versao"],
            status_esperado=proposta["status_fluxo"], campos=campos,
        )
    if tipo == "ajuda_geral":
        alterou = await atualizar_acao(
            contexto["session_id"], usuario.usuario_id, proposta["id"], campos,
            status=proposta["status"],
        )
    else:
        alterou = await atualizar_rascunho_solicitacao(
            contexto["session_id"], usuario.usuario_id, campos, tipo=tipo,
            status_esperados={proposta["status_fluxo"]},
            rascunho_id=proposta["id"], versao=proposta.get("versao", 1),
        )
    if not alterou:
        raise ValueError("A proposta mudou durante a conversa. Consulte os dados atuais antes de continuar.")
    return {**proposta, **campos}


async def tratar_continuacao(estado: dict, contexto: dict, pergunta: str) -> dict | None:
    """Trata aceite, pausa, cancelamento e retomada das propostas, pedindo esclarecimento quando ambíguo. Usado pelo fluxo de graph."""
    ativos = propostas_pendentes(estado)
    pausados = propostas_pendentes(estado, pausadas=True)
    manifestacao = classificar_manifestacao(pergunta)
    if manifestacao in {"cancelamento", "pausa", "retomada"}:
        candidatos = {**ativos, **pausados} if manifestacao != "pausa" else ativos
        normalizada = normalizar_mensagem(pergunta)
        mencionados = {tipo: proposta for tipo, proposta in candidatos.items()
                       if tipo in normalizada or tipo == "ajuda_geral" and any(p in normalizada for p in ("alteracao", "anexo"))
                       or tipo == "analista_compras" and any(p in normalizada for p in ("compra", "pesquisa de produtos"))}
        if mencionados:
            candidatos = mencionados
        if len(candidatos) != 1:
            return esclarecer_continuacao(
                escolher_resposta(candidatos, 'qual_proposta_voce_quer_retomar_pausar_ou_cancelar_solicitacao_ocorrencia_evento_alteracao', 'nao_ha_proposta_pendente_para_essa_acao_como_posso_ajudar')
            )
        tipo, proposta = next(iter(candidatos.items()))
        if manifestacao == "retomada":
            atualizacoes = await pausar_outros_fluxos(estado, contexto, tipo)
            atualizacoes[_chave_estado(tipo)] = await alterar_continuacao(tipo, proposta, contexto, pausado=False)
            return {**atualizacoes, "intencao": tipo, "erro": None,
                    "operacao_solicitacao": proposta.get("operacao", "criar") if tipo == "solicitacao" else "criar",
                    "operacao_ocorrencia": proposta.get("operacao", "criar") if tipo == "ocorrencia" else "criar",
                    "justificativa_roteamento": "Retomada explícita da proposta salva."}
        campos = {"pausado": True}
        if manifestacao == "cancelamento":
            campos["status" if tipo == "ajuda_geral" else "status_fluxo"] = "cancelada"
        proposta = await alterar_continuacao(tipo, proposta, contexto, **campos)
        resposta = resposta_interrupcao_proposta(tipo, manifestacao)
        return {**esclarecer_continuacao(resposta), _chave_estado(tipo): proposta}
    if (len(ativos) == 1 and "analista_compras" in ativos
            and ativos["analista_compras"].get("status_fluxo") == "aguardando_opcionais"
            and normalizar_mensagem(pergunta) in {"nao", "sem mais detalhes", "pode pesquisar", "pode buscar", "so isso"}):
        return {"intencao": "analista_compras", "erro": None,
                "justificativa_roteamento": "Resposta aos campos opcionais da compra."}
    if manifestacao == "aceite" or estado.get("imagens_recebidas") and not pergunta.strip():
        if len(ativos) == 1:
            tipo = next(iter(ativos))
            outros_tipos = {"solicitacao", "ocorrencia", "evento"} - {tipo}
            if any(outro in normalizar_mensagem(pergunta) for outro in outros_tipos):
                return esclarecer_continuacao(MENSAGENS['a_confirmacao_menciona_outro_registro_qual_proposta_voce_quer_continuar'])
            return {"intencao": tipo, "erro": None,
                    "operacao_solicitacao": ativos[tipo].get("operacao", "criar") if tipo == "solicitacao" else "criar",
                    "operacao_ocorrencia": ativos[tipo].get("operacao", "criar") if tipo == "ocorrencia" else "criar",
                    "justificativa_roteamento": "Continuação da única proposta ativa."}
        if ativos or pausados:
            return esclarecer_continuacao(
                MENSAGENS['ha_mais_de_uma_proposta_ou_uma_proposta_pausada_informe_qual_deseja']
            )
    return None


async def pausar_outros_fluxos(estado: dict, contexto: dict, escolhido: str | None) -> dict:
    """Persiste pausa de fluxos ativos diferentes do escolhido. Usado por tratar_continuacao."""
    atualizacoes = {}
    for tipo, proposta in propostas_pendentes(estado).items():
        if tipo != escolhido:
            atualizacoes[_chave_estado(tipo)] = await alterar_continuacao(tipo, proposta, contexto, pausado=True)
    return atualizacoes


# O grafo persiste transições; a consulta pura de estado pertence ao core.
