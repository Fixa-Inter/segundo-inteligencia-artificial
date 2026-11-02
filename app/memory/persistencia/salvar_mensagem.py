from bson import BSON
from fastapi import HTTPException, status
from pymongo.errors import PyMongoError
from app.core import Emocao
from app.memory.persistencia.sessoes import iniciar_sessao
from app.memory.persistencia.utilitarios import obter_documento_sessao_id, agora
from app.memory.persistencia.rascunho_solicitacao import (
    adicionar_imagens_sessao,
)
from app.core.clients.mongo import abrir_cliente_mongo
from app.core.configuracao import MONGO_BANCO_DADOS, MONGO_COLECAO_SESSOES
from app.services.visualizacoes.publicacao import (
    validar_visualizacao_publica, LimiteVisualizacaoExcedido,
    MAXIMO_BYTES_CONVERSA_COM_VISUALIZACAO,
)

from app.core.respostas import MENSAGENS


async def salvar_mensagem(
    sessao_id: str,
    papel: str,
    conteudo: str,
    usuario_id: int,
    imagens: list[str] | None = None,
    *, associar_imagens: bool = True,
    emocao: Emocao | str | None = None,
    turno_id: str | None = None,
    visualizacao: dict | None = None,
) -> None:
    if visualizacao is not None:
        if papel != "assistant" or not turno_id:
            raise ValueError("Visualização exige mensagem do assistente e identificação do turno.")
        try:
            visualizacao = validar_visualizacao_publica(visualizacao).model_dump(mode="json")
        except LimiteVisualizacaoExcedido as erro:
            raise HTTPException(status_code=413, detail=str(erro)) from None
    try:
        documento_id = await obter_documento_sessao_id(sessao_id, usuario_id)
    except (PyMongoError, TimeoutError, OSError, RuntimeError):
        if visualizacao is None:
            raise
        raise HTTPException(status_code=503, detail=MENSAGENS['nao_foi_possivel_acessar_a_conversa_para_salvar_a_resposta']) from None
    if not documento_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MENSAGENS['inicie_uma_conversa_para_salvar_a_mensagem'],
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    mensagem = {"role": papel, "content": conteudo}
    if papel == "assistant":
        mensagem["emocao"] = Emocao(emocao or Emocao.NEUTRO).value
        mensagem["confirmacao"] = "nao"
        if turno_id:
            mensagem["turno_id"] = turno_id
        if visualizacao is not None:
            mensagem["visualizacao"] = visualizacao
    imagens_validas = [
        url.strip()
        for url in (imagens or [])
        if isinstance(url, str) and url.strip()
    ]
    if papel == "human" and imagens_validas:
        mensagem["imagens"] = imagens_validas

    try:
        async with abrir_cliente_mongo() as cliente:
            banco = cliente[MONGO_BANCO_DADOS]
            colecao_sessoes = banco[MONGO_COLECAO_SESSOES]
            mensagem["timestamp"] = agora()
            if visualizacao is not None:
                await _salvar_com_visualizacao(colecao_sessoes, documento_id, sessao_id, usuario_id, mensagem)
            else:
                await colecao_sessoes.update_one(
                    {"_id": documento_id, "user_id": usuario_id, "esta_ativo": True},
                    {
                        "$push": {"mensagens": mensagem},
                        "$set": {"atualizada_em": mensagem["timestamp"]},
                    },
                )
    except (PyMongoError, TimeoutError, OSError, RuntimeError):
        if visualizacao is None:
            raise
        raise HTTPException(status_code=503, detail=(
            MENSAGENS['nao_foi_possivel_confirmar_a_gravacao_da_resposta_consulte_o_historico_antes']
        )) from None

    if papel == "human" and imagens_validas and associar_imagens:
        await adicionar_imagens_sessao(
            sessao_id=sessao_id,
            usuario_id=usuario_id,
            imagens=imagens_validas,
        )


async def _salvar_com_visualizacao(colecao, documento_id, sessao_id, usuario_id, mensagem):
    if len(BSON.encode(mensagem)) > MAXIMO_BYTES_CONVERSA_COM_VISUALIZACAO:
        raise HTTPException(status_code=413, detail=MENSAGENS['a_resposta_excede_o_limite_de_tamanho_da_conversa'])
    instante = mensagem["timestamp"]
    base = {"_id": documento_id, "session_id": sessao_id, "user_id": usuario_id, "esta_ativo": True}
    proximo = {"$mergeObjects": ["$$ROOT", {
        "mensagens": {"$concatArrays": [{"$ifNull": ["$mensagens", []]}, {"$literal": [mensagem]}]},
        "atualizada_em": {"$literal": instante},
    }]}
    filtro = {**base, "mensagens.turno_id": {"$ne": mensagem["turno_id"]}, "$expr": {
        "$cond": [
            {"$lte": [{"$bsonSize": "$$ROOT"}, MAXIMO_BYTES_CONVERSA_COM_VISUALIZACAO]},
            {"$lte": [{"$bsonSize": proximo}, MAXIMO_BYTES_CONVERSA_COM_VISUALIZACAO]},
            False,
        ],
    }}
    try:
        resultado = await colecao.update_one(filtro, {
            "$push": {"mensagens": mensagem}, "$set": {"atualizada_em": instante},
        })
        if resultado.matched_count:
            return
        # Distingue repetição idêntica, conflito, conversa indisponível e limite,
        # sem ler ou substituir o histórico completo da conversa.
        existente = await colecao.find_one(base, {"mensagens": {"$elemMatch": {
            "role": "assistant", "turno_id": mensagem["turno_id"],
        }}})
    except (PyMongoError, TimeoutError, OSError):
        raise HTTPException(status_code=503, detail=(
            MENSAGENS['nao_foi_possivel_confirmar_a_gravacao_da_resposta_consulte_o_historico_antes']
        )) from None
    if existente is None:
        raise HTTPException(status_code=404, detail=MENSAGENS['conversa_nao_encontrada'])
    anteriores = existente.get("mensagens", [])
    if anteriores:
        # Uma repetição idêntica conserva o instante da primeira gravação.
        if len(anteriores) == 1 and (
            {k: v for k, v in anteriores[0].items() if k != "timestamp"}
            == {k: v for k, v in mensagem.items() if k != "timestamp"}
        ):
            return
        raise HTTPException(status_code=409, detail=MENSAGENS['ja_existe_uma_resposta_diferente_para_este_turno'])
    raise HTTPException(status_code=413, detail=(
        MENSAGENS['a_conversa_excederia_8_mib_inicie_outra_conversa_para_gerar_a_visualizacao']
    ))


async def marcar_confirmacao_mensagem(
    sessao_id: str, usuario_id: int, turno_id: str,
) -> None:
    documento_id = await obter_documento_sessao_id(sessao_id, usuario_id)
    if not documento_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MENSAGENS['conversa_nao_encontrada'])

    async with abrir_cliente_mongo() as cliente:
        colecao = cliente[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES]
        resultado = await colecao.update_one(
            {
                "_id": documento_id,
                "user_id": usuario_id,
                "esta_ativo": True,
                "mensagens": {"$elemMatch": {"role": "assistant", "turno_id": turno_id}},
            },
            {"$set": {"mensagens.$.confirmacao": "sim"}},
        )
    if resultado.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MENSAGENS['conversa_nao_encontrada'])
