"""Interface pública de app/graph; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'CONSULTAS_COM_ORIENTACAO': ('.respostas_padrao', 'CONSULTAS_COM_ORIENTACAO'),
    'ContextoGrafo': ('.contexto', 'ContextoGrafo'),
    'EstadoGrafo': ('.estado', 'EstadoGrafo'),
    'PERFIS_VALIDOS': ('.executor', 'PERFIS_VALIDOS'),
    'Perfil': ('.executor', 'Perfil'),
    'TEXTOS': ('.respostas_padrao', 'TEXTOS'),
    'alterar_continuacao': ('.continuacoes', 'alterar_continuacao'),
    'construir_grafo': ('.fluxo', 'construir_grafo'),
    'criar_estado_inicial': ('.executor', 'criar_estado_inicial'),
    'decidir_apos_entrada': ('.transicoes', 'decidir_apos_entrada'),
    'decidir_apos_julgamento': ('.transicoes', 'decidir_apos_julgamento'),
    'decidir_apos_visualizacao': ('.transicoes', 'decidir_apos_visualizacao'),
    'esclarecer_continuacao': ('.continuacoes', 'esclarecer_continuacao'),
    'executar_ajuda_geral': ('.nos', 'executar_ajuda_geral'),
    'executar_analista_compras': ('.nos', 'executar_analista_compras'),
    'executar_com_evidencias': ('.evidencias', 'executar_com_evidencias'),
    'executar_faq': ('.nos', 'executar_faq'),
    'executar_grafo': ('.executor', 'executar_grafo'),
    'executar_indicadores': ('.nos', 'executar_indicadores'),
    'executar_operacoes': ('.operacoes', 'executar_operacoes'),
    'executar_retorno_usuario': ('.nos', 'executar_retorno_usuario'),
    'executar_servico': ('.operacoes', 'executar_servico'),
    'executar_solicitacao': ('.nos', 'executar_solicitacao'),
    'executar_visualizacao': ('.nos', 'executar_visualizacao'),
    'extrair_evidencias': ('.evidencias', 'extrair_evidencias'),
    'grafo': ('.fluxo', 'grafo'),
    'ids_chamadas': ('.evidencias', 'ids_chamadas'),
    'limpar_visualizacao': ('.estado', 'limpar_visualizacao'),
    'obter_pergunta': ('.nos', 'obter_pergunta'),
    'pausar_outros_fluxos': ('.continuacoes', 'pausar_outros_fluxos'),
    'preparar_resposta': ('.propostas', 'preparar_resposta'),
    'preparar_resposta_padrao': ('.respostas_padrao', 'preparar_resposta_padrao'),
    'propostas_pendentes': ('app.core.continuacoes', 'propostas_pendentes'),
    'propostas_resposta': ('.propostas', 'propostas_resposta'),
    'resposta_interrupcao_proposta': ('.respostas_padrao', 'resposta_interrupcao_proposta'),
    'resposta_padrao_validada': ('.respostas_padrao', 'resposta_padrao_validada'),
    'resposta_resultados': ('.operacoes', 'resposta_resultados'),
    'selecionar_especialista': ('.transicoes', 'selecionar_especialista'),
    'selecionar_resposta_fallback': ('.respostas_padrao', 'selecionar_resposta_fallback'),
    'selecionar_resposta_saida': ('.respostas_padrao', 'selecionar_resposta_saida'),
    'supervisionar': ('.nos', 'supervisionar'),
    'tratar_continuacao': ('.continuacoes', 'tratar_continuacao'),
    'tratar_erro': ('.nos', 'tratar_erro'),
    'validar_entrada': ('.nos', 'validar_entrada'),
    'validar_saida': ('.nos', 'validar_saida'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
