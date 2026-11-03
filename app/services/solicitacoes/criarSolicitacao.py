import httpx
from app.core import FIXA_URL_BASE_API, MENSAGENS
from app.schemas.cadastros import CriarSolicitacaoEntrada
from app.services.gerais import interpretar_cadastro

async def adicionar_solicitacao(
    solicitacao: CriarSolicitacaoEntrada,
    access_token: str,
    *, imagens: list[str],
) -> dict:
    """Envia o cadastro diretamente. Sem estado de conversa ou repetição de POST.

    Envia os dados da solicitação e as URLs em urlsFoto, usando Bearer token.
    Espera resposta 2xx com titulo. A API valida a identidade, sede e os IDs.
    """
    # Validação: rejeita entrada/contexto incompatível antes de prosseguir.
    if not isinstance(imagens, list) or not imagens or any(
        not isinstance(url, str) or not url.strip() for url in imagens
    ):
        raise ValueError(MENSAGENS['forneca_pelo_menos_uma_url_de_imagem_em_uma_lista_de_strings'])
    if not FIXA_URL_BASE_API:
        raise ValueError(MENSAGENS['configure_fixa_api_base_url'])

    # Validação: exige o token autenticado encaminhado pelo contexto.
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError(MENSAGENS['token_autenticado_obrigatorio'])

    indeterminado = {"status": "RESULTADO_INDETERMINADO", "mensagem": MENSAGENS['nao_foi_possivel_confirmar_o_cadastro_consulte_a_api_antes_de_repetir']}

    # Lógica: executa esta etapa e preserva o tratamento de falhas do domínio.
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
        return interpretar_cadastro(
            resposta, access_token=access_token, titulo=solicitacao.titulo,
            mensagem_sucesso=MENSAGENS['solicitacao_cadastrada_com_sucesso'],
            mensagem_recusa=MENSAGENS['a_api_recusou_o_cadastro_confira_os_dados_e_as_permissoes'],
            indeterminado=indeterminado, campo_id='problema_id',
            incluir_status_backend=True, detalhes_indeterminado=True,
        )

    except (httpx.HTTPError, ValueError):
        return indeterminado
