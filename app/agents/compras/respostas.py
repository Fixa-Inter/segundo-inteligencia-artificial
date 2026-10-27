"""Apresentação de promoções e ressalvas ao usuário."""


def resposta_ofertas(ofertas: list[dict], diferencas: str) -> str:
    if not ofertas:
        return "A busca trouxe promoções, mas nenhuma tem link válido ou dados suficientes para comparação segura."
    linhas = ["Encontrei estas promoções ativas no Pechincha.ai para comparar:"]
    for oferta in ofertas:
        preco = oferta["preco"]
        preco_texto = f"R$ {preco:.2f}".replace(".", ",") if isinstance(preco, (int, float)) else "preço não informado"
        linhas.append(
            f"- {oferta['descricao'] or 'Produto sem descrição'} — {oferta['loja'] or 'loja não informada'}; "
            f"{preco_texto}. {oferta['url']}\n"
            f"  Requisitos confirmados: {', '.join(oferta['confirmados']) or 'nenhum no anúncio'}. "
            f"Informações ausentes: {', '.join(oferta['ausentes']) or 'nenhuma dos requisitos informados'}. "
            f"Motivo: {oferta['motivo']}"
        )
    if diferencas:
        linhas.append(diferencas)
    linhas.append("São promoções cadastradas no Pechincha.ai, não o catálogo completo das lojas. "
                  "Confirme o preço final na loja e, se necessário, quantidade por embalagem e compatibilidade.")
    return "\n".join(linhas)
