"""Interface pública do domínio, carregada sob demanda."""

from importlib import import_module

_EXPORTACOES = {'iniciar_sessao': 'inicio', 'encerrar_sessao': 'encerramento'}

__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    modulo = _EXPORTACOES.get(nome)
    if modulo is None:
        raise AttributeError(f"{__name__} não exporta {nome!r}.")
    valor = getattr(import_module(f".{modulo}", __name__), nome)
    globals()[nome] = valor
    return valor
