"""Renderização determinística de visualizacoes, usada pelo grafo, tools e serviços."""

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

def resposta_consulta_visualizacao(periodos_parciais: bool) -> str:
    """Seleciona texto de consulta concluída, incluindo referência a períodos parciais quando necessário. Usado pelo fluxo de apresentacao."""
    return escolher_resposta(periodos_parciais, 'consulta_concluida_periodos_parciais_identificados_nos_pontos', 'consulta_concluida')


def _avisos_base(base, analise):
    """Executa a etapa avisos base no escopo de visualizacoes. Usado pelo fluxo de apresentacao."""
    avisos = []
    if base.qtd_registros_elegiveis < base.qtd_registros_total:
        complemento = COMPLEMENTOS_BASE_CALCULO.get(analise.formato_dados, COMPLEMENTOS_BASE_CALCULO["media"])
        avisos.append(
            formatar_resposta('base_elegivel_valor_1_de_valor_2_registros_valor_3', valor_1=base.qtd_registros_elegiveis, valor_2=base.qtd_registros_total, valor_3=complemento)
        )
    if base.qtd_tempos_negativos_excluidos:
        avisos.append(
            formatar_resposta('tempos_negativos_excluidos_valor_1', valor_1=base.qtd_tempos_negativos_excluidos)
        )
    return avisos
