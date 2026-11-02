"""Seleção e renderização centralizadas das respostas padrão da aplicação."""

import json

from app.core.respostas import (
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


TEXTOS = {"ferramenta_indisponivel": FERRAMENTA_INDISPONIVEL, "faq_sem_informacao": FAQ_SEM_INFORMACAO}


def formatar_resposta(chave: str, **valores) -> str:
    """Interpola somente um template conhecido do catálogo de mensagens."""
    return MENSAGENS[chave].format(**valores)


def escolher_resposta(condicao, quando_sim: str, quando_nao: str) -> str:
    """Seleciona um texto do catálogo a partir de um resultado já apurado."""
    return MENSAGENS[quando_sim if condicao else quando_nao]


def resposta_bloqueio_seguranca(categoria: str) -> dict | None:
    if categoria in RESPOSTAS_BLOQUEIO:
        return {"bloqueado": True, **RESPOSTAS_BLOQUEIO[categoria]}
    return None


def selecionar_resposta_saida(estado: dict, resposta: str) -> tuple[str, str | None] | None:
    if estado.get("veredito") != "aprovado":
        return MENSAGENS['a_resposta_nao_foi_aprovada_para_envio'], estado.get("erro")
    if not resposta:
        return MENSAGENS['nao_foi_possivel_produzir_uma_resposta_valida'], "Resposta final vazia."
    return None


def resposta_interrupcao_proposta(tipo: str, manifestacao: str) -> str:
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


def resultado_indeterminado() -> dict:
    return {"status": "RESULTADO_INDETERMINADO",
            "mensagem": MENSAGENS['o_processamento_pode_ter_ocorrido_confira_seus_registros_antes_de_repetir_o']}


def texto_resultados(resultados: list[dict]) -> str:
    mensagens = []
    for item in resultados:
        resultado = item["resultado"]
        status = resultado.get("status")
        if status == "SUCESSO":
            mensagem = RESPOSTAS_OPERACAO_SUCESSO[item["tipo"]]
        elif status == "RESULTADO_INDETERMINADO":
            mensagem = resultado_indeterminado()["mensagem"]
        else:
            mensagem = RESPOSTAS_OPERACAO_FALHA[item["tipo"]]
        mensagens.append(mensagem)
    return "\n\n".join(mensagens)


def _anexar_orientacao_consulta(resposta: str, evidencias_novas: list[str]) -> str:
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


def resumo_confirmacao(rascunho: dict) -> str:
    from app.core.propostas import campos_pendentes
    pendentes = campos_pendentes(rascunho)
    if not pendentes:
        return MENSAGENS['os_dados_ja_estao_confirmados_nao_e_necessario_confirma_los_novamente']
    titulo = TEXTOS_CONFIRMACAO["titulo" if not rascunho.get("dados_confirmados") else "alteracoes"]
    linhas = [titulo]
    for campo in pendentes:
        valor = rascunho.get("rotulos", {}).get(campo, rascunho["dados"][campo])
        # IDs são internos; as ferramentas devem fornecer descrições verificadas.
        if campo in {"local_endereco_id", "local_unidade_id", "categoria_equipamento_id"} and campo not in rascunho.get("rotulos", {}):
            valor = TEXTOS_CONFIRMACAO["rotulo_ausente"]
        linhas.append(TEXTOS_CONFIRMACAO["campo"].format(nome=NOMES_CAMPOS.get(campo, campo), valor=str(valor).replace(chr(10), ' ')))
    linhas.append(TEXTOS_CONFIRMACAO["pergunta"])
    return "\n".join(linhas)


def resposta_ofertas(ofertas: list[dict], diferencas: str) -> str:
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
    texto = TEXTOS_COMPRAS["lojas"].format(nomes=", ".join(nomes)) if nomes else TEXTOS_COMPRAS["lojas_vazias"]
    return texto + TEXTOS_COMPRAS["ressalva_lojas"]


def pergunta_opcionais_compra(campos: list[str], questao_compatibilidade: str | None) -> str:
    pergunta = TEXTOS_COMPRAS["opcionais"].format(campos=", ".join(campos)) if campos else TEXTOS_COMPRAS["dados_completos"]
    if questao_compatibilidade:
        pergunta += " " + questao_compatibilidade.strip()
    return pergunta + TEXTOS_COMPRAS["dispensar_opcionais"]


def resposta_busca_compra(produtos: list[dict], ofertas: list[dict], diferencas: str) -> str:
    if produtos:
        return resposta_ofertas(ofertas, diferencas)
    return MENSAGENS['nao_encontrei_promocoes_ativas_cadastradas_no_pechincha_ai_para_esses_criterios_se']


def resposta_erro_compra(codigo: str, erro) -> str:
    if codigo == "filtro_invalido":
        return formatar_resposta('exc_informe_outro_filtro_ou_peca_para_buscar_apenas_pelo_nome_do', exc=erro)
    if codigo == "limite_http":
        return MENSAGENS['o_pechincha_ai_limitou_temporariamente_as_consultas_seus_criterios_foram_salvos']
    return MENSAGENS['a_pesquisa_de_promocoes_esta_indisponivel_no_momento_seus_criterios_foram_salvos']


def resposta_consulta_visualizacao(periodos_parciais: bool) -> str:
    return escolher_resposta(periodos_parciais, 'consulta_concluida_periodos_parciais_identificados_nos_pontos', 'consulta_concluida')


CONSULTAS_COM_ORIENTACAO = {
    "listar_minhas_solicitacoes", "listar_todas_solicitacoes_pendentes",
    "listar_minhas_ocorrencias", "listar_minhas_ordens_servico",
    "listar_todas_ordens_servico", "buscar_ordem_servico",
}


def selecionar_resposta_fallback(estado: dict) -> str:
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


def _avisos_base(base, analise):
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
