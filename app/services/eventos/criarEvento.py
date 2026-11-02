"""Cadastro de evento na API FIXA, sem repetição automática de POST."""


import httpx

from app.core.configuracao import FIXA_URL_BASE_API
from app.tools.toolsRequest.CriarEventoEntrada import CriarEventoEntrada

from app.core.respostas import MENSAGENS


async def adicionar_evento(evento: CriarEventoEntrada, access_token: str, *, usuario_id: int) -> dict:
    if not FIXA_URL_BASE_API:
        raise ValueError(MENSAGENS['configure_fixa_api_base_url'])
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError(MENSAGENS['token_autenticado_obrigatorio'])
    if type(usuario_id) is not int or usuario_id <= 0:
        raise ValueError(MENSAGENS['usuario_invalido'])
    evento = CriarEventoEntrada.model_validate(evento.model_dump())
    dados = evento.model_dump(mode="json")
    corpo = {
        "usuarioId": usuario_id,
        "localUnidadeId": evento.local_unidade_id,
        "titulo": evento.titulo,
        "descricao": evento.descricao,
        "descricaoLocal": evento.descricao_local,
        "observacao": evento.observacao,
        "dataHoraInicio": dados["data_hora_inicio"],
        "dataHoraFim": dados["data_hora_fim"],
    }
    indeterminado = {
        "status": "RESULTADO_INDETERMINADO",
        "mensagem": MENSAGENS['nao_foi_possivel_confirmar_o_cadastro_do_evento_consulte_os_registros_antes'],
    }
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as cliente:
            resposta = await cliente.post(
                f"{FIXA_URL_BASE_API.rstrip('/')}/api/v1/eventos",
                json=corpo, headers={"Authorization": f"Bearer {access_token}"},
            )
    except httpx.HTTPError:
        return indeterminado
    http_status = resposta.status_code
    if 400 <= http_status < 500:
        return {
            "status": "ERRO_API", "http_status": http_status,
            "detalhes_api": resposta.text.replace(access_token, "[TOKEN]")[:4000],
            "mensagem": MENSAGENS['a_api_recusou_o_cadastro_do_evento_confira_os_dados_e_as'],
        }
    if not 200 <= http_status < 300 or http_status == 202:
        return {**indeterminado, "http_status": http_status}
    if http_status == 204:
        return {"status": "SUCESSO", "http_status": http_status, "titulo": evento.titulo,
                "mensagem": MENSAGENS['evento_cadastrado_com_sucesso']}
    try:
        dados = resposta.json()
    except ValueError:
        return {**indeterminado, "http_status": http_status}
    if not isinstance(dados, dict) or not isinstance(dados.get("titulo"), str) or not dados["titulo"].strip():
        return {**indeterminado, "http_status": http_status}
    return {"status": "SUCESSO", "http_status": http_status, "titulo": dados["titulo"],
            "evento_id": dados.get("id"), "mensagem": MENSAGENS['evento_cadastrado_com_sucesso']}
