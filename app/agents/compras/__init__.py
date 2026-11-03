"""Interface pública de app/agents/compras; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'AvaliacaoOferta': ('.avaliacao', 'AvaliacaoOferta'),
    'AvaliacoesOfertas': ('.avaliacao', 'AvaliacoesOfertas'),
    'DadosCompra': ('.coleta', 'DadosCompra'),
    'Verificacao': ('.avaliacao', 'Verificacao'),
    'avaliar': ('.avaliacao', 'avaliar'),
    'campos_prioritarios_ausentes': ('.coleta', 'campos_prioritarios_ausentes'),
    'consultar': ('.consulta', 'consultar'),
    'dados_persistiveis': ('.coleta', 'dados_persistiveis'),
    'extrair': ('.coleta', 'extrair'),
    'normalizar': ('.avaliacao', 'normalizar'),
    'oferta_sem_avaliacao': ('.avaliacao', 'oferta_sem_avaliacao'),
    'opcionais_ausentes': ('.coleta', 'opcionais_ausentes'),
    'pergunta_opcionais': ('.coleta', 'pergunta_opcionais'),
    'resposta_ofertas': ('.respostas', 'resposta_ofertas'),
    'texto_curto': ('.avaliacao', 'texto_curto'),
    'url_produto': ('.avaliacao', 'url_produto'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
