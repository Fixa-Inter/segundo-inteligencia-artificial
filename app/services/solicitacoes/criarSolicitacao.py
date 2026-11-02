import httpx

from app.core.configuracao import FIXA_URL_BASE_API
from app.tools.toolsRequest import CriarSolicitacaoEntrada

from app.core.respostas import MENSAGENS


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
        raise ValueError(MENSAGENS['forneca_pelo_menos_uma_url_de_imagem_em_uma_lista_de_strings'])
    if not FIXA_URL_BASE_API:
        raise ValueError(MENSAGENS['configure_fixa_api_base_url'])

    # LEMBRAR DE FAZER A VALIDAÇÃO DO ACCESS_TOKEN
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError(MENSAGENS['token_autenticado_obrigatorio'])
    
    indeterminado = {"status": "RESULTADO_INDETERMINADO", "mensagem": MENSAGENS['nao_foi_possivel_confirmar_o_cadastro_consulte_a_api_antes_de_repetir']}

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
                    "mensagem": MENSAGENS['a_api_recusou_o_cadastro_confira_os_dados_e_as_permissoes']}
        
        if not 200 <= resposta.status_code < 300 or resposta.status_code == 202:
            return {**indeterminado, "http_status": resposta.status_code,
                    "detalhes_api": resposta.text.replace(access_token, "[TOKEN]")[:4000]}
        if resposta.status_code == 204:
            return {"status": "SUCESSO", "http_status": 204, "titulo": solicitacao.titulo,
                    "mensagem": MENSAGENS['solicitacao_cadastrada_com_sucesso']}
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
            "mensagem": MENSAGENS['solicitacao_cadastrada_com_sucesso']
        }
    
    except (httpx.HTTPError, ValueError):
        return indeterminado
