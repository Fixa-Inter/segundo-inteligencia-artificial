from app.core.clients import abrir_cliente_mongo
from app.core import Emocao, MONGO_BANCO_DADOS, MONGO_COLECAO_SESSOES

async def recuperar_mensagens(documento_id: str, usuario_id: int) -> list[dict]:
    """Lê mensagens próprias com padrões compatíveis com dados legados. Usado pelo fluxo de persistencia."""
    async with abrir_cliente_mongo() as cliente:
        banco = cliente[MONGO_BANCO_DADOS]
        colecao_sessoes = banco[MONGO_COLECAO_SESSOES]
        documento = await colecao_sessoes.find_one(
            {"_id": documento_id, "user_id": usuario_id, "esta_ativo": True},
            {"mensagens": 1},
        )
        mensagens = documento["mensagens"] if documento else []
        for mensagem in mensagens:
            if mensagem.get("role") == "assistant":
                mensagem.setdefault("emocao", Emocao.NEUTRO.value)
        return mensagens
