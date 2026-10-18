"""Regras compartilhadas de apresentação e confirmação dos dados de cadastro."""

from app.core.confirmacoes import classificar_manifestacao, aceite_explicito, normalizar_mensagem

NOMES_CAMPOS = {
    "titulo": "Título", "descricao_problema": "Problema",
    "descricao_ocorrencia": "Serviço realizado", "descricao_local": "Detalhes do local",
    "local_endereco_id": "Local", "categoria_equipamento_id": "Categoria do equipamento",
    "categoria_problema_id": "Categoria do problema", "prioridade": "Prioridade",
}


def campos_pendentes(rascunho: dict) -> list[str]:
    confirmados = rascunho.get("dados_confirmados", {})
    return [campo for campo, valor in rascunho.get("dados", {}).items()
            if campo not in confirmados or confirmados[campo] != valor]


def resumo_confirmacao(rascunho: dict) -> str:
    pendentes = campos_pendentes(rascunho)
    if not pendentes:
        return "Os dados já estão confirmados. Não é necessário confirmá-los novamente."
    titulo = "Confira os dados:" if not rascunho.get("dados_confirmados") else "Confira somente o que mudou:"
    linhas = [titulo]
    for campo in pendentes:
        valor = rascunho.get("rotulos", {}).get(campo, rascunho["dados"][campo])
        # IDs são internos; as ferramentas devem fornecer descrições verificadas.
        if campo in {"local_endereco_id", "categoria_equipamento_id"} and campo not in rascunho.get("rotulos", {}):
            valor = "Descrição ainda não resolvida; consulte as opções antes de confirmar"
        linhas.append(f"- {NOMES_CAMPOS.get(campo, campo)}: {str(valor).replace(chr(10), ' ')}")
    linhas.append("Essas informações estão corretas? Se precisar, indique somente o que devo corrigir.")
    return "\n".join(linhas)


def campos_aceite(texto: str, dados: dict, pendentes: list[str]) -> list[str]:
    normalizada = normalizar_mensagem(texto)
    alvos = (
        ("categoria do equipamento", ["categoria_equipamento_id"]),
        ("categoria do problema", ["categoria_problema_id"]),
        ("detalhes do local", ["descricao_local"]),
        ("descricao do local", ["descricao_local"]),
        ("local", ["local_endereco_id", "descricao_local"]),
        ("titulo", ["titulo"]), ("prioridade", ["prioridade"]),
        ("descricao", ["descricao_problema", "descricao_ocorrencia"]),
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

    if rascunho.get("pausado"):
        return solicitar("A proposta está pausada. Retome a conversa antes de cadastrar.")
    if contexto.get("intencao_atual") and contexto["intencao_atual"] != rascunho.get("tipo"):
        return solicitar("A mensagem atual não foi direcionada a esta proposta.")
    texto = contexto.get("mensagem_atual", "")
    outro_tipo = "solicitacao" if rascunho.get("tipo") == "ocorrencia" else "ocorrencia"
    if outro_tipo in normalizar_mensagem(texto):
        return solicitar("A confirmação menciona outro tipo de registro. Esclareça qual proposta deve continuar.")
    turno = contexto.get("turno_id")
    if not turno or not rascunho.get("turno_id") or rascunho["turno_id"] == turno:
        return solicitar("Prepare a proposta com os dados já coletados e responda apresentando as informações pendentes. Aguarde outra mensagem antes de enviar.")
    manifestacao = classificar_manifestacao(texto)
    if manifestacao == "aceite" and not aceite_explicito(texto, acoes=(
        "cadastrar", "criar", "registrar", "enviar", "prosseguir", "seguir", "continuar", "salvar",
    )):
        return solicitar("O aceite é de outra operação; esclareça a intenção antes de cadastrar.")
    if manifestacao in {"negacao", "cancelamento", "pausa", "pergunta", "retomada"}:
        return solicitar("Esclareça a pergunta ou a correção solicitada; não envie o cadastro agora.")
    if rascunho.get("confirmado") and not campos_pendentes(rascunho):
        if manifestacao == "aceite" or contexto.get("imagens"):
            return None
        return solicitar("Os dados já estão confirmados. Aguarde o anexo ou um pedido explícito para prosseguir.")
    if (
        not rascunho.get("turno_apresentacao") or rascunho["turno_apresentacao"] == turno
        or rascunho.get("versao_apresentada") != rascunho.get("versao")
        or rascunho.get("dados_apresentados") != rascunho.get("dados")
    ):
        return solicitar("Mostre os dados pendentes na resposta antes de pedir o aceite.")
    if manifestacao != "aceite":
        return solicitar("Confirme somente as informações apresentadas que ainda estão pendentes.")
    selecionados = campos_aceite(texto, rascunho["dados"], campos_pendentes(rascunho))
    if set(campos_pendentes(rascunho)) - set(selecionados):
        if not set(campos_pendentes(rascunho)) & set(selecionados):
            return solicitar("Esse aceite não identifica as informações pendentes. Esclareça quais dados estão corretos.")
        return {"status": "CONFIRMACAO_PARCIAL", "campos_confirmados": selecionados,
                "mensagem": "Preserve o aceite desses campos e apresente somente os que ainda faltam."}
    return None


def metadados_proposta(rascunho: dict) -> dict:
    return {"tipo": rascunho["tipo"], "proposta_id": rascunho["id"],
            "versao": rascunho["versao"], "dados": rascunho["dados"],
            "resumo_confirmacao": resumo_confirmacao(rascunho)}
