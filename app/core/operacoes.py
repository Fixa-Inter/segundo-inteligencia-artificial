"""Projeções puras de propostas, usadas na confirmação e aprovação de operações."""

def dados_cadastro(rascunho: dict) -> dict:
    """Inclui os anexos na aprovação, além dos campos e da versão do rascunho."""
    return {"proposta_id": rascunho["id"], "versao": rascunho["versao"],
            "dados": rascunho["dados"], "imagens": rascunho.get("imagens", [])}


def dados_edicao(acao: dict) -> dict:
    """Projeta ação de edição para aprovação. Usado pelo fluxo de core."""
    return {campo: acao.get(campo) for campo in ("id", "tipo", "registro_id", "campo", "novo_valor", "imagens")}


def dados_atualizacao(rascunho: dict) -> dict:
    """Projeta seleção, snapshot, alterações e fotos da atualização. Usado pelo fluxo de core."""
    return {"proposta_id": rascunho["id"], "versao": rascunho["versao"],
            "registro_id": rascunho["registro_id"], "original": rascunho["original"],
            "alteracoes": rascunho.get("alteracoes", {}), "imagens": rascunho.get("imagens", []),
            "acao_fotos": rascunho.get("acao_fotos", "manter")}
