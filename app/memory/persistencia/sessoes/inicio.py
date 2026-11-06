import uuid
from app.memory.persistencia import obter_documento_sessao_id, agora, sessoes_ativas
from app.core.clients import abrir_cliente_mongo
from app.core import MONGO_BANCO_DADOS, MONGO_COLECAO_SESSOES

async def iniciar_sessao(
        sessao_id: str,
        usuario_id: int
) -> None:
    """Cria documento da conversa e registra seu ID no cache local. Usado pelo fluxo de sessoes."""
    # Validação: Caso haja um documento na sessão interna da aplicação com esse sessao_id e usuario_id, não cria um novo documento (pois a conversa está ativa).
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
        # Registra a sessão criada como ativa no cache local.
        sessoes_ativas[(usuario_id, sessao_id)] = documento_id
