from app.core.clients.mongo import abrir_cliente_mongo
from app.core.configuracao import MONGO_BANCO_DADOS, MONGO_COLECAO_SESSOES
from datetime import datetime, timezone

sessoes_ativas: dict[tuple[int, str], str] = {}

def agora() -> datetime:
    return datetime.now(timezone.utc)

async def obter_documento_sessao_id(sessao_id: str, usuario_id: int) -> str | None:
    chave = (usuario_id, sessao_id)
    documento_id = sessoes_ativas.get(chave)
    if documento_id:
        return documento_id

    async with abrir_cliente_mongo() as cliente:
        banco = cliente[MONGO_BANCO_DADOS]
        colecao_sessoes = banco[MONGO_COLECAO_SESSOES]
        documento = await colecao_sessoes.find_one(
            {
                "user_id": usuario_id,
                "session_id": sessao_id,
                "esta_ativo": True,
            },
            {"_id": 1},
            sort=[("iniciada_em", -1)],
        )
        if not documento:
            return None

        sessoes_ativas[chave] = documento["_id"]
        return documento["_id"]
