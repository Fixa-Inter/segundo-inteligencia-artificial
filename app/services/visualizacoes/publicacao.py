"""Projeção do resultado aprovado para o contrato público e sua validação."""


import json

from app.guardrails import proteger_saida
from app.observability.metricas import BYTES_VISUALIZACAO
from app.schemas.visualizacao import VisualizacaoPublica
from . import obter_analise
from .aprovacao import liberar_visualizacao
from .limites import validar_limites_resultado

from app.core.respostas import MENSAGENS


MAXIMO_BYTES_VISUALIZACAO = 256 * 1024
MAXIMO_BYTES_CONVERSA_COM_VISUALIZACAO = 8 * 1024 * 1024


class LimiteVisualizacaoExcedido(ValueError):
    pass


def validar_visualizacao_publica(dados) -> VisualizacaoPublica:
    if isinstance(dados, VisualizacaoPublica):
        dados = dados.model_dump(warnings="error")
    visualizacao = VisualizacaoPublica.model_validate(dados)
    validar_limites_resultado(visualizacao.dados)
    tamanho = len(visualizacao.model_dump_json().encode("utf-8"))
    if tamanho > MAXIMO_BYTES_VISUALIZACAO:
        raise LimiteVisualizacaoExcedido(MENSAGENS['a_visualizacao_excede_256_kib_reduza_o_periodo_ou_os_grupos'])
    return visualizacao


def publicar_visualizacao(estado, contexto) -> VisualizacaoPublica | None:
    if estado.get("visualizacao_aprovada") is None and estado.get("visualizacao_candidata") is None:
        return None
    aprovado = liberar_visualizacao(estado, contexto)
    if aprovado is None or json.dumps(aprovado, sort_keys=True) != json.dumps(estado.get("visualizacao_aprovada"), sort_keys=True):
        raise ValueError(MENSAGENS['resultado_publico_diferente_do_resultado_liberado'])
    texto = estado["visualizacao_aprovacao"]["texto_avaliado"]
    protegido = proteger_saida(texto, estado.get("mapa_pii", {}))
    if protegido.get("bloqueado") or protegido["conteudo"] != estado.get("resposta_final"):
        raise ValueError(MENSAGENS['o_texto_final_nao_corresponde_ao_conteudo_protegido'])
    meta = aprovado["metadados"]
    analise = obter_analise(meta["analise_id"])
    publico = validar_visualizacao_publica({
        "versao_contrato": "1.0", "visualizacao_id": meta["consulta_id"],
        "titulo": analise.titulo, "status": aprovado["status"],
        "metadados": {
            **{k: meta[k] for k in (
                "analise_id", "unidade_medida", "escala_percentual", "periodo", "granularidade",
                "instante_snapshot", "consultado_em", "qtd_registros_considerados", "base_calculo",
            )}, "unidade_id": meta["filtros_aplicados"]["unidade_id"],
            "filtros": meta["filtros_solicitados"],
        },
        "dados": aprovado["dados"], "avisos": aprovado["avisos"],
    })
    BYTES_VISUALIZACAO.labels("publico").observe(len(publico.model_dump_json().encode("utf-8")))
    return publico
