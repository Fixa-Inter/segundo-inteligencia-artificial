import httpx

from app.core.config import FIXA_API_BASE_URL

async def login(email: str, senha: str) -> str:
    """Autentica na API. Contrato provisório: {email, senha} -> {access_token}.

    Chamar pelo código da aplicação; não enviar credenciais ao modelo.
    """
    if not FIXA_API_BASE_URL:
        raise ValueError("Configure FIXA_API_BASE_URL.")
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as client:
            resposta = await client.post(
                f"{FIXA_API_BASE_URL.rstrip('/')}/login",
                json={"email": email, "senha": senha},
            )
            resposta.raise_for_status()
            token = resposta.json()["access_token"]
            if not isinstance(token, str) or not token.strip():
                raise ValueError("Token ausente.")
            return token
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        raise ValueError("Não foi possível autenticar na API FIXA.") from None