"""Adapta a política gerencial existente ao contrato das visualizações."""


from app.schemas import UsuarioContexto
from app.schemas.visualizacao import ResultadoConsultaVisualizacao
from app.services.visualizacoes import PERFIS_VISUALIZACOES
from app.tools.metricas_kpis import contexto as contexto_indicadores

from app.core.respostas import MENSAGENS, MENSAGEM_BLOQUEIO_MOBILE
from app.graph.respostas_padrao import escolher_resposta


def validar_acesso(runtime) -> ResultadoConsultaVisualizacao | None:
    contexto = getattr(runtime, "context", None)
    if isinstance(contexto, dict) and contexto.get("plataforma") == "mobile":
        return ResultadoConsultaVisualizacao(
            status="ACESSO_NEGADO", mensagem=MENSAGEM_BLOQUEIO_MOBILE,
        )
    usuario = contexto.get("usuario") if isinstance(contexto, dict) else None
    # O contexto já vem da autenticação; não coagir IDs adulterados em memória.
    if isinstance(usuario, UsuarioContexto) and type(usuario.usuario_id) is not int:
        return ResultadoConsultaVisualizacao(
            status="ACESSO_NEGADO", mensagem=MENSAGENS['usuario_autenticado_invalido_para_consultar_visualizacoes'],
        )
    try:
        negado = contexto_indicadores.validar_gestor(runtime, perfis_permitidos=PERFIS_VISUALIZACOES)
    except (AttributeError, TypeError):
        negado = True
    if negado:
        return ResultadoConsultaVisualizacao(
            status="ACESSO_NEGADO",
            mensagem=MENSAGENS['e_necessario_um_contexto_autenticado_de_gestor_ou_administrador_para_consultar_visualizacoes'],
        )
    return None


async def resolver_unidade(runtime) -> int | ResultadoConsultaVisualizacao:
    negado = validar_acesso(runtime)
    if negado is not None:
        return negado
    resultado = await contexto_indicadores.resolver_unidade_indicadores(
        runtime, perfis_permitidos=PERFIS_VISUALIZACOES,
    )
    if isinstance(resultado, dict):
        negado = resultado.get("status") == "ACESSO_NEGADO"
        return ResultadoConsultaVisualizacao(
            status="ACESSO_NEGADO" if negado else "ERRO_FERRAMENTA",
            mensagem=(
                escolher_resposta(negado, 'nao_foi_possivel_validar_sua_unidade_para_consultar_visualizacoes', 'nao_foi_possivel_resolver_a_unidade_autenticada_agora')
            ),
        )
    return resultado
