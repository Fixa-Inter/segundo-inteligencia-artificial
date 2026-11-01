import logging
from langchain.tools import ToolRuntime, tool
from pydantic import model_validator
from app.core.propostas import avaliar_confirmacao, metadados_proposta
from app.tools.propostas import resolver_rotulos
from app.core.configuracao import QDRANT_COLECAO_LOCAL, QDRANT_COLECAO_CATEGORIA
from app.core.clients.qdrant import abrir_cliente_qdrant
from app.memory.vectorSearch.busca import validar_selecao
from app.memory.persistencia import (
    salvar_rascunho_solicitacao, obter_rascunho_solicitacao, atualizar_rascunho_solicitacao,
)
from app.services.ocorrencias import adicionar_ocorrencia
from app.tools.toolsRequest import CriarOcorrenciaEntrada, CategoriaProblema, Prioridade
from app.tools.solicitacoes.criarSolicitacao import _contexto
from app.observability.metricas import adicionar_resolucao_pendente
from app.services.gerais import obter_unidade_id
from app.services.operacoes import dados_cadastro, preparar_operacao

registrador = logging.getLogger(__name__)


class _ArgumentosCriarOcorrencia(CriarOcorrenciaEntrada):
    @model_validator(mode="before")
    @classmethod
    def separar_runtime_injetado(cls, dados):
        if isinstance(dados, dict) and isinstance(dados.get("runtime"), ToolRuntime):
            return {k: v for k, v in dados.items() if k != "runtime"}
        return dados


@tool(args_schema=_ArgumentosCriarOcorrencia)
async def salvar_rascunho_ocorrencia(
    local_endereco_id: int, categoria_equipamento_id: int,
    categoria_problema_id: CategoriaProblema, titulo: str, descricao_ocorrencia: str,
    descricao_local: str, prioridade: Prioridade, runtime: ToolRuntime,
) -> dict:
    """Salva a proposta e associa fotos recebidas antes de pedir confirmação.

    Use IDs consultados no Qdrant, enums textuais, título até 100 caracteres
    e descrições até 255. Disponível para técnicos, administradores e gestores.
    """
    contexto, usuario, sessao_id = _contexto(runtime)
    if contexto.get("intencao_atual") not in {None, "ocorrencia"}:
        return {"status": "INTENCAO_DIVERGENTE", "mensagem": "Prepare o tipo de registro solicitado nesta mensagem."}
    if usuario.tipo_acesso not in {"tecnico", "gestor", "administrador"}:
        return {"status": "ACESSO_NEGADO", "mensagem": "Perfil sem permissão para ocorrências."}
    dados = CriarOcorrenciaEntrada(
        local_endereco_id=local_endereco_id, categoria_equipamento_id=categoria_equipamento_id,
        categoria_problema_id=categoria_problema_id, titulo=titulo,
        descricao_ocorrencia=descricao_ocorrencia, descricao_local=descricao_local, prioridade=prioridade,
    )
    rascunho = await salvar_rascunho_solicitacao(
        sessao_id, usuario.usuario_id, dados.model_dump(), tipo="ocorrencia",
        turno_id=contexto.get("turno_id", ""), rotulos=await resolver_rotulos(dados.model_dump(), usuario),
    )
    return {"status": "RASCUNHO_SALVO", "dados_salvos": rascunho["dados"],
            "proposta": metadados_proposta(rascunho),
            "imagens_recebidas": len(rascunho["imagens"]),
            "imagens_associadas_ao_rascunho": bool(rascunho["imagens"]),
            "mensagem": "Mostre somente os dados pendentes. Não repita a confirmação dos campos já aceitos. "
                        + ("A foto já foi recebida." if rascunho["imagens"] else "Ainda é necessária uma foto.")}


@tool
async def criar_ocorrencia(runtime: ToolRuntime) -> dict:
    """Prepara a ocorrência confirmada e suas fotos para aprovação interna.

    Se confirmada sem foto, aguarda a imagem. Retome quando a imagem chegar.
    Não repita envios com resultado indeterminado.
    """
    return await processar_ocorrencia(runtime)


async def processar_ocorrencia(runtime: ToolRuntime, *, operacao_aprovada: dict | None = None) -> dict:
    contexto, usuario, sessao_id = _contexto(runtime)
    if usuario.tipo_acesso not in {"tecnico", "gestor", "administrador"}:
        return {"status": "ACESSO_NEGADO", "mensagem": "Perfil sem permissão para ocorrências."}
    rascunho = await obter_rascunho_solicitacao(sessao_id, usuario.usuario_id, tipo="ocorrencia")
    if not rascunho:
        return {"status": "SEM_RASCUNHO", "mensagem": "Prepare e salve a proposta antes do cadastro."}
    status = rascunho.get("status_fluxo")
    if status == "cadastrada":
        return {"status": "SUCESSO", "ocorrencia_id": rascunho.get("ocorrencia_id_api"), "mensagem": "Ocorrência já cadastrada."}
    if status in {"enviando", "resultado_indeterminado"}:
        return {"status": "RESULTADO_INDETERMINADO", "mensagem": "Consulte os registros antes de repetir o envio."}
    if status not in {"aguardando_confirmacao", "aguardando_imagem", "erro_api"}:
        return {"status": "RASCUNHO_INDISPONIVEL", "mensagem": "Rascunho indisponível para cadastro."}
    bloqueio = avaliar_confirmacao(rascunho, contexto)
    if bloqueio:
        if bloqueio["status"] == "CONFIRMACAO_PARCIAL":
            aceitos = {**rascunho.get("dados_confirmados", {}), **{
                campo: rascunho["dados"][campo] for campo in bloqueio["campos_confirmados"]}}
            atualizou = await atualizar_rascunho_solicitacao(
                sessao_id, usuario.usuario_id, {"dados_confirmados": aceitos}, tipo="ocorrencia",
                status_esperados={rascunho["status_fluxo"]}, rascunho_id=rascunho["id"],
                versao=rascunho["versao"], exigir_ativo=True,
            )
            if not atualizou:
                return {"status": "RESULTADO_INDETERMINADO", "mensagem": "A proposta mudou. Releia os dados."}
            rascunho = {**rascunho, "dados_confirmados": aceitos}
        if rascunho.get("id") and rascunho.get("versao") and rascunho.get("tipo"):
            bloqueio["proposta"] = metadados_proposta(rascunho)
        return bloqueio
    controle = {"rascunho_id": rascunho["id"], "versao": rascunho["versao"], "exigir_ativo": True}
    confirmou = await atualizar_rascunho_solicitacao(
        sessao_id, usuario.usuario_id, {"confirmado": True, "dados_confirmados": rascunho["dados"]},
        status_esperados={status}, tipo="ocorrencia", **controle,
    )
    if not confirmou:
        return {"status": "RESULTADO_INDETERMINADO", "mensagem": "A proposta mudou. Confira os dados antes de repetir."}
    if not rascunho.get("imagens"):
        await atualizar_rascunho_solicitacao(sessao_id, usuario.usuario_id,
            {"confirmado": True, "status_fluxo": "aguardando_imagem"},
            status_esperados={status}, tipo="ocorrencia", **controle)
        return {"status": "AGUARDANDO_INFORMACAO", "mensagem": "Proposta confirmada. Envie pelo menos uma foto."}
    dados = CriarOcorrenciaEntrada.model_validate(rascunho["dados"])
    if operacao_aprovada is None:
        return await preparar_operacao(
            contexto, "ocorrencia", f"{rascunho['id']}:{rascunho['versao']}:{contexto['turno_id']}",
            dados_cadastro(rascunho),
        )
    if dados_cadastro(rascunho) != operacao_aprovada:
        return {"status": "ERRO_VALIDACAO", "mensagem": "A proposta ou suas fotos mudaram após a aprovação. Confira os dados novamente."}
    unidade_id = await obter_unidade_id(usuario)
    async with abrir_cliente_qdrant() as cliente:
        try:
            await validar_selecao(QDRANT_COLECAO_LOCAL, dados.local_endereco_id, unidade_id, cliente)
            await validar_selecao(QDRANT_COLECAO_CATEGORIA, dados.categoria_equipamento_id, unidade_id, cliente)
        except ValueError:
            return {"status": "ERRO_VALIDACAO", "mensagem": "Local ou categoria indisponível. Consulte e confirme novamente."}
    iniciou = await atualizar_rascunho_solicitacao(sessao_id, usuario.usuario_id,
        {"status_fluxo": "enviando", "confirmado": True}, status_esperados={status}, tipo="ocorrencia", **controle)
    if not iniciou:
        return {"status": "RESULTADO_INDETERMINADO", "mensagem": "Outro envio pode estar em andamento. Consulte os registros."}
    try:
        resultado = await adicionar_ocorrencia(dados, usuario.access_token,
            usuario_id=usuario.usuario_id, imagens=rascunho["imagens"])
    except Exception:
        registrador.exception("Falha ao enviar ocorrência")
        resultado = {"status": "RESULTADO_INDETERMINADO", "mensagem": "Consulte os registros antes de repetir o envio."}
    status_resultado = resultado.get("status", "ERRO_FERRAMENTA")
    resultado_operacao = (
        "success" if status_resultado == "SUCESSO"
        else "indeterminate" if status_resultado == "RESULTADO_INDETERMINADO"
        else "error"
    )
    if resultado_operacao == "success":
        adicionar_resolucao_pendente()
    proximo = {"SUCESSO": "cadastrada", "RESULTADO_INDETERMINADO": "resultado_indeterminado"}.get(status_resultado, "erro_api")
    try:
        await atualizar_rascunho_solicitacao(sessao_id, usuario.usuario_id,
            {"status_fluxo": proximo, "ocorrencia_id_api": resultado.get("ocorrencia_id")},
            status_esperados={"enviando"}, tipo="ocorrencia", **controle)
    except Exception:
        registrador.exception("Resultado da API recebido sem conseguir atualizar o rascunho")
    return resultado
