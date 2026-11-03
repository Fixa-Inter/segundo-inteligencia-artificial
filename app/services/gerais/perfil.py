import httpx
from app.core import FIXA_URL_BASE_API, MENSAGENS

# ErroConsultaPerfil: contrato/estrutura de perfil; usado pelos consumidores desta interface.
class ErroConsultaPerfil(Exception):
    def __init__(self, status_code: int, mensagem: str):
        """Inicializa os atributos da instância para as operações da classe. Usado pelo fluxo de gerais."""
        self.status_code = status_code
        self.mensagem = mensagem
        super().__init__(mensagem)


async def consultar_perfil(access_token: str) -> dict:
    # Validação: rejeita entrada/contexto incompatível antes de prosseguir.
    """Consulta perfil pela API FIXA usando Bearer e traduz falhas para ErroConsultaPerfil. Usado pelo fluxo de gerais."""
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

    # Lógica: executa esta etapa e preserva o tratamento de falhas do domínio.
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
