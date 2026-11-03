from typing import Any
from pymongo.errors import PyMongoError
from app.core import Emocao, MONGO_BANCO_DADOS, MONGO_COLECAO_SESSOES, MENSAGENS
from app.core.clients import abrir_cliente_mongo
from app.memory.persistencia import sessoes_ativas
from app.services.visualizacoes import validar_visualizacao_publica

# ErroConsultaHistorico: contrato/estrutura de historico; usado pelos consumidores desta interface.
class ErroConsultaHistorico(Exception):
    def __init__(self, status_code: int, mensagem: str):
        """Inicializa os atributos da instância para as operações da classe. Usado pelo fluxo de sessoes."""
        self.status_code = status_code
        self.mensagem = mensagem
        super().__init__(mensagem)


# _PROJECAO: Recurso compartilhado de projecao usado pelas funções deste módulo e pela interface pública.
_PROJECAO = {
    "_id": 0,
    "session_id": 1,
    "iniciada_em": 1,
    "atualizada_em": 1,
    "titulo": 1,
    "resumo": 1,
    "mensagens": 1,
}


def _formatar_mensagens(mensagens: Any, *, incluir_visualizacoes: bool = False) -> list[dict[str, Any]]:
    """Executa a etapa formatar mensagens no escopo de historico. Usado por _formatar_conversa."""
    if not isinstance(mensagens, list):
        return []

    resultado = []
    for mensagem in mensagens:
        if not isinstance(mensagem, dict):
            continue

        role = mensagem.get("role")
        conteudo = mensagem.get("content")
        imagens = mensagem.get("imagens")
        if role not in {"human", "assistant"} or not isinstance(conteudo, str):
            continue
        item = {"role": role, "mensagem": conteudo, "timestamp": mensagem.get("timestamp")}
        if imagens is not None:
            item["imagens"] = imagens
        item["confirmacao"] = "sim" if role == "assistant" and mensagem.get("confirmacao") == "sim" else "nao"
        if role == "assistant":
            emocao = mensagem.get("emocao", Emocao.NEUTRO.value)
            item["emocao"] = (
                emocao if emocao in Emocao._value2member_map_ else Emocao.NEUTRO.value
            )
            if incluir_visualizacoes and mensagem.get("visualizacao") is not None:
                item["visualizacao"] = validar_visualizacao_publica(mensagem["visualizacao"]).model_dump(mode="json")
        resultado.append(item)
    return resultado


def _formatar_conversa(documento: dict[str, Any], *, incluir_visualizacoes: bool = False) -> dict[str, Any]:
    """Executa a etapa formatar conversa no escopo de historico. Usado por buscar_conversa, buscar_conversas_usuario."""
    titulo = documento.get("titulo")
    resumo = documento.get("resumo")
    return {
        "session_id": documento["session_id"],
        "iniciada_em": documento["iniciada_em"],
        "atualizada_em": documento["atualizada_em"],
        "titulo": titulo if isinstance(titulo, str) else "",
        "resumo": resumo if isinstance(resumo, str) else "",
        "mensagens": _formatar_mensagens(documento.get("mensagens", []), incluir_visualizacoes=incluir_visualizacoes),
    }


async def excluir_conversa(session_id: str, usuario_id: int) -> bool:
    """Oculta conversa própria com exclusão lógica e remove cache da sessão. Usado pelo fluxo de sessoes."""
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
            503, MENSAGENS['o_historico_de_conversas_esta_temporariamente_indisponivel']
        ) from None
    except RuntimeError:
        raise ErroConsultaHistorico(
            500, MENSAGENS['o_servico_de_historico_de_conversas_nao_esta_configurado']
        ) from None

    if resultado.modified_count > 0:
        sessoes_ativas.pop((usuario_id, session_id), None)
        return True
    return False


async def buscar_conversas_usuario(usuario_id: int, *, incluir_visualizacoes: bool = False) -> list[dict[str, Any]]:
    """Consulta conversas ativas do usuário e formata mensagens/payloads históricos. Usado pelo fluxo de sessoes."""
    try:
        async with abrir_cliente_mongo() as cliente:
            colecao = cliente[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES]
            cursor = colecao.find(
                {"user_id": usuario_id, "esta_ativo": True}, _PROJECAO
            ).sort("atualizada_em", -1)
            documentos = await cursor.to_list(length=None)
    except (PyMongoError, TimeoutError, OSError):
        raise ErroConsultaHistorico(
            503, MENSAGENS['o_historico_de_conversas_esta_temporariamente_indisponivel']
        ) from None
    except RuntimeError:
        raise ErroConsultaHistorico(
            500, MENSAGENS['o_servico_de_historico_de_conversas_nao_esta_configurado']
        ) from None

    try:
        return [_formatar_conversa(documento, incluir_visualizacoes=incluir_visualizacoes) for documento in documentos]
    except (KeyError, TypeError, ValueError):
        raise ErroConsultaHistorico(
            500, MENSAGENS['nao_foi_possivel_interpretar_o_historico_de_conversas']
        ) from None


async def buscar_conversa(
    session_id: str, usuario_id: int, *, incluir_visualizacoes: bool = False,
) -> dict[str, Any] | None:
    """Obtém conversa ativa por proprietário e ID, com visualização quando permitido. Usado pelo fluxo de sessoes."""
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
            503, MENSAGENS['o_historico_de_conversas_esta_temporariamente_indisponivel']
        ) from None
    except RuntimeError:
        raise ErroConsultaHistorico(
            500, MENSAGENS['o_servico_de_historico_de_conversas_nao_esta_configurado']
        ) from None

    if documento is None:
        return None

    try:
        return _formatar_conversa(documento, incluir_visualizacoes=incluir_visualizacoes)
    except (KeyError, TypeError, ValueError):
        raise ErroConsultaHistorico(
            500, MENSAGENS['nao_foi_possivel_interpretar_o_historico_de_conversas']
        ) from None
