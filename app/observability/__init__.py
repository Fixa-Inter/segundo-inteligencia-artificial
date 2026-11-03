"""Interface pública de app/observability; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'BYTES_VISUALIZACAO': ('.metricas', 'BYTES_VISUALIZACAO'),
    'CONSULTAS_VISUALIZACAO': ('.metricas', 'CONSULTAS_VISUALIZACAO'),
    'CUSTO_MODELO_USD': ('.metricas', 'CUSTO_MODELO_USD'),
    'CUSTO_RESOLUCAO_USD': ('.metricas', 'CUSTO_RESOLUCAO_USD'),
    'CUSTO_SEMANAL_ESTIMADO_USD': ('.metricas', 'CUSTO_SEMANAL_ESTIMADO_USD'),
    'DURACAO_CONSULTAS_VISUALIZACAO': ('.metricas', 'DURACAO_CONSULTAS_VISUALIZACAO'),
    'DURACAO_JEV': ('.metricas', 'DURACAO_JEV'),
    'DURACAO_NO_GRAFO': ('.metricas', 'DURACAO_NO_GRAFO'),
    'DURACAO_RESPOSTA_CONVERSA': ('.metricas', 'DURACAO_RESPOSTA_CONVERSA'),
    'EXECUCOES_NO_GRAFO': ('.metricas', 'EXECUCOES_NO_GRAFO'),
    'EXECUCOES_OPERACAO': ('.metricas', 'EXECUCOES_OPERACAO'),
    'MonitorMetricas': ('.metricas', 'MonitorMetricas'),
    'REAIS_POR_DOLAR': ('.metricas', 'REAIS_POR_DOLAR'),
    'REQUISICOES_CONVERSA': ('.metricas', 'REQUISICOES_CONVERSA'),
    'REQUISICOES_JEV': ('.metricas', 'REQUISICOES_JEV'),
    'REQUISICOES_PECHINCHA': ('.metricas', 'REQUISICOES_PECHINCHA'),
    'RESOLUCOES': ('.metricas', 'RESOLUCOES'),
    'ROI_CONFIGURADO': ('.metricas', 'ROI_CONFIGURADO'),
    'SomenteMetricasMiddleware': ('.tracing', 'SomenteMetricasMiddleware'),
    'TOKENS_MODELO': ('.metricas', 'TOKENS_MODELO'),
    'VALOR_ROI_BRL': ('.metricas', 'VALOR_ROI_BRL'),
    'adicionar_resolucao_pendente': ('.metricas', 'adicionar_resolucao_pendente'),
    'configurar_indicadores_cenarios': ('.metricas', 'configurar_indicadores_cenarios'),
    'configurar_somente_metricas': ('.tracing', 'configurar_somente_metricas'),
    'finalizar_resolucoes': ('.metricas', 'finalizar_resolucoes'),
    'gerar_conteudo_prometheus': ('.metricas', 'gerar_conteudo_prometheus'),
    'marcar_falha_requisicao': ('.metricas', 'marcar_falha_requisicao'),
    'obter_custo_requisicao_usd': ('.metricas', 'obter_custo_requisicao_usd'),
    'registrar_operacao': ('.metricas', 'registrar_operacao'),
    'registrar_resolucao': ('.metricas', 'registrar_resolucao'),
    'registrar_uso_modelo': ('.metricas', 'registrar_uso_modelo'),
    'reiniciar_custo_requisicao': ('.metricas', 'reiniciar_custo_requisicao'),
    'reiniciar_resolucoes_pendentes': ('.metricas', 'reiniciar_resolucoes_pendentes'),
    'reiniciar_resultado_requisicao': ('.metricas', 'reiniciar_resultado_requisicao'),
    'requisicao_falhou': ('.metricas', 'requisicao_falhou'),
    'restaurar_custo_requisicao': ('.metricas', 'restaurar_custo_requisicao'),
    'restaurar_resolucoes_pendentes': ('.metricas', 'restaurar_resolucoes_pendentes'),
    'restaurar_resultado_requisicao': ('.metricas', 'restaurar_resultado_requisicao'),
    'somente_metricas': ('.tracing', 'somente_metricas'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
