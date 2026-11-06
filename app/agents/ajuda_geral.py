from langchain.agents import create_agent
from app.schemas.resultados_agentes import FAQResultado
from app.graph import ContextoGrafo
from app.tools.ajuda_geral import (
    contar_meus_registros,
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
    alterar_informacao_solicitacao,
    anexar_foto_solicitacao,
    anexar_foto_ocorrencia,
    anexar_foto_observacao_conclusao,
)
from app.tools.memoria import buscar_historico
from app.tools.feedback import listar_meus_feedbacks
from app.tools.solicitacoes import (
    buscar_solicitacoes_para_atualizar,
    atualizar_solicitacao,
    listar_minhas_solicitacoes,
    listar_todas_solicitacoes_pendentes,
)
from app.tools.ocorrencias import (
    listar_minhas_ocorrencias,
    buscar_ocorrencias_para_atualizar,
    atualizar_ocorrencia,
)
from app.tools.ordensServico import (
    listar_minhas_ordens_servico,
    listar_todas_ordens_servico,
    buscar_ordem_servico,
)
from app.tools.tecnicos import buscar_tecnicos_disponiveis

def criar_agente_ajuda_geral(modelo, instrucao: str, *, perfil: str):
    # Validação: rejeita entrada/contexto incompatível antes de prosseguir.
    """Compõe agente de ajuda geral com ferramentas e contrato do perfil. Usado pelo fluxo de agents."""
    if perfil not in {"solicitante", "tecnico", "gestor", "administrador"}:
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
        contar_meus_registros,
        listar_meus_feedbacks, buscar_solicitacoes_para_atualizar, atualizar_solicitacao,
        buscar_historico,
        buscar_problemas_por_local,
        consultar_situacao_problema,
        consultar_modelos_por_marca_categoria,
        alterar_informacao_solicitacao,
        anexar_foto_solicitacao,
    ]
    if perfil in {"solicitante", "tecnico"}:
        ferramentas.append(listar_minhas_solicitacoes)
    if perfil in {"tecnico", "gestor", "administrador"}:
        ferramentas.extend([
            buscar_ocorrencias_para_atualizar, atualizar_ocorrencia,
            listar_minhas_ocorrencias,
            listar_minhas_ordens_servico,
            buscar_ordem_servico,
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
    if perfil in {"gestor", "administrador"}:
        ferramentas.extend([
            listar_todas_solicitacoes_pendentes,
            listar_todas_ordens_servico,
            buscar_tecnicos_disponiveis,
        ])
    return create_agent(
        model=modelo,
        system_prompt=instrucao,
        tools=ferramentas,
        response_format=FAQResultado,
        context_schema=ContextoGrafo,
    )
