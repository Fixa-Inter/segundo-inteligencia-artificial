from app.tools import ArgumentosComRuntime
from typing import Literal
from langchain.tools import ToolRuntime, tool
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.schemas import UsuarioContexto
from app.services.ajuda_geral import (
    buscar_em_multiplas_colecoes as consultar_multiplas,
    buscar_semanticamente as consultar_semantica,
    buscar_termo_literal as consultar_literal,
    buscar_textos_semelhantes as consultar_semelhantes,
    listar_registros as consultar_registros,
)
from app.core import MENSAGENS

# Colecao: Recurso compartilhado de colecao usado pelas funções deste módulo e pela interface pública.
Colecao = Literal[
    "problema", "ocorrencia", "ordem_servico", "tarefa",
    "observacao_conclusao", "evento", "equipamento", "modelo_equipamento",
    "categoria_equipamento", "marca_equipamento", "local_unidade",
]
# ColecaoSolicitante: Recurso compartilhado de colecaosolicitante usado pelas funções deste módulo e pela interface pública.
ColecaoSolicitante = Literal[
    "problema", "local_unidade", "modelo_equipamento",
    "categoria_equipamento", "marca_equipamento",
]


# _Argumentos: contrato/estrutura de consultas; usado pelos consumidores desta interface.
class _Argumentos(ArgumentosComRuntime):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


# _BuscaSemantica: contrato/estrutura de consultas; usado pelos consumidores desta interface.
class _BuscaSemantica(_Argumentos):
    colecao: Colecao
    pergunta: str = Field(min_length=1, max_length=500)
    limite: int = Field(default=5, strict=True, ge=1, le=10)


# _BuscaMultipla: contrato/estrutura de consultas; usado pelos consumidores desta interface.
class _BuscaMultipla(_Argumentos):
    colecoes: list[Colecao] = Field(min_length=1, max_length=5)
    pergunta: str = Field(min_length=1, max_length=500)
    limite_por_colecao: int = Field(default=3, strict=True, ge=1, le=5)


# _Listagem: contrato/estrutura de consultas; usado pelos consumidores desta interface.
class _Listagem(_Argumentos):
    colecao: Colecao
    cursor_paginacao: str | None = Field(default=None, max_length=512)
    limite: int = Field(default=10, strict=True, ge=1, le=20)


# _BuscaLiteral: contrato/estrutura de consultas; usado pelos consumidores desta interface.
class _BuscaLiteral(_Argumentos):
    colecao: Colecao
    termo: str = Field(min_length=1, max_length=200)
    limite: int = Field(default=10, strict=True, ge=1, le=20)


# _BuscaSemelhantes: contrato/estrutura de consultas; usado pelos consumidores desta interface.
class _BuscaSemelhantes(_Argumentos):
    colecao: Colecao
    entidade_id: int = Field(strict=True, gt=0)
    limite: int = Field(default=5, strict=True, ge=1, le=10)


# _BuscaSemanticaSolicitante: contrato/estrutura de consultas; usado pelos consumidores desta interface.
class _BuscaSemanticaSolicitante(_BuscaSemantica):
    colecao: ColecaoSolicitante


# _BuscaMultiplaSolicitante: contrato/estrutura de consultas; usado pelos consumidores desta interface.
class _BuscaMultiplaSolicitante(_BuscaMultipla):
    colecoes: list[ColecaoSolicitante] = Field(min_length=1, max_length=5)


# _ListagemSolicitante: contrato/estrutura de consultas; usado pelos consumidores desta interface.
class _ListagemSolicitante(_Listagem):
    colecao: ColecaoSolicitante


# _BuscaLiteralSolicitante: contrato/estrutura de consultas; usado pelos consumidores desta interface.
class _BuscaLiteralSolicitante(_BuscaLiteral):
    colecao: ColecaoSolicitante


# _BuscaSemelhantesSolicitante: contrato/estrutura de consultas; usado pelos consumidores desta interface.
class _BuscaSemelhantesSolicitante(_BuscaSemelhantes):
    colecao: ColecaoSolicitante


def _usuario(runtime: ToolRuntime) -> UsuarioContexto | None:
    """Extrai o usuário autenticado do runtime sem aceitar identidade da conversa. Usado por buscar_em_multiplas_colecoes, buscar_semanticamente, buscar_termo_literal."""
    contexto = runtime.context
    if isinstance(contexto, dict) and isinstance(contexto.get("usuario"), UsuarioContexto):
        return contexto["usuario"]
    return None


def _acesso_negado() -> dict:
    """Monta resposta estruturada de acesso negado para a ferramenta. Usado por buscar_em_multiplas_colecoes, buscar_semanticamente, buscar_termo_literal."""
    return {
        "status": "ACESSO_NEGADO",
        "resultados": [],
        "cursor_paginacao": None,
        "mensagem": MENSAGENS['usuario_autenticado_nao_disponivel'],
    }


@tool(args_schema=_BuscaSemantica)
async def buscar_semanticamente(
    colecao: Colecao, pergunta: str, runtime: ToolRuntime, limite: int = 5,
) -> dict:
    """Busca textos relacionados à pergunta em uma collection permitida."""
    usuario = _usuario(runtime)
    if usuario is None:
        return _acesso_negado()
    return await consultar_semantica(usuario, colecao, pergunta, limite)


@tool(args_schema=_BuscaMultipla)
async def buscar_em_multiplas_colecoes(
    colecoes: list[Colecao], pergunta: str, runtime: ToolRuntime, limite_por_colecao: int = 3,
) -> dict:
    """Busca em várias collections e identifica a origem de cada texto."""
    usuario = _usuario(runtime)
    if usuario is None:
        return _acesso_negado()
    return await consultar_multiplas(usuario, colecoes, pergunta, limite_por_colecao)


@tool(args_schema=_Listagem)
async def listar_registros(
    colecao: Colecao, runtime: ToolRuntime, cursor_paginacao: str | None = None,
    limite: int = 10,
) -> dict:
    """Lista registros ativos da collection com cursor de paginação."""
    usuario = _usuario(runtime)
    if usuario is None:
        return _acesso_negado()
    return await consultar_registros(usuario, colecao, cursor_paginacao, limite)


@tool(args_schema=_BuscaLiteral)
async def buscar_termo_literal(
    colecao: Colecao, termo: str, runtime: ToolRuntime, limite: int = 10,
) -> dict:
    """Localiza palavra ou expressão na sequência escrita no campo texto."""
    usuario = _usuario(runtime)
    if usuario is None:
        return _acesso_negado()
    return await consultar_literal(usuario, colecao, termo, limite)


@tool(args_schema=_BuscaSemelhantes)
async def buscar_textos_semelhantes(
    colecao: Colecao, entidade_id: int, runtime: ToolRuntime, limite: int = 5,
) -> dict:
    """Busca textos parecidos com um registro da mesma collection, sem inferir vínculos."""
    usuario = _usuario(runtime)
    if usuario is None:
        return _acesso_negado()
    return await consultar_semelhantes(usuario, colecao, entidade_id, limite)


# Mesmo nome público, mas parâmetros de collections limitados no agente solicitante.
buscar_semanticamente_solicitante = tool(
    "buscar_semanticamente", args_schema=_BuscaSemanticaSolicitante,
)(buscar_semanticamente.coroutine)
# buscar_em_multiplas_colecoes_solicitante: Recurso compartilhado de buscar em multiplas colecoes solicitante usado pelas funções deste módulo e pela interface pública.
buscar_em_multiplas_colecoes_solicitante = tool(
    "buscar_em_multiplas_colecoes", args_schema=_BuscaMultiplaSolicitante,
)(buscar_em_multiplas_colecoes.coroutine)
# listar_registros_solicitante: Recurso compartilhado de listar registros solicitante usado pelas funções deste módulo e pela interface pública.
listar_registros_solicitante = tool(
    "listar_registros", args_schema=_ListagemSolicitante,
)(listar_registros.coroutine)
# buscar_termo_literal_solicitante: Recurso compartilhado de buscar termo literal solicitante usado pelas funções deste módulo e pela interface pública.
buscar_termo_literal_solicitante = tool(
    "buscar_termo_literal", args_schema=_BuscaLiteralSolicitante,
)(buscar_termo_literal.coroutine)
# buscar_textos_semelhantes_solicitante: Recurso compartilhado de buscar textos semelhantes solicitante usado pelas funções deste módulo e pela interface pública.
buscar_textos_semelhantes_solicitante = tool(
    "buscar_textos_semelhantes", args_schema=_BuscaSemelhantesSolicitante,
)(buscar_textos_semelhantes.coroutine)
