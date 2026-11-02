import uuid
from app.memory.persistencia.utilitarios import (
    obter_documento_sessao_id,
    agora,
    sessoes_ativas,
)
from app.core.clients.mongo import abrir_cliente_mongo
from app.core.configuracao import MONGO_BANCO_DADOS, MONGO_COLECAO_SESSOES

async def iniciar_sessao(
        sessao_id: str,
        usuario_id: int
) -> None:
    if await obter_documento_sessao_id(sessao_id, usuario_id):
        return

    documento_id = str(uuid.uuid4())
    agora_val  = agora()

    async with abrir_cliente_mongo() as cliente:
        banco = cliente[MONGO_BANCO_DADOS]
        colecao_sessoes = banco[MONGO_COLECAO_SESSOES]
        await colecao_sessoes.insert_one({
            "_id":           documento_id,
            "session_id":    sessao_id,
            "user_id":       usuario_id,
            "iniciada_em":   agora_val,
            "atualizada_em": agora_val,
            "esta_ativo":   True,
            "titulo":        "",
            "resumo":        "",
            "mensagens":     [],
            "anexos_pendentes": [],
            "solicitacao_pendente": None,
            "ocorrencia_pendente": None,
            "evento_pendente": None,
            "solicitacoes": [],
            "ocorrencias": [],
            "eventos": [],
        })
        sessoes_ativas[(usuario_id, sessao_id)] = documento_id
