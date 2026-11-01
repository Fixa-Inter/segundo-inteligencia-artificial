import logging
from typing import Any

from langchain.tools import ToolRuntime, tool
from pydantic import field_validator, model_validator
from app.core.propostas import avaliar_confirmacao, metadados_proposta
from app.tools.propostas import resolver_rotulos

from app.core.clients.qdrant import abrir_cliente_qdrant
from app.core.configuracao import QDRANT_COLECAO_CATEGORIA, QDRANT_COLECAO_LOCAL
from app.memory.persistencia import (
    atualizar_rascunho_solicitacao,
    obter_rascunho_solicitacao,
    salvar_rascunho_solicitacao as persistir_rascunho,
)
from app.memory.vectorSearch import validar_selecao
from app.schemas import UsuarioContexto
from app.services.solicitacoes import adicionar_solicitacao
from app.services.gerais import obter_unidade_id
from app.services.operacoes import dados_cadastro, preparar_operacao
from app.tools.toolsRequest import CriarSolicitacaoEntrada


registrador = logging.getLogger(__name__)


class _ArgumentosCriarSolicitacao(CriarSolicitacaoEntrada):
    @field_validator("titulo")
    @classmethod
    def validar_titulo(cls, valor):
        if len(valor.split()) > 10:
            raise ValueError("O título deve conter no máximo 10 palavras.")
        return valor

    @model_validator(mode="before")
    @classmethod
    def separar_runtime_injetado(cls, dados):
        if isinstance(dados, dict) and isinstance(dados.get("runtime"), ToolRuntime):
            return {chave: valor for chave, valor in dados.items() if chave != "runtime"}
        return dados


def _contexto(runtime: ToolRuntime) -> tuple[dict[str, Any], UsuarioContexto, str]:
    contexto = runtime.context
    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError("Forneça UsuarioContexto em context['usuario'].")

    sessao_id = contexto.get("session_id")
    if not isinstance(sessao_id, str) or not sessao_id.strip():
        raise ValueError("A sessão atual não foi informada ao agente.")
    if not isinstance(contexto.get("turno_id"), str) or not contexto["turno_id"].strip():
        raise ValueError("O turno atual não foi informado ao agente.")

    return contexto, contexto["usuario"], sessao_id


def _normalizar_status_backend(status: Any) -> str | None:
    if not isinstance(status, str) or not status.strip():
        return None

    normalizado = status.strip().upper()
    return {
        "PENDENTE": "em_aprovacao",
        "EM APROVAÇÃO": "em_aprovacao",
        "REPROVADO": "reprovada",
        "REPROVADA": "reprovada",
        "APROVADO": "aprovada",
        "APROVADA": "aprovada",
        "REALIZADO": "realizada",
        "REALIZADA": "realizada",
        "CONCLUÍDO": "realizada",
        "CONCLUIDO": "realizada",
        "CONCLUÍDA": "realizada",
        "CONCLUIDA": "realizada",
    }.get(normalizado, normalizado.lower().replace(" ", "_"))


@tool(args_schema=_ArgumentosCriarSolicitacao)
async def salvar_rascunho_solicitacao(
    categoria_equipamento_id: int,
    local_endereco_id: int,
    titulo: str,
    descricao_problema: str,
    runtime: ToolRuntime,
    descricao_local: str,
) -> dict:
    """Persiste no Mongo a proposta de solicitação antes de pedir confirmação.

    As imagens já recebidas nesta sessão são associadas ao rascunho. Esta tool
    não cria a solicitação na API.
    """
    contexto, usuario, sessao_id = _contexto(runtime)
    if contexto.get("intencao_atual") not in {None, "solicitacao"}:
        return {"status": "INTENCAO_DIVERGENTE", "mensagem": "Prepare o tipo de registro solicitado nesta mensagem."}
    if usuario.tipo_acesso.lower() not in {"tecnico", "solicitante"}:
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Somente técnicos e solicitantes podem criar solicitações.",
        }

    dados = _ArgumentosCriarSolicitacao(
        categoria_equipamento_id=categoria_equipamento_id,
        local_endereco_id=local_endereco_id,
        titulo=titulo,
        descricao_problema=descricao_problema,
        descricao_local=descricao_local,
    )
    rascunho = await persistir_rascunho(
        sessao_id=sessao_id,
        usuario_id=usuario.usuario_id,
        dados=dados.model_dump(),
        turno_id=contexto.get("turno_id", ""),
        rotulos=await resolver_rotulos(dados.model_dump(), usuario),
    )
    return {
        "status": "RASCUNHO_SALVO",
        "proposta": metadados_proposta(rascunho),
        "mensagem": "Apresente somente os dados pendentes. Preserve os campos já confirmados; não peça autorização de cadastro novamente.",
        "dados_salvos": rascunho["dados"],
        "imagens_recebidas": len(rascunho.get("imagens", [])),
        "imagens_associadas_ao_rascunho": bool(rascunho.get("imagens")),
    }


@tool
async def criar_solicitacao(runtime: ToolRuntime) -> dict:
    """Prepara o envio da solicitação confirmada para aprovação interna.

    A proposta e as imagens vêm do rascunho da sessão. A confirmação pode vir
    junto com as imagens; se as imagens forem enviadas depois, ficam anexadas
    ao rascunho até o envio.
    """
    return await processar_solicitacao(runtime)


async def processar_solicitacao(runtime: ToolRuntime, *, operacao_aprovada: dict | None = None) -> dict:
    contexto, usuario, sessao_id = _contexto(runtime)
    if usuario.tipo_acesso.lower() not in {"tecnico", "solicitante"}:
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Somente técnicos e solicitantes podem criar solicitações.",
        }

    rascunho = await obter_rascunho_solicitacao(sessao_id, usuario.usuario_id)
    if not rascunho:
        return {
            "status": "SEM_RASCUNHO",
            "mensagem": "Não há uma proposta salva para cadastrar.",
        }

    status_fluxo = rascunho.get("status_fluxo")
    if status_fluxo == "cadastrada":
        return {
            "status": "SUCESSO",
            "problema_id": rascunho.get("problema_id_api"),
            "status_backend": rascunho.get("status_backend"),
            "mensagem": "Esta solicitação já foi cadastrada.",
        }
    if status_fluxo in {"enviando", "resultado_indeterminado"}:
        return {
            "status": "RESULTADO_INDETERMINADO",
            "mensagem": (
                "O envio anterior pode ter sido processado. Consulte a solicitação "
                "na API antes de tentar novamente."
            ),
        }
    if status_fluxo not in {"aguardando_confirmacao", "aguardando_imagem", "erro_api"}:
        return {
            "status": "RASCUNHO_INDISPONIVEL",
            "mensagem": "O rascunho não está em uma etapa que permita cadastro.",
        }

    # Rascunhos anteriores à exigência da API podem ter descrição nula.
    descricao_local = rascunho.get("dados", {}).get("descricao_local")
    if not isinstance(descricao_local, str) or not descricao_local.strip():
        return {
            "status": "AGUARDANDO_INFORMACAO",
            "mensagem": (
                "Informe os detalhes do local. Atualize o rascunho e confirme "
                "a proposta corrigida antes de cadastrar."
            ),
        }

    bloqueio = avaliar_confirmacao(rascunho, contexto)
    if bloqueio:
        if bloqueio["status"] == "CONFIRMACAO_PARCIAL":
            aceitos = {**rascunho.get("dados_confirmados", {}), **{
                campo: rascunho["dados"][campo] for campo in bloqueio["campos_confirmados"]}}
            atualizou = await atualizar_rascunho_solicitacao(
                sessao_id, usuario.usuario_id, {"dados_confirmados": aceitos},
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
    confirmado = await atualizar_rascunho_solicitacao(
        sessao_id, usuario.usuario_id,
        {"confirmado": True, "dados_confirmados": rascunho["dados"]},
        status_esperados={"aguardando_confirmacao", "aguardando_imagem", "erro_api"}, **controle,
    )
    if not confirmado:
        return {"status": "RESULTADO_INDETERMINADO", "mensagem": "A proposta mudou. Confira os dados antes de repetir."}

    imagens = rascunho.get("imagens", [])
    if not imagens:
        await atualizar_rascunho_solicitacao(
            sessao_id,
            usuario.usuario_id,
            {"status_fluxo": "aguardando_imagem", "confirmado": True},
            status_esperados={"aguardando_confirmacao", "aguardando_imagem", "erro_api"}, **controle,
        )
        return {
            "status": "AGUARDANDO_INFORMACAO",
            "mensagem": (
                "A proposta foi confirmada. Envie pelo menos uma imagem para concluir o cadastro."
            ),
        }

    dados = CriarSolicitacaoEntrada.model_validate(rascunho.get("dados", {}))
    if operacao_aprovada is None:
        return await preparar_operacao(
            contexto, "solicitacao", f"{rascunho['id']}:{rascunho['versao']}:{contexto['turno_id']}",
            dados_cadastro(rascunho),
        )
    if dados_cadastro(rascunho) != operacao_aprovada:
        return {"status": "ERRO_VALIDACAO", "mensagem": "A proposta ou suas fotos mudaram após a aprovação. Confira os dados novamente."}
    unidade_id = await obter_unidade_id(usuario)
    async with abrir_cliente_qdrant() as cliente:
        await validar_selecao(
            QDRANT_COLECAO_CATEGORIA,
            dados.categoria_equipamento_id,
            unidade_id,
            cliente,
        )
        await validar_selecao(
            QDRANT_COLECAO_LOCAL,
            dados.local_endereco_id,
            unidade_id,
            cliente,
        )

    iniciou_envio = await atualizar_rascunho_solicitacao(
        sessao_id,
        usuario.usuario_id,
        {"status_fluxo": "enviando", "confirmado": True},
        status_esperados={"aguardando_confirmacao", "aguardando_imagem", "erro_api"}, **controle,
    )
    if not iniciou_envio:
        return {
            "status": "RESULTADO_INDETERMINADO",
            "mensagem": "O envio já está em andamento. Consulte a API antes de repetir.",
        }

    try:
        resultado = await adicionar_solicitacao(
            dados,
            access_token=usuario.access_token,
            imagens=imagens,
        )
    except Exception:
        registrador.exception("Falha ao enviar rascunho de solicitação à API")
        resultado = {
            "status": "RESULTADO_INDETERMINADO",
            "mensagem": (
                "Não foi possível confirmar o resultado do envio. "
                "Consulte a solicitação na API antes de repetir."
            ),
        }

    status_operacao = resultado.get("status")
    status_backend = resultado.get("status_backend")
    campos = {"status_fluxo": {
        "SUCESSO": "cadastrada", "RESULTADO_INDETERMINADO": "resultado_indeterminado",
    }.get(status_operacao, "erro_api")}
    if status_operacao == "SUCESSO":
        campos.update(problema_id_api=resultado.get("problema_id"), status_backend=status_backend,
                      status_solicitacao=_normalizar_status_backend(status_backend))
    try:
        await atualizar_rascunho_solicitacao(
            sessao_id, usuario.usuario_id, campos,
            status_esperados={"enviando"}, **controle,
        )
    except Exception:
        registrador.exception("Resultado da API recebido sem conseguir atualizar o rascunho")
    return resultado
