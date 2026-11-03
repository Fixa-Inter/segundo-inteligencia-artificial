"""Interface pública de app/agents/prompts/reutilizaveis; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'ADMINISTRADOR_INSTRUCAO': ('app.agents.prompts.reutilizaveis.usuarios.administrador', 'ADMINISTRADOR_INSTRUCAO'),
    'CONTEXTO_INSTRUCAO': ('app.agents.prompts.reutilizaveis.gerais.contexto', 'CONTEXTO_INSTRUCAO'),
    'GESTOR_INSTRUCAO': ('app.agents.prompts.reutilizaveis.usuarios.gestor', 'GESTOR_INSTRUCAO'),
    'GLOSSARIO_INSTRUCAO': ('app.agents.prompts.reutilizaveis.gerais.glossario', 'GLOSSARIO_INSTRUCAO'),
    'MAPEAMENTO_CATEGORIA_PROBLEMA_INSTRUCAO': ('app.agents.prompts.reutilizaveis.gerais.mapeamento_categoria_problema', 'MAPEAMENTO_CATEGORIA_PROBLEMA_INSTRUCAO'),
    'SOLICITANTE_INSTRUCAO': ('app.agents.prompts.reutilizaveis.usuarios.solicitante', 'SOLICITANTE_INSTRUCAO'),
    'TECNICO_INSTRUCAO': ('app.agents.prompts.reutilizaveis.usuarios.tecnico', 'TECNICO_INSTRUCAO'),
    'construir_contexto_temporal': ('app.agents.prompts.reutilizaveis.gerais.contexto_temporal', 'construir_contexto_temporal'),
    'gerais': ('.gerais', None),
    'usuarios': ('.usuarios', None),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
