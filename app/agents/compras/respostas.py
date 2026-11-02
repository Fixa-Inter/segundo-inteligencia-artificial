"""Apresentação de promoções e ressalvas ao usuário."""


def resposta_ofertas(ofertas: list[dict], diferencas: str) -> str:
    from app.graph.respostas_padrao import resposta_ofertas as renderizar
    return renderizar(ofertas, diferencas)
