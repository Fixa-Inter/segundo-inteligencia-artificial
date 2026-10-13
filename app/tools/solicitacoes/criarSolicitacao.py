import logging
import re
import unicodedata
from typing import Any

from langchain.tools import ToolRuntime, tool
from pydantic import field_validator, model_validator

from app.core.clients.qdrant import abrir_cliente_qdrant
from app.core.config import QDRANT_CATEGORIA_COLLECTION, QDRANT_LOCAL_COLLECTION
from app.memory.persistencia.rascunho_solicitacao import (
    atualizar_rascunho_solicitacao,
    obter_rascunho_solicitacao,
    salvar_rascunho_solicitacao as persistir_rascunho,
)
from app.memory.vectorSearch import validar_selecao
from app.schemas.UsuarioContexto import UsuarioContexto
from app.services.solicitacoes.criarSolicitacao import adicionar_solicitacao
from app.tools.toolsRequest.CriarSolicitacaoRequest import CriarSolicitacaoRequest


logger = logging.getLogger(__name__)


class _ArgumentosCriarSolicitacao(CriarSolicitacaoRequest):
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

    session_id = contexto.get("session_id")
    if not isinstance(session_id, str) or not session_id.strip():
        raise ValueError("A sessão atual não foi informada ao agente.")

    return contexto, contexto["usuario"], session_id


def _confirmacao_explicita(texto: str) -> bool:
    if "?" in texto:
        return False
    normalizado = unicodedata.normalize("NFKD", texto.lower())
    normalizado = "".join(
        caractere for caractere in normalizado
        if not unicodedata.combining(caractere)
    )
    normalizado = re.sub(r"[^a-z0-9 ]", " ", normalizado)
    normalizado = " ".join(normalizado.split())

    if not normalizado or re.search(
        r"\b(nao|mas|porem|corrija|alterar|mude|como|qual|quando|onde|porque)\b",
        normalizado,
    ):
        return False

    frases = (
        "sim",
        "confirmo",
        "confirmado",
        "autorizo",
        "isso",
        "tudo certo",
        "pode cadastrar",
        "pode criar",
        "pode registrar",
        "pode enviar",
        "pode prosseguir",
        "pode seguir",
        "esta correto",
        "isso mesmo",
        "esta bom",
        "esta certo",
        "beleza",
        "fechado",
        "perfeito",
        "ok",
        "okay",
        "certo",
        "correto",
    )
    return any(
        normalizado == frase or normalizado.startswith(f"{frase} ")
        for frase in frases
    )


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
    _, usuario, session_id = _contexto(runtime)
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
        session_id=session_id,
        user_id=usuario.usuario_id,
        dados=dados.model_dump(),
    )
    return {
        "status": "RASCUNHO_SALVO",
        "mensagem": "Proposta salva na sessão. Ainda aguarda confirmação explícita.",
        "dados_salvos": rascunho["dados"],
        "imagens_recebidas": len(rascunho.get("imagens", [])),
        "imagens_associadas_ao_rascunho": bool(rascunho.get("imagens")),
    }


@tool
async def criar_solicitacao(runtime: ToolRuntime) -> dict:
    """Cria na API a solicitação salva no Mongo, somente após confirmação.

    A proposta e as imagens vêm do rascunho da sessão. A confirmação pode vir
    junto com as imagens; se as imagens forem enviadas depois, ficam anexadas
    ao rascunho até o envio.
    """
    contexto, usuario, session_id = _contexto(runtime)
    if usuario.tipo_acesso.lower() not in {"tecnico", "solicitante"}:
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Somente técnicos e solicitantes podem criar solicitações.",
        }

    rascunho = await obter_rascunho_solicitacao(session_id, usuario.usuario_id)
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

    mensagem_atual = contexto.get("mensagem_atual", "")
    ja_confirmado = (
        rascunho.get("confirmado") is True
        and status_fluxo == "aguardando_imagem"
    )
    if not ja_confirmado and not _confirmacao_explicita(str(mensagem_atual)):
        return {
            "status": "CONFIRMACAO_NECESSARIA",
            "mensagem": "Peça confirmação explícita da proposta antes de cadastrar.",
        }

    if not ja_confirmado:
        await atualizar_rascunho_solicitacao(
            session_id,
            usuario.usuario_id,
            {"confirmado": True},
            status_esperados={"aguardando_confirmacao", "erro_api"},
        )
        rascunho["confirmado"] = True

    imagens = rascunho.get("imagens", [])
    if not imagens:
        await atualizar_rascunho_solicitacao(
            session_id,
            usuario.usuario_id,
            {"status_fluxo": "aguardando_imagem", "confirmado": True},
            status_esperados={"aguardando_confirmacao", "aguardando_imagem", "erro_api"},
        )
        return {
            "status": "AGUARDANDO_INFORMACAO",
            "mensagem": (
                "A proposta foi confirmada. Envie pelo menos uma imagem para concluir o cadastro."
            ),
        }

    dados = CriarSolicitacaoRequest.model_validate(rascunho.get("dados", {}))
    async with abrir_cliente_qdrant() as client:
        await validar_selecao(
            QDRANT_CATEGORIA_COLLECTION,
            dados.categoria_equipamento_id,
            usuario.cnpj_endereco,
            client,
        )
        await validar_selecao(
            QDRANT_LOCAL_COLLECTION,
            dados.local_endereco_id,
            usuario.cnpj_endereco,
            client,
        )

    iniciou_envio = await atualizar_rascunho_solicitacao(
        session_id,
        usuario.usuario_id,
        {"status_fluxo": "enviando", "confirmado": True},
        status_esperados={"aguardando_confirmacao", "aguardando_imagem", "erro_api"},
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
        logger.exception("Falha ao enviar rascunho de solicitação à API")
        resultado = {
            "status": "RESULTADO_INDETERMINADO",
            "mensagem": (
                "Não foi possível confirmar o resultado do envio. "
                "Consulte a solicitação na API antes de repetir."
            ),
        }

    status_operacao = resultado.get("status")
    if status_operacao == "SUCESSO":
        status_backend = resultado.get("status_backend")
        await atualizar_rascunho_solicitacao(
            session_id,
            usuario.usuario_id,
            {
                "status_fluxo": "cadastrada",
                "problema_id_api": resultado.get("problema_id"),
                "status_backend": status_backend,
                "status_solicitacao": _normalizar_status_backend(status_backend),
            },
            status_esperados={"enviando"},
        )
    elif status_operacao == "RESULTADO_INDETERMINADO":
        await atualizar_rascunho_solicitacao(
            session_id,
            usuario.usuario_id,
            {"status_fluxo": "resultado_indeterminado"},
            status_esperados={"enviando"},
        )
    else:
        await atualizar_rascunho_solicitacao(
            session_id,
            usuario.usuario_id,
            {"status_fluxo": "erro_api"},
            status_esperados={"enviando"},
        )

    return resultado
