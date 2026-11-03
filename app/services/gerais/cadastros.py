"""Interpretação comum de respostas de cadastro FIXA, sem executar/repetir POST."""


def interpretar_cadastro(resposta, *, access_token, titulo, mensagem_sucesso, mensagem_recusa,
                        indeterminado, campo_id, incluir_status_backend=False,
                        detalhes_indeterminado=True) -> dict:
    """Preserva diferenças explícitas entre solicitação, ocorrência e evento.

    Somente HTTP 2xx, exceto 202, pode confirmar gravação. No 204 o título vem
    da proposta; em resposta JSON exige título não vazio. Detalhes, nomes de ID
    e status de solicitação são definidos pelo serviço proprietário.
    """
    http_status = resposta.status_code
    if 400 <= http_status < 500:
        return {"status": "ERRO_API", "http_status": http_status,
                "detalhes_api": resposta.text.replace(access_token, "[TOKEN]")[:4000],
                "mensagem": mensagem_recusa}
    if not 200 <= http_status < 300 or http_status == 202:
        resultado = {**indeterminado, "http_status": http_status}
        if detalhes_indeterminado:
            resultado["detalhes_api"] = resposta.text.replace(access_token, "[TOKEN]")[:4000]
        return resultado
    if http_status == 204:
        return {"status": "SUCESSO", "http_status": http_status, "titulo": titulo,
                "mensagem": mensagem_sucesso}
    try:
        dados = resposta.json()
    except ValueError:
        return {**indeterminado, "http_status": http_status}
    if not isinstance(dados, dict) or not isinstance(dados.get("titulo"), str) or not dados["titulo"].strip():
        return {**indeterminado, "http_status": http_status}
    resultado = {"status": "SUCESSO", "http_status": http_status, "titulo": dados["titulo"],
                 campo_id: dados.get("id"), "mensagem": mensagem_sucesso}
    if incluir_status_backend:
        resultado["status_backend"] = dados.get("status")
    return resultado
