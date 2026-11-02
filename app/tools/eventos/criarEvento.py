"""Rascunho, confirmação e preparação do envio de eventos."""


import logging
from datetime import datetime

from langchain.tools import ToolRuntime, tool
from pydantic import model_validator

from app.core.clients.qdrant import abrir_cliente_qdrant
from app.core.configuracao import QDRANT_COLECAO_LOCAL
from app.core.propostas import avaliar_confirmacao, metadados_proposta
from app.core.tempo import FUSO_HORARIO
from app.memory.persistencia import (
    atualizar_rascunho_solicitacao, obter_rascunho_solicitacao, salvar_rascunho_solicitacao,
)
from app.memory.vectorSearch import validar_selecao
from app.services.eventos import adicionar_evento
from app.services.gerais import obter_unidade_id
from app.services.operacoes import dados_cadastro, preparar_operacao
from app.tools.solicitacoes.criarSolicitacao import _contexto
from app.tools.toolsRequest.CriarEventoEntrada import CriarEventoEntrada

from app.core.respostas import MENSAGENS

registrador = logging.getLogger(__name__)


class _ArgumentosCriarEvento(CriarEventoEntrada):
    @model_validator(mode="before")
    @classmethod
    def separar_runtime_injetado(cls, dados):
        if isinstance(dados, dict) and isinstance(dados.get("runtime"), ToolRuntime):
            return {k: v for k, v in dados.items() if k != "runtime"}
        return dados


@tool(args_schema=_ArgumentosCriarEvento)
async def salvar_rascunho_evento(
    local_unidade_id: int, titulo: str, descricao: str,
    data_hora_inicio: datetime, data_hora_fim: datetime, runtime: ToolRuntime,
    descricao_local: str = "Não foi especificado", observacao: str = "Não foi especificado",
) -> dict:
    """Salva a proposta de evento antes de apresentar os dados para confirmação.

    Não cadastra na API. Use o ID consultado no Qdrant; eventos não exigem foto
    nem categoria de equipamento. Datas sem fuso usam America/Sao_Paulo.
    """
    contexto, usuario, sessao_id = _contexto(runtime)
    if usuario.tipo_acesso not in {"gestor", "administrador"}:
        return {"status": "ACESSO_NEGADO", "mensagem": MENSAGENS['somente_gestores_e_administradores_podem_criar_eventos']}
    if contexto.get("intencao_atual") not in {None, "evento"}:
        return {"status": "INTENCAO_DIVERGENTE", "mensagem": MENSAGENS['prepare_o_tipo_de_registro_solicitado_nesta_mensagem']}
    dados = CriarEventoEntrada(
        local_unidade_id=local_unidade_id, titulo=titulo, descricao=descricao,
        descricao_local=descricao_local, observacao=observacao,
        data_hora_inicio=data_hora_inicio, data_hora_fim=data_hora_fim,
    )
    unidade_id = await obter_unidade_id(usuario)
    async with abrir_cliente_qdrant() as cliente:
        local = await validar_selecao(QDRANT_COLECAO_LOCAL, dados.local_unidade_id, unidade_id, cliente)
    rotulos = {"local_unidade_id": local}
    for campo in ("data_hora_inicio", "data_hora_fim"):
        rotulos[campo] = getattr(dados, campo).astimezone(FUSO_HORARIO).strftime(
            "%d/%m/%Y às %H:%M:%S (America/Sao_Paulo)"
        )
    rascunho = await salvar_rascunho_solicitacao(
        sessao_id, usuario.usuario_id, dados.model_dump(mode="json"), tipo="evento",
        turno_id=contexto["turno_id"], rotulos=rotulos,
    )
    return {"status": "RASCUNHO_SALVO", "dados_salvos": rascunho["dados"],
            "proposta": metadados_proposta(rascunho),
            "mensagem": MENSAGENS['a_proposta_esta_salva_o_fluxo_apresenta_os_dados_pendentes_para_conferencia']}


@tool
async def criar_evento(runtime: ToolRuntime) -> dict:
    """Prepara o evento confirmado para aprovação interna, sem executar o POST.

    Dados vêm exclusivamente do rascunho apresentado e confirmado na sessão.
    Não repita envios com resultado indeterminado.
    """
    return await processar_evento(runtime)


async def processar_evento(runtime: ToolRuntime, *, operacao_aprovada: dict | None = None) -> dict:
    contexto, usuario, sessao_id = _contexto(runtime)
    if usuario.tipo_acesso not in {"gestor", "administrador"}:
        return {"status": "ACESSO_NEGADO", "mensagem": MENSAGENS['somente_gestores_e_administradores_podem_criar_eventos']}
    rascunho = await obter_rascunho_solicitacao(sessao_id, usuario.usuario_id, tipo="evento")
    if not rascunho:
        return {"status": "SEM_RASCUNHO", "mensagem": MENSAGENS['prepare_e_apresente_a_proposta_antes_do_cadastro']}
    status = rascunho.get("status_fluxo")
    if status == "cadastrada":
        return {"status": "SUCESSO", "evento_id": rascunho.get("evento_id_api"), "mensagem": MENSAGENS['evento_ja_cadastrado']}
    if status in {"enviando", "resultado_indeterminado"}:
        return {"status": "RESULTADO_INDETERMINADO", "mensagem": MENSAGENS['consulte_os_eventos_antes_de_repetir_o_envio']}
    if status not in {"aguardando_confirmacao", "erro_api"}:
        return {"status": "RASCUNHO_INDISPONIVEL", "mensagem": MENSAGENS['o_rascunho_ainda_nao_esta_pronto_para_cadastro']}
    bloqueio = avaliar_confirmacao(rascunho, contexto)
    controle = {"tipo": "evento", "rascunho_id": rascunho["id"],
                "versao": rascunho["versao"], "exigir_ativo": True}
    if bloqueio:
        if bloqueio["status"] == "CONFIRMACAO_PARCIAL":
            aceitos = {**rascunho.get("dados_confirmados", {}), **{
                campo: rascunho["dados"][campo] for campo in bloqueio["campos_confirmados"]}}
            atualizou = await atualizar_rascunho_solicitacao(
                sessao_id, usuario.usuario_id, {"dados_confirmados": aceitos},
                status_esperados={status}, **controle,
            )
            if not atualizou:
                return {"status": "ERRO_VALIDACAO", "mensagem": MENSAGENS['a_proposta_mudou_confira_os_dados_atuais']}
            rascunho = {**rascunho, "dados_confirmados": aceitos}
        bloqueio["proposta"] = metadados_proposta(rascunho)
        return bloqueio
    dados = CriarEventoEntrada.model_validate(rascunho["dados"])
    if operacao_aprovada is not None and dados_cadastro(rascunho) != operacao_aprovada:
        return {"status": "ERRO_VALIDACAO", "mensagem": MENSAGENS['a_proposta_mudou_apos_a_aprovacao_confira_os_dados_novamente']}
    confirmou = await atualizar_rascunho_solicitacao(
        sessao_id, usuario.usuario_id, {"confirmado": True, "dados_confirmados": rascunho["dados"]},
        status_esperados={status}, **controle,
    )
    if not confirmou:
        return {"status": "ERRO_VALIDACAO", "mensagem": MENSAGENS['a_proposta_mudou_confira_os_dados_atuais']}
    if operacao_aprovada is None:
        return await preparar_operacao(
            contexto, "evento", f"{rascunho['id']}:{rascunho['versao']}:{contexto['turno_id']}",
            dados_cadastro(rascunho),
        )
    unidade_id = await obter_unidade_id(usuario)
    async with abrir_cliente_qdrant() as cliente:
        try:
            await validar_selecao(QDRANT_COLECAO_LOCAL, dados.local_unidade_id, unidade_id, cliente)
        except ValueError:
            return {"status": "ERRO_VALIDACAO", "mensagem": MENSAGENS['local_indisponivel_consulte_e_confirme_novamente']}
    iniciou = await atualizar_rascunho_solicitacao(
        sessao_id, usuario.usuario_id, {"status_fluxo": "enviando", "confirmado": True},
        status_esperados={status}, **controle,
    )
    if not iniciou:
        return {"status": "RESULTADO_INDETERMINADO", "mensagem": MENSAGENS['outro_envio_pode_estar_em_andamento_consulte_os_eventos']}
    try:
        resultado = await adicionar_evento(dados, usuario.access_token, usuario_id=usuario.usuario_id)
    except Exception:
        registrador.exception("Falha ao enviar evento")
        resultado = {"status": "RESULTADO_INDETERMINADO", "mensagem": MENSAGENS['consulte_os_eventos_antes_de_repetir_o_envio']}
    proximo = {"SUCESSO": "cadastrada", "RESULTADO_INDETERMINADO": "resultado_indeterminado"}.get(
        resultado.get("status"), "erro_api"
    )
    try:
        await atualizar_rascunho_solicitacao(
            sessao_id, usuario.usuario_id,
            {"status_fluxo": proximo, "evento_id_api": resultado.get("evento_id")},
            status_esperados={"enviando"}, **controle,
        )
    except Exception:
        registrador.exception("Resultado da API recebido sem conseguir atualizar o rascunho do evento")
    return resultado
