"""Ferramenta de contagem com identidade injetada pelo servidor."""

from datetime import date
from typing import Literal

from langchain.tools import ToolRuntime, tool
from app.tools.ajuda_geral.consultas import _Argumentos, _usuario, _acesso_negado
from app.services.ajuda_geral import contagens as servico


class _ContagemPessoal(_Argumentos):
    tipo_registro: Literal["solicitacao", "ocorrencia", "ordem_servico", "feedback"]
    situacao: Literal["PENDENTE", "REPROVADA", "APROVADA", "CONCLUIDA", "NAO_INICIADA",
                      "ATRASADA", "PAUSADA", "EM_ANDAMENTO", "ABERTA"] | None = None
    inicio: date | None = None
    fim: date | None = None


@tool(args_schema=_ContagemPessoal)
async def contar_meus_registros(
    tipo_registro: str, runtime: ToolRuntime, situacao: str | None = None,
    inicio: date | None = None, fim: date | None = None,
) -> dict:
    """Conta todos os registros próprios autorizados, sem limite de listagem.

    Solicitações e feedbacks: todos os perfis. Ocorrências e OS: técnico,
    gestor e administrador. OS próprias são as atribuídas ao usuário.
    Sem datas, conta todo o histórico ativo; se informadas, início inclusivo e
    fim exclusivo filtram a criação. Não aceita usuário ou unidade nos argumentos.
    Situação só se aplica a solicitação/OS; ABERTA é OS não concluída.
    """
    usuario = _usuario(runtime)
    if usuario is None:
        return _acesso_negado()
    return await servico.contar_meus_registros(
        usuario, tipo_registro, situacao=situacao, inicio=inicio, fim=fim,
    )
