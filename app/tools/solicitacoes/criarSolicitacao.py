from typing import Literal

from langchain.tools import ToolRuntime, tool
from pydantic import field_validator, model_validator

from app.tools.toolsRequest.CriarSolicitacaoRequest import CriarSolicitacaoRequest
from app.services.solicitacoes.criarSolicitacao import adicionar_solicitacao
from app.schemas.UsuarioContexto import UsuarioContexto
from app.memory.vectorSearch import validar_selecao
from app.memory.vectorSearch.cliente import abrir_cliente_qdrant
from app.core.config import QDRANT_LOCAL_COLLECTION, QDRANT_CATEGORIA_COLLECTION


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
        # LangChain 1.3 injeta runtime antes da validação do args_schema.
        # Retirar somente o objeto real injetado; outros campos continuam proibidos.
        if isinstance(dados, dict) and isinstance(dados.get("runtime"), ToolRuntime):
            return {k: v for k, v in dados.items() if k != "runtime"}
        return dados


@tool(args_schema=_ArgumentosCriarSolicitacao)
async def criar_solicitacao(
    categoria_equipamento_id: int,
    local_endereco_id: int,
    categoria_problema: int,
    titulo: str,
    descricao_problema: str,
    runtime: ToolRuntime,
    descricao_local: str | None = None,
) -> dict:
    """Cadastra uma solicitação diretamente na API usando os IDs consultados.

    O código fornece UsuarioContexto em runtime.context["usuario"], com a
    identidade, a sede e o token autenticados. Não solicite esses dados à IA.
    Esta tool executa o POST imediatamente; não gerencia confirmação ou conversa.
    """
    contexto = runtime.context

    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
            raise ValueError("Forneça uma instância de UsuarioContexto em context['usuario'].")

    async with abrir_cliente_qdrant() as client:

        await validar_selecao(
                QDRANT_CATEGORIA_COLLECTION,
                categoria_equipamento_id,
                contexto["usuario"].endereco_id,
                client
            )

        await validar_selecao(
                QDRANT_LOCAL_COLLECTION,
                local_endereco_id,
                contexto["usuario"].endereco_id,
                client
            )
    
    usuario = contexto["usuario"]

    entrada = _ArgumentosCriarSolicitacao(
        categoria_equipamento_id=categoria_equipamento_id,
        local_endereco_id=local_endereco_id, categoria_problema=categoria_problema,
        titulo=titulo, descricao_problema=descricao_problema, descricao_local=descricao_local,
    )

    return await adicionar_solicitacao(
        entrada, 
        access_token=usuario.access_token
    )
