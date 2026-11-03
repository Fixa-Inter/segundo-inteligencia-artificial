"""Apresentação de promoções e ressalvas ao usuário."""


def resposta_ofertas(ofertas: list[dict], diferencas: str) -> str:
    """Renderiza ofertas e ressalvas com os dados reais recebidos. Usado pelo fluxo de compras."""
    from app.core.apresentacao import resposta_ofertas as renderizar
    return renderizar(ofertas, diferencas)
