import httpx

from app.core.configuracao import FIXA_URL_BASE_API
from app.tools.toolsRequest import CriarSolicitacaoEntrada


async def adicionar_solicitacao(
    solicitacao: CriarSolicitacaoEntrada,
    access_token: str,
    *, imagens: list[str],
) -> dict:
    """Envia o cadastro diretamente. Sem estado de conversa ou repetição de POST.

    Envia os dados da solicitação e as URLs em urlsFoto, usando Bearer token.
    Espera resposta 2xx com titulo. A API valida a identidade, sede e os IDs.
    """
    if not isinstance(imagens, list) or not imagens or any(
        not isinstance(url, str) or not url.strip() for url in imagens
    ):
        raise ValueError("Forneça pelo menos uma URL de imagem em uma lista de strings.")
    if not FIXA_URL_BASE_API:
        raise ValueError("Configure FIXA_API_BASE_URL.")

    # LEMBRAR DE FAZER A VALIDAÇÃO DO ACCESS_TOKEN
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("Token autenticado obrigatório.")
    
    indeterminado = {"status": "RESULTADO_INDETERMINADO", "mensagem": "Não foi possível confirmar o cadastro. Consulte a API antes de repetir o envio."}

    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as cliente:
            resposta = await cliente.post(
                f"{FIXA_URL_BASE_API.rstrip('/')}/api/v1/solicitacoes",
                json={
                    "titulo": solicitacao.titulo,
                    "descricaoProblema": solicitacao.descricao_problema,
                    "localUnidadeID": solicitacao.local_endereco_id,
                    "descricaoLocal": solicitacao.descricao_local,
                    "categoriaEquipamentoId": solicitacao.categoria_equipamento_id,
                    "urlsFoto": imagens,
                },
                headers={
                    "Authorization": f"Bearer {access_token}"
                },
            )
        if 400 <= resposta.status_code < 500:
            return {"status": "ERRO_API", "http_status": resposta.status_code,
                    "detalhes_api": resposta.text.replace(access_token, "[TOKEN]")[:4000],
                    "mensagem": "A API recusou o cadastro. Confira os dados e as permissões."}
        
        if not 200 <= resposta.status_code < 300 or resposta.status_code == 202:
            return {**indeterminado, "http_status": resposta.status_code,
                    "detalhes_api": resposta.text.replace(access_token, "[TOKEN]")[:4000]}
        if resposta.status_code == 204:
            return {"status": "SUCESSO", "http_status": 204, "titulo": solicitacao.titulo,
                    "mensagem": "Solicitação cadastrada com sucesso."}
        try:
            dados = resposta.json()
        except ValueError:
            return {**indeterminado, "http_status": resposta.status_code}
        titulo_registro = dados.get("titulo") if isinstance(dados, dict) else None
        problema_id = dados.get("id") if isinstance(dados, dict) else None
        status_backend = dados.get("status") if isinstance(dados, dict) else None

        if not isinstance(titulo_registro, str) or not titulo_registro.strip():
            return {**indeterminado, "http_status": resposta.status_code}
        
        return {
            "status": "SUCESSO",
            "http_status": resposta.status_code,
            "titulo": titulo_registro,
            "problema_id": problema_id,
            "status_backend": status_backend,
            "mensagem": "Solicitação cadastrada com sucesso."
        }
    
    except (httpx.HTTPError, ValueError):
        return indeterminado
