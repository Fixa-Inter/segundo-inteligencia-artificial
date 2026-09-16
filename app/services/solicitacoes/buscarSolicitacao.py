from datetime import date

import httpx

from app.core.config import FIXA_API_BASE_URL


async def listar_solicitacoes_pendentes(access_token: str) -> dict:
    """Consulta a organização identificada pelo token e filtra o status PENDENTE."""
    if not FIXA_API_BASE_URL:
        raise ValueError("Configure FIXA_API_BASE_URL.")
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("Token autenticado obrigatório.")

    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as client:
            resposta = await client.get(
                f"{FIXA_API_BASE_URL.rstrip('/')}/api/v1/solicitacoes",
                headers={"Authorization": f"Bearer {access_token}"},
            )
    except httpx.TimeoutException:
        return {"status": "TIMEOUT", "mensagem": "A consulta das solicitações excedeu o tempo limite."}
    except httpx.HTTPError:
        return {"status": "ERRO_FERRAMENTA", "mensagem": "Não foi possível conectar à API FIXA."}

    if resposta.status_code != 200:
        mensagens = {
            401: "A autenticação não foi aceita. É necessário autenticar-se novamente.",
            403: "O usuário não possui permissão para consultar essas solicitações.",
        }
        return {
            "status": "ERRO_API",
            "http_status": resposta.status_code,
            "mensagem": mensagens.get(resposta.status_code, "A API não concluiu a consulta das solicitações."),
        }

    try:
        dados = resposta.json()
        if not isinstance(dados, list):
            raise ValueError("Resposta deve ser uma lista.")
        solicitacoes = []
        for item in dados:
            if not isinstance(item, dict) or any(
                not isinstance(item.get(campo), str) or not item[campo].strip()
                for campo in ("titulo", "dataCriacao", "nomeUsuario", "status")
            ):
                raise ValueError("Campos da solicitação inválidos.")
            data_criacao = date.fromisoformat(item["dataCriacao"])
            if data_criacao.isoformat() != item["dataCriacao"]:
                raise ValueError("Data deve usar YYYY-MM-DD.")
            if item["status"] == "PENDENTE":
                solicitacoes.append({
                    "titulo": item["titulo"],
                    "dataCriacao": item["dataCriacao"],
                    "nomeUsuario": item["nomeUsuario"],
                    "status": item["status"],
                })
    except ValueError:
        return {"status": "ERRO_VALIDACAO", "mensagem": "A API retornou solicitações em formato incompatível."}

    return {
        "status": "SUCESSO" if solicitacoes else "SEM_RESULTADO",
        "solicitacoes": solicitacoes,
        "mensagem": "Solicitações pendentes consultadas com sucesso." if solicitacoes else "Nenhuma solicitação pendente encontrada na organização.",
    }


async def listar_minhas_solicitacoes(access_token: str) -> dict:
    """Consulta as solicitações do usuário identificado pelo Bearer token."""
    if not FIXA_API_BASE_URL:
        raise ValueError("Configure FIXA_API_BASE_URL.")
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("Token autenticado obrigatório.")

    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as client:
            resposta = await client.get(
                f"{FIXA_API_BASE_URL.rstrip('/')}/api/v1/solicitacoes/minhas",
                headers={"Authorization": f"Bearer {access_token}"},
            )
    except httpx.TimeoutException:
        return {"status": "TIMEOUT", "mensagem": "A consulta das solicitações excedeu o tempo limite."}
    except httpx.HTTPError:
        return {"status": "ERRO_FERRAMENTA", "mensagem": "Não foi possível conectar à API FIXA."}

    if resposta.status_code != 200:
        mensagens = {
            401: "A autenticação não foi aceita. É necessário autenticar-se novamente.",
            403: "O usuário não possui permissão para consultar essas solicitações.",
        }
        return {
            "status": "ERRO_API",
            "http_status": resposta.status_code,
            "mensagem": mensagens.get(resposta.status_code, "A API não concluiu a consulta das solicitações."),
        }

    try:
        dados = resposta.json()
        if not isinstance(dados, list):
            raise ValueError("Resposta deve ser uma lista.")
        solicitacoes = []
        for item in dados:
            if not isinstance(item, dict) or any(
                not isinstance(item.get(campo), str) or not item[campo].strip()
                for campo in ("titulo", "dataCriacao", "nomeUsuario")
            ):
                raise ValueError("Campos da solicitação inválidos.")
            data_criacao = date.fromisoformat(item["dataCriacao"])
            if data_criacao.isoformat() != item["dataCriacao"]:
                raise ValueError("Data deve usar YYYY-MM-DD.")
            solicitacoes.append({
                "titulo": item["titulo"],
                "dataCriacao": item["dataCriacao"],
                "nomeUsuario": item["nomeUsuario"],
            })
    except ValueError:
        return {"status": "ERRO_VALIDACAO", "mensagem": "A API retornou solicitações em formato incompatível."}

    return {
        "status": "SUCESSO" if solicitacoes else "SEM_RESULTADO",
        "solicitacoes": solicitacoes,
        "mensagem": "Solicitações consultadas com sucesso." if solicitacoes else "Nenhuma solicitação encontrada para o usuário.",
    }
