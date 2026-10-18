import httpx
from app.core.configuracao import FIXA_URL_BASE_API
from app.tools.toolsRequest import CriarOcorrenciaEntrada


async def adicionar_ocorrencia(
    ocorrencia: CriarOcorrenciaEntrada, access_token: str, *, usuario_id: int, imagens: list[str],
) -> dict:
    """Envia uma única requisição conforme OcorrenciaCadastrarInputDTO."""
    if not FIXA_URL_BASE_API:
        raise ValueError("Configure FIXA_API_BASE_URL.")
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("Token autenticado obrigatório.")
    if type(usuario_id) is not int or usuario_id <= 0:
        raise ValueError("Usuário inválido.")
    if not isinstance(imagens, list) or not imagens or any(not isinstance(url, str) or not url.strip() for url in imagens):
        return {"status": "AGUARDANDO_INFORMACAO", "mensagem": "Envie pelo menos uma foto da ocorrência."}
    corpo = {
        "usuarioId": usuario_id,
        "localUnidadeId": ocorrencia.local_endereco_id,
        "categoriaEquipamentoId": ocorrencia.categoria_equipamento_id,
        "categoriaProblemaId": ocorrencia.categoria_problema_id,
        "titulo": ocorrencia.titulo,
        "descricaoOcorrencia": ocorrencia.descricao_ocorrencia,
        "descricaoLocal": ocorrencia.descricao_local,
        "prioridade": ocorrencia.prioridade,
        "urlsFoto": imagens,
    }
    indeterminado = {"status": "RESULTADO_INDETERMINADO", "mensagem":
                     "Não foi possível confirmar o cadastro. Consulte os registros antes de repetir o envio."}
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as cliente:
            resposta = await cliente.post(
                f"{FIXA_URL_BASE_API.rstrip('/')}/api/v1/ocorrencias",
                json=corpo, headers={"Authorization": f"Bearer {access_token}"},
            )
    except httpx.HTTPError:
        return indeterminado
    http_status = resposta.status_code
    if 400 <= http_status < 500:
        return {"status": "ERRO_API", "http_status": http_status,
                "detalhes_api": resposta.text.replace(access_token, "[TOKEN]")[:4000],
                "mensagem": "A API recusou o cadastro da ocorrência. Confira os dados e as permissões."}
    if not 200 <= http_status < 300 or http_status == 202:
        return {**indeterminado, "http_status": http_status,
                "detalhes_api": resposta.text.replace(access_token, "[TOKEN]")[:4000]}
    if http_status == 204:
        return {"status": "SUCESSO", "http_status": http_status, "titulo": ocorrencia.titulo,
                "mensagem": "Ocorrência cadastrada com sucesso."}
    try:
        dados = resposta.json()
    except ValueError:
        return {**indeterminado, "http_status": http_status}
    if not isinstance(dados, dict) or not isinstance(dados.get("titulo"), str) or not dados["titulo"].strip():
        return {**indeterminado, "http_status": http_status}
    return {"status": "SUCESSO", "http_status": http_status, "titulo": dados["titulo"],
            "ocorrencia_id": dados.get("id"), "mensagem": "Ocorrência cadastrada com sucesso."}
