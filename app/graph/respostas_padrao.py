"""Seleção e renderização centralizadas das respostas padrão da aplicação."""

import json
from app.core import (
    FERRAMENTA_INDISPONIVEL,
    FAQ_SEM_INFORMACAO,
    TRECHO_FAQ_AUSENTE,
    MENSAGENS,
    NOMES_CAMPOS,
    RESPOSTAS_OPERACAO_SUCESSO,
    RESPOSTAS_OPERACAO_FALHA,
    TEXTOS_CONFIRMACAO,
    RESPOSTAS_BLOQUEIO,
    TEXTOS_COMPRAS,
    COMPLEMENTOS_BASE_CALCULO,
)
from app.core.apresentacao import (
    formatar_resposta,
    escolher_resposta,
    resposta_bloqueio_seguranca,
    resultado_indeterminado,
    texto_resultados,
    resumo_confirmacao,
    resumo_atualizacao,
    resposta_ofertas,
    resposta_cobertura_lojas,
    pergunta_opcionais_compra,
    resposta_busca_compra,
    resposta_erro_compra,
    resposta_consulta_visualizacao,
    _avisos_base,
)

# Compatibilidade: seleção do fluxo permanece aqui; renderização pertence ao core.


# TEXTOS: Recurso compartilhado de textos usado pelas funções deste módulo e pela interface pública.
TEXTOS = {"ferramenta_indisponivel": FERRAMENTA_INDISPONIVEL, "faq_sem_informacao": FAQ_SEM_INFORMACAO}


def selecionar_resposta_saida(estado: dict, resposta: str) -> tuple[str, str | None] | None:
    """Aplica texto padronizado compatível com o estado final do fluxo. Usado pelo fluxo de graph."""
    if estado.get("veredito") != "aprovado":
        return MENSAGENS['a_resposta_nao_foi_aprovada_para_envio'], estado.get("erro")
    if not resposta:
        return MENSAGENS['nao_foi_possivel_produzir_uma_resposta_valida'], "Resposta final vazia."
    return None


def resposta_interrupcao_proposta(tipo: str, manifestacao: str) -> str:
    """Renderiza mensagem de pausa/cancelamento da proposta. Usado pelo fluxo de graph."""
    if manifestacao == "cancelamento":
        return escolher_resposta(tipo == "analista_compras", 'analise_de_compra_cancelada',
                                 'proposta_cancelada_nao_vou_enviar_esse_cadastro_nem_executar_essa_alteracao')
    alvo = (
        MENSAGENS['a_analise_de_compra'] if tipo == "analista_compras" else
        MENSAGENS['a_alteracao'] if tipo == "ajuda_geral" else
        MENSAGENS['o_evento'] if tipo == "evento" else
        "a " + tipo.replace("solicitacao", "solicitação").replace("ocorrencia", "ocorrência") + "."
    )
    return MENSAGENS['proposta_pausada_para_continuar_depois_peca_para_retomar'] + alvo


def _registros(evidencias: list[str]) -> list[dict]:
    """Executa a etapa registros no escopo de respostas_padrao. Usado por preparar_resposta_padrao, resposta_padrao_validada."""
    registros = []
    for evidencia in evidencias:
        try:
            registro = json.loads(evidencia)
        except (TypeError, ValueError):
            continue
        if isinstance(registro, dict):
            registros.append(registro)
    return registros


def _pode_padronizar(registros: list[dict], contexto: dict) -> bool:
    """Executa a etapa pode padronizar no escopo de respostas_padrao. Usado por preparar_resposta_padrao, resposta_padrao_validada."""
    if contexto.get("operacoes_pendentes") or contexto.get("resultados_operacoes"):
        return False
    for registro in registros:
        status = str(registro.get("status_operacao") or "").upper()
        resultado = registro.get("resultado")
        if (registro.get("status_execucao") != "success"
                or status.startswith(("ERRO", "TIMEOUT", "ACESSO_NEGADO", "RESULTADO_INDETERMINADO"))
                or str(registro.get("ferramenta", "")).startswith(("criar_", "salvar_rascunho_", "alterar_", "anexar_"))):
            return False
        if isinstance(resultado, dict) and isinstance(resultado.get("http_status"), int) and resultado["http_status"] >= 400:
            return False
    return True


def preparar_resposta_padrao(status: str, intencao: str, evidencias: list[str], contexto: dict) -> dict:
    """Confere status/intenção/evidências antes de padronizar limitação ou FAQ sem informação. Usado por resposta_padrao_validada."""
    registros = _registros(evidencias)
    if not _pode_padronizar(registros, contexto):
        return {}
    faq = [r for r in registros if r.get("ferramenta") == "buscar_faq"]
    motivo = None
    if intencao == "faq" and status in {"SUCESSO", "SEM_RESULTADO"} and faq and (
        status == "SEM_RESULTADO" or faq[-1].get("resultado") == TRECHO_FAQ_AUSENTE
    ):
        motivo = "faq_sem_informacao"
    elif status == "FERRAMENTA_INDISPONIVEL":
        motivo = "ferramenta_indisponivel"
    if motivo is None:
        return {}
    return {"motivo_resposta_padrao": motivo, "resposta_especialista": TEXTOS[motivo]}


def resposta_padrao_validada(estado: dict) -> str | None:
    """Revalida a resposta padronizada antes do julgamento. Usado pelo fluxo de graph."""
    motivo = estado.get("motivo_resposta_padrao")
    texto = TEXTOS.get(motivo)
    if (not texto or estado.get("erro") or estado.get("resposta_especialista") != texto
            or not _pode_padronizar(_registros(estado.get("evidencias", [])), estado)):
        return None
    preparada = preparar_resposta_padrao(
        "SEM_RESULTADO" if motivo == "faq_sem_informacao" else "FERRAMENTA_INDISPONIVEL",
        estado.get("intencao"), estado.get("evidencias", []), estado,
    )
    return texto if preparada.get("motivo_resposta_padrao") == motivo else None


def _anexar_orientacao_consulta(resposta: str, evidencias_novas: list[str]) -> str:
    """Executa a etapa anexar orientacao consulta no escopo de respostas_padrao. Usado pelo fluxo de graph."""
    for evidencia in reversed(evidencias_novas):
        try:
            registro = json.loads(evidencia)
        except (TypeError, ValueError):
            continue
        if not isinstance(registro, dict) or registro.get("ferramenta") not in CONSULTAS_COM_ORIENTACAO:
            continue
        if registro.get("status_operacao") not in {"SUCESSO", "SEM_RESULTADO"}:
            return resposta
        resultado = registro.get("resultado")
        orientacao = resultado.get("orientacao") if isinstance(resultado, dict) else None
        if not isinstance(orientacao, str) or not orientacao.strip():
            return resposta
        return f"{resposta.replace(orientacao, '').strip()}\n\n{orientacao}"
    return resposta


# CONSULTAS_COM_ORIENTACAO: Recurso compartilhado de consultas com orientacao usado pelas funções deste módulo e pela interface pública.
CONSULTAS_COM_ORIENTACAO = {
    "listar_minhas_solicitacoes", "listar_todas_solicitacoes_pendentes",
    "listar_minhas_ocorrencias", "listar_minhas_ordens_servico",
    "listar_todas_ordens_servico", "buscar_ordem_servico",
}


def selecionar_resposta_fallback(estado: dict) -> str:
    """Escolhe resposta segura compatível com falha ou pedido fora do escopo. Usado pelo fluxo de graph."""
    resposta_existente = estado.get(
        "resposta_final"
    )

    if resposta_existente:
        resposta = resposta_existente

    elif estado.get("intencao") == "visualizacao":
        resposta = (
            MENSAGENS['nao_foi_possivel_validar_esta_visualizacao_ajuste_o_periodo_os_filtros_ou']
        )

    elif estado.get("veredito") in {"revisar", "bloqueado"}:
        resposta = (
            MENSAGENS['nao_foi_possivel_validar_a_resposta_sobre_sua_solicitacao_caso_tenha_solicitado']
        )

    elif estado.get("erro"):
        resposta = (
            MENSAGENS['nao_foi_possivel_processar_sua_solicitacao_neste_momento_tente_novamente_mais_tarde']
        )

    elif (
        estado.get("intencao")
        == "fora_de_escopo"
    ):
        resposta = (
            MENSAGENS['posso_ajudar_com_duvidas_sobre_o_aplicativo_chamados_de_manutencao_indicadores_visualizacoes']
        )

    else:
        resposta = FERRAMENTA_INDISPONIVEL

    return resposta
