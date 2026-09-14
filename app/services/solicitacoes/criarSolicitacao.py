import httpx

from app.core.config import FIXA_API_BASE_URL
from app.tools.toolsRequest.CriarSolicitacaoRequest import CriarSolicitacaoRequest


async def adicionar_solicitacao(
    solicitacao: CriarSolicitacaoRequest, access_token: str, endereco_id: int,
) -> dict:
    """Envia o cadastro diretamente. Sem estado de conversa ou repetição de POST.

    Contrato provisório: JSON da solicitação, Bearer token, X-Endereco-Id e
    resposta 2xx com id. A API deve validar a identidade, sede e os IDs recebidos.
    """
    if not FIXA_API_BASE_URL:
        raise ValueError("Configure FIXA_API_BASE_URL.")
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("Token autenticado obrigatório.")
    if type(endereco_id) is not int or endereco_id <= 0:
        raise ValueError("Sede autenticada obrigatória.")
    indeterminado = {"status": "RESULTADO_INDETERMINADO", "mensagem":
                     "Não foi possível confirmar o cadastro. Consulte a API antes de repetir o envio."}
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as client:
            resposta = await client.post(
                f"{FIXA_API_BASE_URL.rstrip('/')}/adicionar/solicitacao",
                json=solicitacao.model_dump(),
                headers={"Authorization": f"Bearer {access_token}",
                         "X-Endereco-Id": str(endereco_id)},
            )
        if 400 <= resposta.status_code < 500:
            return {"status": "ERRO_API", "http_status": resposta.status_code,
                    "mensagem": "A API recusou o cadastro. Confira os dados e as permissões."}
        resposta.raise_for_status()
        dados = resposta.json()
        registro_id = dados.get("id") if isinstance(dados, dict) else None
        if type(registro_id) not in (str, int) or not registro_id:
            return indeterminado
        return {"status": "SUCESSO", "id": registro_id,
                "mensagem": "Solicitação cadastrada com sucesso."}
    except (httpx.HTTPError, ValueError):
        return indeterminado
