from calendar import monthrange
from datetime import date, datetime

import httpx

from app.core.config import FIXA_API_BASE_URL


ORDEM_STATUS = ("ATRASADA", "PENDENTE", "EM ANDAMENTO", "CONCLUIDA")


def inicio_periodo(hoje: date) -> date:
    """Subtrai três meses de calendário, ajustando dias que não existem no mês."""
    indice_mes = hoje.year * 12 + hoje.month - 1 - 3
    ano, mes_zero = divmod(indice_mes, 12)
    mes = mes_zero + 1
    return date(ano, mes, min(hoje.day, monthrange(ano, mes)[1]))


def ler_data(valor: str) -> date:
    if not isinstance(valor, str):
        raise ValueError("Data deve ser uma string DD-MM-AAAA.")
    resultado = datetime.strptime(valor, "%d-%m-%Y").date()
    if resultado.strftime("%d-%m-%Y") != valor:
        raise ValueError("Data deve usar DD-MM-AAAA.")
    return resultado


def filtrar_e_ordenar_ordens(dados: list, hoje: date) -> list[dict]:
    if not isinstance(dados, list):
        raise ValueError("Resposta deve ser uma lista.")
    
    inicio = inicio_periodo(hoje)

    ordens = []

    for item in dados:
        if not isinstance(item, dict):
            raise ValueError("Ordem de serviço inválida.")
        
        criacao = ler_data(item.get("dataCriacao"))

        if not inicio <= criacao <= hoje:
            continue

        problema = item.get("problema")

        if not isinstance(problema, dict) or any(
            not isinstance(problema.get(campo), str)
            for campo in ("titulo", "descricaoProblema", "local", "descricaoLocal")
        ):
            raise ValueError("Dados do problema inválidos.")
        
        status = item.get("statusOrdemServico")
        prioridade = item.get("prioridade")

        if status not in ORDEM_STATUS:
            raise ValueError("Status da ordem de serviço inválido.")
        
        if type(prioridade) is not int or prioridade not in (0, 1, 2):
            raise ValueError("Prioridade deve ser 0, 1 ou 2.")
        
        if not isinstance(item.get("categoriaProblema"), str):
            raise ValueError("Categoria do problema inválida.")
        
        if "dataPrevista" not in item:
            raise ValueError("Campo dataPrevista ausente.")
        
        if item["dataPrevista"] is not None:
            ler_data(item["dataPrevista"])

        ordens.append({
            "titulo": problema["titulo"],
            "descricaoProblema": problema["descricaoProblema"],
            "local": problema["local"],
            "descricaoLocal": problema["descricaoLocal"],
            "statusOrdemServico": status,
            "categoriaProblema": item["categoriaProblema"],
            "dataPrevista": item["dataPrevista"],
            "prioridade": prioridade,
        })

    return sorted(ordens, key=lambda ordem: (
        ORDEM_STATUS.index(ordem["statusOrdemServico"]), ordem["prioridade"],
    ))


async def consultar_minhas_ordens_servico(access_token: str) -> dict:
    """Consulta as OSs do usuário e seleciona os últimos três meses até hoje."""
    if not FIXA_API_BASE_URL:
        raise ValueError("Configure FIXA_API_BASE_URL.")
    
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("Token autenticado obrigatório.")
    
    hoje = date.today()

    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as client:
            resposta = await client.get(
                f"{FIXA_API_BASE_URL.rstrip('/')}/api/v1/os/minhas",
                headers={"Authorization": f"Bearer {access_token}"},
            )

    except httpx.TimeoutException:
        return {"status": "TIMEOUT", "mensagem": "A consulta das ordens de serviço excedeu o tempo limite."}
    except httpx.HTTPError:
        return {"status": "ERRO_FERRAMENTA", "mensagem": "Não foi possível conectar à API FIXA."}
    
    if resposta.status_code != 200:
        mensagens = {
            401: "A autenticação não foi aceita. É necessário autenticar-se novamente.",
            403: "O usuário não possui permissão para consultar essas ordens de serviço.",
        }
        return {
            "status": "ERRO_API",
            "http_status": resposta.status_code,
            "mensagem": mensagens.get(resposta.status_code, "A API não concluiu a consulta das ordens de serviço."),
        }
    
    try:
        ordens = filtrar_e_ordenar_ordens(resposta.json(), hoje)
    except ValueError:
        return {"status": "ERRO_VALIDACAO", "mensagem": "A API retornou ordens de serviço em formato incompatível."}
    return {
        "status": "SUCESSO" if ordens else "SEM_RESULTADO",
        "ordens_servico": ordens,
        "periodo": {
            "inicio": inicio_periodo(hoje).strftime("%d-%m-%Y"),
            "fim": hoje.strftime("%d-%m-%Y"),
        },
        "mensagem": "Ordens de serviço consultadas com sucesso." if ordens else "Nenhuma ordem de serviço encontrada nos últimos três meses.",
    }
