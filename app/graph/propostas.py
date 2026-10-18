"""Apresentação das propostas geradas pelas ferramentas no turno atual."""

import json


def propostas_resposta(estado: dict) -> list[dict]:
    propostas = {}
    for evidencia in estado.get("evidencias", []):
        try:
            registro = json.loads(evidencia)
        except (ValueError, TypeError):
            continue
        if not isinstance(registro, dict) or registro.get("status_execucao") != "success":
            continue
        if registro.get("ferramenta") not in {
            "salvar_rascunho_solicitacao", "salvar_rascunho_ocorrencia", "criar_solicitacao", "criar_ocorrencia",
        }:
            continue
        resultado = registro.get("resultado")
        proposta = resultado.get("proposta") if isinstance(resultado, dict) else None
        if not isinstance(proposta, dict) or not all(proposta.get(campo) for campo in (
            "tipo", "proposta_id", "versao", "dados", "resumo_confirmacao",
        )):
            continue
        propostas[proposta["tipo"]] = proposta
    return list(propostas.values())


def incluir_resumos(resposta: str, estado: dict) -> str:
    for proposta in propostas_resposta(estado):
        resumo = proposta["resumo_confirmacao"]
        if resumo not in resposta:
            resposta += "\n\n" + resumo
    return resposta.strip()
