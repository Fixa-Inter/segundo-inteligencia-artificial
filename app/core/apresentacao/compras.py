"""Renderização determinística de compras, usada pelo grafo, tools e serviços."""

from app.core import (
    MENSAGENS,
    NOMES_CAMPOS,
    RESPOSTAS_OPERACAO_SUCESSO,
    RESPOSTAS_OPERACAO_FALHA,
    TEXTOS_CONFIRMACAO,
    RESPOSTAS_BLOQUEIO,
    TEXTOS_COMPRAS,
    COMPLEMENTOS_BASE_CALCULO,
)
from .textos import formatar_resposta, escolher_resposta

def resposta_ofertas(ofertas: list[dict], diferencas: str) -> str:
    """Renderiza ofertas e ressalvas com os dados reais recebidos. Usado por resposta_busca_compra."""
    if not ofertas:
        return MENSAGENS['a_busca_trouxe_promocoes_mas_nenhuma_tem_link_valido_ou_dados_suficientes']
    linhas = [TEXTOS_COMPRAS["cabecalho_ofertas"]]
    for oferta in ofertas:
        preco = oferta["preco"]
        preco_texto = TEXTOS_COMPRAS["preco"].format(preco=preco).replace(".", ",") if isinstance(preco, (int, float)) else TEXTOS_COMPRAS["preco_ausente"]
        linhas.append(
            TEXTOS_COMPRAS["oferta"].format(
                descricao=oferta['descricao'] or TEXTOS_COMPRAS["descricao_ausente"],
                loja=oferta['loja'] or TEXTOS_COMPRAS["loja_ausente"], preco=preco_texto, url=oferta['url'],
                confirmados=', '.join(oferta['confirmados']) or TEXTOS_COMPRAS["confirmados_ausentes"],
                ausentes=', '.join(oferta['ausentes']) or TEXTOS_COMPRAS["requisitos_ausentes"], motivo=oferta['motivo'],
            )
        )
    if diferencas:
        linhas.append(diferencas)
    linhas.append(TEXTOS_COMPRAS["ressalva_ofertas"])
    return "\n".join(linhas)


def resposta_cobertura_lojas(nomes: list[str]) -> str:
    """Apresenta lojas cadastradas sem afirmar oferta ativa para o item. Usado pelo fluxo de apresentacao."""
    texto = TEXTOS_COMPRAS["lojas"].format(nomes=", ".join(nomes)) if nomes else TEXTOS_COMPRAS["lojas_vazias"]
    return texto + TEXTOS_COMPRAS["ressalva_lojas"]


def pergunta_opcionais_compra(campos: list[str], questao_compatibilidade: str | None) -> str:
    """Renderiza campos opcionais de compra e questão de compatibilidade. Usado pelo fluxo de apresentacao."""
    pergunta = TEXTOS_COMPRAS["opcionais"].format(campos=", ".join(campos)) if campos else TEXTOS_COMPRAS["dados_completos"]
    if questao_compatibilidade:
        pergunta += " " + questao_compatibilidade.strip()
    return pergunta + TEXTOS_COMPRAS["dispensar_opcionais"]


def resposta_busca_compra(produtos: list[dict], ofertas: list[dict], diferencas: str) -> str:
    """Escolhe apresentação de ofertas ou ausência de promoções ativas. Usado pelo fluxo de apresentacao."""
    if produtos:
        return resposta_ofertas(ofertas, diferencas)
    return MENSAGENS['nao_encontrei_promocoes_ativas_cadastradas_no_pechincha_ai_para_esses_criterios_se']


def resposta_erro_compra(codigo: str, erro) -> str:
    """Seleciona mensagem conforme código de falha da pesquisa. Usado pelo fluxo de apresentacao."""
    if codigo == "filtro_invalido":
        return formatar_resposta('exc_informe_outro_filtro_ou_peca_para_buscar_apenas_pelo_nome_do', exc=erro)
    if codigo == "limite_http":
        return MENSAGENS['o_pechincha_ai_limitou_temporariamente_as_consultas_seus_criterios_foram_salvos']
    return MENSAGENS['a_pesquisa_de_promocoes_esta_indisponivel_no_momento_seus_criterios_foram_salvos']
