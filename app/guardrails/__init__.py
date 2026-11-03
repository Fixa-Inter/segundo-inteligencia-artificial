"""Interface pública de app/guardrails; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'ClassificacaoSeguranca': ('.validacao', 'ClassificacaoSeguranca'),
    'PADROES_DADOS_INTERNOS': ('.validacao', 'PADROES_DADOS_INTERNOS'),
    'PADROES_INJECAO': ('.validacao', 'PADROES_INJECAO'),
    'PII': ('.validacao', 'PII'),
    'PROMPT_CLASSIFICADOR': ('.validacao', 'PROMPT_CLASSIFICADOR'),
    'anonimizar_entrada': ('.validacao', 'anonimizar_entrada'),
    'aprovar': ('.validacao', 'aprovar'),
    'bloquear': ('.validacao', 'bloquear'),
    'classificador_seguranca': ('.validacao', 'classificador_seguranca'),
    'desanonimizar_saida': ('.validacao', 'desanonimizar_saida'),
    'proteger_entrada': ('.validacao', 'proteger_entrada'),
    'proteger_saida': ('.validacao', 'proteger_saida'),
    'remover_dados_pessoais_saida': ('.validacao', 'remover_dados_pessoais_saida'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
