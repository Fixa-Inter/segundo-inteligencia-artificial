import logging
from langchain.tools import ToolRuntime, tool
from pydantic import model_validator
from app.core.config import QDRANT_LOCAL_COLLECTION, QDRANT_CATEGORIA_COLLECTION
from app.core.clients.qdrant import abrir_cliente_qdrant
from app.memory.vectorSearch.busca import validar_selecao
from app.memory.persistencia.rascunho_solicitacao import (
    salvar_rascunho_solicitacao, obter_rascunho_solicitacao, atualizar_rascunho_solicitacao,
)
from app.services.ocorrencias.criarOcorrencia import adicionar_ocorrencia
from app.tools.toolsRequest.CriarOcorrenciaRequest import CriarOcorrenciaRequest, CategoriaProblema, Prioridade
from app.tools.solicitacoes.criarSolicitacao import _contexto, _confirmacao_explicita

logger = logging.getLogger(__name__)


class _ArgumentosCriarOcorrencia(CriarOcorrenciaRequest):
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
    e descrições até 255. Exclusiva de técnicos e gestores.
    """
    _, usuario, session_id = _contexto(runtime)
    if usuario.tipo_acesso not in {"tecnico", "gestor"}:
        return {"status": "ACESSO_NEGADO", "mensagem": "Perfil sem permissão para ocorrências."}
    dados = CriarOcorrenciaRequest(
        local_endereco_id=local_endereco_id, categoria_equipamento_id=categoria_equipamento_id,
        categoria_problema_id=categoria_problema_id, titulo=titulo,
        descricao_ocorrencia=descricao_ocorrencia, descricao_local=descricao_local, prioridade=prioridade,
    )
    rascunho = await salvar_rascunho_solicitacao(session_id, usuario.usuario_id, dados.model_dump(), tipo="ocorrencia")
    return {"status": "RASCUNHO_SALVO", "dados_salvos": rascunho["dados"],
            "imagens_recebidas": len(rascunho["imagens"]),
            "imagens_associadas_ao_rascunho": bool(rascunho["imagens"]),
            "mensagem": "Proposta salva. Peça confirmação; é necessária pelo menos uma foto."}


@tool
async def criar_ocorrencia(runtime: ToolRuntime) -> dict:
    """Envia a ocorrência salva na sessão após confirmação, com suas fotos.

    Se confirmada sem foto, aguarda a imagem. Retome quando a imagem chegar.
    Não repita envios com resultado indeterminado.
    """
    contexto, usuario, session_id = _contexto(runtime)
    if usuario.tipo_acesso not in {"tecnico", "gestor"}:
        return {"status": "ACESSO_NEGADO", "mensagem": "Perfil sem permissão para ocorrências."}
    rascunho = await obter_rascunho_solicitacao(session_id, usuario.usuario_id, tipo="ocorrencia")
    if not rascunho:
        return {"status": "SEM_RASCUNHO", "mensagem": "Prepare e salve a proposta antes do cadastro."}
    status = rascunho.get("status_fluxo")
    if status == "cadastrada":
        return {"status": "SUCESSO", "ocorrencia_id": rascunho.get("ocorrencia_id_api"), "mensagem": "Ocorrência já cadastrada."}
    if status in {"enviando", "resultado_indeterminado"}:
        return {"status": "RESULTADO_INDETERMINADO", "mensagem": "Consulte os registros antes de repetir o envio."}
    if status not in {"aguardando_confirmacao", "aguardando_imagem", "erro_api"}:
        return {"status": "RASCUNHO_INDISPONIVEL", "mensagem": "Rascunho indisponível para cadastro."}
    confirmado = rascunho.get("confirmado") is True and status == "aguardando_imagem"
    if not confirmado and not _confirmacao_explicita(contexto.get("mensagem_atual", "")):
        return {"status": "CONFIRMACAO_NECESSARIA", "mensagem": "Confirme os dados antes de cadastrar."}
    if not rascunho.get("imagens"):
        await atualizar_rascunho_solicitacao(session_id, usuario.usuario_id,
            {"confirmado": True, "status_fluxo": "aguardando_imagem"},
            status_esperados={status}, tipo="ocorrencia")
        return {"status": "AGUARDANDO_INFORMACAO", "mensagem": "Proposta confirmada. Envie pelo menos uma foto."}
    dados = CriarOcorrenciaRequest.model_validate(rascunho["dados"])
    async with abrir_cliente_qdrant() as cliente:
        try:
            await validar_selecao(QDRANT_LOCAL_COLLECTION, dados.local_endereco_id, usuario.cnpj_endereco, cliente)
            await validar_selecao(QDRANT_CATEGORIA_COLLECTION, dados.categoria_equipamento_id, usuario.cnpj_endereco, cliente)
        except ValueError:
            return {"status": "ERRO_VALIDACAO", "mensagem": "Local ou categoria indisponível. Consulte e confirme novamente."}
    iniciou = await atualizar_rascunho_solicitacao(session_id, usuario.usuario_id,
        {"status_fluxo": "enviando", "confirmado": True}, status_esperados={status}, tipo="ocorrencia")
    if not iniciou:
        return {"status": "RESULTADO_INDETERMINADO", "mensagem": "Outro envio pode estar em andamento. Consulte os registros."}
    try:
        resultado = await adicionar_ocorrencia(dados, usuario.access_token,
            usuario_id=usuario.usuario_id, imagens=rascunho["imagens"])
    except Exception:
        logger.exception("Falha ao enviar ocorrência")
        resultado = {"status": "RESULTADO_INDETERMINADO", "mensagem": "Consulte os registros antes de repetir o envio."}
    proximo = {"SUCESSO": "cadastrada", "RESULTADO_INDETERMINADO": "resultado_indeterminado"}.get(resultado["status"], "erro_api")
    await atualizar_rascunho_solicitacao(session_id, usuario.usuario_id,
        {"status_fluxo": proximo, "ocorrencia_id_api": resultado.get("ocorrencia_id")},
        status_esperados={"enviando"}, tipo="ocorrencia")
    return resultado
