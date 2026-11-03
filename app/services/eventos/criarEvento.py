"""Cadastro de evento na API FIXA, sem repetição automática de POST."""

import httpx
from app.core import FIXA_URL_BASE_API, MENSAGENS
from app.schemas.cadastros import CriarEventoEntrada
from app.services.gerais import interpretar_cadastro

async def adicionar_evento(evento: CriarEventoEntrada, access_token: str, *, usuario_id: int) -> dict:
    # Validação: rejeita entrada/contexto incompatível antes de prosseguir.
    """Faz POST autenticado de evento e interpreta sucesso, erro ou resultado incerto sem repetir envio. Usado pelo fluxo de eventos."""
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
    # Lógica: executa esta etapa e preserva o tratamento de falhas do domínio.
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as cliente:
            resposta = await cliente.post(
                f"{FIXA_URL_BASE_API.rstrip('/')}/api/v1/eventos",
                json=corpo, headers={"Authorization": f"Bearer {access_token}"},
            )
    except httpx.HTTPError:
        return indeterminado
    return interpretar_cadastro(
        resposta, access_token=access_token, titulo=evento.titulo,
        mensagem_sucesso=MENSAGENS['evento_cadastrado_com_sucesso'],
        mensagem_recusa=MENSAGENS['a_api_recusou_o_cadastro_do_evento_confira_os_dados_e_as'],
        indeterminado=indeterminado, campo_id='evento_id',
        incluir_status_backend=False, detalhes_indeterminado=False,
    )
