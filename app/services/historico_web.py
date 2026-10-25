"""Leitura do histórico autenticado; não expõe rascunhos nem tokens."""

from datetime import datetime

from fastapi import HTTPException
from pydantic import BaseModel, Field

from app.core.clients.mongo import abrir_cliente_mongo
from app.core.configuracao import MONGO_BANCO_DADOS, MONGO_COLECAO_SESSOES


class MensagemWeb(BaseModel):
    id: str
    author: str
    text: str
    images: list[str] = Field(default_factory=list)


class ResumoConversaWeb(BaseModel):
    thread_id: str
    title: str
    updated_at: datetime
    closed: bool = False


class HistoricoConversaWeb(ResumoConversaWeb):
    messages: list[MensagemWeb]
    confirmacao: str = "nao"


def resumo_documento(documento: dict) -> ResumoConversaWeb:
    primeira = next((m for m in documento.get("mensagens", []) if m.get("role") in {"human", "user"}), {})
    return ResumoConversaWeb(
        thread_id=documento["session_id"],
        title=str(primeira.get("content", "Nova conversa"))[:80],
        updated_at=documento.get("atualizada_em") or documento["iniciada_em"],
        closed=bool(documento.get("encerrada_em")),
    )


async def listar_conversas_web(usuario_id: int, limite: int = 50) -> list[ResumoConversaWeb]:
    async with abrir_cliente_mongo() as cliente:
        colecao = cliente[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES]
        cursor = colecao.find(
            {"user_id": usuario_id},
            {"session_id": 1, "mensagens": {"$slice": 1}, "atualizada_em": 1, "iniciada_em": 1, "encerrada_em": 1},
        ).sort("atualizada_em", -1).limit(limite)
        return [resumo_documento(documento) async for documento in cursor]


async def obter_conversa_web(thread_id: str, usuario_id: int) -> HistoricoConversaWeb:
    async with abrir_cliente_mongo() as cliente:
        documento = await cliente[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES].find_one(
            {"user_id": usuario_id, "session_id": thread_id},
            {"session_id": 1, "mensagens": 1, "atualizada_em": 1, "iniciada_em": 1, "encerrada_em": 1, "confirmacao": 1},
        )
    if not documento:
        raise HTTPException(404, "Conversa não encontrada.")
    mensagens = []
    for indice, mensagem in enumerate(documento.get("mensagens", [])):
        role = mensagem.get("role")
        if role not in {"human", "user", "assistant"}:
            continue
        mensagens.append(MensagemWeb(
            id=f"{thread_id}:{indice}",
            author="manu" if role == "assistant" else "user",
            text=str(mensagem.get("content", "")),
            images=[url for url in mensagem.get("imagens", []) if isinstance(url, str) and url.startswith(("https://", "http://"))],
        ))
    return HistoricoConversaWeb(
        **resumo_documento(documento).model_dump(), messages=mensagens,
        confirmacao="sim" if documento.get("confirmacao") == "sim" and not documento.get("encerrada_em") else "nao",
    )


async def atualizar_estado_conversa(thread_id: str, usuario_id: int, **campos) -> None:
    async with abrir_cliente_mongo() as cliente:
        await cliente[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES].update_one(
            {"user_id": usuario_id, "session_id": thread_id}, {"$set": campos},
        )
