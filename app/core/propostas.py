"""Regras compartilhadas de apresentação e confirmação dos dados de cadastro."""


from app.core.confirmacoes import classificar_manifestacao, aceite_explicito, normalizar_mensagem

from app.core.respostas import MENSAGENS, NOMES_CAMPOS


def campos_pendentes(rascunho: dict) -> list[str]:
    confirmados = rascunho.get("dados_confirmados", {})
    return [campo for campo, valor in rascunho.get("dados", {}).items()
            if campo not in confirmados or confirmados[campo] != valor]


def resumo_confirmacao(rascunho: dict) -> str:
    from app.graph.respostas_padrao import resumo_confirmacao as renderizar
    return renderizar(rascunho)


def campos_aceite(texto: str, dados: dict, pendentes: list[str]) -> list[str]:
    normalizada = normalizar_mensagem(texto)
    alvos = (
        ("categoria do equipamento", ["categoria_equipamento_id"]),
        ("categoria do problema", ["categoria_problema_id"]),
        ("detalhes do local", ["descricao_local"]),
        ("descricao do local", ["descricao_local"]),
        ("local", ["local_endereco_id", "local_unidade_id", "descricao_local"]),
        ("titulo", ["titulo"]), ("prioridade", ["prioridade"]),
        ("descricao", ["descricao_problema", "descricao_ocorrencia", "descricao"]),
        ("observacao", ["observacao"]),
        ("inicio", ["data_hora_inicio"]), ("fim", ["data_hora_fim"]),
        ("termino", ["data_hora_fim"]),
        ("horarios", ["data_hora_inicio", "data_hora_fim"]),
        ("datas", ["data_hora_inicio", "data_hora_fim"]),
        ("categoria", ["categoria_equipamento_id", "categoria_problema_id"]),
        ("foto", []), ("imagem", []),
    )
    for nome, campos in alvos:
        if nome in normalizada:
            if nome == "categoria" and len(set(campos) & set(pendentes)) > 1:
                return []
            return [campo for campo in campos if campo in dados]
    return list(dados)


def avaliar_confirmacao(rascunho: dict, contexto: dict) -> dict | None:
    def solicitar(mensagem):
        return {"status": "CONFIRMACAO_NECESSARIA", "mensagem": mensagem,
                "campos_pendentes": campos_pendentes(rascunho)}

    if rascunho.get("status_fluxo") == "coletando_dados":
        return solicitar(MENSAGENS['complete_e_apresente_a_proposta_antes_de_confirmar_o_cadastro'])
    if rascunho.get("pausado"):
        return solicitar(MENSAGENS['a_proposta_esta_pausada_retome_a_conversa_antes_de_cadastrar'])
    if contexto.get("intencao_atual") and contexto["intencao_atual"] != rascunho.get("tipo"):
        return solicitar(MENSAGENS['a_mensagem_atual_nao_foi_direcionada_a_esta_proposta'])
    texto = contexto.get("mensagem_atual", "")
    outros_tipos = {"solicitacao", "ocorrencia", "evento"} - {rascunho.get("tipo")}
    if any(tipo in normalizar_mensagem(texto) for tipo in outros_tipos):
        return solicitar(MENSAGENS['a_confirmacao_menciona_outro_tipo_de_registro_esclareca_qual_proposta_deve_continuar'])
    turno = contexto.get("turno_id")
    if not turno or not rascunho.get("turno_id") or rascunho["turno_id"] == turno:
        return solicitar(MENSAGENS['prepare_a_proposta_com_os_dados_ja_coletados_e_responda_apresentando_as'])
    manifestacao = classificar_manifestacao(texto)
    if manifestacao == "aceite" and not aceite_explicito(texto, acoes=(
        "cadastrar", "criar", "registrar", "enviar", "prosseguir", "seguir", "continuar", "salvar",
    )):
        return solicitar(MENSAGENS['o_aceite_e_de_outra_operacao_esclareca_a_intencao_antes_de_cadastrar'])
    if manifestacao in {"negacao", "cancelamento", "pausa", "pergunta", "retomada"}:
        return solicitar(MENSAGENS['esclareca_a_pergunta_ou_a_correcao_solicitada_nao_envie_o_cadastro_agora'])
    if rascunho.get("confirmado") and not campos_pendentes(rascunho):
        if manifestacao == "aceite" or contexto.get("imagens"):
            return None
        return solicitar(MENSAGENS['os_dados_ja_estao_confirmados_aguarde_o_anexo_ou_um_pedido_explicito'])
    if (
        not rascunho.get("turno_apresentacao") or rascunho["turno_apresentacao"] == turno
        or rascunho.get("versao_apresentada") != rascunho.get("versao")
        or rascunho.get("dados_apresentados") != rascunho.get("dados")
    ):
        return solicitar(MENSAGENS['mostre_os_dados_pendentes_na_resposta_antes_de_pedir_o_aceite'])
    if manifestacao != "aceite":
        return solicitar(MENSAGENS['confirme_somente_as_informacoes_apresentadas_que_ainda_estao_pendentes'])
    selecionados = campos_aceite(texto, rascunho["dados"], campos_pendentes(rascunho))
    if set(campos_pendentes(rascunho)) - set(selecionados):
        if not set(campos_pendentes(rascunho)) & set(selecionados):
            return solicitar(MENSAGENS['esse_aceite_nao_identifica_as_informacoes_pendentes_esclareca_quais_dados_estao_corretos'])
        return {"status": "CONFIRMACAO_PARCIAL", "campos_confirmados": selecionados,
                "mensagem": MENSAGENS['preserve_o_aceite_desses_campos_e_apresente_somente_os_que_ainda_faltam']}
    return None


def metadados_proposta(rascunho: dict) -> dict:
    return {"tipo": rascunho["tipo"], "proposta_id": rascunho["id"],
            "versao": rascunho["versao"], "dados": rascunho["dados"],
            "resumo_confirmacao": resumo_confirmacao(rascunho)}
