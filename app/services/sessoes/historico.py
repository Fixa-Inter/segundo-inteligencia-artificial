from typing import Any

from pymongo.errors import PyMongoError

from app.core import Emocao
from app.core.clients.mongo import abrir_cliente_mongo
from app.core.configuracao import MONGO_BANCO_DADOS, MONGO_COLECAO_SESSOES
from app.memory.persistencia.utilitarios import sessoes_ativas


class ErroConsultaHistorico(Exception):
    def __init__(self, status_code: int, mensagem: str):
        self.status_code = status_code
        self.mensagem = mensagem
        super().__init__(mensagem)


_PROJECAO = {
    "_id": 0,
    "session_id": 1,
    "iniciada_em": 1,
    "atualizada_em": 1,
    "resumo": 1,
    "mensagens": 1,
}


def _separar_resumo(resumo: Any) -> tuple[str, str]:
    if not isinstance(resumo, str) or not resumo.strip():
        return "", ""

    linhas = resumo.strip().splitlines()
    return linhas[0].strip(), "\n".join(linhas[1:]).strip()


def _formatar_mensagens(mensagens: Any) -> list[dict[str, Any]]:
    if not isinstance(mensagens, list):
        return []

    resultado = []
    for mensagem in mensagens:
        if not isinstance(mensagem, dict):
            continue

        role = mensagem.get("role")
        conteudo = mensagem.get("content")
        if role not in {"human", "assistant"} or not isinstance(conteudo, str):
            continue

        item = {"role": role, "mensagem": conteudo}
        if role == "assistant":
            emocao = mensagem.get("emocao", Emocao.NEUTRO.value)
            item["emocao"] = (
                emocao if emocao in Emocao._value2member_map_ else Emocao.NEUTRO.value
            )
        resultado.append(item)
    return resultado


def _formatar_conversa(documento: dict[str, Any]) -> dict[str, Any]:
    titulo, resumo = _separar_resumo(documento.get("resumo"))
    return {
        "session_id": documento["session_id"],
        "iniciada_em": documento["iniciada_em"],
        "atualizada_em": documento["atualizada_em"],
        "titulo": titulo,
        "resumo": resumo,
        "mensagens": _formatar_mensagens(documento.get("mensagens", [])),
    }


async def excluir_conversa(session_id: str, usuario_id: int) -> bool:
    try:
        async with abrir_cliente_mongo() as cliente:
            colecao = cliente[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES]
            resultado = await colecao.update_many(
                {
                    "session_id": session_id,
                    "user_id": usuario_id,
                    "esta_ativo": True,
                },
                {"$set": {"esta_ativo": False}},
            )
    except (PyMongoError, TimeoutError, OSError):
        raise ErroConsultaHistorico(
            503, "O histórico de conversas está temporariamente indisponível."
        ) from None
    except RuntimeError:
        raise ErroConsultaHistorico(
            500, "O serviço de histórico de conversas não está configurado."
        ) from None

    if resultado.modified_count > 0:
        sessoes_ativas.pop((usuario_id, session_id), None)
        return True
    return False


async def buscar_conversas_usuario(usuario_id: int) -> list[dict[str, Any]]:
    try:
        async with abrir_cliente_mongo() as cliente:
            colecao = cliente[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES]
            cursor = colecao.find(
                {"user_id": usuario_id, "esta_ativo": True}, _PROJECAO
            ).sort("atualizada_em", -1)
            documentos = await cursor.to_list(length=None)
    except (PyMongoError, TimeoutError, OSError):
        raise ErroConsultaHistorico(
            503, "O histórico de conversas está temporariamente indisponível."
        ) from None
    except RuntimeError:
        raise ErroConsultaHistorico(
            500, "O serviço de histórico de conversas não está configurado."
        ) from None

    try:
        return [_formatar_conversa(documento) for documento in documentos]
    except (KeyError, TypeError, ValueError):
        raise ErroConsultaHistorico(
            500, "Não foi possível interpretar o histórico de conversas."
        ) from None


async def buscar_conversa(
    session_id: str, usuario_id: int
) -> dict[str, Any] | None:
    try:
        async with abrir_cliente_mongo() as cliente:
            colecao = cliente[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES]
            documento = await colecao.find_one(
                {
                    "session_id": session_id,
                    "user_id": usuario_id,
                    "esta_ativo": True,
                },
                _PROJECAO,
            )
    except (PyMongoError, TimeoutError, OSError):
        raise ErroConsultaHistorico(
            503, "O histórico de conversas está temporariamente indisponível."
        ) from None
    except RuntimeError:
        raise ErroConsultaHistorico(
            500, "O serviço de histórico de conversas não está configurado."
        ) from None

    if documento is None:
        return None

    try:
        return _formatar_conversa(documento)
    except (KeyError, TypeError, ValueError):
        raise ErroConsultaHistorico(
            500, "Não foi possível interpretar o histórico de conversas."
        ) from None
