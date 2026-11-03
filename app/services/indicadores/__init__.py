"""Interface pública de app/services/indicadores; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'gerais': ('.gerais', None),
    'obter_carga_ativa_tecnicos': ('.ordem_servico', 'obter_carga_ativa_tecnicos'),
    'obter_media_tarefas_por_os': ('.ordem_servico', 'obter_media_tarefas_por_os'),
    'obter_ocorrencias_ativas': ('.ocorrencia', 'obter_ocorrencias_ativas'),
    'obter_ocorrencias_por_categoria_equipamento': ('.ocorrencia', 'obter_ocorrencias_por_categoria_equipamento'),
    'obter_ocorrencias_por_categoria_problema': ('.ocorrencia', 'obter_ocorrencias_por_categoria_problema'),
    'obter_ocorrencias_por_local': ('.ocorrencia', 'obter_ocorrencias_por_local'),
    'obter_ocorrencias_por_periodo': ('.ocorrencia', 'obter_ocorrencias_por_periodo'),
    'obter_ocorrencias_por_prioridade': ('.ocorrencia', 'obter_ocorrencias_por_prioridade'),
    'obter_ocorrencias_por_tecnico': ('.ocorrencia', 'obter_ocorrencias_por_tecnico'),
    'obter_ocorrencias_por_unidade': ('.ocorrencia', 'obter_ocorrencias_por_unidade'),
    'obter_os_abertas': ('.ordem_servico', 'obter_os_abertas'),
    'obter_os_atrasadas': ('.ordem_servico', 'obter_os_atrasadas'),
    'obter_os_finalizadas': ('.ordem_servico', 'obter_os_finalizadas'),
    'obter_produtividade_tecnicos': ('.ordem_servico', 'obter_produtividade_tecnicos'),
    'obter_solicitacoes_aprovadas': ('.problema', 'obter_solicitacoes_aprovadas'),
    'obter_solicitacoes_pendentes': ('.problema', 'obter_solicitacoes_pendentes'),
    'obter_solicitacoes_por_categoria_equipamento': ('.problema', 'obter_solicitacoes_por_categoria_equipamento'),
    'obter_solicitacoes_por_local': ('.problema', 'obter_solicitacoes_por_local'),
    'obter_solicitacoes_por_periodo': ('.problema', 'obter_solicitacoes_por_periodo'),
    'obter_solicitacoes_por_unidade': ('.problema', 'obter_solicitacoes_por_unidade'),
    'obter_solicitacoes_reprovadas': ('.problema', 'obter_solicitacoes_reprovadas'),
    'obter_taxa_aprovacao_solicitacoes': ('.problema', 'obter_taxa_aprovacao_solicitacoes'),
    'obter_taxa_atraso_os': ('.ordem_servico', 'obter_taxa_atraso_os'),
    'obter_taxa_conclusao_prazo': ('.ordem_servico', 'obter_taxa_conclusao_prazo'),
    'obter_taxa_conversao_solicitacoes_os': ('.problema', 'obter_taxa_conversao_solicitacoes_os'),
    'obter_taxa_ocorrencias_alta_prioridade': ('.ocorrencia', 'obter_taxa_ocorrencias_alta_prioridade'),
    'obter_taxa_reabertura_os': ('.ordem_servico', 'obter_taxa_reabertura_os'),
    'obter_taxa_reatribuicao_os': ('.ordem_servico', 'obter_taxa_reatribuicao_os'),
    'obter_taxa_recorrencia_local_categoria': ('.problema', 'obter_taxa_recorrencia_local_categoria'),
    'obter_taxa_reprovacao_solicitacoes': ('.problema', 'obter_taxa_reprovacao_solicitacoes'),
    'obter_tempo_medio_espera_os': ('.ordem_servico', 'obter_tempo_medio_espera_os'),
    'obter_tempo_medio_pausado_os': ('.ordem_servico', 'obter_tempo_medio_pausado_os'),
    'obter_tempo_medio_resolucao_os': ('.ordem_servico', 'obter_tempo_medio_resolucao_os'),
    'obter_total_ocorrencias': ('.ocorrencia', 'obter_total_ocorrencias'),
    'obter_total_os': ('.ordem_servico', 'obter_total_os'),
    'obter_total_solicitacoes': ('.problema', 'obter_total_solicitacoes'),
    'ordem_servico': ('.ordem_servico', None),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
