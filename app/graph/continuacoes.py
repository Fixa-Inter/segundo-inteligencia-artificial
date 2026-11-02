"""Continuação, pausa e cancelamento de propostas da sessão."""


from app.core.confirmacoes import classificar_manifestacao, normalizar_mensagem
from app.memory.persistencia import atualizar_acao, atualizar_rascunho_solicitacao
from app.memory.persistencia.analise_compra import atualizar_analise_compra

from app.core.respostas import MENSAGENS
from app.graph.respostas_padrao import escolher_resposta, resposta_interrupcao_proposta

STATUS_RASCUNHO = {"coletando_dados", "aguardando_confirmacao", "aguardando_imagem", "erro_api"}
STATUS_ACAO = {"aguardando_confirmacao", "aguardando_imagem"}


def _chave_estado(tipo: str) -> str:
    return "analise_compra_pendente" if tipo == "analista_compras" else f"{tipo}_pendente"


def propostas_pendentes(estado: dict, *, pausadas: bool = False) -> dict[str, dict]:
    propostas = {}
    for tipo in ("solicitacao", "ocorrencia", "evento", "ajuda_geral", "analista_compras"):
        chave = _chave_estado(tipo)
        proposta = estado.get(chave)
        if not isinstance(proposta, dict):
            continue
        status = proposta.get("status" if tipo == "ajuda_geral" else "status_fluxo")
        permitidos = STATUS_ACAO if tipo == "ajuda_geral" else (
            {"coletando_dados", "aguardando_opcionais", "pronto_para_busca", "erro_busca"}
            if tipo == "analista_compras" else STATUS_RASCUNHO
        )
        if status in permitidos and bool(proposta.get("pausado")) == pausadas:
            propostas[tipo] = proposta
    return propostas


def esclarecer_continuacao(mensagem: str) -> dict:
    return {"intencao": None, "resposta_especialista": mensagem,
            "esclarecimento_roteamento": True, "erro": None}


async def alterar_continuacao(tipo: str, proposta: dict, contexto: dict, **campos) -> dict:
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
                    "justificativa_roteamento": "Continuação da única proposta ativa."}
        if ativos or pausados:
            return esclarecer_continuacao(
                MENSAGENS['ha_mais_de_uma_proposta_ou_uma_proposta_pausada_informe_qual_deseja']
            )
    return None


async def pausar_outros_fluxos(estado: dict, contexto: dict, escolhido: str | None) -> dict:
    atualizacoes = {}
    for tipo, proposta in propostas_pendentes(estado).items():
        if tipo != escolhido:
            atualizacoes[_chave_estado(tipo)] = await alterar_continuacao(tipo, proposta, contexto, pausado=True)
    return atualizacoes
