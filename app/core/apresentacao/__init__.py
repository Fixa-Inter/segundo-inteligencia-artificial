"""Interface pública de app/core/apresentacao; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    '_avisos_base': ('.visualizacoes', '_avisos_base'),
    'avisos_base': ('.visualizacoes', '_avisos_base'),
    'escolher_resposta': ('.textos', 'escolher_resposta'),
    'formatar_resposta': ('.textos', 'formatar_resposta'),
    'pergunta_opcionais_compra': ('.compras', 'pergunta_opcionais_compra'),
    'resposta_bloqueio_seguranca': ('.textos', 'resposta_bloqueio_seguranca'),
    'resposta_busca_compra': ('.compras', 'resposta_busca_compra'),
    'resposta_cobertura_lojas': ('.compras', 'resposta_cobertura_lojas'),
    'resposta_consulta_visualizacao': ('.visualizacoes', 'resposta_consulta_visualizacao'),
    'resposta_erro_compra': ('.compras', 'resposta_erro_compra'),
    'resposta_ofertas': ('.compras', 'resposta_ofertas'),
    'resultado_indeterminado': ('.textos', 'resultado_indeterminado'),
    'resumo_atualizacao': ('.propostas', 'resumo_atualizacao'),
    'resumo_confirmacao': ('.propostas', 'resumo_confirmacao'),
    'texto_resultados': ('.textos', 'texto_resultados'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
