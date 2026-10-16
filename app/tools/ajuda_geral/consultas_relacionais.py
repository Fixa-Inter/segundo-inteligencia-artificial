"""Ferramentas de consulta com relações verificadas no banco FIXA."""

from datetime import date

from langchain.tools import ToolRuntime, tool
from pydantic import Field

from app.tools.ajuda_geral.consultas import _Argumentos, _acesso_negado, _usuario
from app.services.ajuda_geral import consultas_relacionais as servico


class _PorLocal(_Argumentos):
    nome_local: str = Field(min_length=1, max_length=100)
    limite: int = Field(default=10, strict=True, ge=1, le=10)


class _SituacaoProblema(_Argumentos):
    problema_id: int = Field(strict=True, gt=0)


class _Modelos(_Argumentos):
    marca: str | None = Field(default=None, min_length=1, max_length=100)
    categoria: str | None = Field(default=None, min_length=1, max_length=100)
    limite: int = Field(default=10, strict=True, ge=1, le=10)


class _Codigo(_Argumentos):
    codigo: str = Field(min_length=1, max_length=100)


class _EncontrarCodigo(_Argumentos):
    modelo: str | None = Field(default=None, min_length=1, max_length=100)
    local: str | None = Field(default=None, min_length=1, max_length=100)
    marca: str | None = Field(default=None, min_length=1, max_length=100)
    categoria: str | None = Field(default=None, min_length=1, max_length=100)
    limite: int = Field(default=10, strict=True, ge=1, le=10)


class _PorOrdem(_Argumentos):
    ordem_servico_id: int = Field(strict=True, gt=0)
    limite: int = Field(default=20, strict=True, ge=1, le=20)


class _Eventos(_Argumentos):
    nome_local: str = Field(min_length=1, max_length=100)
    data_inicio: date
    data_fim: date
    limite: int = Field(default=20, strict=True, ge=1, le=20)


@tool(args_schema=_PorLocal)
async def buscar_problemas_por_local(
    nome_local: str, runtime: ToolRuntime, limite: int = 10,
) -> dict:
    """Busca problemas de um local; solicitantes veem apenas os próprios."""
    usuario = _usuario(runtime)
    return await servico.buscar_problemas_por_local(usuario, nome_local, limite) if usuario else _acesso_negado()


@tool(args_schema=_SituacaoProblema)
async def consultar_situacao_problema(problema_id: int, runtime: ToolRuntime) -> dict:
    """Consulta a situação atual e o motivo de recusa de um problema autorizado."""
    usuario = _usuario(runtime)
    return await servico.consultar_situacao_problema(usuario, problema_id) if usuario else _acesso_negado()


@tool(args_schema=_Modelos)
async def consultar_modelos_por_marca_categoria(
    runtime: ToolRuntime, marca: str | None = None,
    categoria: str | None = None, limite: int = 10,
) -> dict:
    """Lista modelos vinculados à marca, à categoria ou a ambas."""
    usuario = _usuario(runtime)
    return await servico.consultar_modelos_por_marca_categoria(
        usuario, marca, categoria, limite,
    ) if usuario else _acesso_negado()


@tool(args_schema=_Codigo)
async def consultar_equipamento_por_codigo(codigo: str, runtime: ToolRuntime) -> dict:
    """Consulta equipamento pelo código exato; apenas técnico e gestor."""
    usuario = _usuario(runtime)
    return await servico.consultar_equipamento_por_codigo(usuario, codigo) if usuario else _acesso_negado()


@tool(args_schema=_EncontrarCodigo)
async def encontrar_codigo_equipamento(
    runtime: ToolRuntime, modelo: str | None = None, local: str | None = None,
    marca: str | None = None, categoria: str | None = None, limite: int = 10,
) -> dict:
    """Encontra códigos de equipamentos por modelo, local, marca ou categoria."""
    usuario = _usuario(runtime)
    return await servico.encontrar_codigo_equipamento(
        usuario, modelo, local, marca, categoria, limite,
    ) if usuario else _acesso_negado()


@tool(args_schema=_PorLocal)
async def listar_equipamentos_por_local(
    nome_local: str, runtime: ToolRuntime, limite: int = 10,
) -> dict:
    """Lista equipamentos cadastrados em um local; apenas técnico e gestor."""
    usuario = _usuario(runtime)
    return await servico.listar_equipamentos_por_local(usuario, nome_local, limite) if usuario else _acesso_negado()


@tool(args_schema=_PorLocal)
async def listar_ocorrencias_por_local(
    nome_local: str, runtime: ToolRuntime, limite: int = 10,
) -> dict:
    """Lista ocorrências registradas em um local; apenas técnico e gestor."""
    usuario = _usuario(runtime)
    return await servico.listar_ocorrencias_por_local(usuario, nome_local, limite) if usuario else _acesso_negado()


@tool(args_schema=_PorOrdem)
async def listar_tarefas_da_ordem(
    ordem_servico_id: int, runtime: ToolRuntime, limite: int = 20,
) -> dict:
    """Lista tarefas vinculadas à ordem informada; apenas técnico e gestor."""
    usuario = _usuario(runtime)
    return await servico.listar_tarefas_da_ordem(usuario, ordem_servico_id, limite) if usuario else _acesso_negado()


@tool(args_schema=_PorOrdem)
async def listar_observacoes_da_ordem(
    ordem_servico_id: int, runtime: ToolRuntime, limite: int = 20,
) -> dict:
    """Lista observações de conclusão da ordem; apenas técnico e gestor."""
    usuario = _usuario(runtime)
    return await servico.listar_observacoes_da_ordem(usuario, ordem_servico_id, limite) if usuario else _acesso_negado()


@tool(args_schema=_Eventos)
async def listar_eventos_por_local_e_periodo(
    nome_local: str, data_inicio: date, data_fim: date,
    runtime: ToolRuntime, limite: int = 20,
) -> dict:
    """Lista eventos de um local e período; apenas técnico e gestor."""
    usuario = _usuario(runtime)
    return await servico.listar_eventos_por_local_e_periodo(
        usuario, nome_local, data_inicio, data_fim, limite,
    ) if usuario else _acesso_negado()
