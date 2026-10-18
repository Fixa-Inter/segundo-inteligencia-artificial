from langchain.agents import create_agent

from app.agents.agentsResult import FAQResultado
from app.graph import ContextoGrafo
from app.tools.ajuda_geral import (
    buscar_semanticamente,
    buscar_em_multiplas_colecoes,
    listar_registros,
    buscar_termo_literal,
    buscar_textos_semelhantes,
    buscar_semanticamente_solicitante,
    buscar_em_multiplas_colecoes_solicitante,
    listar_registros_solicitante,
    buscar_termo_literal_solicitante,
    buscar_textos_semelhantes_solicitante,
)
from app.tools.ajuda_geral import (
    buscar_problemas_por_local,
    consultar_situacao_problema,
    consultar_modelos_por_marca_categoria,
    consultar_equipamento_por_codigo,
    encontrar_codigo_equipamento,
    listar_equipamentos_por_local,
    listar_ocorrencias_por_local,
    listar_tarefas_da_ordem,
    listar_observacoes_da_ordem,
    listar_eventos_por_local_e_periodo,
)
from app.tools.ajuda_geral import (
    alterar_informacao_solicitacao,
    anexar_foto_solicitacao,
    anexar_foto_ocorrencia,
    anexar_foto_observacao_conclusao,
)


def criar_agente_ajuda_geral(modelo, instrucao: str, *, perfil: str):
    if perfil not in {"solicitante", "tecnico", "gestor"}:
        raise ValueError("Perfil inválido para o agente ajuda_geral.")
    ferramentas_genericas = [
        buscar_semanticamente_solicitante,
        buscar_em_multiplas_colecoes_solicitante,
        listar_registros_solicitante,
        buscar_termo_literal_solicitante,
        buscar_textos_semelhantes_solicitante,
    ] if perfil == "solicitante" else [
        buscar_semanticamente,
        buscar_em_multiplas_colecoes,
        listar_registros,
        buscar_termo_literal,
        buscar_textos_semelhantes,
    ]
    ferramentas = ferramentas_genericas + [
        buscar_problemas_por_local,
        consultar_situacao_problema,
        consultar_modelos_por_marca_categoria,
        alterar_informacao_solicitacao,
        anexar_foto_solicitacao,
    ]
    if perfil in {"tecnico", "gestor"}:
        ferramentas.extend([
            consultar_equipamento_por_codigo,
            encontrar_codigo_equipamento,
            listar_equipamentos_por_local,
            listar_ocorrencias_por_local,
            listar_tarefas_da_ordem,
            listar_observacoes_da_ordem,
            listar_eventos_por_local_e_periodo,
            anexar_foto_ocorrencia,
            anexar_foto_observacao_conclusao,
        ])
    return create_agent(
        model=modelo,
        system_prompt=instrucao,
        tools=ferramentas,
        response_format=FAQResultado,
        context_schema=ContextoGrafo,
    )
