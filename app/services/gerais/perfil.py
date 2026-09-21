import httpx

from app.core.config import FIXA_API_BASE_URL


class ErroConsultaPerfil(Exception):
    def __init__(self, status_code: int, mensagem: str):
        self.status_code = status_code
        self.mensagem = mensagem
        super().__init__(mensagem)


async def consultar_perfil(access_token: str) -> dict:
    if not FIXA_API_BASE_URL:
        raise ErroConsultaPerfil(
            500,
            "FIXA_API_BASE_URL não foi configurada.",
        )

    if not access_token.strip():
        raise ErroConsultaPerfil(
            401,
            "Token de acesso não informado.",
        )

    try:
        async with httpx.AsyncClient(
            timeout=15,
            follow_redirects=False,
        ) as client:
            resposta = await client.get(
                f"{FIXA_API_BASE_URL.rstrip('/')}/api/v1/perfil",
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
            )

    except httpx.TimeoutException:
        raise ErroConsultaPerfil(
            503,
            "A consulta do perfil excedeu o tempo limite.",
        ) from None

    except httpx.HTTPError:
        raise ErroConsultaPerfil(
            503,
            "Não foi possível conectar à API FIXA.",
        ) from None

    if resposta.status_code == 401:
        raise ErroConsultaPerfil(
            401,
            "Token inválido ou expirado.",
        )

    if resposta.status_code == 403:
        raise ErroConsultaPerfil(
            403,
            "Usuário sem permissão de acesso.",
        )

    if resposta.status_code != 200:
        raise ErroConsultaPerfil(
            502,
            "A API FIXA não conseguiu consultar o perfil.",
        )

    try:
        dados = resposta.json()
    except ValueError:
        raise ErroConsultaPerfil(
            502,
            "A API FIXA retornou um perfil inválido.",
        ) from None

    if not isinstance(dados, dict):
        raise ErroConsultaPerfil(
            502,
            "A API FIXA retornou um perfil em formato inválido.",
        )

    return dados