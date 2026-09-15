import httpx

from app.core.config import FIXA_API_BASE_URL
from app.tools.toolsRequest.CriarSolicitacaoRequest import CriarSolicitacaoRequest


async def adicionar_solicitacao(
    solicitacao: CriarSolicitacaoRequest,
    access_token: str,
) -> dict:
    """Envia o cadastro diretamente. Sem estado de conversa ou repetição de POST.

    Contrato provisório: JSON da solicitação com usuario_id, Bearer token, X-Endereco-Id e
    resposta 2xx com id. A API deve validar a identidade, sede e os IDs recebidos.
    """
    if not FIXA_API_BASE_URL:
        raise ValueError("Configure FIXA_API_BASE_URL.")

    # LEMBRAR DE FAZER A VALIDAÇÃO DO ACCESS_TOKEN
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("Token autenticado obrigatório.")
    
    indeterminado = {"status": "RESULTADO_INDETERMINADO", "mensagem": "Não foi possível confirmar o cadastro. Consulte a API antes de repetir o envio."}

    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as client:
            resposta = await client.post(
                f"{FIXA_API_BASE_URL.rstrip('/')}/api/v1/solicitacoes",
                json={
                    **solicitacao.model_dump()
                },
                headers={
                    "Authorization": f"Bearer {access_token}"
                },
            )
        if 400 <= resposta.status_code < 500:
            return {"status": "ERRO_API", "http_status": resposta.status_code,
                    "mensagem": "A API recusou o cadastro. Confira os dados e as permissões."}
        
        resposta.raise_for_status()
        dados = resposta.json()
        titulo_registro = dados.get("titulo") if isinstance(dados, dict) else None

        if type(titulo_registro) not in (str, int) or not titulo_registro:
            return indeterminado
        
        return {
            "status": "SUCESSO",
            "titulo": titulo_registro,
            "mensagem": "Solicitação cadastrada com sucesso."
        }
    
    except (httpx.HTTPError, ValueError):
        return indeterminado
