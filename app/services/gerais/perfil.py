import httpx

from app.core.configuracao import FIXA_URL_BASE_API

from app.core.respostas import MENSAGENS


class ErroConsultaPerfil(Exception):
    def __init__(self, status_code: int, mensagem: str):
        self.status_code = status_code
        self.mensagem = mensagem
        super().__init__(mensagem)


async def consultar_perfil(access_token: str) -> dict:
    if not FIXA_URL_BASE_API:
        raise ErroConsultaPerfil(
            500,
            MENSAGENS['fixa_api_base_url_nao_foi_configurada'],
        )

    if not access_token.strip():
        raise ErroConsultaPerfil(
            401,
            MENSAGENS['token_de_acesso_nao_informado'],
        )

    try:
        async with httpx.AsyncClient(
            timeout=15,
            follow_redirects=False,
        ) as cliente:
            resposta = await cliente.get(
                f"{FIXA_URL_BASE_API.rstrip('/')}/api/v1/perfil",
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
            )

    except httpx.TimeoutException:
        raise ErroConsultaPerfil(
            503,
            MENSAGENS['a_consulta_do_perfil_excedeu_o_tempo_limite'],
        ) from None

    except httpx.HTTPError:
        raise ErroConsultaPerfil(
            503,
            MENSAGENS['nao_foi_possivel_conectar_a_api_fixa'],
        ) from None

    if resposta.status_code == 401:
        raise ErroConsultaPerfil(
            401,
            MENSAGENS['token_invalido_ou_expirado'],
        )

    if resposta.status_code == 403:
        raise ErroConsultaPerfil(
            403,
            MENSAGENS['usuario_sem_permissao_de_acesso'],
        )

    if resposta.status_code != 200:
        raise ErroConsultaPerfil(
            502,
            MENSAGENS['a_api_fixa_nao_conseguiu_consultar_o_perfil'],
        )

    try:
        dados = resposta.json()
    except ValueError:
        raise ErroConsultaPerfil(
            502,
            MENSAGENS['a_api_fixa_retornou_um_perfil_invalido'],
        ) from None

    if not isinstance(dados, dict):
        raise ErroConsultaPerfil(
            502,
            MENSAGENS['a_api_fixa_retornou_um_perfil_em_formato_invalido'],
        )

    return dados