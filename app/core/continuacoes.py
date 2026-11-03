"""Seleção pura de propostas pendentes, usada por roteadores e pelo grafo."""

# STATUS_RASCUNHO: Estados reconhecidos no fluxo deste domínio; usados para validar continuidade e execução.
STATUS_RASCUNHO = {"coletando_dados", "aguardando_confirmacao", "aguardando_imagem", "erro_api"}

# STATUS_ACAO: Estados reconhecidos no fluxo deste domínio; usados para validar continuidade e execução.
STATUS_ACAO = {"aguardando_confirmacao", "aguardando_imagem"}

def _chave_estado(tipo: str) -> str:
    """Seleciona a chave do estado que armazena a proposta deste tipo. Usado por propostas_pendentes."""
    return "analise_compra_pendente" if tipo == "analista_compras" else f"{tipo}_pendente"

def propostas_pendentes(estado: dict, *, pausadas: bool = False) -> dict[str, dict]:
    """Obtém propostas ativas ou pausadas do estado. Usado pelo fluxo de core."""
    propostas = {}
    for tipo in ("solicitacao", "ocorrencia", "evento", "ajuda_geral", "analista_compras"):
        chave = _chave_estado(tipo)
        proposta = estado.get(chave)
        if not isinstance(proposta, dict):
            continue
        status = proposta.get("status" if tipo == "ajuda_geral" else "status_fluxo")
        permitidos = STATUS_ACAO if tipo == "ajuda_geral" else (
            {"coletando_dados", "aguardando_opcionais", "pronto_para_busca", "erro_busca"}
            if tipo == "analista_compras" else STATUS_RASCUNHO
        )
        if status in permitidos and bool(proposta.get("pausado")) == pausadas:
            propostas[tipo] = proposta
    return propostas
