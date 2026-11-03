"""Interface pública de app/memory/persistencia; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'ARQUIVOS_RASCUNHOS': ('.rascunho_solicitacao', 'ARQUIVOS_RASCUNHOS'),
    'CAMPO': ('.analise_compra', 'CAMPO'),
    'COLECAO': ('.operacoes', 'COLECAO'),
    'ResumoGerado': ('.gerar_resumo', 'ResumoGerado'),
    'STATUS_ATIVOS_ANALISE_COMPRA': ('.analise_compra', 'STATUS_ATIVOS'),
    'STATUS_ATIVOS_RASCUNHO_SOLICITACAO': ('.rascunho_solicitacao', 'STATUS_ATIVOS'),
    'TipoRascunho': ('.rascunho_solicitacao', 'TipoRascunho'),
    'adicionar_imagens_sessao': ('.rascunho_solicitacao', 'adicionar_imagens_sessao'),
    'agora': ('.utilitarios', 'agora'),
    'atualizar_acao': ('.acao_ajuda_geral', 'atualizar_acao'),
    'atualizar_analise_compra': ('.analise_compra', 'atualizar_analise_compra'),
    'atualizar_rascunho_solicitacao': ('.rascunho_solicitacao', 'atualizar_rascunho_solicitacao'),
    'finalizar': ('.operacoes', 'finalizar'),
    'garantir_indice_persistencia': ('.garantir_indice', 'garantir_indice_persistencia'),
    'gerar_resumo': ('.gerar_resumo', 'gerar_resumo'),
    'iniciar': ('.operacoes', 'iniciar'),
    'iniciar_acao': ('.acao_ajuda_geral', 'iniciar_acao'),
    'marcar_confirmacao_mensagem': ('.salvar_mensagem', 'marcar_confirmacao_mensagem'),
    'obter': ('.operacoes', 'obter'),
    'obter_acao': ('.acao_ajuda_geral', 'obter_acao'),
    'obter_analise_compra': ('.analise_compra', 'obter_analise_compra'),
    'obter_documento_sessao_id': ('.utilitarios', 'obter_documento_sessao_id'),
    'obter_quantidade_anexos_pendentes': ('.rascunho_solicitacao', 'obter_quantidade_anexos_pendentes'),
    'obter_rascunho_solicitacao': ('.rascunho_solicitacao', 'obter_rascunho_solicitacao'),
    'preparar': ('.operacoes', 'preparar'),
    'recuperar_mensagens': ('.recuperar_mensagens', 'recuperar_mensagens'),
    'registrar_coleta_parcial': ('.rascunho_solicitacao', 'registrar_coleta_parcial'),
    'salvar_acao': ('.acao_ajuda_geral', 'salvar_acao'),
    'salvar_analise_compra': ('.analise_compra', 'salvar_analise_compra'),
    'salvar_mensagem': ('.salvar_mensagem', 'salvar_mensagem'),
    'salvar_rascunho_solicitacao': ('.rascunho_solicitacao', 'salvar_rascunho_solicitacao'),
    'sessao_acessivel': ('.utilitarios', 'sessao_acessivel'),
    'sessoes': ('.sessoes', None),
    'sessoes_ativas': ('.utilitarios', 'sessoes_ativas'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
