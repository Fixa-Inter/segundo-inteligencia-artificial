from datetime import date

import httpx

from app.core.config import FIXA_API_BASE_URL


async def buscar_equipamento_por_codigo(codigo: str, access_token: str) -> dict:
    """Resolve um código para um único equipamento ativo. Endpoint provisório."""
    if not FIXA_API_BASE_URL:
        raise ValueError("Configure FIXA_API_BASE_URL.")
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("Token autenticado obrigatório.")
    if not isinstance(codigo, str) or not codigo.strip():
        return {"status": "ERRO_VALIDACAO", "mensagem": "Informe o código do equipamento."}
    codigo = codigo.strip()
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as client:
            resposta = await client.get(
                f"{FIXA_API_BASE_URL.rstrip('/')}/api/v1/ocorrencias",
                params={"filter": f"codigo eq {codigo}"},
                headers={"Authorization": f"Bearer {access_token}"},
            )
    except httpx.TimeoutException:
        return {"status": "TIMEOUT", "mensagem": "A consulta do equipamento excedeu o tempo limite."}
    except httpx.HTTPError:
        return {"status": "ERRO_FERRAMENTA", "mensagem": "Não foi possível consultar o equipamento na API FIXA."}
    if resposta.status_code != 200:
        return {"status": "ERRO_API", "http_status": resposta.status_code,
                "mensagem": "A API recusou a consulta do equipamento. Confira a autenticação e as permissões."}
    try:
        dados = resposta.json()
        if not isinstance(dados, list) or any(not isinstance(item, dict) for item in dados):
            raise ValueError("Resposta incompatível.")
        encontrados = [item for item in dados if item.get("codigo") == codigo]
        if not encontrados:
            return {"status": "AGUARDANDO_INFORMACAO", "mensagem": "Equipamento não encontrado pelo código informado. Peça ao usuário para conferir o código."}
        if len(encontrados) != 1:
            return {"status": "AGUARDANDO_INFORMACAO", "mensagem": "O código corresponde a mais de um equipamento. Esclareça o cadastro antes de continuar."}
        item = encontrados[0]
        if type(item.get("id")) is not int or item["id"] <= 0 or type(item.get("estaAtivo")) is not bool:
            raise ValueError("Identificação ou estado do equipamento inválido.")
        if any(not isinstance(item.get(campo), str) for campo in ("nomeModelo", "nomeLocalEndereco")):
            raise ValueError("Descrição do equipamento inválida.")
        if not item["estaAtivo"]:
            return {"status": "ERRO_VALIDACAO", "mensagem": "O equipamento informado está inativo e não pode ser usado no cadastro."}
        return {"status": "SUCESSO", "equipamento": {
            campo: item[campo] for campo in ("id", "codigo", "nomeModelo", "nomeLocalEndereco", "estaAtivo")
        }}
    except ValueError:
        return {"status": "ERRO_VALIDACAO", "mensagem": "A API retornou um equipamento em formato incompatível."}


async def consultar_minhas_ocorrencias(access_token: str) -> dict:
    """Consulta ocorrências do usuário; o filtro de três meses é aplicado pela API."""
    if not FIXA_API_BASE_URL:
        raise ValueError("Configure FIXA_API_BASE_URL.")
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("Token autenticado obrigatório.")

    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as client:
            resposta = await client.get(
                f"{FIXA_API_BASE_URL.rstrip('/')}/api/v1/ocorrencias/minhas",
                headers={"Authorization": f"Bearer {access_token}"},
            )
    except httpx.TimeoutException:
        return {"status": "TIMEOUT", "mensagem": "A consulta das ocorrências excedeu o tempo limite."}
    except httpx.HTTPError:
        return {"status": "ERRO_FERRAMENTA", "mensagem": "Não foi possível conectar à API FIXA."}

    if resposta.status_code != 200:
        mensagens = {
            401: "A autenticação não foi aceita. É necessário autenticar-se novamente.",
            403: "O usuário não possui permissão para consultar essas ocorrências.",
        }
        return {
            "status": "ERRO_API",
            "http_status": resposta.status_code,
            "mensagem": mensagens.get(resposta.status_code, "A API não concluiu a consulta das ocorrências."),
        }

    campos = (
        "titulo", "descricaoOcorrencia", "categoriaProblema", "prioridade",
        "localEndereco", "descricaoLocal", "dataCriacao",
    )
    try:
        dados = resposta.json()
        if not isinstance(dados, list):
            raise ValueError("Resposta deve ser uma lista.")
        ocorrencias = []
        for item in dados:
            if not isinstance(item, dict) or any(
                not isinstance(item.get(campo), str) for campo in campos
            ):
                raise ValueError("Campos da ocorrência inválidos.")
            criacao = date.fromisoformat(item["dataCriacao"])
            if criacao.isoformat() != item["dataCriacao"]:
                raise ValueError("Data de criação deve usar AAAA-MM-DD.")
            if "equipamentoCodigo" not in item or (
                item["equipamentoCodigo"] is not None
                and not isinstance(item["equipamentoCodigo"], str)
            ):
                raise ValueError("Código do equipamento inválido.")
            ocorrencias.append({
                **{campo: item[campo] for campo in campos},
                "equipamentoCodigo": item["equipamentoCodigo"],
            })
    except ValueError:
        return {"status": "ERRO_VALIDACAO", "mensagem": "A API retornou ocorrências em formato incompatível."}

    return {
        "status": "SUCESSO" if ocorrencias else "SEM_RESULTADO",
        "ocorrencias": ocorrencias,
        "mensagem": "Ocorrências consultadas com sucesso." if ocorrencias else "Nenhuma ocorrência encontrada no período retornado pela API.",
    }
