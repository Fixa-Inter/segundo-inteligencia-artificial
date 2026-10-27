"""Propostas e confirmação de alterações em registros existentes."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Literal
from urllib.parse import urlparse

from langchain.tools import ToolRuntime, tool
from pydantic import Field
from app.core.confirmacoes import aceite_explicito

from app.memory.persistencia import (
    atualizar_acao, iniciar_acao, obter_acao, salvar_acao,
)
from app.schemas import UsuarioContexto
from app.services.ajuda_geral import edicoes as servico
from app.tools.ajuda_geral.consultas import _Argumentos


registrador = logging.getLogger(__name__)
Tipo = Literal["solicitacao", "ocorrencia", "observacao_conclusao"]


class _Alteracao(_Argumentos):
    problema_id: int | None = Field(default=None, strict=True, gt=0)
    campo: Literal[
        "categoria_equipamento_id", "local_unidade_id",
        "titulo", "descricao_problema", "descricao_local",
    ] | None = None
    novo_valor: int | str | None = None


class _AnexoSolicitacao(_Argumentos):
    problema_id: int | None = Field(default=None, strict=True, gt=0)


class _AnexoOcorrencia(_Argumentos):
    ocorrencia_id: int | None = Field(default=None, strict=True, gt=0)


class _AnexoObservacao(_Argumentos):
    observacao_conclusao_id: int | None = Field(default=None, strict=True, gt=0)


def _contexto(runtime: ToolRuntime) -> tuple[dict, UsuarioContexto, str]:
    contexto = runtime.context
    if not isinstance(contexto, dict):
        raise PermissionError("Contexto de autenticação ausente.")
    usuario = contexto.get("usuario")
    sessao = contexto.get("session_id")
    turno = contexto.get("turno_id")
    if not isinstance(usuario, UsuarioContexto) or usuario.tipo_acesso not in {
        "solicitante", "tecnico", "gestor", "administrador",
    } or not isinstance(sessao, str) or not sessao or not isinstance(turno, str) or not turno:
        raise PermissionError("Contexto de autenticação ou sessão inválido.")
    return contexto, usuario, sessao


def _imagens(contexto: dict) -> list[str]:
    bruto = contexto.get("imagens", [])
    if not isinstance(bruto, list) or len(bruto) > 5:
        raise ValueError("Envie no máximo cinco imagens.")
    urls = []
    for imagem in bruto:
        if not isinstance(imagem, str):
            raise ValueError("Imagem inválida.")
        url = imagem.strip()
        partes = urlparse(url)
        if len(url) > 255 or partes.scheme not in {"https", "http"} or not partes.netloc or partes.username:
            raise ValueError("A imagem deve ter uma URL HTTP(S) válida de até 255 caracteres.")
        if url not in urls:
            urls.append(url)
    return urls


def _erro(erro: Exception) -> dict:
    if isinstance(erro, PermissionError):
        return {"status": "ACESSO_NEGADO", "mensagem": str(erro)}
    if isinstance(erro, ValueError):
        return {"status": "ENTRADA_INVALIDA", "mensagem": str(erro)}
    registrador.exception("Falha na edição do ajuda_geral")
    return {"status": "ERRO", "mensagem": "Não foi possível processar a alteração."}


def _confirmacao_edicao(mensagem: str) -> bool:
    return aceite_explicito(mensagem, acoes=("alterar", "atualizar", "anexar", "enviar", "salvar", "prosseguir", "seguir", "continuar"))


async def _executar_pendente(contexto: dict, usuario: UsuarioContexto, sessao: str, acao: dict) -> dict:
    if acao.get("pausado"):
        return {"status": "CONFIRMACAO_NECESSARIA", "mensagem": "Retome explicitamente a proposta pausada antes de confirmar."}
    if acao.get("status") != "aguardando_confirmacao":
        return {"status": "AGUARDANDO_INFORMACAO", "mensagem": "A proposta ainda não está pronta para confirmação."}
    if acao.get("turno_id") == contexto["turno_id"]:
        return {"status": "CONFIRMACAO_NECESSARIA", "mensagem": "Confirme em uma nova mensagem após ver a proposta."}
    criada_em = acao.get("criada_em")
    if not isinstance(criada_em, datetime):
        return {"status": "PROPOSTA_EXPIRADA", "mensagem": "A proposta expirou. Peça uma nova consulta."}
    if criada_em.tzinfo is None:
        criada_em = criada_em.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) - criada_em > timedelta(minutes=30):
        return {"status": "PROPOSTA_EXPIRADA", "mensagem": "A proposta expirou. Peça uma nova consulta."}
    if not _confirmacao_edicao(str(contexto.get("mensagem_atual", ""))):
        return {"status": "CONFIRMACAO_NECESSARIA", "mensagem": "Confirme explicitamente a proposta exibida antes da alteração."}
    if not await iniciar_acao(sessao, usuario.usuario_id, acao["id"]):
        return {"status": "RESULTADO_INDETERMINADO", "mensagem": "Esta proposta já foi processada ou está em processamento."}
    try:
        if acao["tipo"] == "alteracao":
            resultado = await servico.alterar_solicitacao(
                usuario, acao["registro_id"], acao["campo"], acao["novo_valor"],
            )
            if resultado is None:
                resposta = {"status": "NAO_PERMITIDO", "mensagem": "A solicitação deixou de estar pendente, a opção escolhida ficou indisponível ou o usuário perdeu acesso."}
            else:
                resposta = {"status": "SUCESSO", "registro": resultado}
        else:
            ids = await servico.anexar_fotos(
                usuario, acao["tipo"], acao["registro_id"], acao["imagens"],
            )
            if ids is None:
                resposta = {"status": "NAO_PERMITIDO", "mensagem": "O registro não está mais disponível para este usuário."}
            else:
                resposta = {"status": "SUCESSO", "registro_id": acao["registro_id"], "foto_ids": ids}
        finalizada = await atualizar_acao(
            sessao, usuario.usuario_id, acao["id"],
            {"status": "concluida" if resposta["status"] == "SUCESSO" else "recusada", "resultado": resposta},
            status="executando",
        )
        if not finalizada:
            registrador.error("Mutação SQL concluída sem conseguir finalizar a ação %s no Mongo", acao["id"])
            return {"status": "RESULTADO_INDETERMINADO", "mensagem": "A alteração pode ter sido concluída. Confira o registro antes de repetir."}
        return resposta
    except Exception:
        registrador.exception("Resultado de mutação SQL não confirmado")
        await atualizar_acao(
            sessao, usuario.usuario_id, acao["id"], {"status": "resultado_indeterminado"},
            status="executando",
        )
        return {"status": "RESULTADO_INDETERMINADO", "mensagem": "Confira o registro no banco antes de tentar novamente."}


async def _propor(
    runtime: ToolRuntime, tipo: Tipo | Literal["alteracao"], registro_id: int | None,
    campo: str | None = None, novo_valor: int | str | None = None,
) -> dict:
    try:
        contexto, usuario, sessao = _contexto(runtime)
        if tipo in {"ocorrencia", "observacao_conclusao"} and usuario.tipo_acesso == "solicitante":
            raise PermissionError("Seu perfil não pode alterar esse tipo de registro.")
        acao = await obter_acao(sessao, usuario.usuario_id)
        if acao and acao.get("status") in {"executando", "resultado_indeterminado"}:
            return {"status": "RESULTADO_INDETERMINADO", "mensagem": "Confira a última alteração no banco antes de criar outra proposta."}
        if (acao and acao.get("tipo") == tipo and acao.get("status") == "concluida"
                and registro_id is None and _confirmacao_edicao(str(contexto.get("mensagem_atual", "")))):
            return {"status": "JA_CONCLUIDA", "resultado_anterior": acao.get("resultado"),
                    "mensagem": "A proposta anterior já foi executada."}
        imagens = _imagens(contexto) if tipo != "alteracao" else []
        if acao and not acao.get("pausado") and acao.get("tipo") == tipo and acao.get("status") == "aguardando_imagem" and registro_id is None:
            if not imagens:
                return {"status": "AGUARDANDO_IMAGEM", "mensagem": "Envie a imagem da proposta apresentada."}
            registro_id = acao["registro_id"]
        if acao and not acao.get("pausado") and acao.get("tipo") == tipo and acao.get("status") == "aguardando_confirmacao":
            if registro_id is None or (registro_id == acao.get("registro_id") and not imagens
                    and (tipo != "alteracao" or (campo is None and novo_valor is None))):
                return await _executar_pendente(contexto, usuario, sessao, acao)
        if registro_id is None:
            return {"status": "ID_NECESSARIO", "mensagem": "Encontre primeiro o ID exato do registro."}
        if tipo == "alteracao":
            if campo in servico.CAMPOS_RELACIONAIS:
                if type(novo_valor) is not int or novo_valor <= 0:
                    raise ValueError("Encontre o ID da nova categoria ou do novo local e informe-o como inteiro positivo.")
            elif campo in servico.CAMPOS_EDITAVEIS:
                if not isinstance(novo_valor, str):
                    raise ValueError("Informe o novo texto para esse campo.")
                novo_valor = novo_valor.strip()
                if not novo_valor or len(novo_valor) > servico.CAMPOS_EDITAVEIS[campo]:
                    raise ValueError("O valor está vazio ou excede o tamanho permitido.")
            else:
                raise ValueError("Informe um dos cinco campos editáveis e o novo valor.")
            tipo_sql = "solicitacao"
        else:
            tipo_sql = tipo
        registro = await servico.localizar_registro(usuario, tipo_sql, registro_id)
        if registro is None:
            return {"status": "NAO_ENCONTRADO", "mensagem": "Registro não encontrado, indisponível ou sem autorização."}
        opcao_destino = None
        if tipo == "alteracao" and campo in servico.CAMPOS_RELACIONAIS:
            opcao_destino = await servico.localizar_opcao(usuario, campo, novo_valor)
            if opcao_destino is None:
                return {"status": "OPCAO_INVALIDA", "mensagem": "A nova categoria ou local não está ativo na unidade do usuário."}
        status = "aguardando_confirmacao" if tipo == "alteracao" or imagens else "aguardando_imagem"
        proposta = await salvar_acao(sessao, usuario.usuario_id, {
            "tipo": tipo, "registro_id": registro_id, "campo": campo,
            "novo_valor": novo_valor, "imagens": imagens,
            "status": status, "turno_id": contexto["turno_id"],
        })
        return {
            "status": "AGUARDANDO_CONFIRMACAO" if status == "aguardando_confirmacao" else "AGUARDANDO_IMAGEM",
            "proposta_id": proposta["id"], "registro": registro,
            "mudanca": {"campo": campo, "novo_valor": novo_valor} if tipo == "alteracao"
                       else {"quantidade_imagens": len(imagens)},
            "opcao_destino": opcao_destino,
            "mensagem": "Confirme em uma nova mensagem se este é o registro correto e autoriza a mudança."
                        if status == "aguardando_confirmacao" else "Envie a imagem; depois mostrarei a proposta para confirmação.",
        }
    except Exception as erro:
        return _erro(erro)


@tool(args_schema=_Alteracao)
async def alterar_informacao_solicitacao(
    runtime: ToolRuntime, problema_id: int | None = None,
    campo: str | None = None, novo_valor: int | str | None = None,
) -> dict:
    """Propõe ou confirma edição de cinco campos de solicitação própria pendente."""
    return await _propor(runtime, "alteracao", problema_id, campo, novo_valor)


@tool(args_schema=_AnexoSolicitacao)
async def anexar_foto_solicitacao(runtime: ToolRuntime, problema_id: int | None = None) -> dict:
    """Propõe ou confirma anexar imagens da mensagem a solicitação própria pendente."""
    return await _propor(runtime, "solicitacao", problema_id)


@tool(args_schema=_AnexoOcorrencia)
async def anexar_foto_ocorrencia(runtime: ToolRuntime, ocorrencia_id: int | None = None) -> dict:
    """Propõe ou confirma foto de ocorrência própria de técnico ou da unidade do gestor."""
    return await _propor(runtime, "ocorrencia", ocorrencia_id)


@tool(args_schema=_AnexoObservacao)
async def anexar_foto_observacao_conclusao(
    runtime: ToolRuntime, observacao_conclusao_id: int | None = None,
) -> dict:
    """Propõe ou confirma foto da observação da ordem atribuída ao técnico ou da unidade do gestor."""
    return await _propor(runtime, "observacao_conclusao", observacao_conclusao_id)
