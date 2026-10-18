"""Continuação, pausa e cancelamento de propostas da sessão."""

from app.core.confirmacoes import classificar_manifestacao, normalizar_mensagem
from app.memory.persistencia import atualizar_acao, atualizar_rascunho_solicitacao

STATUS_RASCUNHO = {"aguardando_confirmacao", "aguardando_imagem", "erro_api"}
STATUS_ACAO = {"aguardando_confirmacao", "aguardando_imagem"}


def propostas_pendentes(estado: dict, *, pausadas: bool = False) -> dict[str, dict]:
    propostas = {}
    for tipo in ("solicitacao", "ocorrencia", "ajuda_geral"):
        proposta = estado.get(f"{tipo}_pendente")
        if not isinstance(proposta, dict):
            continue
        status = proposta.get("status" if tipo == "ajuda_geral" else "status_fluxo")
        permitidos = STATUS_ACAO if tipo == "ajuda_geral" else STATUS_RASCUNHO
        if status in permitidos and bool(proposta.get("pausado")) == pausadas:
            propostas[tipo] = proposta
    return propostas


def esclarecer_continuacao(mensagem: str) -> dict:
    return {"intencao": None, "resposta_especialista": mensagem,
            "esclarecimento_roteamento": True, "erro": None}


async def alterar_continuacao(tipo: str, proposta: dict, contexto: dict, **campos) -> dict:
    usuario = contexto["usuario"]
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
                       if tipo in normalizada or tipo == "ajuda_geral" and any(p in normalizada for p in ("alteracao", "anexo"))}
        if mencionados:
            candidatos = mencionados
        if len(candidatos) != 1:
            return esclarecer_continuacao(
                "Qual proposta você quer retomar, pausar ou cancelar: solicitação, ocorrência ou alteração?"
                if candidatos else "Não há proposta pendente para essa ação. Como posso ajudar?"
            )
        tipo, proposta = next(iter(candidatos.items()))
        if manifestacao == "retomada":
            atualizacoes = await pausar_outros_fluxos(estado, contexto, tipo)
            atualizacoes[f"{tipo}_pendente"] = await alterar_continuacao(tipo, proposta, contexto, pausado=False)
            return {**atualizacoes, "intencao": tipo, "erro": None,
                    "justificativa_roteamento": "Retomada explícita da proposta salva."}
        campos = {"pausado": True}
        if manifestacao == "cancelamento":
            campos["status" if tipo == "ajuda_geral" else "status_fluxo"] = "cancelada"
        proposta = await alterar_continuacao(tipo, proposta, contexto, **campos)
        resposta = "Proposta cancelada. Não vou enviar esse cadastro nem executar essa alteração." if manifestacao == "cancelamento" else (
            "Proposta pausada. Para continuar depois, peça para retomar a "
            + ("alteração." if tipo == "ajuda_geral" else tipo.replace("solicitacao", "solicitação").replace("ocorrencia", "ocorrência") + ".")
        )
        return {**esclarecer_continuacao(resposta), f"{tipo}_pendente": proposta}
    if manifestacao == "aceite" or estado.get("imagens_recebidas") and not pergunta.strip():
        if len(ativos) == 1:
            tipo = next(iter(ativos))
            outro_tipo = "ocorrencia" if tipo == "solicitacao" else "solicitacao"
            if outro_tipo in normalizar_mensagem(pergunta):
                return esclarecer_continuacao("A confirmação menciona outro registro. Qual proposta você quer continuar?")
            return {"intencao": tipo, "erro": None,
                    "justificativa_roteamento": "Continuação da única proposta ativa."}
        if ativos or pausados:
            return esclarecer_continuacao(
                "Há mais de uma proposta ou uma proposta pausada. Informe qual deseja retomar antes de confirmar."
            )
    return None


async def pausar_outros_fluxos(estado: dict, contexto: dict, escolhido: str | None) -> dict:
    atualizacoes = {}
    for tipo, proposta in propostas_pendentes(estado).items():
        if tipo != escolhido:
            atualizacoes[f"{tipo}_pendente"] = await alterar_continuacao(tipo, proposta, contexto, pausado=True)
    return atualizacoes
