import httpx

from app.core.config import FIXA_API_BASE_URL
from app.tools.toolsRequest.CriarOcorrenciaRequest import CriarOcorrenciaRequest


async def adicionar_ocorrencia(
    ocorrencia: CriarOcorrenciaRequest,
    access_token: str,
    *,
    usuario_id: int,
    equipamento_id: int | None,
) -> dict:
    """Envia o cadastro uma única vez; HTTP 201 confirma a criação, mesmo sem corpo."""
    if not FIXA_API_BASE_URL:
        raise ValueError("Configure FIXA_API_BASE_URL.")
    
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("Token autenticado obrigatório.")
    
    if type(usuario_id) is not int or usuario_id <= 0:
        raise ValueError("ID do usuário autenticado inválido.")
    
    if equipamento_id is not None and (type(equipamento_id) is not int or equipamento_id <= 0):
        raise ValueError("ID do equipamento inválido.")
    
    if (ocorrencia.equipamento_codigo is None) != (equipamento_id is None):
        raise ValueError("O código informado precisa ser resolvido para um ID de equipamento.")
    
    corpo = {
        "usuarioId": usuario_id,
        "localEnderecoId": ocorrencia.local_endereco_id,
        "equipamentoId": equipamento_id,
        "categoriaProblemaId": ocorrencia.categoria_problema_id,
        "titulo": ocorrencia.titulo,
        "descricaoOcorrencia": ocorrencia.descricao_ocorrencia,
        "descricaoLocal": ocorrencia.descricao_local,
        "prioridade": ocorrencia.prioridade,
    }

    indeterminado = {"status": "RESULTADO_INDETERMINADO", "mensagem":
                     "Não foi possível confirmar o cadastro. Verifique se a ocorrência foi criada antes de repetir o envio."}
    
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as client:
            resposta = await client.post(
                f"{FIXA_API_BASE_URL.rstrip('/')}/api/v1/ocorrencias",
                json=corpo, headers={"Authorization": f"Bearer {access_token}"},
            )
        
    except httpx.HTTPError:
        return indeterminado
    
    if resposta.status_code == 201:
        return {"status": "SUCESSO", "titulo": ocorrencia.titulo, "mensagem": "Ocorrência cadastrada com sucesso."}
    
    if 400 <= resposta.status_code < 500:
        return {"status": "ERRO_API", "http_status": resposta.status_code,
                "mensagem": "A API recusou o cadastro da ocorrência. Confira os dados e as permissões."}
    
    return indeterminado
