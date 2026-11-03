import httpx
from app.core import FIXA_URL_BASE_API, MENSAGENS
from app.schemas.cadastros import CriarOcorrenciaEntrada
from app.services.gerais import interpretar_cadastro

async def adicionar_ocorrencia(
    ocorrencia: CriarOcorrenciaEntrada, access_token: str, *, usuario_id: int, imagens: list[str],
) -> dict:
    """Envia uma única requisição conforme OcorrenciaCadastrarInputDTO."""
    # Validação: rejeita entrada/contexto incompatível antes de prosseguir.
    if not FIXA_URL_BASE_API:
        raise ValueError(MENSAGENS['configure_fixa_api_base_url'])
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError(MENSAGENS['token_autenticado_obrigatorio'])
    if type(usuario_id) is not int or usuario_id <= 0:
        raise ValueError(MENSAGENS['usuario_invalido'])
    if not isinstance(imagens, list) or not imagens or any(not isinstance(url, str) or not url.strip() for url in imagens):
        return {"status": "AGUARDANDO_INFORMACAO", "mensagem": MENSAGENS['envie_pelo_menos_uma_foto_da_ocorrencia']}
    corpo = {
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
                     MENSAGENS['nao_foi_possivel_confirmar_o_cadastro_consulte_os_registros_antes_de_repetir']}
    # Lógica: executa esta etapa e preserva o tratamento de falhas do domínio.
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as cliente:
            resposta = await cliente.post(
                f"{FIXA_URL_BASE_API.rstrip('/')}/api/v1/ocorrencias",
                json=corpo, headers={"Authorization": f"Bearer {access_token}"},
            )
    except httpx.HTTPError:
        return indeterminado
    return interpretar_cadastro(
        resposta, access_token=access_token, titulo=ocorrencia.titulo,
        mensagem_sucesso=MENSAGENS['ocorrencia_cadastrada_com_sucesso'],
        mensagem_recusa=MENSAGENS['a_api_recusou_o_cadastro_da_ocorrencia_confira_os_dados_e_as'],
        indeterminado=indeterminado, campo_id='ocorrencia_id',
        incluir_status_backend=False, detalhes_indeterminado=True,
    )
