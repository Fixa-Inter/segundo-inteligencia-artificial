"""Interface pública de app/schemas; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'Agregacao': ('.visualizacao', 'Agregacao'),
    'Analise': ('.visualizacao', 'Analise'),
    'ApiResponse': ('.common', 'ApiResponse'),
    'AprovacaoVisualizacao': ('.visualizacao', 'AprovacaoVisualizacao'),
    'BaseCalculoVisualizacao': ('.visualizacao', 'BaseCalculoVisualizacao'),
    'ClassificarProblemaRequest': ('.ClassificarProblema', 'ClassificarProblemaRequest'),
    'ClassificarProblemaResponse': ('.ClassificarProblema', 'ClassificarProblemaResponse'),
    'ComparacaoPeriodosRequest': ('.analytics', 'ComparacaoPeriodosRequest'),
    'ConsultaVisualizacaoCapturada': ('.visualizacao', 'ConsultaVisualizacaoCapturada'),
    'ConsultaVisualizacaoPeriodo': ('.visualizacao', 'ConsultaVisualizacaoPeriodo'),
    'ConsultaVisualizacaoSnapshot': ('.visualizacao', 'ConsultaVisualizacaoSnapshot'),
    'ConversaEntrada': ('.chat', 'ConversaEntrada'),
    'ConversaEspecificaEntrada': ('.sessao', 'ConversaEspecificaEntrada'),
    'ConversaEspecificaSaida': ('.sessao', 'ConversaEspecificaSaida'),
    'ConversaHistorico': ('.sessao', 'ConversaHistorico'),
    'ConversaSaida': ('.chat', 'ConversaSaida'),
    'DadosBoxplot': ('.visualizacao', 'DadosBoxplot'),
    'DadosCategorias': ('.visualizacao', 'DadosCategorias'),
    'DadosHistograma': ('.visualizacao', 'DadosHistograma'),
    'DadosSerieTemporal': ('.visualizacao', 'DadosSerieTemporal'),
    'DadosVisualizacao': ('.visualizacao', 'DadosVisualizacao'),
    'DimensoesGrupo': ('.visualizacao', 'DimensoesGrupo'),
    'EncerrarSessaoSaida': ('.sessao', 'EncerrarSessaoSaida'),
    'ExcluirConversaSaida': ('.sessao', 'ExcluirConversaSaida'),
    'FiltroObrigatorio': ('.visualizacao', 'FiltroObrigatorio'),
    'Fonte': ('.visualizacao', 'Fonte'),
    'FormatoDados': ('.visualizacao', 'FormatoDados'),
    'GranularidadeTemporal': ('.visualizacao', 'GranularidadeTemporal'),
    'GrupoBoxplot': ('.visualizacao', 'GrupoBoxplot'),
    'GrupoSemBaseBoxplot': ('.visualizacao', 'GrupoSemBaseBoxplot'),
    'HealthResponse': ('.health', 'HealthResponse'),
    'IdSessaoCaminho': ('.id_sessao', 'IdSessaoCaminho'),
    'IntervaloHistograma': ('.visualizacao', 'IntervaloHistograma'),
    'LIMITE_CARACTERES_URL_IMAGEM': ('.imagem', 'LIMITE_CARACTERES_URL_IMAGEM'),
    'LIMITE_ID_SESSAO': ('.id_sessao', 'LIMITE_ID_SESSAO'),
    'LIMITE_IMAGENS_POR_MENSAGEM': ('.imagem', 'LIMITE_IMAGENS_POR_MENSAGEM'),
    'MensagemHistorico': ('.sessao', 'MensagemHistorico'),
    'MetadadosConsultaVisualizacao': ('.visualizacao', 'MetadadosConsultaVisualizacao'),
    'MetadadosVisualizacaoPublica': ('.visualizacao', 'MetadadosVisualizacaoPublica'),
    'PeriodoRequest': ('.analytics', 'PeriodoRequest'),
    'PeriodoSerieTemporal': ('.visualizacao', 'PeriodoSerieTemporal'),
    'PeriodoVisualizacao': ('.visualizacao', 'PeriodoVisualizacao'),
    'PontoCategoria': ('.visualizacao', 'PontoCategoria'),
    'PontoSerieTemporal': ('.visualizacao', 'PontoSerieTemporal'),
    'ReferenciaVisualizacao': ('.visualizacao', 'ReferenciaVisualizacao'),
    'ResultadoConsultaVisualizacao': ('.visualizacao', 'ResultadoConsultaVisualizacao'),
    'ResultadoGrupoBoxplot': ('.visualizacao', 'ResultadoGrupoBoxplot'),
    'ResumoGrupoPequeno': ('.visualizacao', 'ResumoGrupoPequeno'),
    'SelecaoFiltro': ('.visualizacao', 'SelecaoFiltro'),
    'StatusConsultaVisualizacao': ('.visualizacao', 'StatusConsultaVisualizacao'),
    'StatusVisualizacao': ('.visualizacao', 'StatusVisualizacao'),
    'TodasConversasSaida': ('.sessao', 'TodasConversasSaida'),
    'UsuarioContexto': ('.UsuarioContexto', 'UsuarioContexto'),
    'ValorFiltro': ('.visualizacao', 'ValorFiltro'),
    'ValorMedida': ('.visualizacao', 'ValorMedida'),
    'VisualizacaoPublica': ('.visualizacao', 'VisualizacaoPublica'),
    'cadastros': ('.cadastros', None),
    'normalizar_id_sessao': ('.id_sessao', 'normalizar_id_sessao'),
    'resultados_agentes': ('.resultados_agentes', None),
    'validar_url_imagem': ('.imagem', 'validar_url_imagem'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
